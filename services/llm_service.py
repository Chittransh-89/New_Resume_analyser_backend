# # services/llm_service.py — Production-Grade Gemini LLM Service
# import json
# import re
# import asyncio
# import logging
# import warnings
# import config

# # Unnecessary warnings suppress
# warnings.filterwarnings("ignore")
# logging.getLogger("google.genai").setLevel(logging.ERROR)
# logging.getLogger("google").setLevel(logging.ERROR)

# try:
#     from google import genai
#     from google.genai import types

#     if getattr(config, "GEMINI_API_KEY", None):
#         _client = genai.Client(api_key=config.GEMINI_API_KEY)
#     else:
#         _client = None
# except Exception as e:
#     print(f"[llm] genai init failed: {e}")
#     _client = None


# def _ensure():
#     if not getattr(config, "GEMINI_API_KEY", None) or not _client:
#         raise RuntimeError("GEMINI_API_KEY missing — set in .env")


# def _repair_and_parse_json(raw_text: str) -> dict:
#     """Robust JSON cleaner that fixes common LLM syntax errors."""
#     cleaned = raw_text.strip()
    
#     # 1. Strip Markdown code fences
#     if cleaned.startswith("```json"):
#         cleaned = cleaned[7:]
#     elif cleaned.startswith("```"):
#         cleaned = cleaned[3:]
#     if cleaned.endswith("```"):
#         cleaned = cleaned[:-3]
#     cleaned = cleaned.strip()

#     # 2. Extract substring between first '{' and last '}'
#     s = cleaned.find("{")
#     e = cleaned.rfind("}") + 1
#     if s == -1 or e == 0:
#         raise ValueError(f"No JSON brackets found in response: {raw_text[:400]}")
    
#     json_str = cleaned[s:e]

#     # 3. First Try: Standard parsing
#     try:
#         return json.loads(json_str)
#     except Exception:
#         pass

#     # 4. Second Try: Auto-clean trailing commas & control characters
#     try:
#         # Remove trailing commas before } or ]
#         fixed = re.sub(r',\s*([\]}])', r'\1', json_str)
#         # Fix unescaped newlines in strings
#         fixed = re.sub(r'(?<!\\)\n', r' ', fixed)
#         return json.loads(fixed)
#     except Exception:
#         pass

#     # 5. Third Try: Aggressive sanitize
#     try:
#         import ast
#         return ast.literal_eval(json_str)
#     except Exception:
#         raise ValueError(f"Failed to parse JSON even after repair: {json_str[:300]}")


# def call_llm(prompt: str, model: str = None, temperature: float = 0.05, max_tokens: int = 8192, is_json: bool = False) -> str:
#     """Synchronous Gemini call."""
#     _ensure()
#     m = model or getattr(config, "LLM_MODEL", "gemini-2.5-flash")
    
#     gen_config = types.GenerateContentConfig(
#         temperature=temperature,
#         max_output_tokens=max_tokens,
#     )
    
#     if is_json:
#         gen_config.response_mime_type = "application/json"

#     try:
#         response = _client.models.generate_content(
#             model=m,
#             contents=prompt,
#             config=gen_config
#         )
#         return response.text.strip() if (response and response.text) else "{}"
#     except Exception as e:
#         raise e


# async def async_call_llm(prompt: str, model: str = None, temperature: float = 0.05, max_tokens: int = 8192) -> str:
#     """Asynchronous Gemini call."""
#     return await asyncio.to_thread(call_llm, prompt, model, temperature, max_tokens, False)


# def call_llm_json(prompt: str, model: str = None) -> dict:
#     """Sync call returning parsed JSON dict."""
#     raw = call_llm(prompt, model=model, is_json=True)
#     return _repair_and_parse_json(raw)


# async def async_call_llm_json(prompt: str, model: str = None) -> dict:
#     """Async call returning parsed JSON dict."""
#     return await asyncio.to_thread(call_llm_json, prompt, model)

# services/llm_service.py — Production-Grade LLM Service

import json
import re
import asyncio
import logging
import warnings

import config

logger = logging.getLogger(__name__)

# ==========================================================
# GENERAL CONFIG
# ==========================================================

warnings.filterwarnings("ignore")

logging.getLogger("google.genai").setLevel(logging.ERROR)
logging.getLogger("google").setLevel(logging.ERROR)


# ==========================================================
# DEVELOPMENT: OLLAMA
# ==========================================================
# Ollama provides an OpenAI-compatible API.
#
# Development:
#   ollama serve
#
# Example model:
#   gemma4:e4b
#
# When deploying:
#   Comment this section
#   and enable the Gemini section below.
# ==========================================================

try:
    from openai import OpenAI

    _ollama_client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama"
    )

except Exception as e:
    print(f"[llm] Ollama init failed: {e}")
    logger.exception("[llm] Ollama init failed: %s", e)
    _ollama_client = None


# ==========================================================
# DEPLOYMENT: GEMINI
# ==========================================================
# Keep this code for deployment.
#
# Development:
#   Comment this section if using Ollama.
#
# Deployment:
#   Comment OFF the Ollama section above
#   and enable this section.
# ==========================================================

