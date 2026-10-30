import os
import sys
import base64
from dotenv import load_dotenv
from google import genai

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

prompt = "Cinematic 4k realistic shot of an advanced humanoid robot working on code at a desk in a dark futuristic cyber lab, neon lights, slow cinematic camera pan."

print(f"Testing video generation with prompt:\n'{prompt}'\n")

# Try interactions API with gemini-omni-1.1-flash or veo
video_models_to_test = [
    "gemini-omni-1.1-flash",
    "veo-3.1-fast-generate-preview",
    "veo-3.0-generate-preview",
    "veo-2.0-generate-001"
]

for model_name in video_models_to_test:
    print(f"--- Attempting with model: {model_name} ---")
    try:
        interaction = client.interactions.create(
            model=model_name,
            input=prompt
        )
        print("Success! Got interaction response.")
        if hasattr(interaction, "output_video") and interaction.output_video and hasattr(interaction.output_video, "data"):
            video_bytes = base64.b64decode(interaction.output_video.data)
            out_file = f"veo_test_{model_name.replace(':', '_')}.mp4"
            with open(out_file, "wb") as f:
                f.write(video_bytes)
            print(f"Saved video to {out_file} (Size: {len(video_bytes)} bytes)!")
            break
        else:
            print("Interaction response structure:", interaction)
            break
    except Exception as e:
        print(f"Model {model_name} failed: {e}\n")

