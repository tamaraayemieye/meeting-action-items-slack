# Meeting Action Items to Slack

A lightweight transcript-to-Slack tool, built in documented slices for a vibe-coding assignment.

## Current state: Slice 2
- Paste a transcript and validate input (50,000-character maximum).
- Use a **configured OpenAI-compatible chat-completions API** to extract tasks, owners and explicit deadlines.
- Display a read-only list of extracted action items or an empty-state message.
- Editing and Slack posting are **not implemented yet**.

## Configuration (GitHub Codespaces)
Use **Codespace secrets** (or temporary environment variables), never commit actual keys. Configure:
- `AI_API_KEY`: API key for your AI provider.
- `AI_MODEL`: model identifier supported by your provider.
- `AI_BASE_URL`: optional HTTPS API base URL, defaults to `https://api.openai.com/v1`. The provider must support `POST /chat/completions` with OpenAI-style response JSON.

**Important:** A key beginning with `sk-` does not identify its provider. Do not assume your bootcamp's key works with OpenAI. Confirm the correct provider, model and endpoint before configuring.

## Run in GitHub Codespaces
Pull the latest changes, then:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 0.0.0.0
```

Open the forwarded Streamlit port 8501. Restart Streamlit after changing environment variables.

## Test
```bash
python -m unittest discover -s tests -v
python -m py_compile app.py validation.py extraction.py
```

Unit tests use a mocked API; they require no paid credentials. For a live integration test, configure your provider and use a **fictional** transcript.

## Project documents
- [BRD.md](BRD.md): business requirements and workflow.
- [PRD.md](PRD.md): features and acceptance tests.
- [AGENTS.md](AGENTS.md): coding guardrails.
- [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md): progress and checkpoints.

Do not share keys, real meeting transcripts or webhook URLs in screenshots or Git commits.
