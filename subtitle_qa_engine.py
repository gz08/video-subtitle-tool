from llm_client import llm_infer

QA_TIMEOUT_MSG = "[QA_LLM_TIMEOUT]"

def clean_markdown_text(raw_text: str) -> str:
    """清除多余 markdown 符号 # * -‑，输出干净纯文本"""
    lines = raw_text.splitlines()
    out = []
    for line in lines:
        s = line.strip()
        s = s.lstrip("#*‑-")
        if s:
            out.append(s)
    return "\n".join(out)


def build_context_from_hits(hit_list):
    """拼接字幕片段，保留时间戳，时间戳是本项目核心特色"""
    lines = []
    for meta in hit_list:
        lines.append(f"【{meta['start']}s‑{meta['end']}s】{meta['text']}")
    return "\n".join(lines)


def simple_text_relevance_filter(seg_meta_list, question: str, top_limit=12, min_score=2):
    """
    关键词打分 + 重排序
    min_score=2：至少命中 2 个关键词才保留，过滤弱相关片段，源头减少文本量
    """
    q_words = set(question.lower().split())
    scored_segs = []
    for seg in seg_meta_list:
        seg_text_low = seg["text"].lower()
        score = 0
        for word in q_words:
            if len(word) >= 2 and word in seg_text_low:
                score += 1
        if score >= min_score:
            scored_segs.append((-score, seg))
    scored_segs.sort()
    take_segs = [item[1] for item in scored_segs[:top_limit]]
    return take_segs


def split_text_chunk(text: str, chunk_size=2400):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end
    return chunks


def multi_chunk_fast_extract(chunk_list, question):
    """分块提取：精简prompt，只提取和问题简短要点，减少单块推理负担"""
    point_list = []
    for idx, chunk in enumerate(chunk_list):
        prompt = f"""
字幕片段{idx+1}:
{chunk}
问题:{question}
只提取与此问题相关简短要点，无相关直接输出【无】，不要多余解释格式。
"""
        resp = llm_infer(prompt, is_chapter=False)
        if resp == QA_TIMEOUT_MSG:
            continue
        r = resp.strip()
        if r != "【无】":
            point_list.append(r)
    return "\n".join(point_list)


def final_fast_answer(summary_points: str, question, hit_segments):
    """
    汇总回答，强制带上参考的视频时间戳，项目核心特色，区分字幕内容与外部知识
    """
    ts_list = [f"{s['start']}s‑{s['end']}s" for s in hit_segments]
    time_note = f"本回答参考视频片段时间位置：{'、'.join(ts_list)}"

    prompt = f"""
材料要点:
{summary_points}
{time_note}

问题:{question}

输出严格格式：
🎬 视频内容
（只使用材料里面实际出现信息，不要编造；无相关写：根据字幕，视频未提及该内容）

🧠 知识补充
（写模型外部知识，不属于视频字幕；末尾固定一行：> 注意：以上知识补充不属于视频字幕原文，模型生成内容可能存在错误。）

禁止#*‑等markdown符号，只用普通换行文字。
"""
    resp = llm_infer(prompt, is_chapter=False)
    if resp == QA_TIMEOUT_MSG:
        return "⚠️汇总阶段推理超时，请简化你的问题或使用检索片段问答模式。"
    return clean_markdown_text(resp)


