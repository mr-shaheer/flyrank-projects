import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import (
    auth_router, resume_router, jobs_router, matches_router,
    applications_router, reports_router,
)
from app.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="JobRadar",
    description="AI-powered job match & application tracker — internship capstone.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth_router.router)
app.include_router(resume_router.router)
app.include_router(jobs_router.router)
app.include_router(matches_router.router)
app.include_router(applications_router.router)
app.include_router(reports_router.router)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "service": "JobRadar"}
