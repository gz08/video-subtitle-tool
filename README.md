# 视频字幕一体化工具 Video‑Subtitle‑Tool
> 基于 Streamlit + Whisper + Ollama(Qwen2.5‑14B) + FFmpeg
> ✨功能：本地视频字幕提取、AI自动生成章节、字幕AI问答、线上视频下载、图片格式转换

⚠️ **本项目仅支持 Windows10 / Windows11 64位系统**
> 本工具运行在**用户本地浏览器**，不是公网网页服务；所有运算在你的电脑完成。

## 📋 前置软件要求
### 必须安装
1. **Python 3.10.11**
> ⚠️安装过程务必勾选 `Add Python to PATH`
> 下载地址：https://www.python.org/downloads/release/python‑31011/

### 可选（AI功能需要，不装也可以用基础功能）
2. **Ollama**：用于AI章节生成、AI字幕问答
- 下载：https://ollama.com/download/windows
- 安装完成打开cmd执行：
```cmd
ollama pull qwen2.5:14b
