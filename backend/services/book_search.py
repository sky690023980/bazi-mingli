# -*- coding: utf-8 -*-
"""
书库语料全文检索服务
读取本地语料库文件，按关键词全文检索相关段落
语料库路径：C:\Users\Administrator\WorkBuddy\20260409001107\书库\语料库\分类汇总\
"""
import os
import re
from typing import List, Dict, Any

# 语料库文件路径
BOOK_BASE = r"C:\Users\Administrator\WorkBuddy\20260409001107\书库\语料库\分类汇总"

BOOK_FILES = {
    "术数权威": os.path.join(BOOK_BASE, "术数权威_语料库.txt"),
    "经学核心": os.path.join(BOOK_BASE, "经学核心_语料库.txt"),
    "奇门紫微": os.path.join(BOOK_BASE, "奇门紫微_语料库.txt"),
    "全部书籍": os.path.join(BOOK_BASE, "全部书籍语料库.txt"),
}

# 全局缓存：{文件名: [段落列表]}
_BOOK_CACHE: Dict[str, List[str]] = {}
_BOOK_LOADED = False


def _ensure_loaded():
    """懒加载语料库到内存"""
    global _BOOK_LOADED, _BOOK_CACHE
    if _BOOK_LOADED:
        return
    for name, filepath in BOOK_FILES.items():
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8-sig") as f:
                    content = f.read()
                # 按换行+空行切分段落
                raw_paragraphs = re.split(r'\n{2,}', content)
                # 过滤空段落和元数据行
                paragraphs = [
                    p.strip() for p in raw_paragraphs
                    if len(p.strip()) >= 30  # 至少30字
                    and not p.strip().startswith("#")  # 过滤注释行
                    and not re.match(r'^=+$', p.strip())  # 过滤分隔线
                    and not re.match(r'^# \w+语料库', p.strip())  # 过滤元数据头
                ]
                _BOOK_CACHE[name] = paragraphs
            except Exception as e:
                _BOOK_CACHE[name] = []
        else:
            _BOOK_CACHE[name] = []
    _BOOK_LOADED = True


def _score_paragraph(paragraph: str, keywords: List[str]) -> int:
    """计算段落与关键词的匹配得分"""
    score = 0
    p_lower = paragraph.lower()
    for kw in keywords:
        kw_lower = kw.lower()
        # 包含关键词
        if kw_lower in p_lower:
            score += 10
            # 计算关键词在段落中的密度
            count = p_lower.count(kw_lower)
            score += min(count * 2, 20)  # 最多加20分
    # 长度惩罚（太长或太短都降低）
    if len(paragraph) > 500:
        score -= 5
    if len(paragraph) < 50:
        score -= 5
    return max(score, 0)