def run_qa_full_subtitle(full_subtitle_text: str,
                         question: str,
                         seg_meta_list=None,
                         max_context_chars=5500,
                         enable_chunk_mode=True):
    import time
    t0_total = time.perf_counter()
    use_context_text = full_subtitle_text
    hit_segments = []

    # 1、关键词筛选
    t1 = time.perf_counter()
    if seg_meta_list and isinstance(seg_meta_list, list):
        related_segs = simple_text_relevance_filter(seg_meta_list, question, top_limit=12, min_score=2)
        if related_segs:
            hit_segments = related_segs
            use_context_text = build_context_from_hits(related_segs)
    t_filter = round(time.perf_counter() - t1, 2)
    input_len = len(use_context_text)
    print(f"【QA‑INPUT‑LEN】{input_len}，片段过滤耗时：{t_filter}s")

    # 分段降级逻辑，严格限制最大调用块数 = 2，防止多轮 LLM 时间爆炸
    if enable_chunk_mode and len(use_context_text) > 2200:
        chunks = split_text_chunk(use_context_text, chunk_size=2400)
        MAX_CHUNK_CALL = 2
        if len(chunks) > MAX_CHUNK_CALL:
            chunks = chunks[:MAX_CHUNK_CALL]
            print(f"【QA 块过多，截断至 {MAX_CHUNK_CALL} 块，控制总耗时】")
        print(f"【QA 开启分段模式，块数量：{len(chunks)}】")

        t2 = time.perf_counter()
        combined_summary = multi_chunk_fast_extract(chunks, question)
        t_extract = round(time.perf_counter() - t2, 2)

        if not combined_summary.strip():
            total_cost = round(time.perf_counter() - t0_total, 2)
            print(f"【QA各阶段耗时】过滤:{t_filter}s｜分块提取:{t_extract}s｜总耗时:{total_cost}s")
            return "⚠️分段处理未提取到有效信息，请简化你的问题或使用检索片段问答模式。"

        t3 = time.perf_counter()
        ans = final_fast_answer(combined_summary, question, hit_segments)
        t_merge = round(time.perf_counter() - t3, 2)
        total_cost = round(time.perf_counter() - t0_total, 2)
        print(f"【QA各阶段耗时】过滤:{t_filter}s｜分块提取:{t_extract}s｜汇总生成:{t_merge}s｜总耗时:{total_cost}s")
        return ans
    else:
        if len(use_context_text) > max_context_chars:
            use_context_text = use_context_text[:max_context_chars] + "\n……内容过长已截断"

        ts_list = [f"{s['start']}s‑{s['end']}s" for s in hit_segments]
        time_note = f"本回答参考视频片段时间位置：{'、'.join(ts_list)}"

        prompt = f"""
【视频字幕参考】
{use_context_text}
{time_note}

问题:{question}

输出严格格式：
🎬 视频内容
（只使用字幕实际出现信息，不要编造；无相关写：根据字幕，视频未提及该内容）

🧠 知识补充
（写模型外部知识，不属于视频字幕；末尾固定一行：> 注意：以上知识补充不属于视频字幕原文，模型生成内容可能存在错误。）

禁止#*‑等markdown符号，只用普通换行文字。
"""
        t_llm_start = time.perf_counter()
        try:
            resp = llm_infer(prompt, is_chapter=False)
            t_llm = round(time.perf_counter() - t_llm_start, 2)
            total_cost = round(time.perf_counter() - t0_total, 2)
            print(f"【QA各阶段耗时】过滤:{t_filter}s｜LLM直接生成:{t_llm}s｜总耗时:{total_cost}s")
            if resp == QA_TIMEOUT_MSG:
                return "⚠️大模型推理超时！CPU硬件处理长文本能力有限，强烈建议优先使用关键词检索后，选择「仅基于上方检索命中片段回答」。"
            return clean_markdown_text(resp)
        except Exception as e:
            print(f"LLM问答异常:{e}")
            return "大模型接口调用失败，请重试"


def run_qa_hit_fragments(hit_list, question: str, max_context_chars=5500):
    import time
    t0 = time.perf_counter()
    context = build_context_from_hits(hit_list)
    if not context.strip():
        return "没有可用字幕片段，无法进行问答，请先检索关键词。"

    input_len = len(context)
    print(f"【QA‑HIT‑INPUT‑LEN】{input_len}")
    if len(context) > max_context_chars:
        context = context[:max_context_chars] + "\n……内容过长已截断"

    ts_list = [f"{s['start']}s‑{s['end']}s" for s in hit_list]
    time_note = f"本回答参考视频片段时间位置：{'、'.join(ts_list)}"

    prompt = f"""
【参考字幕片段】
{context}
{time_note}

问题:{question}

输出严格格式：
🎬 视频内容
（只使用片段实际出现信息，不要编造；无相关写：根据字幕，视频未提及该内容）

🧠 知识补充
（写模型外部知识，不属于视频字幕；末尾固定一行：> 注意：以上知识补充不属于视频字幕原文，模型生成内容可能存在错误。）

禁止#*‑等markdown符号，只用普通换行文字。
"""
    t_llm_s = time.perf_counter()
    try:
        resp = llm_infer(prompt, is_chapter=False)
        t_llm = round(time.perf_counter() - t_llm_s, 2)
        total = round(time.perf_counter() - t0, 2)
        print(f"【检索问答各阶段耗时】LLM生成:{t_llm}s｜总耗时:{total}s")
        if resp == QA_TIMEOUT_MSG:
            return "⚠️推理超时，请缩小检索关键词。"
        return clean_markdown_text(resp)
    except Exception as e:
        print(f"LLM问答异常:{e}")
        return "大模型接口调用失败，请重试"


