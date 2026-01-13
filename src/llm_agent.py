from __future__ import annotations

import json
from typing import Any, Dict

from openai import OpenAI

SYSTEM_PROMPT = (
    "You are an information extraction system.\n"
    "Extract entities that match the topic definition.\n"
    "Constraints:\n"
    "- Only include entities explicitly present in the provided text.\n"
    "- Do not guess or infer missing items.\n"
    "- Keep entity names short noun phrases.\n"
    "- Descriptions must be one sentence grounded in the text.\n"
    "- If nothing matches, return an empty entities list.\n"
)

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "doc_id": {"type": "string"},
        "topic": {"type": "string"},
        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "evidence": {"type": "string"}
                },
                "required": ["name", "description", "evidence"]
            }
        }
    },
    "required": ["doc_id", "topic", "entities"]
}


def llm_extract(doc_id: str, topic_name: str, topic_def: str, text: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
    client = OpenAI()

    # user prompt combines topic definition w/ selected doc text to condition extraction behavior
    user_prompt = (
        f"Topic name: {topic_name}\n"
        f"Topic definition: {topic_def}\n"
        f"Selection policy: return only entities that directly satisfy the topic definition.\n\n"
        f"Document id: {doc_id}\n\n"
        f"Text:\n{text}"
    )

    # call the responses API w/ structured output enabled
    resp = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],

        # structured outputs for Responses API
        text={
            "format": {
                "type": "json_schema",
                "name": "ExtractionResult",
                "strict": True,
                "schema": SCHEMA,
            }
        },
    )

    # SDK returns structured output as JSON string
    raw = resp.output[0].content[0].text
    return json.loads(raw)


def entities_list_to_dict(items):
    out = {}
    for it in items or []:
        name = (it.get("name") or "").strip()
        desc = (it.get("description") or "").strip()

        # avoid empty values and duplicate entity names
        if name and desc and name.lower() not in (k.lower() for k in out):
            out[name] = desc
    return out
