@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ======================================================
echo         视频字幕一体化工具 启动程序
echo ======================================================
echo.
echo 使用前准备事项:
echo 1. Ollama 需要手动执行 ollama pull qwen2.5:14b
echo 2. FFmpeg 放到本目录 ffmpeg_bin\bin 文件夹，不需要系统PATH
echo 3. 抖音下载功能需要安装 Edge浏览器
echo.

set VENV_PY=venv\Scripts\python.exe
set VENV_PIP=venv\Scripts\pip.exe

if exist "%VENV_PY%" (
echo.
echo [信息] 检测到本地已存在虚拟环境venv，直接使用
echo.
) else (
echo.
echo [信息] 未检测venv虚拟环境，即将自动创建虚拟环境
echo [信息] 仅在本文件夹构建venv，不会修改系统Python环境
echo.

py -m venv venv
if not exist "%VENV_PY%" (
echo [错误] 创建虚拟环境失败！
echo 请确认本机已经安装Python3.10，并且已添加到系统PATH！
pause
exit /b 1
)

echo.
echo [信息] 虚拟环境创建完成，开始安装依赖包
echo [提示] torch、whisper体积很大，请耐心等待，下面会打印下载日志！
echo.

"%VENV_PIP%" install setuptools>=77.0.3 -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --progress on -v
if %errorlevel% equ 0 (
echo.
echo [成功] 全部依赖安装完成
echo.
) else (
echo.
echo [错误] 依赖安装失败，请检查网络！
pause
exit /b 1
)
)

echo.
echo [信息] 正在启动程序，将自动选择空闲端口，浏览器会自动弹出！
echo.
:: --server.port=0：自动挑选系统空闲端口，彻底解决端口占用报错
"%VENV_PY%" -m streamlit run app.py --server.port=0 --server.headless=false
pause
