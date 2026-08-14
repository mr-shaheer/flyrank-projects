from pathlib import Path

from agents import Agent

from schemas.response import ResumeResponse
from model import model

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "extract-skills.md"
PROMPT_VERSION = "extract-skills"


def _load_instructions() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


extractor_agent = Agent(
    name="extractor",
    instructions=_load_instructions(),
    output_type=ResumeResponse,
    model=model,
)