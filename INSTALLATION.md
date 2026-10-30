# 📦 INSTALLATION & SETUP GUIDE
## Stickman AI Video Production Studio (Raj Everyway Study)

This guide walks you through setting up and running the Stickman AI Video Production Studio on Windows.

---

## 1. System Requirements

- **Operating System**: Windows 10 or Windows 11 (64-bit)
- **Python**: Python 3.10 to 3.12 (Installed at `C:\Users\Play Edit Solution\AppData\Local\Programs\Python\Python312` or system path)
- **RAM**: Minimum 8 GB (16 GB recommended for video rendering)
- **Disk Space**: At least 3 GB free space for assets, models, and renders
- **Fonts**: Standard Windows fonts (`C:\Windows\Fonts\Nirmala.ttc`, `arial.ttf`, `impact.ttf`) - already present on Windows.

---

## 2. Fast 1-Click Launch (Batch Files)

For everyday non-technical use, two 1-click batch scripts are provided in the root directory:

| Action | File | Description |
|---|---|---|
| **Launch Web UI** | `run_ui.bat` | Starts the interactive web studio at `http://127.0.0.1:8000` |
| **Run CLI Generator** | `run_cli.bat` | Runs automated production on a curated viral topic |

---

## 3. Step-by-Step Manual Installation

### Step 1: Open Terminal in Project Root
```powershell
cd "E:\raj verma\Raj Projects\New folder"
```

### Step 2: Initialize Virtual Environment
If `.venv` is not created:
```powershell
python -m venv .venv
```
Activate the virtual environment:
```powershell
.\.venv\Scripts\activate
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

#### Core Libraries Installed:
- `moviepy>=2.1.0` (Multi-track video composition & rendering)
- `Pillow>=10.0.0` (Articulated Stickman 2D vector rig & thumbnail generation)
- `google-genai>=0.1.0` (Gemini 2.5 Flash for scriptwriting & storyboard direction)
- `edge-tts>=6.1.0` (100% Free keyless neural Hindi TTS voices)
- `fastapi` & `uvicorn` (Modern Web Studio UI backend)
- `requests` (Pollinations AI 4K artwork & Pexels video fetcher)
- `python-dotenv` (Secure environment credential manager)
- `numpy` & `scipy` (Audio spectrum analysis & motion transformations)

---

## 4. API Credentials Setup (`.env`)

Create or edit `.env` in the root folder:

```env
# Required for Gemini 2.5 Flash Script & Storyboard generation (Free from Google AI Studio)
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Sarvam AI Bulbul v3 Indian TTS Voice Engine
SARVAM_API_KEY=your_sarvam_api_key_here

# Optional: Pexels API Key for vertical stock video B-Roll
PEXELS_API_KEY=your_pexels_api_key_here
```

> **Note on Free / Keyless Operation**:
> Even without `SARVAM_API_KEY`, the system automatically falls back to **Microsoft Edge-TTS** (`edge_swara`, `edge_madhur`) which is 100% free, requires no API key, and has no character limits.
> Even without `PEXELS_API_KEY`, the system uses **Pollinations.ai** and **procedural cyberpunk motion scenes** which are 100% free and keyless.

---

## 5. Running the Application

### Option A: Interactive Web UI (Recommended)
```powershell
.\.venv\Scripts\python.exe web_app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:8000
```
- Browse live trending topics from Google Trends & Hacker News.
- Type any topic and click **"Generate AI Script, SEO & Thumbnail"**.
- Choose your Stickman Style (`Modern Beanie Zeke`, `Classic Minimalist`, `Cyber Neon`).
- Choose your Background Style (`Full-Motion Cyberpunk`, `AI Photorealistic`, `Sketch Notes`).
- Click **"RENDER 1080x1920 SHORT & THUMBNAIL"**.

### Option B: Command-Line Interface (1-Click Automation)
```powershell
# Custom topic
.\.venv\Scripts\python.exe main.py --prompt "भारत में AI का भविष्य"

# Custom voice and style
.\.venv\Scripts\python.exe main.py --prompt "Top 3 Coding Hacks" --speaker edge_madhur --style motion --stickman-style modern_beanie

# Using a curated viral template
.\.venv\Scripts\python.exe main.py --topic ai_study
```

---

## 6. Output Location & Deliverables

Every successful render creates a project bundle under:
```
output/{project_title}/
```
Containing all 7 deliverables:
1. `final_video.mp4` (1080x1920 30FPS MP4 with Stickman main character)
2. `thumbnail.png` (High-CTR portrait thumbnail)
3. `script.txt` (Complete Hindi script breakdown)
4. `storyboard.json` (5-stage scene cinematography plan)
5. `subtitles.srt` (Devanagari subtitle track)
6. `metadata.json` (YouTube title, description, tags, hashtags, SEO score)
7. `quality_report.md` (Automated technical, visual, audio QC scorecard)
