# README.md
```markdown
# Video‑Subtitle‑Tool（视频字幕一体化工具）
> Powered by Streamlit + Whisper + Ollama(Qwen2.5‑14B) + FFmpeg（基于 Streamlit + Whisper + Ollama(Qwen2.5‑14B) + FFmpeg）

✨ Features（✨功能）:
‑ Local video speech‑to‑text subtitle extraction（本地视频语音转文字字幕提取）
‑ AI‑driven chapter generation & subtitle Q&A（AI自动生成视频章节、字幕智能问答）
‑ Online media download: Bilibili / Douyin / Xiaohongshu video support（线上媒体下载：支持B站、抖音、小红书、微博视频）
‑ Multi‑format image conversion tool（多格式图片转换工具，支持jpg，png，bmp和webp转jpg，png，bmp，webp和tiff）
‑ Windows one‑click startup script (`run.bat`), auto‑create python venv（Windows一键启动脚本`run.bat`，自动创建Python虚拟环境）

⚠️ This project only supports Windows 10 / Windows 11 64‑bit system.（⚠️本项目仅支持 Windows10 / Windows11 64位系统）
⚠️ This is a local‑run application, NOT public web service. All computations run on your local computer.（⚠️本工具运行在用户本地浏览器，不是公网网页服务；所有运算在你的电脑完成。）

## 📋 Prerequisite Software（📋 前置软件要求）
### Mandatory（必须安装）
**Python 3.10.11**（Python 3.10）
> ⚠️ Remember to check `Add Python to PATH` during installation.（⚠️安装过程务必勾选 Add Python to PATH）
Download address（下载地址）: https://www.python.org/downloads/release/python-31011/

### Optional (For AI functions; basic features work without it)（可选：用于AI功能；不安装也可以使用基础功能）
**Ollama**: For AI chapter generation and subtitle Q&A.（**Ollama**：用于AI章节生成、AI字幕问答）
Download（下载）: https://ollama.com/download/windows
After installation, open cmd and run the command below:（安装完成打开cmd执行下面命令：）
```cmd
ollama pull qwen2.5:14b
```
> Without Ollama: subtitle extraction, video download, image conversion still work; AI‑related panels will be disabled.（不安装Ollama：字幕提取、视频下载、图片转换依然可用，AI相关面板会被禁用）

## 📦 Required FFmpeg Binaries（📦 FFmpeg 必备组件）
FFmpeg binaries are NOT included in this source repository.（本项目源码不内置FFmpeg二进制程序）
Download address（下载地址）:
https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip

### Operation Steps（操作步骤）
1. Download `ffmpeg‑master‑latest‑win64‑gpl.zip` from the link above.（1.点击上面链接下载 `ffmpeg‑master‑latest‑win64‑gpl.zip`）
2. Fully unzip the compressed archive. The extracted folder name is similar to `ffmpeg‑master‑latest‑win64‑gpl`.（2.将压缩包完整解压，解压出来的文件夹名字类似：`ffmpeg‑master‑latest‑win64‑gpl`）
3. **Rename this extracted folder to `ffmpeg_bin`**.（3. **把这个文件夹重命名为：`ffmpeg_bin`**）
4. Place the renamed `ffmpeg_bin` folder into project root directory (same level as `run.bat` and `app.py`).（4. 将重命名后的 `ffmpeg_bin` 文件夹，放到**项目根目录**，和 `run.bat`、`app.py` 放在同一级）

### ✅ Verify folder structure（✅正确目录结构校验）
```
video‑subtitle‑tool‑main/
├─ ffmpeg_bin/
│  └─ bin/
│     ├─ ffmpeg.exe
│     └─ ffprobe.exe
├─ run.bat
├─ app.py
└─ requirements.txt
```
> ⚠️Important: Do NOT add extra nested folders. The real existing path `./ffmpeg_bin/bin/ffmpeg.exe` is required, otherwise the software cannot run.（⚠️重要：不要嵌套多一层文件夹！必须保证路径 `./ffmpeg_bin/bin/ffmpeg.exe` 真实存在，否则软件无法运行。）

## 💻 Minimum Hardware Requirement（💻硬件最低配置）
‑ RAM ≥8GB; For Qwen2.5‑14B: RAM ≥16GB or NVIDIA GPU with ≥8GB VRAM（‑ 内存 ≥8GB；使用Qwen2.5‑14B推荐 ≥16GB内存 / NVIDIA显卡 ≥8GB显存）
‑ Free disk space ≥5GB (for python libraries, whisper model, ollama LLM)（‑ 磁盘空闲 ≥5GB，存放Python库、Whisper模型、Ollama大模型）

## 🚀 How to run locally（🚀 本地运行步骤）
> Two ways to run the project（项目提供两种运行方式）：
> 🔹 For ordinary users（普通小白用户）：Use `run.bat` one‑click startup（使用 `run.bat` 一键启动）
> 🔹 For developers with Python / VSCode installed（已安装Python、VSCode的开发者）：Directly run `run_app.py`，faster startup（直接运行 `run_app.py`，启动速度更快）

### Method 1: Ordinary user, use run.bat（方式1：普通用户，使用 run.bat）
1. Clone or download source code zip archive from GitHub.（1.从GitHub Clone / Download 本项目源码到本地）
> Or click `Code → Download ZIP` on GitHub webpage.（> 或者在GitHub网页点击 `Code → Download ZIP`）
> You must fully extract the zip archive. Do NOT run bat script inside compressed zip preview window.（> 必须完整解压全部文件，**不要在压缩包预览窗口内直接运行bat**）
2. Enter project root folder, double‑click `run.bat`.（2. 进入项目根目录，双击 `run.bat`）
‑ First launch will auto‑create `venv` virtual environment and download python dependencies, internet connection is required.（‑ 第一次运行会自动创建`venv`虚拟环境，联网下载全部Python依赖库）
‑ Whisper will automatically download base speech recognition model on first use.（‑ Whisper首次运行会自动下载base语音识别模型）
‑ After setup finished, your browser will pop‑up and open the tool page automatically.（‑ 等待完成后会自动唤起浏览器打开工具页面）

### Method 2: Developer with VSCode / local Python environment（方式2：已配置Python环境、使用VSCode的开发者）
> Precondition: Python 3.10.11 is already installed, dependencies in `requirements.txt` have been installed manually.（> 前置条件：本地已经装好Python3.10.11，并且手动安装完`requirements.txt`内全部依赖包）
1. Clone / download and fully unzip source code.（1.Clone或者下载并完整解压源码）
2. Open project root folder in VSCode.（2.使用VSCode打开项目根目录）
3. Select Python 3.10.11 interpreter.（3.选择Python3.10.11解释器）
4. Directly run `run_app.py` inside VSCode.（4.在VSCode中直接运行 `run_app.py`）
‑ Browser will pop‑up and load tool page.（‑ 浏览器会弹出并加载工具页面，省去自动创建venv步骤，启动速度更快）

### Usage（3. 使用）
‑ Upload local video for subtitle extraction.（‑ 上传本地视频提取字幕）
‑ If Ollama service is ready: use AI chapter generation and subtitle Q&A.（‑ 已配置Ollama可使用AI章节生成、AI字幕问答）
‑ Paste link to download online videos.（‑ 输入链接下载线上视频）
‑ Convert image formats.（‑ 图片格式互相转换）

## ⚠️ Important Notes（⚠️重要注意事项）
1. Always fully extract zip archive. Never run `run.bat` directly inside zip preview.（1. 一定要完整解压zip压缩包，不要直接在压缩包预览内运行run.bat）
2. Proper shutdown: Press `Ctrl + C` inside black console window, wait process exit, then close window. Avoid port occupied issues.（2. 关闭程序不要直接点黑窗口右上角×；优先在控制台按 `Ctrl + C`，等待进程正常退出再关闭窗口，避免端口占用）
3. Anti‑virus software may warn files inside venv folder, add project folder to whitelist.（3. 杀毒软件可能会对venv虚拟环境文件告警，请加入白名单）
4. When environment corrupted: delete `venv` folder, double‑click `run.bat` again to rebuild environment.（4. 如果环境损坏，直接删除文件夹内`venv`，再次双击`run.bat`会重新构建）
5. Auto‑generated folders: `video_information`, `video_download`, `graph_transform` for subtitles, downloaded videos and converted images.（5. 程序自动生成缓存目录：`video_information`、`video_download`、`graph_transform`，用于保存字幕、下载视频、转换图片）
6. This tool is for personal‑study only. Please comply with copyright rules when downloading online resources.（6. 仅供个人学习使用，下载线上视频请遵守对应平台版权协议）

## ❓ FAQ（❓常见问题）
1. `'py' is not recognized` → Python not installed, or you missed `Add Python to PATH` checkbox during install.（1. `'py' is not recognized` → Python未安装，或者安装的时候没有勾选`Add Python to PATH`）
2. Port occupied error → Close old process with `Ctrl + C`, or reboot PC.（2. 端口占用报错 → 按`Ctrl+C`正常关闭旧程序，或者重启电脑释放端口）
3. Slow pip download / install failure → Delete venv folder. This script uses aliyun mirror. Remove mirror argument inside bat if you have network trouble.（3. pip下载很慢/失败 → 删除venv文件夹；脚本默认使用阿里云镜像；网络差可以把bat内镜像参数移除）
4. AI buttons grayed out → Ollama not installed / Ollama service not running / model `qwen2.5:14b` not pulled.（4. AI功能按钮灰色不可用 → Ollama未安装 / Ollama服务未启动 / 没有拉取qwen2.5:14b模型）

## 📂 Project structure（📂项目目录说明）
### Core program files（核心程序文件）
‑ `app.py`: Main Streamlit web UI entry, responsible for rendering all web pages, receiving user uploads and form inputs, calling each functional module, displaying results.（‑ `app.py`：Streamlit网页主入口，负责渲染全部页面、接收用户上传与表单输入、调用各个功能模块、展示返回结果）
‑ `run_app.py`: Program startup entry. Start streamlit service programmatically, called by `run.bat`. Developers can directly run this file in VSCode to launch application.（‑ `run_app.py`：程序启动入口，以代码方式启动streamlit服务，供`run.bat`调用；开发者可在VSCode直接运行该文件启动项目）
‑ `run.bat`: Windows one‑click startup batch script. Automatically create local venv virtual environment, install dependencies and invoke `run_app.py`. For ordinary non‑programmer users.（‑ `run.bat`：Windows一键启动批处理脚本，自动在本地创建venv虚拟环境、安装依赖并调用`run_app.py`，面向无编程基础普通用户）
‑ `requirements.txt`: Python dependency list, records all third‑party library versions required for project operation.（‑ `requirements.txt`：Python依赖清单，记录项目运行需要全部第三方库版本）

### Business logic modules（业务功能模块）
‑ `chapter_generator.py`: AI chapter generation module. Accept subtitle text, invoke Ollama large model to analyze video content, output segmented video chapter titles and corresponding time points.（‑ `chapter_generator.py`：AI章节生成模块，接收字幕文本，调用Ollama大模型分析视频内容，输出分段视频章节标题以及对应时间点）
‑ `subtitle_qa_engine.py`: Subtitle Q&A engine. Implement RAG‑based question‑answering logic for subtitle content, split subtitle text, retrieve relevant fragments, call LLM to answer user questions about video.（‑ `subtitle_qa_engine.py`：字幕问答引擎，实现基于RAG的字幕问答逻辑；对字幕文本做分块、检索相关片段，调用大模型回答用户针对视频内容的提问）
‑ `llm_client.py`: Ollama large‑model encapsulated client. Unified HTTP request wrapper for Ollama API, handle model call, timeout, exception capture, reused by chapter generation and Q&A modules.（‑ `llm_client.py`：Ollama大模型封装客户端，对Ollama API做统一HTTP请求封装，处理模型调用、超时、异常捕获，供章节生成、问答模块共用）
‑ `video_download.py`: Online video download module. Realize media resource acquisition from Bilibili, Douyin, Xiaohongshu and other platforms, rely on yt‑dlp, save video files to local cache directory.（‑ `video_download.py`：线上视频下载模块，实现B站、抖音、小红书等平台媒体资源获取，基于yt‑dlp，下载视频保存至本地缓存目录）
‑ `video_search_engine.py`: Subtitle keyword search engine. Search subtitle text by keyword, locate corresponding timestamp segments, return matched time range and text snippets.（‑ `video_search_engine.py`：字幕关键词检索引擎，根据关键词检索字幕文本，定位对应时间戳片段，返回匹配的时间区间与文本片段）
‑ `image_convert.py`: Image format conversion module. Based on Pillow, realize mutual conversion of multiple image formats(jpg/png/bmp/webp/tiff), handle input‑output format check, output file saving logic.（‑ `image_convert.py`：图片格式转换模块，基于Pillow库，实现多种图片格式互相转换(jpg/png/bmp/webp/tiff)，处理输入输出格式校验、输出文件保存逻辑）

### Auxiliary test files（辅助测试文件）
‑ `test_image.py`: Local standalone test script for image conversion functions, used during development to verify image reading‑writing and conversion effect. Not involved in official program workflow.（‑ `test_image.py`：图片转换功能本地独立测试脚本，开发阶段用来验证图片读写、转换效果，不参与正式程序运行流程）

### Other markdown files（其他文档文件）
‑ `LICENSE`: Open source license file(MIT).（‑ `LICENSE`：开源协议文件，MIT协议）
‑ `README.md`: Project documentation (English text with Chinese translation inside).（‑ `README.md`：项目说明文档，英文正文附带句后中文翻译）

> ⚠️ Clean‑up suggestion before GitHub release（⚠️GitHub发布清理建议）：
> Delete these redundant local‑development files: `all（得到文件夹中全部代码）.py`、`README_EN.md`、`ATTENTION.md`、`ATTENTION_EN.md`
> These are local auxiliary files and will not affect program functions after deletion.（删除本地调试冗余文件：`all（得到文件夹中全部代码）.py`、`README_EN.md`、`ATTENTION.md`、`ATTENTION_EN.md`；均为本地辅助文件，删除不影响程序运行）


---
