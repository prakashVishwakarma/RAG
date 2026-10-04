# GEN AI Projects From Scratch

Absolutely. For your first RAG project, I recommend **not building a chatbot UI, agents, multi-tenancy, LangGraph, or a complex database**. The goal should be to understand every stage of the RAG pipeline end-to-end.

# Beginner RAG Project: Company Policy Assistant

### Project idea

Build a small **Company Policy Q&A Assistant**.

You provide 2–4 PDF/text documents such as:

- Leave Policy
- Work From Home Policy
- Employee Benefits Policy
- Travel Policy

A user asks:

> "How many casual leaves can an employee take?"
> 

The system retrieves the relevant document chunks and asks an LLM to answer **using those chunks**.

This is small, realistic, and demonstrates the core RAG architecture.

---

# 1. What you are actually building

The complete pipeline is:

```
                 OFFLINE / INDEXING

 PDF / TXT Documents
         │
         ▼
    Document Loader
         │
         ▼
      Chunking
         │
         ▼
     Embeddings
         │
         ▼
   Vector Database
         │
         │
         │
         ▼
                 ONLINE / QUERYING

      User Question
            │
            ▼
        Embedding
            │
            ▼
       Similarity Search
            │
            ▼
    Relevant Document Chunks
            │
            ▼
         Prompt
     ┌──────────────┐
     │ Context      │
     │ Question     │
     │ Instructions │
     └──────────────┘
            │
            ▼
           LLM
            │
            ▼
         Answer
```

The important concept is that **the LLM does not need to memorize your company documents**.

Instead:

```
Question
   ↓
Retrieve relevant information
   ↓
Give information to LLM
   ↓
Generate answer
```

That's the essence of RAG.

---

# 2. Recommended tech stack

For your **first project**, keep the stack deliberately small.

| Component | Recommendation | Purpose |
| --- | --- | --- |
| Language | Python 3.11/3.12 | Application |
| Framework | LangChain | RAG orchestration |
| LLM | OpenAI GPT model | Answer generation |
| Embeddings | OpenAI embeddings | Convert text → vectors |
| Vector DB | Chroma | Store/search vectors locally |
| Documents | PDF/TXT | Knowledge source |
| Environment | `venv` or `uv` | Python environment |

### LangChain vs external components

This distinction is important.

| Component | Type |
| --- | --- |
| LangChain | GenAI framework/orchestration |
| Document loader | LangChain |
| Text splitter | LangChain |
| Embedding interface | LangChain |
| Vector store interface | LangChain |
| OpenAI model | External service |
| OpenAI embedding model | External service |
| Chroma database | External vector database |

LangChain essentially connects these components together.

---

# 3. Keep the first version extremely simple

Don't start with:

```
LangGraph
Agents
Multi-agent
Reranking
Hybrid search
Redis
PostgreSQL
Elasticsearch
Docker
Kubernetes
React
Authentication
Streaming
```

Your first version should only have:

```
PDF
 ↓
Loader
 ↓
Splitter
 ↓
Embedding
 ↓
Chroma
 ↓
Retriever
 ↓
Prompt
 ↓
LLM
 ↓
Answer
```

Once this works, you can add complexity.

---

# 4. Project structure

Use this:

```
basic-rag/
│
├── data/
│   ├── leave_policy.pdf
│   ├── wfh_policy.pdf
│   └── travel_policy.pdf
│
├── chroma_db/
│
├── .env
├── .gitignore
├── requirements.txt
│
├── ingest.py
├── rag.py
└── app.py
```

You can initially even reduce it to:

```
basic-rag/
│
├── data/
├── ingest.py
├── rag.py
├── .env
└── requirements.txt
```

---

# 5. Step 1 — Create the project

### Windows

```bash
mkdir basic-rag
cd basic-rag

python -m venv .venv
.venv\Scripts\activate
```

Install the required packages:

```bash
pip install -U langchain langchain-openai langchain-chroma langchain-community pypdf python-dotenv
```

