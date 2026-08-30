"""LLM integration layer.

Scores how well a resume fits a job description and returns a short
human-readable reason.

Implementation notes:
- Uses the OpenAI Agents SDK (`openai-agents`) as the agent framework.
- The model is Google Gemini, called through its OpenAI-compatible
  endpoint (https://ai.google.dev/gemini-api/docs/openai) via
  `OpenAIChatCompletionsModel` wrapping an `AsyncOpenAI` client pointed
  at Gemini's base URL. This lets us use the OpenAI Agents SDK's `Agent` /
  `Runner` abstractions and structured `output_type` support with a
  non-OpenAI model, with no other code needing to change.
- Falls back to a deterministic keyword-overlap scorer when no
  GEMINI_API_KEY is set, or if the API call fails for any reason — so the
  rest of the pipeline (matching, reporting, email) always has a score to
  work with, with or without a live LLM.
"""
import re

from pydantic import BaseModel

from app.config import settings

_STOPWORDS = {
    "the", "and", "for", "with", "a", "to", "of", "in", "on", "is", "are",
    "we", "you", "your", "our", "will", "be", "as", "an", "or", "at", "this",
    "that", "have", "has", "from", "by", "it", "into",
}


class MatchScore(BaseModel):
    """Structured output the agent is constrained to return."""
    score: int
    reason: str


def _keywords(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+.#]{1,}", text.lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 2}


def _fallback_score(resume_text: str, job_title: str, job_description: str) -> tuple[float, str]:
    """Deterministic overlap-based scorer used when no LLM is available."""
    resume_kw = _keywords(resume_text)
    job_kw = _keywords(f"{job_title} {job_description or ''}")
    if not job_kw:
        return 0.0, "No job description text available to score against."
    overlap = resume_kw & job_kw
    score = round(100 * len(overlap) / max(len(job_kw), 1), 1)
    score = min(score, 100.0)
    top_terms = ", ".join(sorted(overlap))[:200] or "no strong keyword overlap"
    return score, f"[offline scorer] Keyword overlap with resume: {top_terms}"


_agent = None  # lazily built and cached — avoids re-creating the client per call


def _get_agent():
    global _agent
    if _agent is not None:
        return _agent

    from agents import Agent, OpenAIChatCompletionsModel, set_tracing_disabled
    from openai import AsyncOpenAI

    # Tracing defaults to exporting to OpenAI's platform, which needs an
    # OpenAI API key we don't have (and don't want) here — disable it.
    set_tracing_disabled(True)

    gemini_client = AsyncOpenAI(
        api_key=settings.GEMINI_API_KEY,
        base_url=settings.GEMINI_BASE_URL,
    )

    _agent = Agent(
        name="JobMatchScorer",
        instructions=(
            "You are a recruiting assistant. Given a candidate resume and a job "
            "posting, score how well the candidate fits the role from 0 to 100, "
            "and give one concise sentence (under 30 words) explaining the score. "
            "Be honest about gaps, not just strengths."
        ),
        model=OpenAIChatCompletionsModel(
            model=settings.LLM_MODEL,
            openai_client=gemini_client,
        ),
        output_type=MatchScore,
    )
    return _agent


def score_resume_against_job(resume_text: str, job_title: str, job_description: str) -> tuple[float, str]:
    """Returns (score 0-100, short reasoning string)."""
    if not settings.GEMINI_API_KEY:
        return _fallback_score(resume_text, job_title, job_description)

    try:
        from agents import Runner

        agent = _get_agent()
        prompt = (
            f"JOB TITLE: {job_title}\n"
            f"JOB DESCRIPTION:\n{(job_description or '')[:3000]}\n\n"
            f"CANDIDATE RESUME:\n{resume_text[:3000]}"
        )
        result = Runner.run_sync(agent, prompt)
        output: MatchScore = result.final_output
        return max(0.0, min(100.0, float(output.score))), output.reason.strip()
    except Exception as exc:  # noqa: BLE001 - never let a scoring failure break the pipeline
        score, reason = _fallback_score(resume_text, job_title, job_description)
        return score, f"{reason} (LLM call failed, used fallback: {exc})"
