def build_subtitle_index(raw_segments):
    seg_meta = []
    seg_lower_list = []
    for seg in raw_segments:
        if not isinstance(seg, dict):
            continue
        if "text" not in seg:
            continue
        txt = seg["text"].strip()
        seg_meta.append({
            "start": round(seg.get("start",0),2),
            "end": round(seg.get("end",0),2),
            "text": txt
        })
        seg_lower_list.append(txt.lower())
    return seg_meta, seg_lower_list


def search_subtitle(raw_segments, keyword: str, index_cache=None):
    """
    纯关键词字幕检索，只返回匹配片段，不调用大模型
    :param raw_segments: whisper原始segments
    :param keyword: 检索关键词
    :param index_cache: 索引缓存(seg_meta, seg_lower_list)
    :return: hit_list, notice, new_cache
    """
    try:
        q_ori = keyword.strip()
        q_low = q_ori.lower()
        if not q_low:
            return [], "请输入关键词", None

        if not isinstance(raw_segments, list):
            return [], "字幕片段数据异常，请重新执行字幕提取", None

        if index_cache is None:
            seg_meta, seg_lower_list = build_subtitle_index(raw_segments)
        else:
            seg_meta, seg_lower_list = index_cache

        hit_list = []
        for idx, text_low in enumerate(seg_lower_list):
            if q_low in text_low:
                meta = seg_meta[idx]
                hit_list.append(meta)

        if not hit_list:
            notice = "视频字幕中未找到包含该关键词的片段。"
        else:
            notice = f"共匹配到 {len(hit_list)} 处相关字幕片段"

        new_cache = (seg_meta, seg_lower_list)
        return hit_list, notice, new_cache
    except Exception as e:
        print(f"search_subtitle 异常：{e}")
        return [], f"检索异常：{str(e)}", None