You can save them:

```bash
pip freeze > requirements.txt
```

---

# 6. Step 2 — Configure the API key

Create:

```
.env
```

Add:

```
OPENAI_API_KEY=your_api_key_here
```

Never commit `.env` to Git.

Add this to `.gitignore`:

```
.env
.venv/
chroma_db/
__pycache__/
```

---

# 7. Step 3 — Prepare your documents

Create:

```
data/
```

Put a few small documents inside.

For example:

```
data/
├── leave_policy.pdf
├── wfh_policy.pdf
└── travel_policy.pdf
```

Don't start with 100 PDFs.

**2–4 small documents are enough.**

---

# 8. Step 4 — Load the documents

Create:

```
ingest.py
```

Minimal version:

```python
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader

documents = []

data_dir = Path("data")

for pdf_file in data_dir.glob("*.pdf"):
    loader = PyPDFLoader(str(pdf_file))
    documents.extend(loader.load())

print(f"Loaded {len(documents)} pages")

for doc in documents[:2]:
    print(doc.page_content[:500])
```

Run:

```bash
python ingest.py
```

You should see text extracted from your PDFs.

---

# 9. Understand the loader

The important part is:

```python
loader = PyPDFLoader(str(pdf_file))
```

Then:

```python
loader.load()
```

returns LangChain `Document` objects.

Conceptually:

```
PDF
 │
 ▼
PyPDFLoader
 │
 ▼
Document objects
```

A document roughly contains:

```python
Document(
    page_content="Leave policy says...",
    metadata={
        "source": "leave_policy.pdf",
        "page": 2
    }
)
```

That metadata becomes useful later for citations/source references.

---

# 10. Step 5 — Chunk the documents

You generally don't send an entire 20-page document to the LLM.

Instead:

```
Document
   ↓
Large text
   ↓
Small chunks
```

Use `RecursiveCharacterTextSplitter`.

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = splitter.split_documents(documents)

print(f"Number of chunks: {len(chunks)}")
```

You may need to install:

```bash
pip install -U langchain-text-splitters
```

---

# 11. What are chunk size and overlap?

Suppose the original document contains:

```
Employee can take 12 casual leaves per year...
```

You don't want arbitrary tiny pieces.

For example:

```
chunk 1
----------------
Employee can take
12 casual leaves...
----------------

chunk 2
----------------
Employees must apply
for leave...
----------------
```

### `chunk_size`

Controls approximately how much text goes into each chunk.

### `chunk_overlap`

Repeats some text between adjacent chunks.

For your first project:

```python
chunk_size = 1000
chunk_overlap = 200
```

is a reasonable starting point.

Don't obsess over the "perfect" values yet.

---

# 12. Step 6 — Create embeddings

Now we convert:

```
Text
 ↓
Embedding model
 ↓
Vector
```

For example:

```
"How many casual leaves?"

        ↓

[0.012, -0.283, 0.731, ...]
```

Create:

```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)
```

The embedding model is **not the same thing as the LLM**.

This distinction is extremely important.

### Embedding model

Used for:

```
semantic search
```

### LLM

Used for:

```
answer generation
```

---

# 13. Step 7 — Store vectors in Chroma

Now:

```
Chunks
 ↓
Embeddings
 ↓
Chroma
```

Example:

```python
from langchain_chroma import Chroma

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"
)
```

This creates a local Chroma database.

You now have:

```
data/
     PDFs

       ↓

chunks

       ↓

embeddings

       ↓

chroma_db/
```

---

# 14. Your first complete ingestion script

At this point, combine everything.

### `ingest.py`

```python
import os
from pathlib import Path

from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

# 1. Load documents
documents = []

for pdf_file in Path("data").glob("*.pdf"):
    loader = PyPDFLoader(str(pdf_file))
    documents.extend(loader.load())

print(f"Loaded {len(documents)} pages")

