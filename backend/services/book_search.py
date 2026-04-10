# -*- coding: utf-8 -*-
"""Book library search service - RAG retrieval from classical texts"""
from pathlib import Path
from typing import List, Dict, Any

BOOK_DIR = Path(r"C:\Users\Administrator\WorkBuddy\20260409001107\书库\语料库\分类汇总")

class BookSearch:
    def __init__(self):
        self.corpus_files = {
            "术数权威": BOOK_DIR / "术数权威_语料库.txt",
            "经学核心": BOOK_DIR / "经学核心_语料库.txt",
            "奇门紫微": BOOK_DIR / "奇门紫微_语料库.txt",
            "全部书籍": BOOK_DIR / "全部书籍语料库.txt",
        }
        self._cache = {}

    def search(self, keywords: List[str], top_k: int = 5, max_chars: int = 200) -> List[Dict[str, Any]]:
        results = []
        for name, path in self.corpus_files.items():
            if not path.exists():
                continue
            text = self._load_text(path)
            for kw in keywords:
                matches = self._find_matches(text, kw, max_chars)
                for match in matches[:3]:
                    results.append({
                        "source": name,
                        "keyword": kw,
                        "segment": match["text"],
                    })
        results.sort(key=lambda x: len(x["keyword"]), reverse=True)
        return results[:top_k]

    def _load_text(self, path: Path) -> str:
        if path not in self._cache:
            try:
                self._cache[path] = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                self._cache[path] = ""
        return self._cache[path]

    def _find_matches(self, text: str, keyword: str, max_chars: int) -> List[Dict]:
        matches = []
        pos = 0
        while True:
            idx = text.find(keyword, pos)
            if idx == -1:
                break
            start = max(0, idx - 80)
            end = min(len(text), idx + len(keyword) + 80)
            snippet = text[start:end].replace("\n", " ").strip()
            matches.append({"text": snippet})
            pos = idx + 1
        return matches

    def search_bazi_terms(self, terms: List[str]) -> List[Dict[str, Any]]:
        return self.search(terms, top_k=5)

_book_search = None

def get_book_search() -> "BookSearch":
    global _book_search
    if _book_search is None:
        _book_search = BookSearch()
    return _book_search
