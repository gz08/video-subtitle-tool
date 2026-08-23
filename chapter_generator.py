"""
极速视频章节生成器 V3修复版
修复：章节标题直接摘抄单句字幕、断章取义问题
速度维持120~180s，同时大幅提升标题概括性
"""

def get_hms(seconds: float) -> str:
    """秒数转 00:00:00 时间格式"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def generate_chapters(raw_segments, gap_threshold=10.0, max_block_text_len=800, min_block_duration=45.0):
    """
    :param raw_segments: whisper识别字幕片段
    :param gap_threshold: 断章静默间隔(秒)
    :param max_block_text_len: 单块字幕最大字符
    :param min_block_duration: 最小章节时长，低于该时长强制和下一块合并（重点修复开头小块）
    :return: 章节列表
    """
    blocks = []
    if not raw_segments:
        return []

    cur_block = {
        "start": raw_segments[0]["start"],
        "end": raw_segments[0]["end"],
        "texts": [raw_segments[0]["text"].strip()]
    }

    # 第一步：基于时间间隔合并原始字幕块
    for seg in raw_segments[1:]:
        gap = seg["start"] - cur_block["end"]
        if gap < gap_threshold:
            cur_block["end"] = seg["end"]
            cur_block["texts"].append(seg["text"].strip())
        else:
            blocks.append(cur_block)
            cur_block = {
                "start": seg["start"],
                "end": seg["end"],
                "texts": [seg["text"].strip()]
            }
    blocks.append(cur_block)

    # 新增：合并时长过短的小块，杜绝开头零碎片段独立成章（关键修复！）
    merged_blocks = []
    temp_short_block = None
    for b in blocks:
        duration = b["end"] - b["start"]
        if duration < min_block_duration:
            if temp_short_block is None:
                temp_short_block = b
            else:
                # 和上一个小块合并
                temp_short_block["end"] = b["end"]
                temp_short_block["texts"].extend(b["texts"])
        else:
            if temp_short_block is not None:
                merged_blocks.append(temp_short_block)
                temp_short_block = None
            merged_blocks.append(b)
    if temp_short_block is not None:
        merged_blocks.append(temp_short_block)
    blocks = merged_blocks

    # 控制总段落数量，避免输入token爆炸
    target_max_chunk_count = 30
    if len(blocks) > target_max_chunk_count:
        merge_ratio = len(blocks) // target_max_chunk_count
        new_blocks = []
        temp_block = None
        for b in blocks:
            if temp_block is None:
                temp_block = {
                    "start": b["start"],
                    "end": b["end"],
                    "texts": b["texts"].copy()
                }
            else:
                temp_block["end"] = b["end"]
                temp_block["texts"].extend(b["texts"])
            if len(temp_block["texts"]) >= merge_ratio:
                new_blocks.append(temp_block)
                temp_block = None
        if temp_block is not None:
            new_blocks.append(temp_block)
        blocks = new_blocks

    from llm_client import llm_infer
    full_content = ""
    for idx, b in enumerate(blocks):
        text_merge = " ".join(b["texts"])
        if len(text_merge) > max_block_text_len:
            text_merge = text_merge[:max_block_text_len] + "……"
        full_content += f"{idx+1}|{text_merge}\n"

    # 【强化约束Prompt，解决标题直接摘抄句子】
    prompt = f"""
阅读每一段字幕，提炼整体主题生成章节标题。
硬性规则：
1.标题6~18个字，概括整段核心主题；
2.禁止直接摘抄字幕内完整句子，不要局限于单句话信息；
3.客观总结内容，不要局限局部细节；
4.严格输出格式：序号|标题
只输出结果，不要额外解释。

字幕：
{full_content}
"""
    try:
        res = llm_infer(prompt)
    except Exception as e:
        print(f"章节生成LLM调用异常:{e}")
        chapters = []
        for i, block in enumerate(blocks):
            chapters.append({
                "start": block["start"],
                "end": block["end"],
                "start_hms": get_hms(block["start"]),
                "end_hms": get_hms(block["end"]),
                "title": f"章节{i+1}"
            })
        return chapters

    lines = res.strip().splitlines()
    chapters = []
    for i, block in enumerate(blocks):
        title = f"章节{i+1}"
        if i < len(lines):
            line = lines[i].strip()
            if "|" in line:
                parts = line.split("|", maxsplit=1)
                if len(parts) == 2:
                    title = parts[1].strip()
        chapters.append({
            "start": block["start"],
            "end": block["end"],
            "start_hms": get_hms(block["start"]),
            "end_hms": get_hms(block["end"]),
            "title": title
        })
    return chapters