# 2. Split documents
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = splitter.split_documents(documents)

print(f"Created {len(chunks)} chunks")

# 3. Create embeddings
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

# 4. Store in Chroma
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

print("Documents stored in Chroma")
```

Run:

```bash
python ingest.py
```

If successful:

```
Loaded 15 pages
Created 42 chunks
Documents stored in Chroma
```

You have completed the **indexing phase**.

---

# 15. Step 8 — Create the retriever

Now we enter the second half of RAG.

Load your Chroma database:

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)
```

Create a retriever:

```python
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 4}
)
```

`k=4` means:

> Return the four most relevant chunks.
> 

---

# 16. Step 9 — Test retrieval before involving the LLM

This is one of the most important learning steps.

Don't immediately build the complete chain.

Test:

```python
question = "How many casual leaves can an employee take?"

docs = retriever.invoke(question)

for doc in docs:
    print("=" * 80)
    print(doc.page_content)
    print(doc.metadata)
```

You should see relevant chunks.

For example:

```
================================================

Employees are entitled to 12 casual leaves
during each calendar year...
```

This proves:

```
Question
   ↓
Embedding
   ↓
Vector search
   ↓
Relevant chunks
```

is working.

---

# 17. Step 10 — Create the prompt

Now we give the retrieved context to the LLM.

Example:

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template("""
You are a company policy assistant.

Answer the question using only the provided context.

If the answer is not present in the context,
say: "I don't know based on the provided documents."

Context:
{context}

Question:
{question}

Answer:
""")
```

This is called **grounding**.

You're telling the LLM:

> Don't invent the answer. Use the retrieved information.
> 

---

# 18. Step 11 — Connect the LLM

Use:

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="YOUR_CURRENT_SUPPORTED_MODEL",
    temperature=0
)
```

The exact model name should be selected based on the models available to your OpenAI account/API at the time you build the project.

For a RAG experiment:

```
temperature = 0
```

is a reasonable choice because you generally want consistent, factual answers rather than creative ones.

---

# 19. Step 12 — Build the RAG chain

For learning purposes, I recommend first writing the chain explicitly rather than hiding everything behind a high-level helper.

```python
def ask_question(question):
    docs = retriever.invoke(question)

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    messages = prompt.invoke({
        "context": context,
        "question": question
    })

    response = llm.invoke(messages)

    return response.content
```

Then:

```python
answer = ask_question(
    "How many casual leaves can an employee take?"
)

print(answer)
```

---

# 20. Complete `rag.py`

Your beginner version can therefore be:

```python
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# -----------------------------
# 1. Embedding model
# -----------------------------

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

# -----------------------------
# 2. Load vector database
# -----------------------------

vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)

# -----------------------------
# 3. Create retriever
# -----------------------------

retriever = vectorstore.as_retriever(
    search_kwargs={"k": 4}
)

# -----------------------------
# 4. Prompt
# -----------------------------

prompt = ChatPromptTemplate.from_template("""
You are a company policy assistant.

Answer the question using only the provided context.

If the answer is not present in the context,
say: "I don't know based on the provided documents."

Context:
{context}

Question:
{question}

Answer:
""")

# -----------------------------
# 5. LLM
# -----------------------------

llm = ChatOpenAI(
    model="YOUR_CURRENT_SUPPORTED_MODEL",
    temperature=0
)

# -----------------------------
# 6. RAG function
# -----------------------------

def ask_question(question):

    # Retrieve relevant chunks
    docs = retriever.invoke(question)

    # Combine retrieved text
    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    # Create prompt
    messages = prompt.invoke({
        "context": context,
        "question": question
    })

    # Generate answer
    response = llm.invoke(messages)

    return response.content

# -----------------------------
# 7. Interactive loop
# -----------------------------

while True:

    question = input("\nQuestion: ")

    if question.lower() in ["exit", "quit"]:
        break

    answer = ask_question(question)

    print("\nAnswer:")
    print(answer)
```

