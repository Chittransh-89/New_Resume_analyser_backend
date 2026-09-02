import asyncio
from fastapi import APIRouter, UploadFile, File, HTTPException
from services.pdf_service import extract_text
from services.classifier import classify_pair
from services.parser import async_parse_resume, async_parse_jd
from services.scoring import extract_skills, match_skills, semantic_score, final_score
from services.bullets import extract_bullets, improve_all
from services.llm_service import async_call_llm_json

router = APIRouter()

@router.post("/analyze/")
async def analyze(
    resume: UploadFile = File(...), 
    jd: UploadFile = File(...), 
    debug: bool = False
):
    try:
        # 1. PDF -> Plain Text
        resume_bytes = await resume.read()
        jd_bytes = await jd.read()
        
        r_text = extract_text(resume_bytes)
        j_text = extract_text(jd_bytes)

        if not r_text.strip() or not j_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from one or both PDF files.")

        # 2. Document Validation (1 Call)
        cls = await asyncio.to_thread(classify_pair, r_text, j_text)
        
        if cls.get("document_a", {}).get("type") != "RESUME":
            return {"error": "First file is not a valid Resume"}
        if cls.get("document_b", {}).get("type") != "JOB_DESCRIPTION":
            return {"error": "Second file is not a valid Job Description"}

        # 3. Parse Resume & JD in Parallel using Native Async Functions
        r_json, j_json = await asyncio.gather(
            async_parse_resume(r_text),
            async_parse_jd(j_text)
        )

        # 4. Extract & Match Skills (CPU-bound / Instant)
        r_skills = extract_skills(r_text)
        req_skills = j_json.get("required_skills", [])
        pref_skills = j_json.get("preferred_skills", [])
        skill_res = match_skills(r_skills, req_skills, pref_skills)

        # 5. Semantic Scoring (Sentence Transformers on Worker Thread)
        sem_res = await asyncio.to_thread(semantic_score, r_json, j_json)
        score_res = final_score(r_json, skill_res, sem_res)

        # 6. LLM Review Prompt Helper (Safe with fallback)
        async def _review():
            prompt = (
                f"You are an expert HR. Review this candidate against the job description:\n"
                f"Candidate: {r_json}\n"
                f"Job Requirements: {j_json}\n"
                f"Calculated Score: {score_res.get('final_score')}\n\n"
                f"Return JSON strictly matching this schema:\n"
                f"{{\n"
                f'  "verdict": "STRONG_MATCH / GOOD_MATCH / WEAK_MATCH",\n'
                f'  "strengths": ["point 1", "point 2"],\n'
                f'  "weaknesses": ["point 1", "point 2"],\n'
                f'  "reason": "summary explanation"\n'
                f"}}"
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
                    "reason": "Automated score calculated successfully."
                }

        # 7. Extract & Improve Bullets (Top 5 max to prevent rate limits)
        bullets = extract_bullets(r_text)
        
        # Parallel Execution of Review and Bullet Improvement
        review, improved = await asyncio.gather(
            _review(),
            improve_all(bullets[:5], j_text)  # limit to top 5 to protect RPM
        )

        line_by_line = [
            {
                "original": b.get("original", ""),
                "improved": b.get("improved", ""),
                "changed": b.get("original") != b.get("improved")
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

        # 9. Final Combined JSON Response
        return {
            "document_validation": {
                "resume_roles": r_roles,
                "jd_roles": j_roles,
                "role_match": role_match
            },
            "candidate": {
                "name": r_json.get("name"),
                "email": r_json.get("email"),
                "experience_years": r_json.get("experience_years"),
                "projects_count": len(r_json.get("projects", []))
            },
            "job_needs": {
                "title": j_json.get("job_title"),
                "required_skills": req_skills,
                "preferred_skills": pref_skills
            },
            "analysis": {
                "matched_skills": skill_res.get("matched_required", []),
                "missing_skills": skill_res.get("missing_required", []),
                "semantic_score": sem_res.get("semantic_score", 0)
            },
            "score": {
                "final_score": score_res.get("final_score", 0),
                "verdict": review.get("verdict", score_res.get("verdict"))
            },
            "review": review,
            "improvements": {
                "line_by_line": line_by_line,
                "top_suggestions": suggestions,
                "summary": {
                    "total_bullets": len(line_by_line),
                    "improved_count": len(suggestions)
                }
            }
        }

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        # Production safe: server doesn't crash 500 without info
        raise HTTPException(status_code=500, detail=f"Analysis pipeline error: {str(e)}")