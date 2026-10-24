"""Step 2: split documents into overlapping chunks."""

from langchain_text_splitters import RecursiveCharacterTextSplitter

from hr_assistant import config


def split_into_chunks(documents, chunk_size=None, chunk_overlap=None):
    """Split documents into chunks for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size if chunk_size is not None else config.CHUNK_SIZE,
        chunk_overlap=chunk_overlap if chunk_overlap is not None else config.CHUNK_OVERLAP,
    )
    return splitter.split_documents(documents)