Run:

```bash
python rag.py
```

Now you have a basic RAG system.

---

# 21. What happens when you ask a question?

Suppose you ask:

> "Can I work from home on Friday?"
> 

Internally:

```
User Question
     │
     ▼
"Can I work from home on Friday?"
     │
     ▼
Embedding Model
     │
     ▼
Question Vector
     │
     ▼
Chroma Similarity Search
     │
     ▼
Top 4 relevant chunks
     │
     ▼
Prompt Template
     │
     ├── Context
     └── Question
     │
     ▼
LLM
     │
     ▼
Answer
```

That's the **complete RAG pipeline**.

---

# 22. Your 1–2 day implementation plan

## Day 1 — Understand the pipeline

### Stage 1 — Setup

**30–45 minutes**

Learn:

```
Python environment
API key
packages
project structure
```

---

### Stage 2 — Document loading

**30–45 minutes**

Build:

```
PDF
 ↓
PyPDFLoader
 ↓
Documents
```

Verify the extracted text.

---

### Stage 3 — Chunking

**30–45 minutes**

Build:

```
Documents
 ↓
RecursiveCharacterTextSplitter
 ↓
Chunks
```

Print:

```python
len(documents)
len(chunks)
```

and inspect several chunks.

---

### Stage 4 — Embeddings

**30 minutes**

Understand:

```
Text
 ↓
Embedding model
 ↓
Vector
```

Don't just copy the code. Understand what an embedding represents.

---

### Stage 5 — Chroma

**30–45 minutes**

Build:

```
Chunks
 ↓
Embeddings
 ↓
Chroma
```

Verify that the database is created.

---

# Day 2 — Retrieval + Generation

### Stage 6 — Retrieval

**30–45 minutes**

Test:

```python
retriever.invoke(question)
```

Print the retrieved chunks.

This is critical.

---

### Stage 7 — Prompt

**30 minutes**

Learn:

```
Context
+
Question
+
Instructions
```

---

### Stage 8 — LLM

**20–30 minutes**

Connect:

```
Prompt → LLM
```

---

### Stage 9 — Complete RAG

**30–60 minutes**

Connect:

```
Retriever
     ↓
Context
     ↓
Prompt
     ↓
LLM
     ↓
Answer
```

---

### Stage 10 — Testing

**30–60 minutes**

Ask 10 questions and inspect:

```
Was the correct chunk retrieved?
Was the answer correct?
Did the LLM hallucinate?
```

---

# 23. Dataset

Don't download a huge dataset.

Create 3 small policies.

For example:

### `leave_policy.pdf`

Include information such as:

```
Employees receive:

Casual Leave: 12 days/year
Sick Leave: 10 days/year
Earned Leave: 18 days/year

Leave applications should normally be submitted
at least 2 working days in advance.

Unused casual leave cannot be carried forward.
```

### `wfh_policy.pdf`

```
Employees can work from home up to 2 days per week.

WFH requests must be approved by the reporting manager.

Employees working remotely must remain available
during normal working hours.
```

### `travel_policy.pdf`

```
Domestic travel requires manager approval.

Hotel reimbursement is limited to ₹3,000 per night.

Flight tickets should normally be booked in economy class.
```

This tiny dataset is actually **better for learning** than a huge dataset because you can predict what the correct answer should be.

---

# 24. Testing questions

Use questions covering different situations.

| # | Question | What you're testing |
| --- | --- | --- |
| 1 | How many casual leaves are available? | Basic retrieval |
| 2 | How many sick leaves are available? | Retrieval |
| 3 | Can unused casual leave be carried forward? | Specific fact |
| 4 | How many days can I work from home? | Cross-document retrieval |
| 5 | Who approves WFH requests? | Metadata/content retrieval |
| 6 | What is the hotel reimbursement limit? | Numeric retrieval |
| 7 | What class should domestic flights be booked in? | Policy retrieval |
| 8 | What is the maternity leave policy? | **Out-of-context question** |
| 9 | Can I work remotely from another country? | Hallucination test |
| 10 | What is the WFH policy? | General retrieval |

