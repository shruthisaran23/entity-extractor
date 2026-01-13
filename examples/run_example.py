import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(REPO_ROOT)

from src.extract_entities import extract_entities

DEFAULT_DOC = os.path.join(REPO_ROOT, "data", "Guardian_Accident.pdf")
TOPICS_FILE = os.path.join(os.path.dirname(__file__), "sample_topics.json")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")


def main():
    # load topics
    with open(TOPICS_FILE, "r") as f:
        topics = json.load(f)

    doc = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DOC
    topic_name = sys.argv[2] if len(sys.argv) > 2 else next(iter(topics))
    topic_def = topics.get(topic_name)

    if topic_def is None:
        raise ValueError(f"Unknown topic '{topic_name}'. Available: {list(topics.keys())}")

    # run extraction
    result = extract_entities(doc, topic_name, topic_def)

    # make sure output dir exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # build output filename
    doc_base = os.path.splitext(os.path.basename(doc))[0]
    output_path = os.path.join(
        OUTPUT_DIR,
        f"output_{doc_base}_{topic_name}.json"
    )

    # write JSON
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Extraction complete")
    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    main()
