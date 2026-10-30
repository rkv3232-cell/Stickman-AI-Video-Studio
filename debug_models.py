import os
import sys
from dotenv import load_dotenv
from google import genai

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print("Checking available models on your API key...", flush=True)

try:
    client = genai.Client(api_key=api_key)
    models = list(client.models.list())
    print(f"Total models available: {len(models)}", flush=True)
    video_or_image_models = []
    for m in models:
        name = m.name if hasattr(m, 'name') else str(m)
        if any(keyword in name.lower() for keyword in ["veo", "video", "omni", "imagen"]):
            video_or_image_models.append(name)
    
    print("\nMatched Video / Image Models:", flush=True)
    for vm in video_or_image_models:
        print(f" - {vm}", flush=True)

    if not video_or_image_models:
        print("No dedicated video/image model names found in standard listing.", flush=True)
        print("First 10 models:", [m.name for m in models[:10]], flush=True)

except Exception as e:
    print(f"Error listing models: {e}", flush=True)

