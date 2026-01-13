from __future__ import annotations

import os
import re
from typing import List, Tuple
from urllib.parse import urlparse

import fitz  # PyMuPDF
import requests


def load_pdf_bytes(url_or_path: str) -> Tuple[bytes, str]:

    if os.path.exists(url_or_path):
        path = os.path.abspath(url_or_path)
        with open(path, "rb") as f:
            return f.read(), os.path.basename(path)

    r = requests.get(url_or_path, timeout=30)
    r.raise_for_status()

    parsed = urlparse(url_or_path)
    name = os.path.basename(parsed.path) or "document.pdf"
    if not name.lower().endswith(".pdf"):
        name += ".pdf"

    return r.content, name


def pdf_to_text(pdf_bytes: bytes) -> str:

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return "\n".join(page.get_text("text") for page in doc)


def chunk_text(text: str, max_chars: int = 2600, overlap: int = 300) -> List[str]:

    text = re.sub(r"\r", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    chunks: List[str] = []
    i = 0
    n = len(text)

    while i < n:
        j = min(n, i + max_chars)
        chunks.append(text[i:j])
        if j >= n:
            break
        i = max(0, j - overlap)

    return chunks
