from dotenv import load_dotenv
import os

load_dotenv()

GENAI_API_KEY = os.getenv("GENAI_API_KEY")
if not GENAI_API_KEY:
    raise ValueError("Gemini API Key is not set in the environment variables")
