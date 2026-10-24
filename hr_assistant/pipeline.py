"""Wires all the components together into one ready-to-use assistant.

This is the single entry point that main.py (CLI) and app.py (Streamlit)
both call. Each step is handled by its own small module.
"""

from langchain_core.prompts import ChatPromptTemplate

from hr_assistant import config
from hr_assistant.document_loader import load_documents
from hr_assistant.llm import get_llm
from hr_assistant.splitter import split_into_chunks
from hr_assistant.vector_store import (
    build_vector_store,
    get_retriever,
    load_vector_store,
    vector_store_exists,
)


def build_vector_store_for_document():
    """Load + split + embed the PDFs, syncing Chroma with stable chunk IDs."""
    if vector_store_exists():
        print("Found an existing Chroma database, syncing it with current PDFs...")
        documents = load_documents()
        chunks = split_into_chunks(documents)
        print(f"Loaded PDFs and split them into {len(chunks)} chunks.")
        return build_vector_store(chunks)

    print("No Chroma database found, building one from scratch...")
    documents = load_documents()
    chunks = split_into_chunks(documents)
    print(f"Loaded PDFs and split them into {len(chunks)} chunks.")
    return build_vector_store(chunks)


def build_hr_assistant():
    """Build the full RAG assistant, ready to answer questions."""
    print("Building HR assistant...")
    config.check_api_keys()

    vector_store = build_vector_store_for_document()
    retriever = get_retriever(vector_store)
    llm = get_llm()
    prompt = ChatPromptTemplate.from_template(config.SYSTEM_PROMPT)

    print("HR assistant is ready to take questions")
    return {
        "retriever": retriever,
        "llm": llm,
        "prompt": prompt,
    }


def ask(assistant, question: str) -> str:
    """Ask the assistant a question and return its answer as plain text."""
    docs = assistant["retriever"].invoke(question)
    context = "\n\n".join(doc.page_content for doc in docs)
    messages = assistant["prompt"].invoke({
        "context": context,
        "question": question,
    })
    return assistant["llm"].invoke(messages).content
