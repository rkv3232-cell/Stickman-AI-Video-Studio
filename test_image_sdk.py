import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

models = ["gemini-2.5-flash-image", "gemini-3.1-flash-image", "gemini-nano-banana-2.1"]

for m in models:
    print(f"\n--- Testing model: {m} ---", flush=True)
    try:
        resp = client.models.generate_content(
            model=m,
            contents="A futuristic Indian cityscape at sunset, glowing neon holographic data streams, vertical 9:16 aspect ratio, cinematic background, no text, no characters",
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio="9:16")
            )
        )
        print("Call returned successfully!", flush=True)
        if resp.candidates and resp.candidates[0].content and resp.candidates[0].content.parts:
            for p in resp.candidates[0].content.parts:
                if hasattr(p, "inline_data") and p.inline_data:
                    data = p.inline_data.data
                    out_path = f"output/gemini_{m.replace('.', '_')}.png"
                    with open(out_path, "wb") as f:
                        f.write(data)
                    print(f"SUCCESS! Wrote {len(data)} bytes to {out_path}", flush=True)
                    sys.exit(0)
        print("No inline_data found in parts:", resp.candidates[0].content.parts, flush=True)
    except Exception as e:
        print(f"Error with {m}: {e}", flush=True)

