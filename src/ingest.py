import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHROMA_DB_DIR, RAW_PDF_DIR, ROOT_DIR, SKIP_PDF_SUBSTRINGS
from embeddings import get_embedding_model


def is_knowledge_pdf(path: Path) -> bool:
    name = path.name.lower()
    if not name.endswith(".pdf"):
        return False
    return not any(skip in name for skip in SKIP_PDF_SUBSTRINGS)


def collect_pdfs() -> list[Path]:
    RAW_PDF_DIR.mkdir(parents=True, exist_ok=True)
    pdfs = [p for p in RAW_PDF_DIR.glob("*.pdf") if is_knowledge_pdf(p)]

    if pdfs:
        return sorted(pdfs)

    # Copy Package of Practices PDFs from the project root if the farmer
    # knowledge folder is still empty.
    copied = []
    for path in ROOT_DIR.glob("*.pdf"):
        if not is_knowledge_pdf(path):
            continue
        if not path.name.lower().startswith("pop"):
            continue
        destination = RAW_PDF_DIR / path.name
        if not destination.exists():
            shutil.copy2(path, destination)
        copied.append(destination)
    return sorted(copied)


def ingest_documents() -> int:
    pdfs = collect_pdfs()
    if not pdfs:
        raise FileNotFoundError(
            f"No Package of Practices PDFs found in {RAW_PDF_DIR}. "
            "Copy pop_HF.pdf and pop_veg_culti*.pdf into data/raw_pdfs/"
        )

    print("--- Step 1: Loading Agricultural Manual PDFs ---")
    documents = []
    for pdf_path in pdfs:
        print(f"Loading document: {pdf_path}")
        loader = PyPDFLoader(str(pdf_path))
        documents.extend(loader.load())
    print(f"Total pages successfully loaded: {len(documents)}")

    print("\n--- Step 2: Splitting Documents into Chunks ---")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=80,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    print(f"Total chunks generated: {len(chunks)}")

    print("\n--- Step 3: Generating Embeddings and Building ChromaDB ---")
    persist_dir = Path(CHROMA_DB_DIR)
    if persist_dir.exists():
        shutil.rmtree(persist_dir)

    Chroma.from_documents(
        documents=chunks,
        embedding=get_embedding_model(),
        persist_directory=CHROMA_DB_DIR,
    )
    print(f"\n[SUCCESS] Vector indexing complete. Saved to: {CHROMA_DB_DIR}/")
    return len(chunks)


if __name__ == "__main__":
    ingest_documents()
