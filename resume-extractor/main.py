from fastapi import FastAPI

from route.extractor import router as extractor_router


app = FastAPI(
    title="Resume Skill Extractor API",
    version="1.0.0",
    description="Extract structured information from resumes using the Gemini powered agent"
)


app.include_router(extractor_router)


@app.get("/")
async def root():
    return {
        "message": "Resume Skill Extractor API is running."
    }