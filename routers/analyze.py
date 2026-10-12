import asyncio
from fastapi import APIRouter, UploadFile, File, HTTPException
from services.pdf_service import extract_text, validate_pdf_upload, looks_scanned
from services.classifier import classify_pair
from services.parser import async_parse_resume, async_parse_jd
from services.scoring import extract_skills, match_skills, final_score
from services.evaluation import async_evaluate_resume
from services.bullets import extract_bullets, improve_all
from services.llm_service import async_call_llm_json

router = APIRouter()

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB per file


def _validate_upload(data: bytes, upload: UploadFile, label: str) -> None:
    ok, err = validate_pdf_upload(data, filename=upload.filename or "", max_bytes=MAX_UPLOAD_BYTES)
    if not ok:
        raise HTTPException(status_code=400, detail=f"{label}: {err}")


@router.post("/analyze/")
async def analyze(
    resume: UploadFile = File(...),
    jd: UploadFile = File(...),
    debug: bool = False,
):
    try:
        # 1. PDF -> Plain Text (with validation, no temp files)
        resume_bytes = await resume.read()
        jd_bytes = await jd.read()

        _validate_upload(resume_bytes, resume, "Resume")
        _validate_upload(jd_bytes, jd, "Job description")

        r_text = extract_text(resume_bytes)
        j_text = extract_text(jd_bytes)

        if not r_text.strip() or not j_text.strip():
            # Distinguish scanned/image-only PDFs from other extraction failures.
            if not r_text.strip() and not j_text.strip():
                detail = "Could not extract text from both PDFs. If scanned/image-only, export a text-based PDF or enable OCR."
            elif not r_text.strip():
                detail = "Could not extract text from resume PDF. If scanned/image-only, export a text-based PDF or enable OCR."
            else:
                detail = "Could not extract text from job-description PDF. If scanned/image-only, export a text-based PDF or enable OCR."
            raise HTTPException(status_code=400, detail=detail)
        if looks_scanned(r_text) or looks_scanned(j_text):
            # Warn but continue: extraction produced suspiciously little text.
            pass

        # 2. Document Validation (1 Call)
        cls = await asyncio.to_thread(classify_pair, r_text, j_text)

        if cls.get("document_a", {}).get("type") != "RESUME":
            return {"error": "First file is not a valid Resume"}
        if cls.get("document_b", {}).get("type") != "JOB_DESCRIPTION":
            return {"error": "Second file is not a valid Job Description"}

        # 3. Parse Resume & JD in Parallel using Native Async Functions
        r_json, j_json = await asyncio.gather(
            async_parse_resume(r_text),
            async_parse_jd(j_text),
        )

        # 4. Extract & Match Skills — deterministic, NO embeddings.
        r_skills = extract_skills(r_text)
        req_skills = j_json.get("required_skills", [])
        pref_skills = j_json.get("preferred_skills", [])
        skill_res = match_skills(r_skills, req_skills, pref_skills)

        # 5. LLM contextual evaluation (NO embeddings) + deterministic weighted score.
        # Formula: final = 0.35*required + 0.25*exp + 0.15*projects + 0.10*edu + 0.15*relevance
        llm_eval = await async_evaluate_resume(r_json, j_json, r_text, j_text)
        score_res = final_score(r_json, skill_res, None, j_json, llm_eval=llm_eval)

        # 6. LLM Review Prompt Helper (Safe with fallback)
        async def _review():
            prompt = (
                "You are an expert HR. Review this candidate against the job description:\n"
                f"Candidate: {r_json}\n"
                f"Job Requirements: {j_json}\n"
                f"Calculated Score: {score_res.get('final_score')}\n\n"
                "Return JSON strictly matching this schema:\n"
                "{\n"
                '  "verdict": "STRONG_MATCH / GOOD_MATCH / WEAK_MATCH",\n'
                '  "strengths": ["point 1", "point 2"],\n'
                '  "weaknesses": ["point 1", "point 2"],\n'
                '  "reason": "summary explanation"\n'
                "}"
            )
            try:
                res = await async_call_llm_json(prompt)
                if isinstance(res, dict) and "verdict" in res:
                    return res
                raise ValueError("Invalid format")
            except Exception:
                # Fallback if Gemini rate-limits or fails
                return {
                    "verdict": score_res.get("verdict", "REVIEW_REQUIRED"),
                    "strengths": [f"Matches skills: {', '.join(skill_res.get('matched_required', [])[:3])}"],
                    "weaknesses": [f"Missing: {', '.join(skill_res.get('missing_required', [])[:3])}"],
                    "reason": "Automated score calculated successfully.",
                }

        # 7. Extract & Improve Bullets (Top 5 max to prevent rate limits)
        bullets = extract_bullets(r_text)

        # Parallel Execution of Review and Bullet Improvement
        review, improved = await asyncio.gather(
            _review(),
            improve_all(bullets[:5], j_text),  # limit to top 5 to protect RPM
        )

        line_by_line = [
            {
                "original": b.get("original", ""),
                "improved": b.get("improved", ""),
                "changed": b.get("original") != b.get("improved"),
            }
            for b in improved
        ]
        suggestions = [b["improved"] for b in line_by_line if b["changed"]][:5]

        # 8. Role matching normalization
        r_roles = cls.get("document_a", {}).get("job_role", [])
        j_roles = cls.get("document_b", {}).get("job_role", [])
        r_roles = [r_roles] if isinstance(r_roles, str) else r_roles
        j_roles = [j_roles] if isinstance(j_roles, str) else j_roles

        role_match = bool(set(r_roles) & set(j_roles))

        # 9. Final Combined JSON Response (backwards-compatible keys kept)
        response = {
            "document_validation": {
                "resume_roles": r_roles,
                "jd_roles": j_roles,
                "role_match": role_match,
            },
            "candidate": {
                "name": r_json.get("name"),
                "email": r_json.get("email"),
                "experience_years": r_json.get("experience_years"),
                "projects_count": len(r_json.get("projects", [])),
            },
            "job_needs": {
                "title": j_json.get("job_title"),
                "required_skills": req_skills,
                "preferred_skills": pref_skills,
            },
            "analysis": {
                "matched_skills": skill_res.get("matched_required", []),
                "partial_skills": skill_res.get("partial_required", []),
                "missing_skills": skill_res.get("missing_required", []),
                "matched_preferred": skill_res.get("matched_preferred", []),
                "missing_preferred": skill_res.get("missing_preferred", []),
                # Backwards-compat: old clients read semantic_score; now LLM relevance.
                "semantic_score": llm_eval.jd_relevance.score,
                "category_scores": {
                    "required_skills": score_res["breakdown"]["required_skills"],
                    "experience": score_res["breakdown"]["experience"],
                    "projects": score_res["breakdown"]["projects"],
                    "education": score_res["breakdown"]["education"],
                    "jd_relevance": score_res["breakdown"]["jd_relevance"],
                },
                "missing_qualifications": llm_eval.missing_qualifications,
            },
            "score": {
                "final_score": score_res.get("final_score", 0),
                "verdict": review.get("verdict", score_res.get("verdict")),
                "breakdown": score_res.get("breakdown"),
                "formula": score_res.get("breakdown", {}).get("formula"),
            },
            "review": review,
            "improvements": {
                "line_by_line": line_by_line,
                "top_suggestions": suggestions,
                "summary": {
                    "total_bullets": len(line_by_line),
                    "improved_count": len(suggestions),
                },
            },
        }
        if debug:
            response["debug"] = {
                "skill_result": skill_res,
                "llm_evaluation": llm_eval.model_dump(),
            }
        return response

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        # Production safe: server doesn't crash 500 without info
        raise HTTPException(status_code=500, detail=f"Analysis pipeline error: {str(e)}")
