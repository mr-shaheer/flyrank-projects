from typing import Literal

from pydantic import BaseModel



class Node(BaseModel):
    id: str
    prompt: str

class Edge(BaseModel):
    source: str
    target: str
    condition: Literal["YES", "NO"]

class Workflow(BaseModel):
    nodes: list[Node]
    edges: list[Edge]
    start_node: str

class ExecutionStep(BaseModel):
    node_id: str
    prompt: str
    decision: Literal["YES", "NO"]

class ExecuteRequest(BaseModel):
    workflow: Workflow
    user_input: str