Questions 8 and 9 are particularly important.

Your system should respond something like:

> "I don't know based on the provided documents."
> 

rather than inventing an answer.

---

# 25. How to know whether RAG is actually working

Don't judge RAG only by:

> "The chatbot gave me an answer."
> 

Instead, inspect **three things**.

### 1. Retrieval

Did you retrieve the correct chunk?

```
Question
   ↓
Retriever
   ↓
Correct chunk? ✓
```

### 2. Context

Was the correct information passed to the LLM?

```
Retrieved chunks
       ↓
     Prompt
       ↓
    Correct context? ✓
```

### 3. Generation

Did the LLM answer based on that context?

```
Context
   ↓
 LLM
   ↓
Correct answer? ✓
```

This gives you a much better debugging model:

```
RAG failure

     ┌─────────────────┐
     │ Retrieval issue │
     └─────────────────┘
              OR
     ┌─────────────────┐
     │ Prompt issue    │
     └─────────────────┘
              OR
     ┌─────────────────┐
     │ Generation issue│
     └─────────────────┘
```

---

# 26. Common beginner mistakes

## Mistake 1 — Chunk size is too large

Example:

```
10,000-token chunk
```

You may retrieve a huge amount of irrelevant information.

Start around:

```
500–1,000 characters/tokens depending on your splitter/model
```

and experiment.

---

## Mistake 2 — Chunk size is too small

For example:

```
"Employees receive"

"12 days"

"per year"
```

Now the meaning is fragmented.

Retrieval becomes less useful.

---

## Mistake 3 — No overlap

Suppose a sentence crosses the chunk boundary:

```
Chunk 1:
Employees can take...

Chunk 2:
...12 casual leaves per year.
```

Overlap helps preserve context.

---

# 27. Mistake 4 — Assuming embeddings are the LLM

This is one of the most important concepts.

### Embedding model

```
Text → Vector
```

Purpose:

```
Search
```

### LLM

```
Prompt → Answer
```

Purpose:

```
Generation
```

They perform completely different jobs.

---

# 28. Mistake 5 — Not testing retrieval separately

Bad development approach:

```
Build everything
      ↓
Answer is wrong
      ↓
"I don't know what's wrong."
```

Better:

```
Test loader
      ↓
Test chunks
      ↓
Test embeddings
      ↓
Test retrieval
      ↓
Test prompt
      ↓
Test LLM
```

This is much easier to debug.

---

# 29. Mistake 6 — Trusting the LLM

An LLM can produce:

```
Correct-looking answer
```

even when:

```
The document doesn't contain the answer.
```

That's hallucination.

Your prompt should explicitly say:

```
Answer only from the provided context.

If the answer is not present,
say you don't know.
```

But remember: **prompt instructions alone do not guarantee zero hallucination**.

Production systems need additional controls and evaluation.

---

# 30. Mistake 7 — Putting everything into one giant file

For learning, a small `ingest.py` + `rag.py` is fine.

But eventually separate:

```
loaders/
splitters/
embeddings/
vectorstore/
retrieval/
prompts/
generation/
evaluation/
api/
```

Don't do that yet.

First understand the pipeline.

---

# 31. What LangChain is actually doing

This is the mental model I recommend you memorize.

### LangChain is the orchestration layer.

```
                    LangChain
                        │
        ┌───────────────┼────────────────┐
        │               │                │
        ▼               ▼                ▼
   Documents        Retrieval          LLM
        │               │                │
        ▼               ▼                ▼
    PyPDF          Chroma DB        OpenAI API
```

LangChain provides standardized interfaces that allow you to connect these components.

---

# 32. The most important RAG concepts to learn

After completing this project, you should be able to explain:

### Level 1 — Foundation

