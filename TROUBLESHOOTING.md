# 🔧 TROUBLESHOOTING & COMMON FIXES GUIDE
## Stickman AI Video Production Studio (Raj Everyway Study)

This guide documents diagnostic solutions for common edge cases, environment configuration issues, and rendering considerations.

---

### 1. Terminal Hindi Display / `UnicodeEncodeError: 'charmap'`
- **Symptom**: Error when running CLI on Windows: `UnicodeEncodeError: 'charmap' codec can't encode character '\u092d'`.
- **Cause**: Windows CMD / PowerShell defaults to code page 1252, which cannot encode Devanagari script or emojis.
- **Permanent Fix**: Already included at the top of all Python entrypoints (`main.py`, `web_app.py`, `src/*.py`):
  ```python
  if sys.platform == "win32":
      sys.stdout.reconfigure(encoding='utf-8')
      sys.stderr.reconfigure(encoding='utf-8')
  ```
- **Manual Terminal Fix**: If running external commands, set the terminal code page to UTF-8 before running:
  ```powershell
  chcp 65001
  $env:PYTHONIOENCODING="utf-8"
  ```

---

### 2. Sarvam AI Voiceover 400 Bad Request (Text Length > 500 Characters)
- **Symptom**: `Sarvam AI TTS Error 400: inputs.0: String should have at most 500 characters`.
- **Cause**: Sarvam AI API enforces a hard 500-character ceiling per request.
- **Permanent Fix**: `src/voice_gen.py` implements intelligent sentence chunking (`chunk_text_for_sarvam(max_chars=400)`). It splits the narration at sentence boundaries (`।`, `.`, `?`, `!`), generates audio chunks individually, and concatenates them into a continuous WAV file without audio gaps or clicks.
- **Fail-Safe**: If `SARVAM_API_KEY` is empty, expired, or fails, the engine automatically switches to **Microsoft Edge-TTS** without terminating the render.

---

### 3. Keyless / Free Voiceover Fallback (Edge-TTS)
- **Symptom**: You don't have a paid Sarvam AI API key and want to generate unlimited Hindi videos for free.
- **Solution**: Use the built-in Microsoft Edge-TTS voices:
  - `edge_madhur`: Deep, authoritative Hindi male voice.
  - `edge_swara`: Clear, energetic Hindi female voice.
  - `edge_prabhat`: Natural Indian English male voice.
  - `edge_neerja`: Clear Indian English female voice.
- **Usage via CLI**:
  ```powershell
  .\.venv\Scripts\python.exe main.py --prompt "AI in India" --speaker edge_madhur
  ```
- **Usage via Web UI**: Select `Madhur (Free)` or `Swara (Free)` in the Voiceover dropdown.

---

### 4. Broken Virtual Environment Path (`.venv`)
- **Symptom**: Terminal error `The system cannot find the path specified` or Python executable not found in `.venv`.
- **Cause**: `.venv` was cloned or copied from another machine and contains stale hardcoded absolute paths in `pyvenv.cfg`.
- **Solution**: Recreate the virtual environment:
  ```powershell
  Remove-Item -Recurse -Force .venv
  python -m venv .venv
  .\.venv\Scripts\activate
  pip install -r requirements.txt
  ```

---

### 5. Video Rendering Speed & CPU Utilization
- **Symptom**: Rendering takes 45–75 seconds.
- **Reason**: 1080 × 1920 (Full HD Portrait) at 30 FPS across 35–45 seconds requires rendering approximately 1,200 layered frames (Background + Stickman 2D Rig + Audio Visualizer + Bouncy Subtitles).
- **Optimization Already Applied**:
  - `ffmpeg` multi-threading enabled (`threads=4`).
  - H.264 encoding preset set to `fast`.
  - Vector Stickman rendered using high-speed PIL blitting (2–4ms per frame).
  - Background clips cached in memory.

---

### 6. Hindi Subtitle Fonts
- **Symptom**: Subtitles appear as boxes or default serif text.
- **Cause**: The specified font path is missing on the machine.
- **Solution**:
  - Default primary font: `C:/Windows/Fonts/Nirmala.ttc` (Microsoft Nirmala UI, optimized for Devanagari text).
  - Fallback font: `C:/Windows/Fonts/arial.ttf`.
  - Both fonts ship standard on Windows 10 and 11. To add custom fonts, copy any TTF (e.g., Google's `NotoSansDevanagari-Bold.ttf`) to `assets/fonts/` and update `FONT_PATH` in `config.py`.

---

### 7. Port 8000 Already in Use (Web UI)
- **Symptom**: `OSError: [WinError 10048] Only one usage of each socket address is normally permitted`.
- **Solution**: An existing instance of `web_app.py` is already running on port 8000.
  - Either open your browser directly at `http://127.0.0.1:8000`.
  - Or terminate the previous process via PowerShell:
    ```powershell
    Get-Process python* | Stop-Process -Force
    .\.venv\Scripts\python.exe web_app.py
    ```
