# Meeting Action Items to Slack

A lightweight meeting transcript-to-Slack project, built incrementally for a vibe-coding assignment.

## Current state: Slice 1
A Streamlit page accepts pasted meeting transcripts and validates empty/whitespace input and a 50,000-character limit. The **Extract Action Items** button currently validates only; it does **not** call AI or Slack. Those features are reserved for later slices.

## Run in GitHub Codespaces

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 0.0.0.0
```

Open the forwarded Streamlit port (typically 8501) from the Codespaces **Ports** tab.

## Test

```bash
python -m unittest discover -s tests -v
```

## Project documents
- [BRD.md](BRD.md): business objectives and workflow.
- [PRD.md](PRD.md): product requirements and acceptance criteria.
- [AGENTS.md](AGENTS.md): instructions for coding agents.
- [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md): slice history, test results and known limitations.

Use only fictional transcripts for development. Never commit API keys or Slack webhooks.
