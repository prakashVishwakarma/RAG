"""Step 2: split documents into overlapping chunks."""

from langchain_text_splitters import RecursiveCharacterTextSplitter

from hr_assistant import config
from hr_assistant.logger import get_logger

logger = get_logger(__name__)


def split_into_chunks(documents, chunk_size=None, chunk_overlap=None):
    """Split documents into chunks for embedding."""
    size = chunk_size if chunk_size is not None else config.CHUNK_SIZE
    overlap = chunk_overlap if chunk_overlap is not None else config.CHUNK_OVERLAP
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=overlap,
    )
    chunks = splitter.split_documents(documents)
    logger.info(
        "Split document(s) into %d chunk(s) (chunk_size=%d, chunk_overlap=%d)",
        len(chunks),
        size,
        overlap,
    )
    return chunks