try:
    from google import genai
    from google.genai import types

    if getattr(config, "GEMINI_API_KEY", None):
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    else:
        _client = None

except Exception as e:
    print(f"[llm] genai init failed: {e}")
    logger.exception("[llm] genai init failed: %s", e)
    _client = None


# ==========================================================
# LLM PROVIDER
# ==========================================================
#
# DEVELOPMENT:
#   "ollama"
#
# DEPLOYMENT:
#   "gemini"
#
# You can put this in config.py later if you want.
# ==========================================================

LLM_PROVIDER = getattr(config, "LLM_PROVIDER", "ollama")


# ==========================================================
# ENSURE CLIENT
# ==========================================================

def _ensure():

    if LLM_PROVIDER == "ollama":

        if not _ollama_client:
            raise RuntimeError(
                "Ollama client unavailable — make sure Ollama is installed "
                "and running."
            )

    elif LLM_PROVIDER == "gemini":

        if not getattr(config, "GEMINI_API_KEY", None) or not _client:
            raise RuntimeError(
                "GEMINI_API_KEY missing — set in .env"
            )

    else:

        raise RuntimeError(
            f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}"
        )


# ==========================================================
# JSON REPAIR
# ==========================================================

def _repair_and_parse_json(raw_text: str) -> dict:
    """Robust JSON cleaner that fixes common LLM syntax errors."""

    cleaned = raw_text.strip()

    # 1. Strip Markdown code fences

    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]

    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    cleaned = cleaned.strip()

    # 2. Extract substring between first '{' and last '}'

    s = cleaned.find("{")
    e = cleaned.rfind("}") + 1

    if s == -1 or e == 0:
        raise ValueError(
            f"No JSON brackets found in response: {raw_text[:400]}"
        )

    json_str = cleaned[s:e]

    # 3. First Try: Standard parsing

    try:
        return json.loads(json_str)

    except Exception:
        pass

    # 4. Second Try: Auto-clean trailing commas & control characters

    try:

        # Remove trailing commas before } or ]

        fixed = re.sub(
            r',\s*([\]}])',
            r'\1',
            json_str
        )

        # Fix unescaped newlines in strings

        fixed = re.sub(
            r'(?<!\\)\n',
            r' ',
            fixed
        )

        return json.loads(fixed)

    except Exception:
        pass

    # 5. Third Try: Aggressive sanitize

    try:

        import ast

        return ast.literal_eval(json_str)

    except Exception:

        raise ValueError(
            f"Failed to parse JSON even after repair: {json_str[:300]}"
        )


# ==========================================================
# MAIN LLM CALL
# ==========================================================

def call_llm(
    prompt: str,
    model: str = None,
    temperature: float = 0.05,
    max_tokens: int = 8192,
    is_json: bool = False
) -> str:

    """
    Central LLM call.

    The rest of the application should ONLY use this function
    instead of creating its own Gemini/Ollama client.
    """

    _ensure()

    # ======================================================
    # DEVELOPMENT: OLLAMA
    # ======================================================

    if LLM_PROVIDER == "ollama":

        m = model or getattr(
            config,
            "OLLAMA_MODEL",
            "gemma4:e4b"
        )

        try:

            response = _ollama_client.chat.completions.create(

                model=m,

                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                temperature=temperature,

                max_tokens=max_tokens
            )

            if not response or not response.choices:
                return "{}"

            content = response.choices[0].message.content

            return content.strip() if content else "{}"


        except Exception as e:

            raise e


    # ======================================================
    # DEPLOYMENT: GEMINI
    # ======================================================

    elif LLM_PROVIDER == "gemini":

        m = model or getattr(
            config,
            "LLM_MODEL",
            "gemini-2.5-flash"
        )

        gen_config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        if is_json:
            gen_config.response_mime_type = "application/json"

        try:

            response = _client.models.generate_content(

                model=m,

                contents=prompt,

                config=gen_config
            )

            return (
                response.text.strip()
                if (response and response.text)
                else "{}"
            )

        except Exception as e:

            raise e


# ==========================================================
# ASYNC LLM CALL
# ==========================================================

async def async_call_llm(
    prompt: str,
    model: str = None,
    temperature: float = 0.05,
    max_tokens: int = 8192
) -> str:

    """Asynchronous LLM call."""

    return await asyncio.to_thread(
        call_llm,
        prompt=prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        is_json=False
    )


# ==========================================================
# JSON LLM CALL
# ==========================================================

def call_llm_json(
    prompt: str,
    model: str = None
) -> dict:

    """Sync LLM call returning parsed JSON dict."""

    raw = call_llm(
        prompt,
        model=model,
        is_json=True
    )

    return _repair_and_parse_json(raw)


# ==========================================================
# ASYNC JSON LLM CALL
# ==========================================================

async def async_call_llm_json(
    prompt: str,
    model: str = None
) -> dict:

    """Async LLM call returning parsed JSON dict."""

    return await asyncio.to_thread(
        call_llm_json,
        prompt=prompt,
        model=model
    )