import os
import asyncio
import json
import random
from pathlib import Path

import time
from datetime import datetime, timezone

from agents import Runner
from dotenv import load_dotenv
from pydantic import ValidationError

from agent.extractor_agent import extractor_agent, PROMPT_VERSION
from schemas.response import ResumeResponse

load_dotenv()

LOG_DIR = Path("logs")
QUARANTINE_LOG = LOG_DIR / "quarantine.jsonl"
COST_LOG = LOG_DIR / "cost.jsonl"

RETRYABLE_STATUS = {429, 500, 502, 503, 504}
NON_RETRYABLE_STATUS = {400, 401, 403}


class ValidationFailedError(Exception):
    """Raised when the model's output fails schema validation twice (repair also failed)."""


def _status_code_of(exc: Exception) -> int | None:
    for attr_path in ("status_code", "response.status_code"):
        obj = exc
        for part in attr_path.split("."):
            obj = getattr(obj, part, None)
            if obj is None:
                break
        if isinstance(obj, int):
            return obj
    return None


def _is_retryable(exc: Exception) -> bool:
    if isinstance(exc, asyncio.TimeoutError):
        return True
    code = _status_code_of(exc)
    if code in NON_RETRYABLE_STATUS:
        return False
    if code in RETRYABLE_STATUS:
        return True
    return True


def _log_jsonl(path: Path, record: dict) -> None:
    LOG_DIR.mkdir(exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def _extract_usage(result):
    usage = getattr(result, "usage", None)

    if usage:
        return {
            "input_tokens": getattr(usage, "input_tokens", None),
            "output_tokens": getattr(usage, "output_tokens", None),
        }

    raw_responses = getattr(result, "raw_responses", None)
    if raw_responses:
        for response in raw_responses:
            u = getattr(response, "usage", None)
            if u:
                return {
                    "input_tokens": getattr(u, "input_tokens", None),
                    "output_tokens": getattr(u, "output_tokens", None),
                }

    return {
        "input_tokens": None,
        "output_tokens": None,
    }

class ExtractorService:

    @staticmethod
    async def extract(resume_text: str) -> ResumeResponse:

        if os.getenv("LLM_ENABLED", "true").lower() != "true":
            raise RuntimeError("LLM service is disabled.")

        if os.getenv("LLM_STUB") == "1":
            return ResumeResponse(
                skills = ["Python", "FastAPI"],
                experience_level = "Mid",
                years_of_experience = 3,
                confidence = 1.0,
                needs_review = False,
            )

        timeout = int(os.getenv("LLM_TIMEOUT", 30))
        max_retries = int(os.getenv("LLM_MAX_RETRIES", 3))

        last_error: Exception | None = None

        for attempt in range(max_retries):
            start = time.monotonic()
            repaired = False
            try:
                result, repaired = await ExtractorService._run_with_repair(
                    resume_text, timeout
                )
                duration_ms = int((time.monotonic() - start) * 1000)

                usage = _extract_usage(result)
                _log_jsonl(COST_LOG, {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "prompt_version": PROMPT_VERSION,
                    "model": os.getenv("LLM_MODEL", "gemini-2.5-flash"),
                    "input_tokens": usage["input_tokens"],
                    "output_tokens": usage["output_tokens"],
                    "duration_ms": duration_ms,
                    "repaired": repaired,
                    "attempt": attempt + 1,
                })

                return result.final_output

            except ValidationFailedError:
                raise

            except asyncio.TimeoutError:
                last_error = TimeoutError(
                    f"AI request timed out after {timeout} seconds."
                )
                if not _is_retryable(last_error):
                    raise last_error

            except Exception as e:
                last_error = e
                if not _is_retryable(e):
                    raise

            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) + random.uniform(0, 0.5)
                print(f"Retry {attempt + 1}/{max_retries} in {wait_time:.2f}s...")
                await asyncio.sleep(wait_time)

        raise last_error

    @staticmethod
    async def _run_with_repair(resume_text: str, timeout: int):

        try:
            result = await asyncio.wait_for(
                Runner.run(extractor_agent, input=resume_text),
                timeout = timeout,
            )
            return result, False

        except ValidationError as first_error:
            repair_input = (
                f"{resume_text}\n\n---\n"
                f"Your previous answer was rejected for this reason: {first_error}\n"
                f"Return only corrected JSON matching the schema."
            )
            try:
                result = await asyncio.wait_for(
                    Runner.run(extractor_agent, input=repair_input),
                    timeout = timeout,
                )
                return result, True

            except ValidationError as second_error:
                _log_jsonl(QUARANTINE_LOG, {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "prompt_version": PROMPT_VERSION,
                    "input": resume_text,
                    "first_error": str(first_error),
                    "second_error": str(second_error),
                })
                raise ValidationFailedError(
                    "Model output failed validation twice; quarantined."
                ) from second_error