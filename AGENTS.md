# Agent Instructions — Meeting Action Items to Slack

## Mission
Implement the MVP described in BRD.md and PRD.md. Treat those documents as the source of truth. Do not expand scope without explicit approval.

## Working style
- Work **one slice at a time**. Explain the plan and acceptance checks before editing.
- Prefer small, readable changes with minimal dependencies.
- After each slice, run relevant tests and record what passed, failed or remains untested.
- Create a descriptive Git commit only after a slice has been reviewed and tested.
- Do not claim tests passed without actually running them.
- Ask before changing the stack or introducing new services.

## Technology
Prefer Python + Streamlit, a configurable AI model provider, and Slack Incoming Webhooks. Keep credentials in environment variables or Codespaces secrets.

## Guardrails
- Never commit API keys, webhook URLs or real meeting transcripts.
- Never post to Slack without a direct user approval action.
- Do not fabricate owners, deadlines or action items.
- Do not add Google Drive monitoring, HR directories, email routing, login systems or dashboards.
- Use fictional transcripts for testing.

## Slice checklist
1. State slice goal and files to change.
2. Implement only the approved slice.
3. Run its acceptance tests.
4. Record results in DEVELOPMENT_LOG.md.
5. Commit a working checkpoint.
6. Propose the next slice; wait for approval.

## Review
Compare implementation against BRD.md and PRD.md after each slice. Report any deviations and unresolved risks clearly.
