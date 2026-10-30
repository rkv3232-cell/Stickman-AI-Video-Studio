import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SARVAM_API_KEY")
if not API_KEY:
    print("Error: SARVAM_API_KEY not found in .env")
    exit(1)

url = "https://api.sarvam.ai/text-to-speech"

headers = {
    "api-subscription-key": API_KEY,
    "Content-Type": "application/json"
}

sample_text = "नमस्ते दोस्तों! क्या आप जानते हैं कि 2026 में Artificial Intelligence हमारी ज़िंदगी को कैसे बदलने वाला है? चलिए जानते हैं इस वीडियो में।"

payload = {
    "inputs": [sample_text],
    "target_language_code": "hi-IN",
    "speaker": "aditya",
    "model": "bulbul:v3",
    "pace": 1.0,
    "speech_sample_rate": 22050,
    "enable_preprocessing": True
}

print("Calling Sarvam AI TTS API...")
response = requests.post(url, json=payload, headers=headers)

print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    res_data = response.json()
    audios = res_data.get("audios", [])
    if audios:
        audio_bytes = base64.b64decode(audios[0])
        output_file = "test_audio.wav"
        with open(output_file, "wb") as f:
            f.write(audio_bytes)
        print(f"Success! Audio saved as {output_file} (Size: {len(audio_bytes)} bytes)")
    else:
        print("No audio returned in response:", res_data)
else:
    print("Error response:", response.text)
