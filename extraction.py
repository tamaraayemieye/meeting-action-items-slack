"""AI extraction through a configurable OpenAI-compatible chat-completions API.

No model credentials are stored in this repository. Never log transcript text or API keys.
"""
import json
import os
from urllib import error, request
from urllib.parse import urlsplit

SYSTEM_PROMPT = """Extract only explicit meeting action items from the transcript.
Return ONLY JSON: {"action_items":[{"task":"...","owner":"...","due_date":"..."}]}.
An action item must be a clear commitment or assignment, not a general suggestion.
Use "Unassigned" if the owner is not explicitly identifiable.
Use "Not specified" if a deadline is not explicitly stated.
Preserve relative deadline wording (e.g. "Friday") rather than guessing dates.
Never invent tasks, owners, or deadlines. If none exist return {"action_items":[]}."""


class ExtractionError(Exception):
    """Safe, user-facing extraction error."""


def parse_action_items(raw: str) -> list[dict[str, str]]:
    """Validate the AI response rather than trusting arbitrary model output."""
    try:
        obj = json.loads(raw)
    except (TypeError, ValueError) as exc:
        raise ExtractionError("The AI returned invalid JSON. Please try again.") from exc
    if not isinstance(obj, dict) or not isinstance(obj.get("action_items"), list):
        raise ExtractionError("The AI returned an unexpected format. Please try again.")
    items = obj["action_items"]
    if len(items) > 100:
        raise ExtractionError("The AI returned too many items. Please try a shorter transcript.")
    cleaned = []
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("task"), str) or not item["task"].strip():
            raise ExtractionError("The AI returned an incomplete task. Please try again.")
        owner = item.get("owner")
        deadline = item.get("due_date")
        if owner is not None and not isinstance(owner, str):
            raise ExtractionError("The AI returned an invalid owner.")
        if deadline is not None and not isinstance(deadline, str):
            raise ExtractionError("The AI returned an invalid deadline.")
        cleaned.append({
            "task": item["task"].strip(),
            "owner": owner.strip() if owner and owner.strip() else "Unassigned",
            "due_date": deadline.strip() if deadline and deadline.strip() else "Not specified",
        })
    return cleaned


def extract_action_items(transcript: str) -> list[dict[str, str]]:
    """Send transcript to a user-configured OpenAI-compatible endpoint."""
    key = os.getenv("AI_API_KEY", "").strip()
    model = os.getenv("AI_MODEL", "").strip()
    base = os.getenv("AI_BASE_URL", "https://api.openai.com/v1").strip().rstrip("/")
    parsed = urlsplit(base)
    if not key or not model:
        raise ExtractionError("Configure AI_API_KEY and AI_MODEL in Codespaces secrets before extraction.")
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ExtractionError("AI_BASE_URL must be a valid HTTPS API base URL.")
    url = base + "/chat/completions"
    payload = {
        "model": model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": transcript},
        ],
    }
    req = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=40) as response:
            data = json.load(response)
        content = data["choices"][0]["message"]["content"]
        return parse_action_items(content)
    except error.HTTPError as exc:
        if exc.code in (401, 403):
            raise ExtractionError("AI authentication failed. Check your provider and API key.") from exc
        if exc.code == 429:
            raise ExtractionError("AI request limit reached. Please retry later.") from exc
        raise ExtractionError(f"AI request failed (HTTP {exc.code}).") from exc
    except (error.URLError, TimeoutError) as exc:
        raise ExtractionError("Could not reach the AI provider. Check the endpoint or try again.") from exc
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise ExtractionError("The AI provider returned an unexpected response.") from exc
