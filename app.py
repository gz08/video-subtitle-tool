import warnings
import time
import hashlib
import json
import os
import tkinter
from tkinter import filedialog
from pathlib import Path
import re
import socket
warnings.filterwarnings("ignore")
import streamlit as st
from io import BytesIO
import whisper

# ===================== Ollama可用性检测 =====================
def check_ollama_service(host="127.0.0.1", port=11434, timeout=2):
    """检测本地Ollama服务端口是否可连通"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

if "ollama_available" not in st.session_state:
    st.session_state["ollama_available"] = check_ollama_service()
ollama_available = st.session_state["ollama_available"]

# ===================== 模块导入 + 可用性标记，防止name not defined =====================
mod_video_download_ok = False
mod_chapter_generator_ok = False
mod_search_engine_ok = False
mod_qa_engine_ok = False
generate_chapters = None
search_subtitle = None
run_qa_full_subtitle = None
run_qa_hit_fragments = None

try:
    from video_download import download_video
    mod_video_download_ok = True
except ImportError:
    st.warning("缺少业务模块：video_download.py，视频下载功能不可用！")

try:
    from chapter_generator import generate_chapters
    mod_chapter_generator_ok = True
except ImportError:
    st.warning("缺少业务模块：chapter_generator.py，AI章节生成功能不可用！")

try:
    from video_search_engine import search_subtitle, build_subtitle_index
    mod_search_engine_ok = True
except ImportError:
    st.warning("缺少业务模块：video_search_engine.py，字幕检索功能不可用！")

try:
    from subtitle_qa_engine import run_qa_full_subtitle, run_qa_hit_fragments
    mod_qa_engine_ok = True
except ImportError:
    st.warning("缺少业务模块：subtitle_qa_engine.py，AI问答功能不可用！")


# ===================== 基础路径配置 =====================
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CACHE_DIR = os.path.join(APP_ROOT, "video_information")
DEFAULT_DOWNLOAD_DIR = os.path.join(APP_ROOT, "video_download")
DEFAULT_IMAGE_DIR = os.path.join(APP_ROOT, "graph_transform")
# 专门存放上传临时视频的文件夹
TEMP_DIR = os.path.join(APP_ROOT, "temp_upload")

# ============【新增！Python内部注入ffmpeg路径，bat不再处理PATH】============
ffmpeg_local_bin = os.path.join(APP_ROOT, "ffmpeg_bin", "bin")
if os.path.isdir(ffmpeg_local_bin):
    import os
    # 只修改当前Python进程内部PATH，不修改系统、不修改cmd/bat
    os.environ["PATH"] = ffmpeg_local_bin + os.pathsep + os.environ["PATH"]
    
# 创建各个文件夹
for dir_path in [DEFAULT_CACHE_DIR, DEFAULT_DOWNLOAD_DIR, DEFAULT_IMAGE_DIR, TEMP_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# =========【重要】程序启动，清空整个临时上传文件夹，解决崩溃残留临时文件 =========
import glob
# 删除temp_upload内部全部文件，不删除文件夹本体
for f in glob.glob(os.path.join(TEMP_DIR, "*")):
    try:
        if os.path.isfile(f):
            os.remove(f)
    except OSError:
        pass

for dir_path in [DEFAULT_CACHE_DIR, DEFAULT_DOWNLOAD_DIR, DEFAULT_IMAGE_DIR]:
    os.makedirs(dir_path, exist_ok=True)


MAP_FILE_PATH = os.path.join(DEFAULT_CACHE_DIR, ".index_map.json")


# ===================== 工具函数 =====================
def select_folder_dialog():
    try:
        root = tkinter.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        folder_path = filedialog.askdirectory(title="选择保存文件夹")
        root.destroy()
        if folder_path:
            return folder_path
        return None
    except Exception:
        return None


def safe_filename(name: str) -> str:
    illegal_chars = r'\/:*?"<>|'
    for c in illegal_chars:
        name = name.replace(c, "_")
    return name.strip()


def load_name_mapping() -> dict:
    if not os.path.exists(MAP_FILE_PATH):
        return {}
    try:
        with open(MAP_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_name_mapping(mapping: dict):
    with open(MAP_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)


def get_video_hash(file_bytes, file_name):
    hash_obj = hashlib.sha256()
    hash_obj.update(file_bytes)
    hash_obj.update(file_name.encode("utf-8"))
    return hash_obj.hexdigest()


def get_video_folder_path(root_cache_dir: str, user_folder_name: str) -> str:
    clean_name = safe_filename(user_folder_name)
    target_path = os.path.join(root_cache_dir, clean_name)
    os.makedirs(target_path, exist_ok=True)
    return target_path


def rename_video_folder(root_cache_dir: str, old_user_name: str, new_user_name: str) -> bool:
    old_clean = safe_filename(old_user_name)
    new_clean = safe_filename(new_user_name)
    if old_clean == new_clean:
        return True
    old_path = os.path.join(root_cache_dir, old_clean)
    new_path = os.path.join(root_cache_dir, new_clean)
    if not os.path.exists(old_path):
        return False
    if os.path.exists(new_path):
        st.error("同名文件夹已存在，无法重命名！")
        return False
    try:
        os.rename(old_path, new_path)
        return True
    except Exception as e:
        st.error(f"文件夹改名失败：{str(e)}")
        return False


def write_text_file(folder: str, filename: str, content: str):
    fp = os.path.join(folder, safe_filename(filename))
    with open(fp, "w", encoding="utf-8") as f:
        f.write(content)


def read_text_file(fp: str) -> str | None:
    if not os.path.exists(fp):
        return None
    try:
        with open(fp, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def write_json_file(folder: str, filename: str, data):
    fp = os.path.join(folder, safe_filename(filename))
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_json_file(folder: str, filename: str):
    fp = os.path.join(folder, safe_filename(filename))
    if not os.path.exists(fp):
        return None
    try:
        with open(fp, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


# =====================【核心】文件智能识别模块（支持手动改名自动识别txt） =====================
chapter_pattern = re.compile(r"\d{1,2}:\d{2}:\d{2}\s*-\s*\d{1,2}:\d{2}:\d{2}")


def is_valid_json_text(text: str) -> bool:
    try:
        json.loads(text)
        return True
    except:
        return False


def auto_scan_txt_files(folder_path: str) -> dict:
    result = {
        "subtitle": None,
        "chapter": None,
        "search_cache": None,
        "qa_cache": None
    }
    if not os.path.isdir(folder_path):
        return result

    all_txt = []
    for fname in os.listdir(folder_path):
        if fname.lower().endswith(".txt"):
            fullpath = os.path.join(folder_path, fname)
            all_txt.append(fullpath)

    for fpath in all_txt:
        content = read_text_file(fpath)
        if content is None:
            continue

        if result["search_cache"] is None and is_valid_json_text(content.strip()):
            result["search_cache"] = fpath
            continue
        if result["qa_cache"] is None and is_valid_json_text(content.strip()):
            result["qa_cache"] = fpath
            continue
        if result["chapter"] is None and chapter_pattern.search(content):
            result["chapter"] = fpath
            continue
        if result["subtitle"] is None:
            result["subtitle"] = fpath
    return result


def smart_load_target_file(folder: str, expect_filename: str, auto_map: dict, file_type_key: str):
    exact_path = os.path.join(folder, safe_filename(expect_filename))
    content = read_text_file(exact_path)
    if content is not None:
        return content
    auto_file_path = auto_map.get(file_type_key)
    if auto_file_path and os.path.exists(auto_file_path):
        return read_text_file(auto_file_path)
    return None


# ===================== 载入本地所有缓存数据【支持手动改名自动识别】 =====================
def load_exist_video_data(storage_folder: str, file_cfg: dict):
    auto_file_mapping = auto_scan_txt_files(storage_folder)
    raw_seg_data = read_json_file(storage_folder, "raw_segments.json")
    if raw_seg_data is not None:
        st.session_state["whisper_raw_segments"] = raw_seg_data

    sub_text = smart_load_target_file(storage_folder, file_cfg["subtitle"], auto_file_mapping, "subtitle")
    if sub_text is not None:
        st.session_state["pure_subtitle_text"] = sub_text

    chapter_text = smart_load_target_file(storage_folder, file_cfg["chapter"], auto_file_mapping, "chapter")
    if chapter_text is not None:
        st.session_state["chapter_result_text"] = chapter_text

    search_cache_raw = smart_load_target_file(storage_folder, file_cfg["search_cache"], auto_file_mapping, "search_cache")
    if search_cache_raw is not None:
        try:
            loaded_search = json.loads(search_cache_raw)
            # 强制校验类型，防止读取null变成None
            if isinstance(loaded_search, dict):
                st.session_state["search_cache_dict"] = loaded_search
            else:
                st.session_state["search_cache_dict"] = {}
        except Exception:
            st.session_state["search_cache_dict"] = {}

    qa_cache_raw = smart_load_target_file(storage_folder, file_cfg["qa_cache"], auto_file_mapping, "qa_cache")
    if qa_cache_raw is not None:
        try:
            loaded_qa = json.loads(qa_cache_raw)
            if isinstance(loaded_qa, dict):
                st.session_state["qa_cache_dict"] = loaded_qa
            else:
                st.session_state["qa_cache_dict"] = {}
        except Exception:
            st.session_state["qa_cache_dict"] = {}


# ===================== 页面初始化 =====================
st.set_page_config(page_title="视频字幕工具", layout="wide")


@st.cache_resource
def load_whisper_model(model_size="base"):
    return whisper.load_model(model_size)
model = load_whisper_model("base")


# SessionState KEY定义
init_data_keys = [
    "current_vid_hash",
    "user_video_folder_name",
    "whisper_raw_segments",
    "chapter_result_text",
    "search_hit_data",
    "pure_subtitle_text",
    "rag_index_cache",
    "search_cache_dict",
    "qa_cache_dict",
    "qa_answer"
]
init_display_keys = [
    "show_subtitle_result",
    "show_chapter_result",
    "show_search_result",
    "show_qa_result"
]
time_keys = [
    "trans_cost",
    "chapter_cost",
    "search_cost",
    "qa_cost"
]
# 任务锁
lock_keys = [
    "trans_running",
    "chapter_running",
    "search_running",
    "qa_running"
]


# 默认文件名配置，区分检索缓存、问答缓存
default_file_names = {
    "subtitle": "subtitle.txt",
    "chapter": "chapter.txt",
    "search_cache": "search_cache.txt",
    "qa_cache": "qa_cache.txt"
}
if "file_name_cfg" not in st.session_state:
    st.session_state["file_name_cfg"] = default_file_names.copy()


# 初始化所有状态
for k in init_data_keys:
    if k not in st.session_state:
        st.session_state[k] = None
for k in init_display_keys:
    if k not in st.session_state:
        st.session_state[k] = False
for k in time_keys:
    if k not in st.session_state:
        st.session_state[k] = ""
for k in lock_keys:
    if k not in st.session_state:
        st.session_state[k] = False


# 强制初始化缓存字典为空对象，杜绝None
if "search_cache_dict" not in st.session_state or st.session_state["search_cache_dict"] is None:
    st.session_state["search_cache_dict"] = {}
if "qa_cache_dict" not in st.session_state or st.session_state["qa_cache_dict"] is None:
    st.session_state["qa_cache_dict"] = {}


if "cache_dir" not in st.session_state:
    st.session_state["cache_dir"] = DEFAULT_CACHE_DIR
if "download_dir" not in st.session_state:
    st.session_state["download_dir"] = DEFAULT_DOWNLOAD_DIR
if "image_dir" not in st.session_state:
    st.session_state["image_dir"] = DEFAULT_IMAGE_DIR


# ===================== Tab布局 =====================
tab1, tab2, tab3 = st.tabs([
    "🎬视频提取 & 字幕分析",
    "📥线上视频下载",
    "🖼图片格式转换"
])


with tab1:
    # ========= Ollama状态提示栏【新增】 =========
    if not ollama_available:
        st.warning("⚠️未检测到本地Ollama(127.0.0.1:11434)服务，【AI自动生成视频章节】、【AI字幕问答】已禁用。\n✅字幕提取、关键词检索、视频下载、图片转换功能完全可用；需要AI功能请安装并启动Ollama。")
    else:
        st.success("✅检测到Ollama服务，AI章节生成、AI问答功能已启用")

    with st.expander("📁 顶层视频缓存根路径设置（video_information目录）", expanded=True):
        col_btn1, col_btn2, col_text = st.columns([0.2, 0.2, 0.6])
        with col_btn1:
            if st.button("选择顶层根文件夹", key="sel_cache"):
                new_path = select_folder_dialog()
                if new_path:
                    st.session_state["cache_dir"] = new_path
                    os.makedirs(new_path, exist_ok=True)
                    st.success(f"顶层根目录已切换：{new_path}")
        with col_btn2:
            if st.button("恢复默认顶层路径", key="reset_cache"):
                reset_path = DEFAULT_CACHE_DIR
                st.session_state["cache_dir"] = reset_path
                os.makedirs(reset_path, exist_ok=True)
                st.success("已恢复程序默认顶层缓存文件夹")
        with col_text:
            st.text_input("当前顶层根路径", value=st.session_state["cache_dir"], disabled=True)
        st.info("结构：顶层根目录 /【你自定义的视频文件夹】/ 各类文本与json缓存文件")

    st.divider()
    with st.expander("✏️ 当前视频文件命名设置（【仅控制新文件保存名称，旧文件手动改名可自动识别】）", expanded=True):
        st.warning("提示：JSON文件 raw_segments.json 请勿手动改名！txt文件任意改名程序自动识别")
        has_video = st.session_state["current_vid_hash"] is not None
        current_folder_name = st.session_state.get("user_video_folder_name", "")
        f_cfg = st.session_state["file_name_cfg"]

        placeholder_folder = "请先上传视频加载数据" if not has_video else ""
        new_video_folder_name = st.text_input(
            "视频文件夹名称（中间目录名称）",
            value=current_folder_name,
            disabled=not has_video,
            placeholder=placeholder_folder
        )

        new_sub_name = st.text_input("字幕文本文件名（新文件保存用）", value=f_cfg["subtitle"], disabled=not has_video)
        new_chap_name = st.text_input("章节列表文件名（新文件保存用）", value=f_cfg["chapter"], disabled=not has_video)
        new_srch_name = st.text_input("检索缓存文件名（新文件保存用）", value=f_cfg["search_cache"], disabled=not has_video)
        new_qa_name = st.text_input("问答缓存文件名（新文件保存用）", value=f_cfg["qa_cache"], disabled=not has_video)

        col_save, col_open_folder = st.columns([0.35, 0.35])
        with col_save:
            save_btn = st.button("保存全部命名修改", disabled=not has_video)
            if save_btn:
                vid_hash = st.session_state["current_vid_hash"]
                old_name = st.session_state["user_video_folder_name"]
                new_clean_folder = safe_filename(new_video_folder_name)
                current_cache_root = st.session_state["cache_dir"]
                rename_ok = rename_video_folder(current_cache_root, old_name, new_clean_folder)
                if rename_ok:
                    st.session_state["user_video_folder_name"] = new_clean_folder
                    name_mapping = load_name_mapping()
                    name_mapping[vid_hash] = new_clean_folder
                    save_name_mapping(name_mapping)
                    st.session_state["file_name_cfg"]["subtitle"] = safe_filename(new_sub_name)
                    st.session_state["file_name_cfg"]["chapter"] = safe_filename(new_chap_name)
                    st.session_state["file_name_cfg"]["search_cache"] = safe_filename(new_srch_name)
                    st.session_state["file_name_cfg"]["qa_cache"] = safe_filename(new_qa_name)
                    st.success("命名保存成功！后续生成文件将使用新名称；历史改名txt依然自动识别")
                    st.rerun()
        with col_open_folder:
            open_btn = st.button("📂 在资源管理器打开当前视频文件夹", disabled=not has_video)
            if open_btn:
                current_cache_root = st.session_state["cache_dir"]
                target_dir = get_video_folder_path(current_cache_root, st.session_state["user_video_folder_name"])
                if os.name == "nt":
                    import subprocess
                    subprocess.Popen(["explorer.exe", target_dir])
                elif os.name == "posix":
                    subprocess.Popen(["xdg-open", target_dir])

    st.divider()
    st.subheader("上传本地视频提取字幕")
    uploaded_video = st.file_uploader("上传视频文件", type=["mp4", "mov", "avi", "mkv"])
    current_cache_root = st.session_state["cache_dir"]
    name_mapping = load_name_mapping()

    if uploaded_video is not None:
        file_data = uploaded_video.read()
        file_name = uploaded_video.name
        vid_hash = get_video_hash(file_data, file_name)
        file_cfg = st.session_state["file_name_cfg"]

        # 切换新视频，清空旧状态
        if st.session_state["current_vid_hash"] != vid_hash:
            for k in init_data_keys:
                st.session_state[k] = None
            for k in init_display_keys:
                st.session_state[k] = False
            for k in time_keys:
                st.session_state[k] = ""
            # 清空后强制重置缓存字典，防止变成None
            st.session_state["search_cache_dict"] = {}
            st.session_state["qa_cache_dict"] = {}

            st.session_state["current_vid_hash"] = vid_hash

            if vid_hash in name_mapping:
                folder_name = name_mapping[vid_hash]
            else:
                default_folder_name = os.path.splitext(file_name)[0]
                folder_name = safe_filename(default_folder_name)
                name_mapping[vid_hash] = folder_name
                save_name_mapping(name_mapping)
            st.session_state["user_video_folder_name"] = folder_name
            video_storage_folder = get_video_folder_path(current_cache_root, folder_name)

            load_exist_video_data(video_storage_folder, file_cfg)
            st.info("✅ 自动扫描目录缓存，txt文件手动改名也能识别；结构化片段已恢复，深度分析功能可用")
            st.rerun()

        active_folder_name = st.session_state["user_video_folder_name"]
        video_storage_folder = get_video_folder_path(current_cache_root, active_folder_name)
        import uuid
        rand_suffix = str(uuid.uuid4())
        # 全部临时文件放到独立 temp_upload 文件夹
        temp_video_path = os.path.join(TEMP_DIR, f"upload_{rand_suffix}_{uploaded_video.name}")
        with open(temp_video_path, "wb") as f:
            f.write(file_data)

        # 字幕提取按钮逻辑
        if st.button("开始提取字幕", disabled=st.session_state["trans_running"]) and not st.session_state["trans_running"]:
            st.session_state["trans_running"] = True
            st.session_state["trans_cost"] = ""
            progress_bar = st.progress(0)
            start_time = time.perf_counter()
            try:
                with st.spinner("Whisper音频识别中..."):
                    progress_bar.progress(10)
                    result = model.transcribe(temp_video_path, word_timestamps=True)
                    progress_bar.progress(60)
                    pure_text = "\n".join([seg["text"].strip() for seg in result["segments"]])

                    seg_list_clean = []
                    for seg in result["segments"]:
                        seg_dict = dict(seg)
                        if "words" in seg_dict and seg_dict["words"] is not None:
                            seg_dict["words"] = [dict(w) for w in seg_dict["words"]]
                        seg_list_clean.append(seg_dict)

                    st.session_state["whisper_raw_segments"] = seg_list_clean
                    st.session_state["pure_subtitle_text"] = pure_text
                    st.session_state["rag_index_cache"] = None
                    st.session_state["show_subtitle_result"] = True

                    write_json_file(video_storage_folder, "raw_segments.json", seg_list_clean)
                    write_text_file(video_storage_folder, file_cfg["subtitle"], pure_text)
                    progress_bar.progress(100)
                end_time = time.perf_counter()
                cost = round(end_time - start_time, 2)
                st.session_state["trans_cost"] = f"字幕识别耗时：{cost} 秒"
                st.success("字幕提取完成，数据已写入磁盘")
            finally:
                if os.path.exists(temp_video_path):
                    os.remove(temp_video_path)
                st.session_state["trans_running"] = False

    if st.session_state["trans_cost"]:
        st.caption(st.session_state["trans_cost"])

    # ==========字幕结果渲染 ==========
    if st.session_state["pure_subtitle_text"] is not None:
        if st.session_state["show_subtitle_result"]:
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.markdown("##### 字幕结果（无时间戳）")
            with col2:
                if st.button("关闭", key="close_subtitle"):
                    st.session_state["show_subtitle_result"] = False
                    st.rerun()
            st.text_area("字幕文本", st.session_state["pure_subtitle_text"], height=350)
            txt_bytes = BytesIO(st.session_state["pure_subtitle_text"].encode("utf-8"))
            st.download_button(label="下载字幕txt", data=txt_bytes, file_name="subtitle_no_timestamp.txt")
        else:
            if st.button("重新展示字幕结果", key="reopen_sub"):
                st.session_state["show_subtitle_result"] = True
                st.rerun()

    st.divider()
    st.markdown("#### 字幕深度分析工具")
    raw_segs = st.session_state["whisper_raw_segments"]
    pure_sub_text = st.session_state.get("pure_subtitle_text", "")
    file_cfg = st.session_state["file_name_cfg"]
    current_vid_hash = st.session_state["current_vid_hash"]
    video_storage_folder = None
    if current_vid_hash and st.session_state.get("user_video_folder_name"):
        video_storage_folder = get_video_folder_path(current_cache_root, st.session_state["user_video_folder_name"])

    if raw_segs is None:
        st.info("⚠️暂无Whisper原始片段数据，执行字幕提取后才可运行章节生成、字幕检索、AI问答")
    else:
        # ========= 1. 自动生成视频章节【Ollama + 模块双重禁用】 =========
        st.markdown("##### 1. 自动生成视频章节")
        gap_sec = st.slider("章节分割间隔阈值(秒)", min_value=2.0, max_value=15.0, value=6.0, step=0.5)
        btn_chapter_disabled = st.session_state["chapter_running"] or (not ollama_available) or (not mod_chapter_generator_ok)
        if st.button("生成章节列表", disabled=btn_chapter_disabled) and not st.session_state["chapter_running"] and ollama_available and mod_chapter_generator_ok:
            st.session_state["chapter_running"] = True
            st.session_state["chapter_cost"] = ""
            p_bar = st.progress(0)
            start_time = time.perf_counter()
            try:
                with st.spinner("生成章节..."):
                    p_bar.progress(15)
                    chapters = generate_chapters(raw_segs, gap_threshold=gap_sec)
                    p_bar.progress(85)
                    out_lines = []
                    for ch in chapters:
                        line = f"{ch['start_hms']} - {ch['end_hms']} | {ch['title']}"
                        out_lines.append(line)
                    final_text = "\n".join(out_lines)
                    p_bar.progress(100)
                end_time = time.perf_counter()
                cost = round(end_time - start_time, 2)
                st.session_state["chapter_cost"] = f"章节生成耗时：{cost} 秒"
                st.session_state["chapter_result_text"] = final_text
                st.session_state["show_chapter_result"] = True
                write_text_file(video_storage_folder, file_cfg["chapter"], final_text)
            except Exception as e:
                import traceback
                st.error(f"章节生成异常：{str(e)}")
                print(traceback.format_exc())
            finally:
                st.session_state["chapter_running"] = False

        if st.session_state["chapter_cost"]:
            st.caption(st.session_state["chapter_cost"])

        if st.session_state["chapter_result_text"] is not None:
            if st.session_state["show_chapter_result"]:
                col1, col2 = st.columns([0.9, 0.1])
                with col1:
                    st.markdown("###### 生成章节列表结果")
                with col2:
                    if st.button("关闭", key="close_chapter"):
                        st.session_state["show_chapter_result"] = False
                        st.rerun()
                st.text_area("章节内容", st.session_state["chapter_result_text"], height=320)
            else:
                if st.button("重新展示章节结果", key="reopen_chapter"):
                    st.session_state["show_chapter_result"] = True
                    st.rerun()

        st.divider()
        # ========= 2. 字幕关键词检索（纯文本匹配，不依赖Ollama！！） =========
        st.markdown("##### 2. 字幕关键词检索（仅文本匹配，不调用AI，无需Ollama）")
        keyword_input = st.text_input("输入检索关键词", placeholder="查找视频内相关片段", key="kw_search")
        col_s1, col_s2 = st.columns([0.3, 0.3])
        run_search = False
        with col_s1:
            run_search = st.button("开始检索", disabled=st.session_state["search_running"] or (not mod_search_engine_ok))

        if run_search and keyword_input.strip() and not st.session_state["search_running"] and mod_search_engine_ok:
            st.session_state["search_running"] = True
            start_t = time.perf_counter()
            try:
                hit_list, notice, new_idx = search_subtitle(
                    raw_segs, keyword_input.strip(),
                    index_cache=st.session_state.get("rag_index_cache")
                )
                st.session_state["rag_index_cache"] = new_idx
                st.session_state["search_hit_data"] = (hit_list, notice)
                st.session_state["show_search_result"] = True
                st.session_state["search_cost"] = f"检索耗时：{round(time.perf_counter()-start_t,2)} 秒"
            finally:
                st.session_state["search_running"] = False

        if st.session_state["search_cost"]:
            st.caption(st.session_state["search_cost"])

        if st.session_state.get("search_hit_data") is not None:
            if st.session_state["show_search_result"]:
                col1, col2 = st.columns([0.9, 0.1])
                with col1:
                    st.markdown("###### 检索命中片段")
                with col2:
                    if st.button("关闭检索面板", key="close_search"):
                        st.session_state["show_search_result"] = False
                        st.rerun()
                hit_list, notice = st.session_state["search_hit_data"]
                st.info(notice)
                for hit in hit_list:
                    st.write(f"📍 {hit.get('start',0)}s ~ {hit.get('end',0)}s：{hit.get('text','')}")
            else:
                if st.button("重新展示检索结果", key="reopen_search"):
                    st.session_state["show_search_result"] = True
                    st.rerun()

        st.divider()
        # ========= 3. AI快速问答（依赖Ollama，双重判断禁用按钮） =========
        st.markdown("##### 3. AI字幕问答（需要Ollama服务）")
        qa_question = st.text_input("输入你的问题", placeholder="针对视频内容提问", key="qa_input")
        qa_mode = st.radio(
            "问答模式",
            ["基于全部字幕(关键词粗筛)", "仅基于上方检索命中片段回答"],
            horizontal=True
        )

        col_qa1, col_qa2 = st.columns([0.3, 0.3])
        run_qa = False
        btn_qa_disabled = st.session_state["qa_running"] or (not ollama_available) or (not mod_qa_engine_ok)
        with col_qa1:
            run_qa = st.button("发起问答", disabled=btn_qa_disabled)
        with col_qa2:
            if st.button("清空问答结果"):
                st.session_state["qa_answer"] = ""
                st.session_state["show_qa_result"] = False
                st.rerun()

        if run_qa and qa_question.strip() and not st.session_state["qa_running"] and ollama_available and mod_qa_engine_ok:
            st.session_state["qa_running"] = True
            start_t = time.perf_counter()
            try:
                from video_search_engine import build_subtitle_index
                seg_meta, _ = build_subtitle_index(raw_segs)
                with st.spinner("AI正在思考，请耐心等待（CPU长文本速度较慢）..."):
                    if qa_mode == "基于全部字幕(关键词粗筛)":
                        ans = run_qa_full_subtitle(pure_sub_text, qa_question.strip(), seg_meta_list=seg_meta)
                    else:
                        hit_data = st.session_state.get("search_hit_data")
                        if hit_data is None:
                            ans = "⚠️请先执行关键词检索获取命中片段，再使用该模式！"
                        else:
                            hit_list, _ = hit_data
                            ans = run_qa_hit_fragments(hit_list, qa_question.strip())
                st.session_state["qa_answer"] = ans
                st.session_state["show_qa_result"] = True

                qa_cache_dict = st.session_state.get("qa_cache_dict", {})
                if not isinstance(qa_cache_dict, dict):
                    qa_cache_dict = {}
                qa_cache_dict[qa_question.strip()] = ans
                st.session_state["qa_cache_dict"] = qa_cache_dict
                write_text_file(video_storage_folder, file_cfg["qa_cache"], json.dumps(qa_cache_dict, ensure_ascii=False, indent=2))

                end_t = time.perf_counter()
                st.session_state["qa_cost"] = f"问答耗时：{round(end_t-start_t,2)} 秒"
            except Exception as e:
                import traceback
                err_msg = traceback.format_exc()
                print("问答异常堆栈：", err_msg)
                st.error(f"问答执行异常：{str(e)}")
            finally:
                st.session_state["qa_running"] = False

        if st.session_state["qa_cost"]:
            st.caption(st.session_state["qa_cost"])

        if st.session_state.get("show_qa_result") and st.session_state.get("qa_answer"):
            st.markdown("###### 🤖AI回答")
            st.text_area("回答内容", st.session_state["qa_answer"], height=260)


# Tab2 线上视频下载
with tab2:
    st.subheader("输入链接下载线上视频")
    with st.expander("📁 视频下载保存路径设置", expanded=True):
        col_btn1, col_btn2, col_text = st.columns([0.2, 0.2, 0.6])
        with col_btn1:
            if st.button("选择文件夹", key="sel_dl"):
                new_path = select_folder_dialog()
                if new_path:
                    st.session_state["download_dir"] = new_path
                    os.makedirs(new_path, exist_ok=True)
        with col_btn2:
            if st.button("恢复默认路径", key="reset_dl"):
                st.session_state["download_dir"] = DEFAULT_DOWNLOAD_DIR
                os.makedirs(DEFAULT_DOWNLOAD_DIR, exist_ok=True)
        with col_text:
            st.text_input("当前保存路径", value=st.session_state["download_dir"], disabled=True)

    url_input = st.text_input("粘贴视频链接")
    save_dir = st.session_state["download_dir"]
    if st.button("开始下载", key="dl_btn"):
        if not mod_video_download_ok:
            st.error("❌video_download模块未加载，下载功能不可用！")
        elif not url_input.strip():
            st.warning("请输入视频链接")
        else:
            with st.spinner("正在下载..."):
                ok, msg = download_video(url_input.strip(), save_dir=save_dir)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)


# Tab3 图片转换
with tab3:
    st.subheader("图片格式转换")
    with st.expander("📁 转换图片保存路径设置", expanded=True):
        col_btn1, col_btn2, col_text = st.columns([0.2, 0.2, 0.6])
        with col_btn1:
            if st.button("选择文件夹", key="sel_img"):
                new_path = select_folder_dialog()
                if new_path:
                    st.session_state["image_dir"] = new_path
                    os.makedirs(new_path, exist_ok=True)
        with col_btn2:
            if st.button("恢复默认路径", key="reset_img"):
                st.session_state["image_dir"] = DEFAULT_IMAGE_DIR
                os.makedirs(DEFAULT_IMAGE_DIR, exist_ok=True)
        with col_text:
            st.text_input("当前保存路径", value=st.session_state["image_dir"], disabled=True)

    up_img = st.file_uploader(
        "上传图片",
        type=None,
        help="支持 jpg、jpeg、png、bmp、webp、tif、tiff；⚠️tif/tiff浏览器无法预览，多页tiff只会处理第一页"
    )
    try:
        from io import BytesIO
        from image_convert import convert_image_bytes, SUPPORTED_OUT, SUPPORTED_IN
        target_fmt = st.selectbox("选择输出格式", SUPPORTED_OUT)

        if up_img is not None:
            file_ext = os.path.splitext(up_img.name)[1].lower().strip(".")
            if file_ext not in SUPPORTED_IN:
                st.error(f"不支持输入格式：{file_ext}。支持输入：{SUPPORTED_IN}")
            else:
                if file_ext in ("tif", "tiff"):
                    st.warning("⚠️当前是TIFF文件，浏览器不支持预览；转换功能正常，可直接点击执行转换下载文件；多页TIFF只会处理第一页。")
                else:
                    st.image(up_img, width=400)

                if st.button("执行格式转换"):
                    img_raw_bytes = up_img.getvalue()
                    try:
                        out_bio, new_filename = convert_image_bytes(img_raw_bytes, target_fmt, up_img.name)
                        final_image_bytes = out_bio.getvalue()
                        full_save_path = os.path.join(st.session_state["image_dir"], new_filename)
                        with open(full_save_path, "wb") as f:
                            f.write(final_image_bytes)
                        download_io = BytesIO(final_image_bytes)
                        st.success(f"转换完成，文件已保存至：{full_save_path}")
                        st.download_button(
                            label="下载转换后的图片",
                            data=download_io,
                            file_name=new_filename
                        )
                    except Exception as e:
                        import traceback
                        err_msg = traceback.format_exc()
                        st.error(f"转换失败:{e}")
                        st.code(err_msg)
    except ImportError:
        st.info("未加载图片转换模块，忽略此部分")


st.markdown("---")
current_display_name = st.session_state.get("user_video_folder_name", "未加载视频")
st.caption(f"""
当前视频文件夹名称：【{current_display_name}】
✅ txt文件支持任意手动改名，程序根据内容特征自动识别，不影响章节、检索、问答全部功能
⚠️ raw_segments.json 结构化文件不要手动重命名
✅ 界面文件名设置仅控制【新生成文件保存名称】，读取不受文件名限制
✅ 点击关闭仅隐藏面板，数据保留，可以点击【重新展示xxx结果】再次打开
""")
