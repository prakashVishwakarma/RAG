# Company Policy RAG Assistant

A beginner RAG (Retrieval-Augmented Generation) project that answers questions about company policy PDFs.

- **Embeddings:** Jina (`jina-embeddings-v2-base-en`)
- **Vector database:** Chroma (stored locally in `chroma_db/`)
- **LLM:** Groq (`openai/gpt-oss-20b`)
- **Framework:** LangChain
- **UI:** Streamlit

## How it works

```
PDFs → split into chunks → Jina embeddings → Chroma     (hr_assistant/pipeline)

Question → find similar chunks in Chroma → Groq LLM → Answer
```

## Project structure

```
data/                 Policy PDFs (the knowledge source)
chroma_db/            Vector database (created on first run)
hr_assistant/         Package modules (load, split, embed, store, LLM, pipeline)
docs/                 Notes, eval set, and tuning script
assets/               Images / diagrams (optional)
logs/                 Run logs (future)
NOTES/                Personal notes (optional)
app.py                Streamlit chat UI
main.py               Terminal CLI demo
requirements.txt      Python dependencies
```

## Setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your API keys:

   ```
   JINA_API_KEY=your_jina_api_key_here
   GROQ_API_KEY=your_groq_api_key_here
   ```

   Get free keys from [jina.ai](https://jina.ai/) and [console.groq.com/keys](https://console.groq.com/keys).

4. (Optional) Override settings in `.env`:

   ```
   LLM_MODEL=openai/gpt-oss-120b
   EMBEDDING_MODEL=jina-embeddings-v2-base-en
   CHUNK_SIZE=300
   CHUNK_OVERLAP=100
   TOP_K=4
   DATA_DIR=data
   CHROMA_DIR=./chroma_db
   ```

## Usage

1. Put your PDF files in `data/`.
2. Start the Streamlit chat app:

   ```bash
   streamlit run app.py
   ```

   On first run the app builds/syncs `chroma_db/` from the PDFs automatically.

3. Or run the terminal demo:

   ```bash
   python main.py
   ```

4. (Optional) Tune retrieval settings:

   ```bash
   python docs/tune.py
   ```

## Notes

- If you change the embedding model, delete `chroma_db/` and run the app again.
- Editing or deleting a PDF is handled on the next run (outdated chunks are removed; new ones are added).
