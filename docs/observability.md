# Observability — step-by-step implementation plan

**Reference project:** `d:\D\MY\GEN AI\GEN AI GITHUB REPO\Basic-Rag`  
(especially `hr_assistant/logger.py`, `hr_assistant/tracing.py`, and how each module calls `get_logger`)

**Your app (now):** simple RAG — `retriever → prompt → llm` in `pipeline.ask`  
**Later (after this plan):** agent + tools like Basic-Rag — out of scope here

**Do not skip ahead.** Finish Part 1, verify, then Part 2.

---

## Your locked settings (use these while coding)

| Setting | Value |
| --- | --- |
| Log root folder | `hr_logs` |
| Path layout | `hr_logs/<YYYY-MM-DD>/run_%Y-%m-%d_%H-%M-%S.log` |
| Log level | `DEBUG` |
| `print` | Replace **all** `print(...)` with logger calls |
| Question / answer | Log **full** text |
| Retrieved chunks | Log **full** chunk text |
| Streamlit | **One** log file per process (many Q&As in that file) |
| API keys in logs | **Masked only** (e.g. first/last few chars) |
| Done means | Logging **and** LangSmith |
| `langsmith` package | Add to `requirements.txt` |
| `docs/tune.py` | Do **not** instrument |
| Extra docs | Only this file (no `logger.md` / `LangSmith.md`) |
| Tracing default | On for learning (`LANGSMITH_TRACING=true` in `.env`) |
| Agent / tools | **After** observability — not in this plan |

---

# Part 1 — Local logging

Mirror Basic-Rag’s “Step 0” logger, then wire it into every module.

## Step 1.1 — Create `hr_assistant/logger.py`

Study: `Basic-Rag/hr_assistant/logger.py`

Build the same idea with **your** settings:

1. Import `logging`, `os`, `datetime`.
2. Set root dir to `hr_logs` (not `logs`).
3. Create date folder: `hr_logs/YYYY-MM-DD/` with `os.makedirs(..., exist_ok=True)`.
4. One file per process/run: `run_%Y-%m-%d_%H-%M-%S.log` inside that date folder.
5. `logging.basicConfig(...)`:
   - `level=logging.DEBUG`
   - `format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"` (same as reference)
   - handlers: `FileHandler` (utf-8) + `StreamHandler`
6. Export `get_logger(name) -> logging.getLogger(name)`.

**Stop and check:** from a tiny throwaway test (or temporary call), get a logger, write one `DEBUG`/`INFO` line, confirm the file appears under `hr_logs/<today>/`.

## Step 1.2 — Update `.gitignore`

Study: Basic-Rag ignores `logs/`.

In your project:

1. Add `hr_logs/` (or `hr_logs/*` + keep a `.gitkeep` if you want the empty folder tracked).
2. Decide what to do with the existing `logs/*` rules (keep, remove, or leave — your choice).

## Step 1.3 — Pattern to add in every module

Same as Basic-Rag, at the top of each file you touch:

```python
from hr_assistant.logger import get_logger

logger = get_logger(__name__)
```

Then replace milestones with `logger.debug(...)` / `logger.info(...)` / `logger.warning(...)` as appropriate. Prefer `%s` formatting like the reference (`logger.info("...", value)`), not f-strings inside the log call if you want to match Basic-Rag style.

## Step 1.4 — Wire logging module by module

Do these in order. After each file, you may run a quick smoke test; full review waits until Part 1 is complete.

| Order | File | What to log (adapt names to your code) | Reference |
| --- | --- | --- | --- |
| 1 | `hr_assistant/document_loader.py` | Start load (folder/path); page/doc count when done | Basic-Rag `document_loader.py` |
| 2 | `hr_assistant/splitter.py` | Chunk size/overlap if useful; number of chunks | Basic-Rag `splitter.py` |
| 3 | `hr_assistant/embeddings.py` | Embedding model name when created | Basic-Rag `embeddings.py` |
| 4 | `hr_assistant/vector_store.py` | Exists/load/build; added/skipped/removed counts; retriever `top_k`; **full chunk text** where you retrieve or sync if that is where chunks are visible — otherwise log full chunks in `pipeline.ask` after retrieve | Basic-Rag `vector_store.py` (counts only there; you add full text per your decision) |
| 5 | `hr_assistant/llm.py` | LLM model name (+ temperature) | Basic-Rag `llm.py` |
| 6 | `hr_assistant/pipeline.py` | Build start/ready; reuse vs rebuild store; in `ask`: **full question**, **full retrieved chunks**, **full answer**; remove leftover `print`s | Basic-Rag `pipeline.py` (they log Q + answer; you also log full chunks) |
| 7 | `main.py` | CLI run started / finished | Basic-Rag `main.py` |
| 8 | `app.py` | New question received (process keeps one log file) | Basic-Rag `app.py` |

