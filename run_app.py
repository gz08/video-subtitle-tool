"""
run_app.py
统一启动入口，直接运行此脚本即可拉起streamlit界面
"""
import subprocess
import sys
import asyncio
from pathlib import Path

def main():
    # Windows修复WinError10054连接重置警告
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    app_file = Path(__file__).parent / "app.py"
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_file),
        "--server.headless", "false"
    ]
    print(f"启动Streamlit UI: {app_file}")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
