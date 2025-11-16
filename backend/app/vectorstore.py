from pathlib import Path
from typing import List

from .document import Document
from .config import settings

try:  # pragma: no cover - optional dependency handling
    from langchain_community.vectorstores import FAISS  # type: ignore
    from .llm import get_embeddings
except Exception:  # pragma: no cover
    FAISS = None  # type: ignore[assignment]
    get_embeddings = None  # type: ignore[assignment]


def _month_index_path(year: int, month: int) -> Path:
    return settings.vectorstore_root / str(year) / f"{month:02d}"


def load_or_create_month_index(year: int, month: int):
    """Load FAISS index for a given year/month, or create an empty one.

    Index is stored under: vectorstore_root/<year>/<month>/
    """
    if FAISS is None or get_embeddings is None:
        return None

    index_dir = _month_index_path(year, month)
    embeddings = get_embeddings()

    if index_dir.exists():
        return FAISS.load_local(str(index_dir), embeddings, allow_dangerous_deserialization=True)

    index_dir.mkdir(parents=True, exist_ok=True)
    # Start with an empty index
    return FAISS.from_documents([], embeddings)


def save_month_index(index, year: int, month: int) -> None:
    if index is None:
        return
    index_dir = _month_index_path(year, month)
    index_dir.mkdir(parents=True, exist_ok=True)
    index.save_local(str(index_dir))


def upsert_day_summaries(year: int, month: int, docs: List[Document]) -> None:
    """Add or update day summary documents in the corresponding month index."""
    if not docs:
        return
    index = load_or_create_month_index(year, month)
    if index is None:
        # FAISS/embeddings not available; skip vector indexing
        return
    index.add_documents(docs)
    save_month_index(index, year, month)


def search_month(year: int, month: int, query: str, k: int = 5) -> List[Document]:
    index = load_or_create_month_index(year, month)
    if index is None:
        return []
    return index.similarity_search(query, k=k)
