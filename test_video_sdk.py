import os
import sys
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

print("--- Testing video model: gemini-omni-1.1-flash with delivery: uri ---", flush=True)
try:
    res = client.interactions.create(
        model="gemini-omni-1.1-flash",
        input=[{"type": "text", "text": "Continuous unbroken shot of glowing holographic particles, 9:16 vertical, no text"}],
        response_format={
            "type": "video",
            "delivery": "uri",
            "aspect_ratio": "9:16",
            "duration": 3
        }
    )
    print("Video call returned:", res)
except Exception as e:
    print(f"Error with gemini-omni-1.1-flash: {e}", flush=True)
