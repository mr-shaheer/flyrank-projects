import os
from dotenv import load_dotenv
from agents import AsyncOpenAI

load_dotenv()

external_client = AsyncOpenAI(
     api_key = os.getenv("GEMINI_API_KEY"),
     base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
)

Model = "gemini-2.5-flash"