**Skip for now:** `tools.py`, `agent.py` (Basic-Rag has them; you add those after observability).  
**Skip always for this plan:** `docs/tune.py`.

## Step 1.5 — Helper for masked secrets (optional but matches your rule)

Where you might log that a key exists (e.g. future tracing check), never dump the full key. Example idea: show `abcd...wxyz` only. Put a tiny helper in `logger.py` or `config.py` — your choice.

## Step 1.6 — Part 1 verification

1. Run `python main.py` and/or `streamlit run app.py`.
2. Confirm a new file under `hr_logs/<YYYY-MM-DD>/run_....log`.
3. Confirm console shows the same lines.
4. Ask a policy question; confirm full question, full chunks, and full answer appear in the log.
5. Confirm no full API keys in the log.
6. Confirm no `print(` left in the files you instrumented (search the repo).

**Part 1 review checkpoint:** paste / share the changed files for a whole-part review before Part 2.

---

# Part 2 — LangSmith tracing

Mirror Basic-Rag’s `tracing.py` + config + env pattern.

## Step 2.1 — Create a LangSmith account

You do not have one yet.

1. Sign up at [https://smith.langchain.com](https://smith.langchain.com).
2. Create a project (pick any name; write it into `.env` as `LANGSMITH_PROJECT`).
3. Create an API key (Settings → API Keys).

## Step 2.2 — Add env vars to `.env`

Study: Basic-Rag `.env` / docs `02_langsmith.md`

Add (values from your LangSmith UI):

```env
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=...
```

Never commit `.env`. Optionally add a committed `.env.example` with blank placeholders (Basic-Rag does this).

## Step 2.3 — Read vars in `hr_assistant/config.py`

Study: `Basic-Rag/hr_assistant/config.py` (LANGSMITH_* block)

Add the four variables with `os.getenv`, same names. For learning, default tracing toward on only if you set it in `.env` as above (do not hardcode secrets).

## Step 2.4 — Add `langsmith` to `requirements.txt`

Study: Basic-Rag lists tracing deps explicitly for teaching.

Install after editing requirements.

## Step 2.5 — Create `hr_assistant/tracing.py`

Study: `Basic-Rag/hr_assistant/tracing.py`

1. Import `config` and `get_logger`.
2. Implement `check_langsmith_tracing()`:
   - If tracing is on **and** API key present → `logger.info` that tracing is ENABLED (project name + smith.langchain.com). Mask the key if you mention it at all.
   - Else → log that tracing is OFF.
3. This module does **not** send traces itself. Env vars + LangChain do that after `load_dotenv()`.

## Step 2.6 — Call the check from the pipeline

Study: `Basic-Rag/hr_assistant/pipeline.py` → `build_hr_assistant`

Inside your `build_hr_assistant()`:

1. Keep `config.check_api_keys()`.
2. Call `check_langsmith_tracing()` once at startup (same place as the reference).

No need to wrap every LLM call manually for basic LangSmith.

## Step 2.7 — Part 2 verification

1. Run the app with `LANGSMITH_TRACING=true` and a valid key.
2. Local log should say tracing ENABLED.
3. Ask a real question; open your LangSmith project; confirm a new trace / waterfall (at least the ChatGroq / LLM span; retrieval may appear as part of the chain depending on how LangChain instruments your calls).
4. Set `LANGSMITH_TRACING=false`, rerun: app still works; log says OFF; no new trace.

**Part 2 review checkpoint:** whole-part review of tracing-related changes.

---

# After observability (not this plan)

1. Add agent + tools like Basic-Rag (`tools.py`, `agent.py`, change `pipeline.ask`).
2. Reuse the same `get_logger` pattern in those new files (see Basic-Rag `tools.py` / `agent.py`).
3. Follow the YouTube order next: guardrails / LLM security, then later gateway, evaluations, etc.

---

# Quick file checklist

### Part 1 — create / edit

- [ ] Create `hr_assistant/logger.py`
- [ ] Edit `.gitignore` for `hr_logs`
- [ ] Edit `document_loader.py`, `splitter.py`, `embeddings.py`, `vector_store.py`, `llm.py`, `pipeline.py`, `main.py`, `app.py`
- [ ] Remove all `print` from those files

### Part 2 — create / edit

- [ ] LangSmith account + project + API key
- [ ] `.env` (+ optional `.env.example`)
- [ ] Edit `config.py`
- [ ] Edit `requirements.txt` (`langsmith`)
- [ ] Create `hr_assistant/tracing.py`
- [ ] Edit `pipeline.py` to call `check_langsmith_tracing()`

### Out of scope until later

- [ ] `tools.py` / `agent.py`
- [ ] `docs/tune.py`
- [ ] Guardrails, gateway, evaluations
