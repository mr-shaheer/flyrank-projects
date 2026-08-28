export const API_URL = "http://localhost:8000";

export async function executeWorkflow(workflow: any, userInput: string) {
  const response = await fetch(`${API_URL}/execute`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      workflow,
      user_input: userInput,
    }),
  });

  if (!response.ok) {
    throw new Error("Workflow execution failed");
  }

  return response.json();
}