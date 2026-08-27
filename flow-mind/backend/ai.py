from typing import Literal
from pydantic import BaseModel
from backend.config import external_client, Model
import asyncio


class OutputSchema(BaseModel):
    result: Literal["YES", "NO"]


async def decide(node_prompt: str, user_input: str) -> str:
    response = await external_client.chat.completions.parse(
        model=Model,
        messages=[
               {
               "role": "system",
               "content": """
               You are a strict YES/NO decision engine.

               Your task is to determine whether the user's input satisfies the decision question.

               Rules:
               - Return YES only when the user's input clearly satisfies the question.
               - Return NO when it does not satisfy the question.
               - Do not assume missing information.
               - Do not infer that a message is a support request just because it is from a customer.
               - Return exactly one result: YES or NO.
               """
          },
            {
                "role": "user",
                "content": f"""
Context:
{user_input}

Decision question:
{node_prompt}
""",
            },
        ],
        response_format=OutputSchema,
    )

    return response.choices[0].message.parsed.result


if __name__ == "__main__":
    result = asyncio.run(
        decide(
          "Is the user reporting a problem or asking for help fixing an existing issue?",
          "What is the price of your premium plan?"
        )
    )

    print("Decision:", result)