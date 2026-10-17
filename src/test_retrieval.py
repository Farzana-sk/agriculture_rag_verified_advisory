from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

CHROMA_DB_DIR = "chroma_db"

# Initialize embedding model and connect to persisted ChromaDB
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
vector_db = Chroma(
    persist_directory=CHROMA_DB_DIR, 
    embedding_function=embedding_model
)

# Sample agricultural test query
query = "What are the varieties of cotton?"
print(f"\nSubmitting Query: {query}")
retrieved_docs = vector_db.similarity_search(query, k=5)

print("\n--- TOP RETRIEVED EVIDENCE FROM KNOWLEDGE BASE ---")
for idx, doc in enumerate(retrieved_docs, start=1):
    source = doc.metadata.get("source", "Unknown")
    page = doc.metadata.get("page", "Unknown")
    print(f"\n[Evidence {idx}] (Source: {source} | Page: {page})")
    print(doc.page_content.strip()[:300] + "...")