# Medical FullAgent — Local, Privacy-preserving Triage + Research + Report

This package provides a self-contained `FullAgent` that runs a medical triage
deliberation pipeline together with local research (RAG over example files)
and report generation — without requiring external LLMs.

Included components
- `triage_agent.py` — medical triage deliberation agent (decision logic only).
- `full_agent.py` — `FullAgent` orchestrator (runs triage, optional research, writer).
- `single agent/local_researcher.py` — simple local researcher using example JSONs.
- `single agent/rag_retriever.py` — small TF-based retriever for RAG.
- `single agent/local_writer.py` — simple report generator.
- `single agent/app.py` — Streamlit UI (supports local agents and antigravity easter-egg).

Quick start — run the full agent demo

From the project root:

```powershell
python -m zipapp -o medical_agent.pyz -m "full_agent:demo" .
python medical_agent.pyz
```

Or run directly:

```powershell
python full_agent.py
```

Using the Streamlit frontend (interactive)

```powershell
cd "single agent"
streamlit run app.py
```

Notes
- The local RAG retriever searches `examples/` JSON files. Provide relevant example files to improve retrieval.
- For a production deployment with external LLMs, plug in `ResearcherAgent` and `WriterAgent` backends and set API keys in `.env`.

If you want, I can:
- Add unit tests for `FullAgent` and local components.
- Export a single executable or Dockerfile for deployment.
