## 💻 Minimum Hardware Requirement

‑ RAM ≥8GB; For Qwen2.5‑14B: RAM ≥16GB or NVIDIA GPU with ≥8GB VRAM
‑ Free disk space ≥5GB (for python libraries, whisper model, ollama LLM)

## 🚀 How to run locally

1. Clone or download source code

```
git clone https://github.com/YourUserName/video‑subtitle‑tool.git
cd video‑subtitle‑tool
```

Or click `Code → Download ZIP` on GitHub page.
**You must fully extract the zip archive. Do NOT run bat inside compressed zip viewer.**

2. Go into project root folder, double‑click `run.bat`
‑ First launch will auto‑create `venv` virtual environment and download python dependencies (internet required).
‑ Whisper will automatically download base speech recognition model on first use.
‑ After setup finished, your browser will pop‑up and open the tool page automatically.
3. Usage
‑ Upload local video for subtitle extraction
‑ If Ollama is ready: use AI chapter generation and subtitle Q&A
‑ Paste link to download online videos
‑ Convert image formats

## ⚠️ Important Notes

1. Always fully extract zip archive. Never run `run.bat` directly inside zip preview.
2. Proper shutdown: Press `Ctrl + C` inside black console window, wait process exit, then close window. Avoid port occupied issues.
3. Anti‑virus software may warn files inside venv folder, add project folder to whitelist.
4. When environment corrupted: delete `venv` folder, double‑click `run.bat` again to rebuild environment.
5. Auto‑generated folders: `video_information`, `video_download`, `graph_transform` for subtitles, downloaded videos and converted images.
6. For personal study only. Please comply with copyright rules when downloading online resources.

## ❓ FAQ

1. `'py' is not recognized` → Python not installed, or you missed `Add Python to PATH` checkbox during install.
2. Port occupied error → Close old process with `Ctrl + C`, or reboot PC.
3. Slow pip download / install failure → Delete venv folder. This script uses aliyun mirror. Remove mirror argument inside bat if you have network trouble.
4. AI buttons grayed out → Ollama not installed / Ollama service not running / model `qwen2.5:14b` not pulled.

## 📂 Project structure

‑ `app.py`: Main streamlit application
‑ `ffmpeg_bin/bin`: Built‑in ffmpeg binary, no system environment variable needed
‑ `run.bat`: Windows one‑click startup script
‑ `requirements.txt`: Python dependency list