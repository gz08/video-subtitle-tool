# Video‑Subtitle‑Tool
> Powered by Streamlit + Whisper + Ollama(Qwen2.5‑14B) + FFmpeg
✨ Features: Local video subtitle extraction, AI chapter generation, subtitle Q&A, online video download, image format conversion

⚠️ **Only for Windows 10 / Windows 11 64‑bit**
This is a local‑run application, NOT public web service. All computations run on your local computer.

## 📋 Prerequisite Software
### Mandatory
1. **Python 3.10.11**
> ⚠️ Check `Add Python to PATH` during installation
Download: https://www.python.org/downloads/release/python‑31011/

### Optional (For AI functions; basic features work without it)
2. **Ollama** (AI chapter generation & subtitle Q&A)
- Download: https://ollama.com/download/windows
- After installation, open cmd and run:
```cmd
ollama pull qwen2.5:14b
