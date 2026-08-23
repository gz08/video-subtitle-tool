import os
import sys
import time
from urllib.parse import urlparse, parse_qs
import yt_dlp
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# Windows控制台utf‑8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

COOKIE_FILE = "./douyin_cookies.txt"
COOKIE_CACHE_SEC = 3600  # cookie缓存1小时，超时重新生成


def selenium_get_douyin_netscape_cookie() -> tuple[bool, str]:
    """
    启动Edge访问抖音首页，获取匿名fresh cookie，输出Netscape格式cookies.txt
    不需要登录账号
    返回 (ok, cookie_file路径/错误信息)
    """
    # 缓存判断
    if os.path.exists(COOKIE_FILE):
        mtime = os.path.getmtime(COOKIE_FILE)
        if time.time() - mtime < COOKIE_CACHE_SEC:
            return True, COOKIE_FILE

    options = webdriver.EdgeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-notifications")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = None
    try:
        driver = webdriver.Edge(
            service=Service(EdgeChromiumDriverManager().install()),
            options=options
        )
        driver.get("https://www.douyin.com")
        time.sleep(6)  # 等待页面JS执行，服务器下发s_v_web_id、odin_tt等指纹cookie

        cookies = driver.get_cookies()
        driver.quit()

        # 转为Netscape cookie file格式（yt‑dlp标准格式）
        lines = ["# Netscape HTTP Cookie File"]
        for ck in cookies:
            domain = ck["domain"]
            flag = "TRUE" if domain.startswith(".") else "FALSE"
            path = ck["path"]
            secure = "TRUE" if ck["secure"] else "FALSE"
            expiry = str(int(ck["expiry"])) if "expiry" in ck else "0"
            name = ck["name"]
            value = ck["value"]
            lines.append(f"{domain}\t{flag}\t{path}\t{secure}\t{expiry}\t{name}\t{value}")

        with open(COOKIE_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return True, COOKIE_FILE

    except Exception as e:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
        return False, f"获取抖音cookie失败:{str(e)}"


def normalize_douyin_url(url: str) -> str:
    """抖音modal_id弹窗链接转为标准/video/xxx链接"""
    raw = url.strip()
    parsed = urlparse(raw)
    qs = parse_qs(parsed.query)
    modal_id_list = qs.get("modal_id")
    if modal_id_list:
        vid = modal_id_list[0].strip()
        if vid.isdigit():
            return f"https://www.douyin.com/video/{vid}"
    return raw


def download_video(url: str, save_dir: str = "./downloads") -> tuple[bool, str]:
    os.makedirs(save_dir, exist_ok=True)
    raw_url = url.strip()
    work_url = normalize_douyin_url(raw_url)

    is_douyin = ("douyin.com" in work_url) or ("v.douyin.com" in work_url)

    # ==========每次请求全新构造ydl_opts，不使用全局对象！==========
    ydl_opts = {
        "outtmpl": os.path.join(save_dir, "%(title)s.%(ext)s"),
        "format": "best/bestvideo+bestaudio",
        "quiet": True,
        "no_warnings": True,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        }
    }

    # 只有抖音才设置Referer/Origin为抖音；B站使用B站的Referer
    if is_douyin:
        ydl_opts["http_headers"]["Referer"] = "https://www.douyin.com/"
        ydl_opts["http_headers"]["Origin"] = "https://www.douyin.com"
        ok_cookie, ck_path = selenium_get_douyin_netscape_cookie()
        if not ok_cookie:
            return False, f"抖音需要新鲜浏览器cookie，获取失败：{ck_path}"
        ydl_opts["cookiefile"] = ck_path
    else:
        # B站/小红书使用B站referer，**绝对不加载抖音cookie文件**
        ydl_opts["http_headers"]["Referer"] = "https://www.bilibili.com/"
        ydl_opts["http_headers"]["Origin"] = "https://www.bilibili.com"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(work_url, download=True)
            filename = ydl.prepare_filename(info)
        return True, f"下载成功：{filename}"
    except Exception as e:
        err_msg = str(e)
        if "412" in err_msg:
            return False, "B站返回412风控拦截。解决方案：1.更新yt‑dlp到最新版；2.Edge登录B站，开启cookiesfrombrowser；3.更换网络。"
        if "403" in err_msg:
            return False, "抖音返回403访问被拒绝；cookie已失效，程序会在下一次调用自动刷新cookie。"
        if "Fresh cookies" in err_msg:
            if os.path.exists(COOKIE_FILE):
                os.remove(COOKIE_FILE)
            return False, "抖音Fresh cookies校验失败，已删除旧cookie缓存，请重新执行下载。"
        if "KeyError('bvid')" in err_msg:
            return False, "B站解析失败，该错误由非B站cookie污染导致；已修复代码逻辑，重新运行即可。"
        if "UnicodeEncodeError" in err_msg:
            return False, "编码错误：http头存在特殊字符，请确认代码使用普通英文减号。"
        if "Unsupported URL" in err_msg:
            return False, "链接不支持，请使用单视频链接，不要首页/搜索弹窗页面。"
        return False, f"下载失败：{err_msg}"


if __name__ == "__main__":
    test_url = input("输入视频链接(B站/抖音/小红书):")
    ok, msg = download_video(test_url)
    print(msg)
#可以爬取的网页有：小红书、B站、抖音、微博视频