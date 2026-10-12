# services/llm_service.py — one place for all LLM calls (Gemini or Ollama).
#
# Every other module must use call_llm_json / async_call_llm_json from here
# instead of creating its own API client.

import asyncio
import json
import logging
import re
import warnings

import config

logger = logging.getLogger(__name__)

warnings.filterwarnings("ignore")
logging.getLogger("google.genai").setLevel(logging.ERROR)
logging.getLogger("google").setLevel(logging.ERROR)


# --- Ollama client (local development) ---
try:
    from openai import OpenAI

    _ollama_client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
except Exception as e:
    print(f"[llm] Ollama init failed: {e}")
    logger.exception("[llm] Ollama init failed: %s", e)
    _ollama_client = None


# --- Gemini client (deployment) ---
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


# Which provider to use. Set LLM_PROVIDER in config.py ("gemini" or "ollama").
LLM_PROVIDER = getattr(config, "LLM_PROVIDER", "ollama")


def _ensure():
    """Fail fast with a clear message if the configured provider is unusable."""
    if LLM_PROVIDER == "ollama":
        if not _ollama_client:
            raise RuntimeError("Ollama client unavailable — make sure Ollama is installed and running.")
    elif LLM_PROVIDER == "gemini":
        if not getattr(config, "GEMINI_API_KEY", None) or not _client:
            raise RuntimeError("GEMINI_API_KEY missing — set in .env")
    else:
        raise RuntimeError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")


def _repair_and_parse_json(raw_text: str) -> dict:
    """Parse LLM output as JSON, repairing common mistakes (code fences,
    trailing commas, stray newlines). Raises ValueError if unparseable."""
    cleaned = raw_text.strip()

    # Strip markdown code fences like ```json ... ```
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    # Keep only the part between the first { and the last }.
    start = cleaned.find("{")
    end = cleaned.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"No JSON brackets found in response: {raw_text[:400]}")
    json_str = cleaned[start:end]

    # Try 1: parse as-is.
    try:
        return json.loads(json_str)
    except Exception:
        pass

    # Try 2: remove trailing commas and flatten newlines, then parse.
    try:
        fixed = re.sub(r",\s*([\]}])", r"\1", json_str)
        fixed = re.sub(r"(?<!\\)\n", " ", fixed)
        return json.loads(fixed)
    except Exception:
        pass

    # Try 3: fall back to Python literal parsing.
    try:
        import ast

        return ast.literal_eval(json_str)
    except Exception:
        raise ValueError(f"Failed to parse JSON even after repair: {json_str[:300]}")


def call_llm(prompt: str, model: str = None, temperature: float = 0.05,
             max_tokens: int = 8192, is_json: bool = False) -> str:
    """Send one prompt to the configured LLM and return raw text."""
    _ensure()

    if LLM_PROVIDER == "ollama":
        name = model or getattr(config, "OLLAMA_MODEL", "gemma4:e4b")
        try:
            response = _ollama_client.chat.completions.create(
                model=name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as e:
            raise e
        if not response or not response.choices:
            return "{}"
        content = response.choices[0].message.content
        return content.strip() if content else "{}"

    elif LLM_PROVIDER == "gemini":
        name = model or getattr(config, "LLM_MODEL", "gemini-2.5-flash")
        gen_config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        if is_json:
            gen_config.response_mime_type = "application/json"
        try:
            response = _client.models.generate_content(model=name, contents=prompt, config=gen_config)
        except Exception as e:
            raise e
        return response.text.strip() if (response and response.text) else "{}"


async def async_call_llm(prompt: str, model: str = None, temperature: float = 0.05,
                         max_tokens: int = 8192) -> str:
    """Async version of call_llm (runs the blocking call in a worker thread)."""
    return await asyncio.to_thread(
        call_llm, prompt=prompt, model=model,
        temperature=temperature, max_tokens=max_tokens, is_json=False,
    )


def call_llm_json(prompt: str, model: str = None, temperature: float = 0.05,
                  max_tokens: int = 8192) -> dict:
    """Call the LLM in JSON mode and return the parsed dict."""
    raw = call_llm(prompt, model=model, temperature=temperature,
                   max_tokens=max_tokens, is_json=True)
    return _repair_and_parse_json(raw)


async def async_call_llm_json(prompt: str, model: str = None, temperature: float = 0.05,
                              max_tokens: int = 8192) -> dict:
    """Async version of call_llm_json (runs the blocking call in a worker thread)."""
    return await asyncio.to_thread(
        call_llm_json, prompt=prompt, model=model,
        temperature=temperature, max_tokens=max_tokens,
    )
