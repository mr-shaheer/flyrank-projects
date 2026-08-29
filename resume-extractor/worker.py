import asyncio

from service.queue import job_queue
from service.job_store import (
    get_job,
    update_status,
    save_result,
    save_error,
    increment_retry,
)
from service.extractor_service import (
    ExtractorService
)

MAX_RETRIES = 3


async def worker():

    while True:

        job_id = await job_queue.get()

        job = get_job(job_id)

        if job is None:
            job_queue.task_done()
            continue

        update_status(job_id, "processing")

        try:

            result = await ExtractorService.extract(
                job["resume_text"]
            )

            save_result(job_id, result)

        except Exception as e:

            increment_retry(job_id)

            if job["retries"] < MAX_RETRIES:

                update_status(job_id, "queued")

                await job_queue.put(job_id)

            else:

                save_error(job_id, str(e))

                # Simple alert
                print(f"[ALERT] Job {job_id} failed: {e}")

        finally:

            job_queue.task_done()