def _extract_snippet(paragraph: str, keywords: List[str], max_len: int = 200) -> str:
    """从段落中提取最相关的片段"""
    if len(paragraph) <= max_len:
        return paragraph
    # 找到第一个关键词出现位置，提取其周围上下文
    p_lower = paragraph.lower()
    first_pos = -1
    for kw in keywords:
        pos = p_lower.find(kw.lower())
        if pos != -1:
            first_pos = pos
            break
    if first_pos == -1:
        return paragraph[:max_len] + "..."
    # 从关键词位置前后扩展
    start = max(0, first_pos - 50)
    end = min(len(paragraph), first_pos + max_len - 50)
    snippet = paragraph[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(paragraph):
        snippet = snippet + "..."
    return snippet


def search_book(keyword: str, max_results: int = 5, max_paragraphs: int = 5) -> Dict[str, Any]:
    """
    根据关键词在语料库中全文检索，返回最相关的段落
    参数：
        keyword: 搜索关键词（八字术语、卦名、神煞等）
        max_results: 最大返回条数（默认5条）
        max_paragraphs: 每个文件最多返回段落数（默认5段）
    返回：
        {"keyword": str, "total_found": int, "results": [段落列表], "sources": [来源列表]}
    """
    _ensure_loaded()

    if not keyword or len(keyword.strip()) < 1:
        return {"keyword": keyword, "total_found": 0, "results": [], "sources": []}

    # 关键词预处理（支持多关键词）
    keywords = [k.strip() for k in keyword.replace("，", ",").replace("、", ",").split(",") if k.strip()]

    all_matches: List[Dict[str, Any]] = []

    for name, paragraphs in _BOOK_CACHE.items():
        file_top: List[Dict] = []
        for para in paragraphs:
            score = _score_paragraph(para, keywords)
            if score > 0:
                snippet = _extract_snippet(para, keywords)
                file_top.append({
                    "score": score,
                    "source": name,
                    "text": snippet,
                    "full_text": para[:400] if len(para) > 400 else para,
                })
        # 每个文件取前max_paragraphs个
        file_top.sort(key=lambda x: x["score"], reverse=True)
        all_matches.extend(file_top[:max_paragraphs])

    # 全局排序，取前max_results个
    all_matches.sort(key=lambda x: x["score"], reverse=True)
    top_results = all_matches[:max_results]

    results = [
        {
            "rank": i + 1,
            "source": r["source"],
            "text": r["text"],
            "score": r["score"],
        }
        for i, r in enumerate(top_results)
    ]
    sources = list(dict.fromkeys(r["source"] for r in top_results))

    return {
        "keyword": keyword,
        "total_found": len(all_matches),
        "returned": len(results),
        "results": results,
        "sources": sources,
    }


def search_multi_keywords(keywords: List[str], max_per_keyword: int = 3) -> Dict[str, Any]:
    """
    多关键词检索，合并去重后返回
    参数：
        keywords: 关键词列表
        max_per_keyword: 每个关键词最多返回条数
    返回：聚合检索结果
    """
    all_results = []
    seen_texts = set()
    for kw in keywords:
        result = search_book(kw, max_results=max_per_keyword)
        for r in result["results"]:
            if r["text"] not in seen_texts:
                seen_texts.add(r["text"])
                all_results.append({**r, "keyword": kw})
    # 全局排序
    all_results.sort(key=lambda x: x["score"], reverse=True)
    return {
        "keywords": keywords,
        "total_results": len(all_results),
        "results": all_results[:10],
    }


def build_book_context(pillar_result: Dict, topic: str = "综合解读", max_results: int = 5) -> str:
    """
    从八字排盘结果中提取关键词，在书库中检索相关内容，构建上下文字符串
    用于增强 LLM 解读
    参数：
        pillar_result: 八字排盘结果
        topic: 当前解读主题（如"事业"、"婚姻"、"健康"）
        max_results: 最大检索条数
    返回：书库相关内容拼接字符串
    """
    keywords = []
    pillar = pillar_result.get("pillar", {})
    wuxing = pillar_result.get("wuxing", {})
    geju = pillar_result.get("geju", {})

    # 从排盘结果中提取关键词
    for p in pillar.values():
        if isinstance(p, str) and len(p) >= 2:
            keywords.append(p[:2])  # 取干支前两字

    # 加入格局、用神、主题词
    if isinstance(geju, dict):
        keywords.append(geju.get("name", ""))
    for wx in wuxing.get("xiyongshen", [])[:2]:
        keywords.append(wx)
    for wx in wuxing.get("jishen", [])[:2]:
        keywords.append(wx)
    keywords.append(topic)

    # 去重
    seen = set()
    unique_kw = []
    for k in keywords:
        k_strip = k.strip()
        if k_strip and k_strip not in seen:
            seen.add(k_strip)
            unique_kw.append(k_strip)

    # 检索
    result = search_multi_keywords(unique_kw[:5], max_per_keyword=2)

    if not result["results"]:
        return ""

    # 构建上下文
    context_lines = ["【书库参考】"]
    for r in result["results"][:max_results]:
        context_lines.append(f"（来源：{r['source']}）{r['text']}")
    context_lines.append("【解读依据结束】")
    return "\n".join(context_lines)


# 预热加载（可选，启动时调用）
def preload_books():
    """预加载语料库到内存"""
    _ensure_loaded()
    total = sum(len(p) for p in _BOOK_CACHE.values())
    print(f"[书库] 已加载 {len(_BOOK_CACHE)} 个语料库文件，共 {total} 个有效段落")


if __name__ == "__main__":
    # 测试
    preload_books()
    result = search_book("紫微星", max_results=3)
    print(f"检索「紫微星」，找到 {result['total_found']} 条匹配，返回 {result['returned']} 条")
    for r in result["results"]:
        print(f"  [{r['source']}] {r['text'][:80]}...")