```
Document
Document Loader
Chunk
Chunking
Embedding
Vector
Vector Database
Similarity Search
Retriever
Prompt
LLM
Context
RAG
```

### Level 2 — Retrieval

Then learn:

```
Similarity Search
Top-K
Metadata Filtering
MMR
Hybrid Search
Keyword Search
Semantic Search
```

### Level 3 — Better retrieval

Then:

```
Query Rewriting
Multi-Query Retrieval
Parent Document Retrieval
Contextual Compression
Reranking
```

---

# 33. Then move to production RAG

Your progression should look like this:

```
                    YOUR RAG ROADMAP

Level 1
Basic RAG
│
├── Load
├── Split
├── Embed
├── Store
├── Retrieve
├── Prompt
└── Generate
        │
        ▼
Level 2
Advanced Retrieval
│
├── Metadata filtering
├── MMR
├── Hybrid search
├── Query rewriting
├── Multi-query
└── Reranking
        │
        ▼
Level 3
Production RAG
│
├── PostgreSQL/pgvector
├── Authentication
├── APIs
├── Document processing
├── Async ingestion
├── Caching
├── Observability
└── Evaluation
        │
        ▼
Level 4
Advanced RAG
│
├── Agentic RAG
├── Graph RAG
├── Multi-modal RAG
├── SQL RAG
├── Multi-document RAG
└── Hybrid RAG
```

---

# 34. After basic RAG, build these projects

I would progress through projects rather than jumping directly into advanced theory.

| Stage | Project | Main concept |
| --- | --- | --- |
| 1 | Company Policy Assistant | Basic RAG |
| 2 | PDF Research Assistant | Multi-document RAG |
| 3 | HR Knowledge Assistant | Metadata filtering |
| 4 | Legal Document Q&A | Better chunking |
| 5 | Customer Support RAG | Production-style retrieval |
| 6 | SQL + RAG Assistant | Text-to-SQL + RAG |
| 7 | RAG with citations | Source attribution |
| 8 | Hybrid Search Assistant | BM25 + vector search |
| 9 | RAG with reranking | Retrieval quality |
| 10 | Enterprise Knowledge Assistant | Production architecture |

---

# 35. The one diagram you should understand before moving on

If you understand this diagram, you've understood the basic RAG architecture:

```
                 INDEXING TIME
                 ─────────────

        PDF / Documents
               │
               ▼
       ┌─────────────────┐
       │ Document Loader │
       └────────┬────────┘
                │
                ▼
       ┌─────────────────┐
       │ Text Splitter   │
       └────────┬────────┘
                │
                ▼
             Chunks
                │
                ▼
       ┌─────────────────┐
       │ Embedding Model │
       └────────┬────────┘
                │
                ▼
            Vectors
                │
                ▼
       ┌─────────────────┐
       │   Chroma DB     │
       └─────────────────┘

                 QUERY TIME
                 ──────────

          User Question
                │
                ▼
       ┌─────────────────┐
       │ Embedding Model │
       └────────┬────────┘
                │
                ▼
         Query Vector
                │
                ▼
       ┌─────────────────┐
       │    Retriever    │
       └────────┬────────┘
                │
                ▼
       Relevant Chunks
                │
                ▼
       ┌─────────────────┐
       │     Prompt      │
       │ Context+Question│
       └────────┬────────┘
                │
                ▼
       ┌─────────────────┐
       │       LLM       │
       └────────┬────────┘
                │
                ▼
              Answer
```

## The key mental model

Think of the project as **two separate pipelines**:

### Pipeline A — Indexing

```
Documents
→ Load
→ Split
→ Embed
→ Store
```

This happens **before the user asks questions**.

### Pipeline B — Querying

```
Question
→ Retrieve
→ Build Prompt
→ LLM
→ Answer
```

This happens **every time the user asks a question**.

Once you clearly understand those two pipelines, you're ready to move from a toy RAG implementation to **advanced/production RAG** rather than simply memorizing LangChain APIs.