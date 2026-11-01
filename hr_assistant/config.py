"""All settings for the app live here, in one place."""

import os

from dotenv import load_dotenv

load_dotenv()

# Paths
DATA_DIR = os.getenv("DATA_DIR", "data")
CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_db")

# TRACING
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "false")
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT")

# Models
# Changing EMBEDDING_MODEL requires deleting CHROMA_DIR and rebuilding the store
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "jina-embeddings-v2-base-en")
LLM_MODEL_NAME = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0"))

# Chunking (chosen with docs/tune.py against docs/eval_set.json)
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "300"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

# Retrieval
TOP_K_RESULTS = int(os.getenv("TOP_K", "4"))

SYSTEM_PROMPT = """
You are a company policy assistant.

Answer the question using only the provided context.

If the answer is not present in the context,
say: "I don't know based on the provided documents."

Context:
{context}

Question:
{question}

Answer:
"""


def check_api_keys():
    """Stop early if required API keys are missing."""
    missing = []
    if not os.getenv("JINA_API_KEY"):
        missing.append("JINA_API_KEY")
    if not os.getenv("GROQ_API_KEY"):
        missing.append("GROQ_API_KEY")
    if missing:
        raise SystemExit(
            "Missing API key(s): "
            + ", ".join(missing)
            + ". Add them to your .env file."
        )
