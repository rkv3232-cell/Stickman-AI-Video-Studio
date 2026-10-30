import os
import sys
from dotenv import load_dotenv
from google import genai

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print("API Key loaded:", api_key[:6] + "..." + api_key[-4:])

try:
    client = genai.Client(api_key=api_key)
    print("Testing basic generation with Gemini...")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Say hello in Hindi in 3 words"
    )
    print("Gemini Response:", response.text)
except Exception as e:
    print("Error testing Gemini:", e)
