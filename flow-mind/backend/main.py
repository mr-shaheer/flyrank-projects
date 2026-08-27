from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import inngest
import inngest.fast_api

from backend.inngest_client import inngest_client
from backend.nodes import ExecuteRequest
from backend.functions import (
    execute_workflow_function,
    execution_store,
)

app = FastAPI(
    title="FlowMind API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "FlowMind API is running"
    }



inngest.fast_api.serve(
    app,
    inngest_client,
    [
        execute_workflow_function,
    ],
)


@app.post("/execute")
async def execute(request: ExecuteRequest):

    event = inngest.Event(
        name="flowmind/workflow.execute",
        data={
            **request.model_dump(),
            "execution_id": str(id(request)),
        },
    )

    await inngest_client.send(event)

    return {
        "success": True,
        "event_id": str(id(request)),
    }


@app.get("/execute/{event_id}")
async def get_execution(event_id: str):

    result = execution_store.get(event_id)

    if result is None:
        return {
            "success": True,
            "completed": False,
            "execution": [],
        }

    return result