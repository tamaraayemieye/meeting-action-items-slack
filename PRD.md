# Product Requirements Document (PRD)
## Meeting Action Items to Slack
**Version:** 1.0 | **Status:** Baseline

### Product
A lean web app that turns pasted meeting transcripts into human-approved Slack action-item recaps.

### User flow
1. Paste transcript and click **Extract Action Items**.
2. AI returns a structured list of tasks, owners and deadlines.
3. User reviews, edits, adds or deletes entries.
4. User clicks **Post to Slack**.
5. App reports success or a retryable error.

### Inputs
- Required: transcript text.
- Configuration: AI provider credentials and Slack webhook URL stored as secrets, never in the repository.

### Structured output
Each action item contains `task` (string), `owner` (string or "Unassigned"), and `due_date` (explicit deadline text or "Not specified"). Do not infer a calendar date from ambiguous relative language without a known meeting date.

### Functional requirements
- F-01: Multiline transcript input and empty-input validation.
- F-02: AI extraction of only explicitly supported commitments; no hallucinated owners or deadlines.
- F-03: Editable results, with add/remove controls.
- F-04: Human approval gate before any Slack network request.
- F-05: Readable Slack recap with task, owner and deadline.
- F-06: User-friendly status messages for empty results, API errors, invalid configuration and Slack failures.

### Suggested implementation
Python + Streamlit for the UI, an AI model/API for structured extraction, and a Slack Incoming Webhook for posting. Keep the model provider configurable until its endpoint is confirmed.

### Security and constraints
No credentials in source code, screenshots or Git history. Use environment variables or Codespaces secrets; exclude local secret files with `.gitignore`. Treat transcripts as potentially sensitive; test with fictional content.

### Acceptance tests
1. Empty transcript → validation, no API request.
2. Clear transcript → tasks, owners and deadlines extracted accurately.
3. Missing owner/deadline → "Unassigned" / "Not specified".
4. No action items → helpful empty state.
5. Edit/add/delete → final Slack recap reflects reviewed values.
6. No approval → no Slack message.
7. Failed Slack request → visible error, no false success.
8. Successful test post → message visible in designated test channel.

### Build slices
- Slice 0: BRD, PRD, AGENTS.md and project structure.
- Slice 1: Transcript input UI and validation.
- Slice 2: AI extraction with structured output.
- Slice 3: Human review and editing.
- Slice 4: Slack posting after approval.
- Slice 5: End-to-end tests, README and demo.

### Definition of done
A working, demonstrated transcript-to-Slack workflow that passes the acceptance tests and remains within the BRD scope.
