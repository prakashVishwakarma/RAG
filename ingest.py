import hashlib
from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import JinaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

import config


def is_continuation(previous_line, line):
    """Return True if `line` is the rest of a sentence the PDF wrapped onto a new line."""
    if line.startswith("•"):
        return False  # a new bullet point always starts a new line

    if line[0].islower():
        return True  # e.g. "possible." after "...whenever reasonably"

    # A long line that doesn't end a sentence was wrapped by the PDF
    return len(previous_line) >= 60 and not previous_line.endswith((".", ":", "?", "!"))


def clean_text(text):
    text = text.replace("\x7f", "•")

    cleaned_lines = []
    for line in text.splitlines():
        line = line.strip()

        if line == "":
            continue  # skip blank lines

        if len(cleaned_lines) > 0 and is_continuation(cleaned_lines[-1], line):
            cleaned_lines[-1] = cleaned_lines[-1] + " " + line
        else:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def load_documents():
    """Load every PDF in the data folder and clean its text."""
    documents = []
    for pdf_file in Path(config.DATA_DIR).glob("*.pdf"):
        for page in PyPDFLoader(str(pdf_file)).load():
            page.page_content = clean_text(page.page_content)
            documents.append(page)

    # Stop early, otherwise step 6 would delete every stored chunk
    if len(documents) == 0:
        raise SystemExit(f"No PDFs found in '{config.DATA_DIR}'. Nothing to ingest.")

    return documents


def split_documents(documents, chunk_size, chunk_overlap):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_documents(documents)


def main():
    # 1. Load and clean documents
    documents = load_documents()

    # 2. Split documents
    chunks = split_documents(documents, config.CHUNK_SIZE, config.CHUNK_OVERLAP)

    # 3. Give each chunk a stable ID (same content → same ID on every run)
    unique_chunks = {}
    for chunk in chunks:
        key = f"{chunk.metadata['source']}|{chunk.metadata['page']}|{chunk.page_content}"
        chunk_id = hashlib.sha256(key.encode()).hexdigest()
        unique_chunks[chunk_id] = chunk

    # 4. Open the vector store
    embeddings = JinaEmbeddings(model_name=config.EMBEDDING_MODEL)
    vectorstore = Chroma(persist_directory=config.CHROMA_DIR, embedding_function=embeddings)

    # 5. Add only chunks that aren't stored yet

    # 5a. Ask Chroma which of our chunk IDs it already has
    all_ids = list(unique_chunks.keys())
    stored_result = vectorstore.get(ids=all_ids)
    existing_ids = stored_result["ids"]

    # 5b. Keep only the chunks whose ID is not already stored
    new_ids = []
    new_documents = []

    for chunk_id, chunk in unique_chunks.items():
        if chunk_id in existing_ids:
            continue  # already stored, skip it

        new_ids.append(chunk_id)
        new_documents.append(chunk)

    # 5c. Store the new chunks (if there are any)
    if len(new_documents) > 0:
        vectorstore.add_documents(documents=new_documents, ids=new_ids)

    # 6. Remove chunks from PDFs that were edited or deleted

    # 6a. Get the IDs of every chunk currently stored in Chroma
    everything_stored = vectorstore.get(include=[])
    stored_ids = everything_stored["ids"]

    # 6b. Any stored ID that is not in today's chunks is outdated
    outdated_ids = []

    for stored_id in stored_ids:
        if stored_id not in unique_chunks:
            outdated_ids.append(stored_id)

    # 6c. Delete the outdated chunks (if there are any)
    if len(outdated_ids) > 0:
        vectorstore.delete(ids=outdated_ids)

    print(f"Added {len(new_documents)} new chunks")
    print(f"Skipped {len(existing_ids)} chunks that were already stored")
    print(f"Removed {len(outdated_ids)} outdated chunks")


if __name__ == "__main__":
    main()
