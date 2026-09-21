import os
from dotenv import load_dotenv

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
groq_model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

print("Groq API key loaded:", bool(groq_api_key))
print("Groq model:", groq_model)
