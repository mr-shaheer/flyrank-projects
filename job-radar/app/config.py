import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # --- App ---
    APP_NAME: str = "JobRadar"

    # --- Database ---
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./jobradar.db")

    # --- Auth ---
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    # --- LLM (used to score resume-vs-job fit) ---
    # Gemini is called through its OpenAI-compatible endpoint, via the
    # OpenAI Agents SDK's OpenAIChatCompletionsModel.
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
    GEMINI_BASE_URL: str = os.getenv(
        "GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-2.5-flash")

    # --- Email (used to send the daily PDF digest) ---
    SMTP_HOST: str | None = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str | None = os.getenv("SMTP_USER")
    SMTP_PASSWORD: str | None = os.getenv("SMTP_PASSWORD")
    SMTP_FROM: str | None = os.getenv("SMTP_FROM", os.getenv("SMTP_USER"))

    # --- Scraper ---
    REMOTEOK_URL: str = "https://remoteok.com/api"
    SCRAPE_LIMIT: int = int(os.getenv("SCRAPE_LIMIT", "40"))

    # --- Scheduler ---
    DAILY_RUN_HOUR: int = int(os.getenv("DAILY_RUN_HOUR", "7"))  # 7am server time

    # --- Cache ---
    JOB_LIST_CACHE_TTL_SECONDS: int = int(os.getenv("JOB_LIST_CACHE_TTL_SECONDS", "300"))

    # --- Reports ---
    REPORTS_DIR: str = os.getenv("REPORTS_DIR", "./reports")


settings = Settings()
os.makedirs(settings.REPORTS_DIR, exist_ok=True)
