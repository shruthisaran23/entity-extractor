from __future__ import annotations

from .pdf_utils import load_pdf_bytes, pdf_to_text, chunk_text
from .retrieval import make_keywords, select_top_chunks
from .llm_agent import llm_extract, entities_list_to_dict


def extract_entities(document_url: str, topic_name: str, topic_def: str) -> dict:
    #extract text from pdf (local or url)
    pdf_bytes, doc_id = load_pdf_bytes(document_url)
    text = pdf_to_text(pdf_bytes)


    #generate topic key words and chunk text
    keywords = make_keywords(topic_name, topic_def)
    chunks = chunk_text(text, max_chars=2600, overlap=300)
    picked = select_top_chunks(chunks, keywords, k=6)

    # keep prompt bounded
    context = "\n\n---\n\n".join(picked)

    # call to LLM
    result = llm_extract(doc_id=doc_id, topic_name=topic_name, topic_def=topic_def, text=context)

    #normalize into final dict
    entities = entities_list_to_dict(result.get("entities", []))

    return {
        "doc_id": doc_id,
        "topic": topic_name,
        "entities": entities,
    }
