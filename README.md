# Dynamic NPC Dialogue Generation

Small demo to build persona-aware NPC dialogue with memory + RAG.

Quick start

1. Create a Python 3.10+ virtualenv and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Generation options (free-first)

- Local (recommended free): the demo uses a small local HF transformer (`distilgpt2`) by default. This requires no paid provider and works on CPU. On first run the model will be downloaded.

```bash
python3 test.py
```

- Alternative (remote): if you prefer not to download models locally you can use the Hugging Face Inference API (they offer a free tier) or another remote provider and adapt the generator wrapper accordingly.

If local generation fails, `test.py` prints the assembled prompt for inspection and suggests swapping to another small local model via `LOCAL_GEN_MODEL`.

Files of interest

- `dialogue_engine.py` — main engine: preprocessing, indexing, retrieval, prompt assembly, and generator wrapper.
- `prompts.json` — persona templates and few-shot examples.
- `data.json` — scene/dialogue corpus used for RAG.
- `chroma_db_ff7/` — persistent Chroma DB used for memory/index.

Notes

-- On macOS without a GPU, local HF model loading may be slow or run into OOM. Use a small model like `distilgpt2` or `gpt2` to keep memory usage low, or configure a remote Inference API.
- The demo is conservative by default and will not load heavy models unless explicitly enabled.

Next steps

- Improve few-shot examples in `prompts.json` to better enforce persona.
- Add small unit tests for memory retrieval and prompt assembly.
- Add long-term memory consolidation (summaries) for large histories.
