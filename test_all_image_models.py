import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

image_models = [
    "gemini-nano-banana-2.1",
    "gemini-3.1-flash-image",
    "gemini-3.1-flash-lite-image",
    "gemini-3-pro-image",
    "gemini-2.5-flash-image",
    "nano-banana-pro-preview"
]

print("=== Testing all available image models for active quota ===", flush=True)

for m in image_models:
    print(f"\nModel: {m}...", flush=True)
    try:
        resp = client.models.generate_content(
            model=m,
            contents="A futuristic Indian technology hub, 9:16 vertical, no text",
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio="9:16")
            )
        )
        print(f"SUCCESS with {m}!")
        if resp.candidates and resp.candidates[0].content and resp.candidates[0].content.parts:
            for p in resp.candidates[0].content.parts:
                if hasattr(p, "inline_data") and p.inline_data:
                    data = p.inline_data.data
                    out_path = f"output/gemini_success_{m.replace('.', '_')}.png"
                    with open(out_path, "wb") as f:
                        f.write(data)
                    print(f"Saved {len(data)} bytes to {out_path}!")
                    break
        break
    except Exception as e:
        err_str = str(e)
        if "429" in err_str:
            print(f"FAILED (429 Quota Exceeded / Free Tier Limit 0)")
        elif "404" in err_str:
            print(f"FAILED (404 Not Found / Model Inactive)")
        else:
            print(f"FAILED ({err_str[:120]})")

