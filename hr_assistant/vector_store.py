"""Step 4: store chunk embeddings in Chroma so we can search them later."""

import hashlib
from pathlib import Path

from langchain_chroma import Chroma

from hr_assistant import config
from hr_assistant.embeddings import get_embeddings_model
from hr_assistant.logger import get_logger

logger = get_logger(__name__)


def _chunk_id(chunk):
    """Stable ID from source, page, and text (same content → same ID every run)."""
    key = f"{chunk.metadata['source']}|{chunk.metadata['page']}|{chunk.page_content}"
    return hashlib.sha256(key.encode()).hexdigest()


def vector_store_exists() -> bool:
    """Return True if a Chroma database folder already exists on disk."""
    chroma_path = Path(config.CHROMA_DIR)
    return chroma_path.is_dir() and any(chroma_path.iterdir())


def load_vector_store():
    """Open an existing Chroma database from disk."""
    logger.info("Loading Chroma database from '%s'", config.CHROMA_DIR)
    embeddings_model = get_embeddings_model()
    return Chroma(
        persist_directory=config.CHROMA_DIR,
        embedding_function=embeddings_model,
    )


def build_vector_store(chunks):
    """Embed chunks and sync them into Chroma (add new, remove outdated)."""
    logger.info(
        "Embedding %d chunk(s) and syncing to Chroma at '%s'...",
        len(chunks),
        config.CHROMA_DIR,
    )
    unique_chunks = {}
    for chunk in chunks:
        unique_chunks[_chunk_id(chunk)] = chunk

    embeddings_model = get_embeddings_model()
    vector_store = Chroma(
        persist_directory=config.CHROMA_DIR,
        embedding_function=embeddings_model,
    )

    # Add only chunks that aren't stored yet
    all_ids = list(unique_chunks.keys())
    stored_result = vector_store.get(ids=all_ids)
    existing_ids = stored_result["ids"]

    new_ids = []
    new_documents = []

    for chunk_id, chunk in unique_chunks.items():
        if chunk_id in existing_ids:
            continue

        new_ids.append(chunk_id)
        new_documents.append(chunk)

    if len(new_documents) > 0:
        vector_store.add_documents(documents=new_documents, ids=new_ids)

    # Remove chunks from PDFs that were edited or deleted
    everything_stored = vector_store.get(include=[])
    stored_ids = everything_stored["ids"]

    outdated_ids = []
    for stored_id in stored_ids:
        if stored_id not in unique_chunks:
            outdated_ids.append(stored_id)

    if len(outdated_ids) > 0:
        vector_store.delete(ids=outdated_ids)

    logger.info("Added %d new chunks", len(new_documents))
    logger.info("Skipped %d chunks that were already stored", len(existing_ids))
    logger.info("Removed %d outdated chunks", len(outdated_ids))

    return vector_store


def get_retriever(vector_store, k=None):
    """Return a retriever that fetches the top-k most similar chunks."""
    top_k = k if k is not None else config.TOP_K_RESULTS
    logger.info("Creating retriever with top_k=%d", top_k)
    return vector_store.as_retriever(
        search_kwargs={"k": top_k}
    )
