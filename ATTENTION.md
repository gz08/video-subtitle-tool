## 💻 硬件最低配置

- 内存 ≥8GB；使用 Qwen2.5‑14B 推荐 ≥16GB 内存 / NVIDIA 显卡 ≥8GB 显存
- 磁盘空闲 ≥5GB（存放 Python 库、Whisper 模型、Ollama 大模型）

## 🚀 本地运行步骤

1. Clone / Download 本项目源码到本地

```
git clone https://github.com/你的用户名/video‑subtitle‑tool.git
cd video‑subtitle‑tool
```

> 
> 或者在 GitHub 网页点击 `Code → Download ZIP`，完整解压到本地，**不要在压缩包内直接运行 bat**

2. 进入项目根目录，双击 `run.bat`

- 第一次运行会自动创建`venv`虚拟环境，联网下载全部 Python 依赖库；
- Whisper 会首次运行自动下载 base 语音识别模型；
- 等待完成后会自动唤起浏览器打开工具页面。

3. 使用

- 上传本地视频提取字幕；
- 有 Ollama 可使用 AI 章节生成、AI 字幕问答；
- 输入链接下载线上视频；
- 图片格式互相转换。

## ⚠️重要注意事项

1. 不要直接双击压缩包内部的`run.bat`，**必须完整解压全部文件**；
2. 关闭程序不要直接点黑窗口右上角 ×；优先在控制台按 `Ctrl + C`，等待进程正常退出再关闭窗口，避免端口占用；
3. 杀毒软件可能会对 venv 虚拟环境文件告警，请加入白名单；
4. 如果环境损坏，直接删除文件夹内`venv`，再次双击`run.bat`会重新构建；
5. 项目生成缓存目录：`video_information`、`video_download`、`graph_transform`，用于保存字幕、下载视频、转换图片；
6. 仅供个人学习使用，下载线上视频请遵守对应平台版权协议。

## ❓常见问题

1. `'py' is not recognized` → Python 未安装，或者没有勾选`Add Python to PATH`
2. 端口占用报错 → 按`Ctrl+C`正常关闭旧程序，或者重启电脑释放端口
3. pip 下载很慢 / 失败 → 删除 venv，run.bat 会使用阿里云镜像；网络差可以把 bat 内镜像参数移除
4. AI 功能灰色不可用 → Ollama 未安装 / Ollama 服务未启动 / 没有 pull qwen2.5:14b 模型

## 📂项目目录说明

- `app.py`：主页面逻辑（Streamlit）
- `ffmpeg_bin/bin`：内置 ffmpeg 二进制程序，无需系统环境变量
- `run.bat`：Windows 一键启动脚本
- `requirements.txt`：Python 依赖列表