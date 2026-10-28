from functools import lru_cache

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

try:
    from .config import CHROMA_DB_DIR, EMBEDDING_MODEL_NAME
except ImportError:  # pragma: no cover - script execution support
    from config import CHROMA_DB_DIR, EMBEDDING_MODEL_NAME


@lru_cache(maxsize=1)
def get_embedding_model():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)


def get_vector_store(create: bool = False) -> Chroma:
    return Chroma(
        persist_directory=CHROMA_DB_DIR,
        embedding_function=get_embedding_model(),
    )
