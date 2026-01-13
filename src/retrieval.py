from __future__ import annotations

import re
from typing import List, Tuple


def make_keywords(topic_name: str, topic_def: str) -> List[str]:
    # build keyword set, used for retrieval

    #normalize combined name and definition
    raw = f"{topic_name} {topic_def}".lower()
    words = re.findall(r"[a-z]{3,}", raw)

    # combine stopwords that don't distinguish sections
    stop = {
        "the", "and", "for", "with", "that", "this", "from", "are", "under", "into",
        "your", "you", "will", "shall", "such", "than", "then", "include", "including",
        "explicitly", "listed", "definition",
    }
    # preserve order and uniqueness
    out: List[str] = []
    for w in words:
        if w not in stop and w not in out:
            out.append(w)
    return out


def score_chunk(chunk: str, keywords: List[str]) -> float:
    c = chunk.lower()
    score = 0.0

    # keyword overlap with the topic definition
    score += sum(1.0 for kw in keywords if kw in c)

    # heuristics tuned for insurance docs
    score += min(10.0, 0.9 * chunk.count("$"))
    score += 3.0 if re.search(r"\n\s*[\-\u2022•\u00B7\uF0B7\u25CF]\s+", chunk) else 0.0
    score += 2.5 if "schedule" in c else 0.0
    score += 1.5 if "benefit" in c or "benefits" in c else 0.0

    # small generic penalty for front matter
    if "customer service" in c or "welcome to" in c:
        score -= 1.5

    return score


def select_top_chunks(chunks: List[str], keywords: List[str], k: int = 6) -> List[str]:
    # score each chunk
    scored: List[Tuple[str, float]] = [(ch, score_chunk(ch, keywords)) for ch in chunks]

    # highest score first
    scored.sort(key=lambda x: x[1], reverse=True)

    # keep wider candidate set, but drop irrelevant chunks
    top = [ch for ch, s in scored[: max(14, k * 3)] if s > 0]

    # if nothing scores well, fall back to the first couple chunks
    return top[:k] if top else chunks[:k]
