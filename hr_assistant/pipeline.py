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
from hr_assistant.tracing import check_langsmith_tracing
from hr_assistant.logger import get_logger

logger = get_logger(__name__)


def build_vector_store_for_document():
    """Load + split + embed the PDFs, syncing Chroma with stable chunk IDs."""
    if vector_store_exists():
        logger.info("Found an existing Chroma database, syncing it with current PDFs...")
        documents = load_documents()
        chunks = split_into_chunks(documents)
        logger.info("Loaded PDFs and split them into %d chunks.", len(chunks))
        return build_vector_store(chunks)

    logger.info("No Chroma database found, building one from scratch...")
    documents = load_documents()
    chunks = split_into_chunks(documents)
    logger.info("Loaded PDFs and split them into %d chunks.", len(chunks))
    return build_vector_store(chunks)


def build_hr_assistant():
    """Build the full RAG assistant, ready to answer questions."""
    logger.info("Building HR assistant...")
    config.check_api_keys()
    check_langsmith_tracing()

    vector_store = build_vector_store_for_document()
    retriever = get_retriever(vector_store)
    llm = get_llm()
    prompt = ChatPromptTemplate.from_template(config.SYSTEM_PROMPT)

    logger.info("HR assistant is ready to take questions")
    return {
        "retriever": retriever,
        "llm": llm,
        "prompt": prompt,
    }


def ask(assistant, question: str) -> str:
    """Ask the assistant a question and return its answer as plain text."""
    logger.info("User question: %s", question)
    docs = assistant["retriever"].invoke(question)
    logger.info("Retrieved %d chunk(s)", len(docs))
    for i, doc in enumerate(docs, start=1):
        logger.debug(
            "Retrieved chunk %d (source=%s, page=%s): %s",
            i,
            doc.metadata.get("source"),
            doc.metadata.get("page"),
            doc.page_content,
        )
    context = "\n\n".join(doc.page_content for doc in docs)
    messages = assistant["prompt"].invoke({
        "context": context,
        "question": question,
    })
    answer = assistant["llm"].invoke(messages).content
    logger.info("Final answer: %s", answer)
    return answer
