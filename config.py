import os

from dotenv import load_dotenv

load_dotenv()

# Paths
DATA_DIR = os.getenv("DATA_DIR", "data")
CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_db")

# Models
# Changing EMBEDDING_MODEL requires deleting CHROMA_DIR and re-running ingest.py
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "jina-embeddings-v2-base-en")
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0"))

# Chunking
# Chosen with tune.py; re-run it after changing the PDFs or eval_set.json
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "300"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

# Retrieval
TOP_K = int(os.getenv("TOP_K", "4"))
