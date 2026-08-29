from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from service.job_store import get_job
from service.job_store import create_job
from service.queue import job_queue
from schemas.request import ResumeRequest
from schemas.response import ResumeResponse
from service.extractor_service import ExtractorService, ValidationFailedError

router = APIRouter()


@router.get("/jobs/{job_id}", tags=["Resume Extractor"])
async def get_job_status(job_id: str):

    job = get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return {
        "job_id": job["id"],
        "status": job["status"],
        "result": job["result"],
        "error": job["error"],
    }

@router.post(
    "/extract-skills",
    tags = ["Resume Extractor"],
)
async def extract_skills(request: ResumeRequest):

    try:
        job_id = create_job(request.resume_text)

        await job_queue.put(job_id)

        return JSONResponse(
            status_code=202,
            content={
                "job_id": job_id,
                "status": "queued"
            }
        )

    except ValidationFailedError as e:
        raise HTTPException(status_code = 422, detail=str(e))

    except TimeoutError:
        raise HTTPException(status_code=504, detail="The AI request timed out.")

    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error.")