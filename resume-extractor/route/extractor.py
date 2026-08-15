from fastapi import APIRouter, HTTPException

from schemas.request import ResumeRequest
from schemas.response import ResumeResponse
from service.extractor_service import ExtractorService, ValidationFailedError

router = APIRouter()


@router.post(
    "/extract-skills",
    response_model = ResumeResponse,
    tags = ["Resume Extractor"],
)
async def extract_skills(request: ResumeRequest):

    try:
        return await ExtractorService.extract(request.resume_text)

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