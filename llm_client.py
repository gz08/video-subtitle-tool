import requests
import json
import time
OLLAMA_URL = "http://127.0.0.1:11434"
MODEL_NAME = "qwen2.5:14b"
MAX_TIMEOUT = 300
MAX_RETRY = 1

CHAPTER_TIMEOUT_MSG = "[LLM生成超时，使用简易标题]"

def llm_infer(prompt: str, timeout=MAX_TIMEOUT, is_chapter: bool = False) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "temperature": 0.1,
        "num_ctx": 2048,
        "num_thread": 6,
        "num_gpu": 0
    }
    retry_count = 0
    while retry_count <= MAX_RETRY:
        try:
            resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "").strip()
        except requests.exceptions.ReadTimeout:
            retry_count += 1
            if retry_count > MAX_RETRY:
                if is_chapter:
                    return CHAPTER_TIMEOUT_MSG
                else:
                    return "[QA_LLM_TIMEOUT]"
            time.sleep(1)
        except Exception as e:
            retry_count += 1
            print(f"llm_infer exception: {str(e)}")
            if retry_count > MAX_RETRY:
                return f"[LLM异常]{str(e)}"
            time.sleep(1)
    return "[LLM请求失败]"

def seconds_to_hms(total_sec: float) -> str:
    total = int(round(total_sec))
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    return f"{h:02d}:{m:02d}:{s:02d}"
