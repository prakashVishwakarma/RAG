# Company Policy RAG Assistant

A beginner RAG (Retrieval-Augmented Generation) project that answers questions about company policy PDFs.

- **Embeddings:** Jina (`jina-embeddings-v2-base-en`)
- **Vector database:** Chroma (stored locally in `chroma_db/`)
- **LLM:** Groq (`openai/gpt-oss-20b`)
- **Framework:** LangChain

## How it works

```
PDFs → split into chunks → Jina embeddings → Chroma     (ingest.py)

Question → find similar chunks in Chroma → Groq LLM → Answer     (rag.py)
```

## Project structure

```
data/          Policy PDFs (the knowledge source)
chroma_db/     Vector database (created by ingest.py)
config.py      All settings (models, chunk size, paths, top-k)
eval_set.json  Test questions with the text their answers come from
tune.py        Finds the best chunk_size, chunk_overlap and k using eval_set.json
ingest.py      Loads, splits, embeds and stores the PDFs
rag.py         Retrieves relevant chunks and generates an answer
app.py         Interactive question-answer loop in the terminal
```

## Setup

1. Install [uv](https://docs.astral.sh/uv/).
2. Install dependencies:

   ```bash
   uv sync
   ```

3. Create a `.env` file with your API keys:

   ```
   JINA_API_KEY=your_jina_api_key_here
   GROQ_API_KEY=your_groq_api_key_here
   ```

   Get free keys from [jina.ai](https://jina.ai/) and [console.groq.com/keys](https://console.groq.com/keys).

4. (Optional) Override any setting from `config.py` by adding it to `.env`:

   ```
   LLM_MODEL=openai/gpt-oss-120b
   EMBEDDING_MODEL=jina-embeddings-v2-base-en
   CHUNK_SIZE=1000
   CHUNK_OVERLAP=200
   TOP_K=4
   DATA_DIR=data
   CHROMA_DIR=./chroma_db
   ```

## Usage

1. Put your PDF files in `data/`.
2. Build the vector database:

   ```bash
   uv run ingest.py
   ```

   Running it again only adds chunks that aren't stored yet.

3. Ask questions:

   ```bash
   uv run app.py
   ```

   Or run a single test question with `uv run rag.py`.

## Notes

- If you change the embedding model, delete `chroma_db/` and run `ingest.py` again.
- If you edit or delete a PDF, delete `chroma_db/` and run `ingest.py` again (old chunks are not removed automatically).
