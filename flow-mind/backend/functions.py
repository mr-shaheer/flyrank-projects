import inngest

from backend.inngest_client import inngest_client
from backend.nodes import ExecuteRequest
from backend.ai import decide

execution_store: dict[str, dict] = {}


@inngest_client.create_function(
    fn_id="execute-flowmind-workflow",
    trigger=inngest.TriggerEvent(
        event="flowmind/workflow.execute"
    ),
)
async def execute_workflow_function(
    ctx: inngest.Context,
):
    request = ExecuteRequest.model_validate(
        ctx.event.data
    )

    workflow = request.workflow
    user_input = request.user_input

    current_node_id = workflow.start_node

    execution = []
    visited = set()

    while current_node_id:

        if current_node_id in visited:
            raise RuntimeError(
                f"Workflow loop detected at node {current_node_id}"
            )

        visited.add(current_node_id)

        node = next(
            (
                node
                for node in workflow.nodes
                if node.id == current_node_id
            ),
            None,
        )

        if node is None:
            raise ValueError(
                f"Node {current_node_id} not found"
            )

        decision = await ctx.step.run(
            f"decision-node-{node.id}",
            lambda node_prompt=node.prompt: decide(
                node_prompt,
                user_input,
            ),
        )

        if decision not in {"YES", "NO"}:
            raise ValueError(
                f"Invalid AI decision: {decision}"
            )

        execution.append(
            {
                "node_id": node.id,
                "prompt": node.prompt,
                "decision": decision,
            }
        )

        next_edge = next(
            (
                edge
                for edge in workflow.edges
                if edge.source == current_node_id
                and edge.condition == decision
            ),
            None,
        )

        if next_edge is None:
            break

        current_node_id = next_edge.target

    execution_id = ctx.event.data["execution_id"]

    execution_store[execution_id] = {
        "success": True,
        "execution": execution,
        "completed": True,
    }

    return execution_store[execution_id]