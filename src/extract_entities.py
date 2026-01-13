from __future__ import annotations

from .pdf_utils import load_pdf_bytes, pdf_to_pages, chunk_text
from .llm_agent import llm_extract


def extract_entities(document_url: str, topic_name: str, topic_def: str) -> dict:
    #extract text from pdf (local or url)
    pdf_bytes, doc_id = load_pdf_bytes(document_url)

    # full coverage
    pages = pdf_to_pages(pdf_bytes)

    merged = {}

    for page_idx, page_text in enumerate(pages, start=1):
        if not page_text or not page_text.strip():
            continue

        # chunk just to stay within limits
        page_chunks = chunk_text(page_text, max_chars=2600, overlap=300)

        for chunk in page_chunks:
            if not chunk.strip():
                continue

            # llm call per chunk
            result = llm_extract(
                doc_id=doc_id,
                topic_name=topic_name,
                topic_def=topic_def,
                text=chunk,
            )

            # build new entities dict in merged
            for it in result.get("entities", []) or []:
                name = (it.get("name") or "").strip()
                desc = (it.get("description") or "").strip()

                if not name or not desc:
                    continue

                key = name.lower()
                if key not in merged:
                    merged[key] = {"name": name, "description": desc}

    # build final output
    entities = {v["name"]: v["description"] for v in merged.values()}
    return {
        "doc_id": doc_id,
        "topic": topic_name,
        "entities": entities,
    }


