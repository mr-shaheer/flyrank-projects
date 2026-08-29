import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from route.extractor import router as extractor_router
from worker import worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the background worker
    asyncio.create_task(worker())
    yield


app = FastAPI(
    title="Resume Skill Extractor API",
    version="1.0.0",
    description="Extract structured information from resumes using the Gemini powered agent",
    lifespan=lifespan,
)

app.include_router(extractor_router)


@app.get("/")
async def root():
    return {
        "message": "Resume Skill Extractor API is running."
    }