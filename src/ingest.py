import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Directory paths
DATA_DIR = "data/raw_pdfs"
CHROMA_DB_DIR = "chroma_db"

print("--- Step 1: Loading Agricultural Manual PDFs ---")
documents = []

if not os.path.exists(DATA_DIR):
    raise FileNotFoundError(f"Directory not found: {DATA_DIR}. Please verify the path.")

# Read all PDF files from the raw_pdfs folder
for file in os.listdir(DATA_DIR):
    if file.endswith(".pdf"):
        pdf_path = os.path.join(DATA_DIR, file)
        print(f"Loading document: {pdf_path}")
        loader = PyPDFLoader(pdf_path)
        documents.extend(loader.load())

print(f"Total pages successfully loaded: {len(documents)}")

# Step 2: Split text into manageable chunks
print("\n--- Step 2: Splitting Documents into Chunks ---")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", " ", ""]
)

chunks = text_splitter.split_documents(documents)
print(f"Total chunks generated: {len(chunks)}")

# Step 3: Embed chunks and persist to ChromaDB
print("\n--- Step 3: Generating Embeddings and Building ChromaDB ---")
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_db = Chroma.from_documents(
    documents=chunks,
    embedding=embedding_model,
    persist_directory=CHROMA_DB_DIR
)

print(f"\n[SUCCESS] Vector indexing complete. Vector database saved to: {CHROMA_DB_DIR}/")