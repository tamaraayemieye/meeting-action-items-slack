# Meeting Action Items to Slack

A lightweight transcript-to-Slack tool built in documented slices for a vibe-coding assignment.

## Current state: Slices 3 and 4 implemented; final testing pending
- Paste a transcript (50,000-character maximum).
- Extract tasks, owners and explicit deadlines using a configured AI API.
- Review the extracted results, edit cells, add rows or delete incorrect items.
- Preview the formatted Slack recap.
- Explicitly approve and submit the reviewed recap to Slack.
- See success or error feedback. **No automatic Slack posting.**

## Configuration in GitHub Codespaces
Add **Codespaces secrets** (not source files or chat messages):
- `AI_API_KEY` — API key for the provider.
- `AI_MODEL` — model identifier supported by that provider.
- `AI_BASE_URL` — optional OpenAI-compatible HTTPS base URL (defaults to `https://api.openai.com/v1`). Provider must support `POST /chat/completions`.
- `SLACK_WEBHOOK_URL` — Slack Incoming Webhook URL for a **test channel** (must be a Slack webhook host).

An `sk-` key prefix does **not** identify the provider. Cline's key is not automatically available to the Streamlit application. Never commit or screenshot secrets.

## Run in Codespaces
```bash
git pull origin main
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 0.0.0.0
```
Open forwarded port 8501. Restart the Streamlit process after adding or changing secrets.

## Final testing (deferred at user's request)
```bash
python -m unittest discover -s tests -v
python -m py_compile app.py validation.py extraction.py slack_delivery.py
```

Then use a **fictional transcript** and verify extraction, edits, add/remove, approval gate, correct Slack delivery, missing credentials and API errors. Confirm the Slack message appears in the designated test channel before retrying failed requests to avoid duplicates.

## Documents
- [BRD.md](BRD.md): business problem, scope and workflow.
- [PRD.md](PRD.md): requirements and acceptance criteria.
- [AGENTS.md](AGENTS.md): coding guardrails.
- [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md): checkpoint history and test status.

**Do not send real meeting transcripts to an unapproved third-party AI provider.**
