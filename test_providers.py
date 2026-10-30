import os
import sys
import time
import base64
from dotenv import load_dotenv
from google import genai
from google.genai import types, errors

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
print(f"Loaded GEMINI_API_KEY: {api_key[:6]}...{api_key[-4:] if api_key else 'NONE'}", flush=True)

client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=60000))

# 1. Test Text Generation for Hinglish script
print("\n=== 1. Testing Script Generation (gemini-2.5-flash) ===", flush=True)
try:
    t0 = time.time()
    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Write a 1-sentence catchy Hinglish hook about AI in India. Use Roman Hinglish only, no Devanagari."
    )
    print(f"Success in {time.time()-t0:.2f}s: {resp.text.strip()}", flush=True)
except Exception as e:
    print(f"Failed: {e}", flush=True)

# 2. Test Image Generation Models
print("\n=== 2. Testing Image Generation ===", flush=True)
image_models = ["gemini-nano-banana-2.1", "gemini-3.1-flash-image", "gemini-2.5-flash-image"]
for model_name in image_models:
    print(f"\nTesting image model: {model_name}...", flush=True)
    t0 = time.time()
    try:
        interaction = client.interactions.create(
            model=model_name,
            input="A sleek vertical 9:16 cinematic digital art background of futuristic India with high-tech buildings and holographic networks, dark neon aesthetic, no text, no characters",
            response_format={"type": "image"}
        )
        print(f"Interaction returned in {time.time()-t0:.2f}s! Status: {getattr(interaction, 'status', 'N/A')}", flush=True)
        img = getattr(interaction, "output_image", None)
        if img and getattr(img, "data", None):
            raw = base64.b64decode(img.data)
            out_file = f"output/test_{model_name.replace(':', '_').replace('.', '_')}.png"
            with open(out_file, "wb") as f:
                f.write(raw)
            print(f"SUCCESS: Saved {len(raw)} bytes to {out_file}", flush=True)
            break
        elif img and getattr(img, "uri", None):
            print(f"SUCCESS with URI: {img.uri}", flush=True)
            break
        else:
            print(f"No image data in output_image: {img}", flush=True)
    except Exception as e:
        print(f"Model {model_name} failed: {e}", flush=True)

# 3. Test Video Generation Models
print("\n=== 3. Testing Video Generation ===", flush=True)
video_models = ["gemini-omni-1.1-flash", "veo-3.1-generate-preview", "veo-2.0-generate-001"]
for vmodel in video_models:
    print(f"\nTesting video model: {vmodel}...", flush=True)
    t0 = time.time()
    try:
        res = client.interactions.create(
            model=vmodel,
            input="Continuous unbroken shot of glowing holographic particles flowing over a motherboard in dark neon lighting, 9:16 vertical, no text, no characters",
            response_format={
                "type": "video",
                "aspect_ratio": "9:16",
                "duration": 3
            }
        )
        print(f"Video interaction returned in {time.time()-t0:.2f}s! Status: {getattr(res, 'status', 'N/A')}", flush=True)
        out_vid = getattr(res, "output_video", None)
        if out_vid and getattr(out_vid, "uri", None):
            print(f"SUCCESS: Generated video URI: {out_vid.uri}", flush=True)
            break
        else:
            print(f"Response: {res}", flush=True)
    except Exception as e:
        print(f"Model {vmodel} failed: {e}", flush=True)

