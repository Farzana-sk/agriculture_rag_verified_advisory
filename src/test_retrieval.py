import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from .retrieve import retrieve_documents
except ImportError:  # pragma: no cover - script execution support
    from retrieve import retrieve_documents

QUERIES = [
    "What are the varieties of cotton?",
    "Recommended fertilizer for tomato",
    "Chilli pest management",
    "Vegetable nursery management",
]


def main() -> None:
    for query in QUERIES:
        print(f"\nSubmitting Query: {query}")
        retrieved_docs = retrieve_documents(query, k=5)
        print("--- TOP RETRIEVED EVIDENCE FROM KNOWLEDGE BASE ---")
        if not retrieved_docs:
            print("No documents retrieved. Run: python src/ingest.py")
            continue
        for idx, doc in enumerate(retrieved_docs, start=1):
            snippet = doc["snippet"][:300]
            print(f"\n[Evidence {idx}] (Source: {doc['file']} | Page: {doc['page']})")
            print(snippet + ("..." if len(doc["snippet"]) > 300 else ""))


if __name__ == "__main__":
    main()
