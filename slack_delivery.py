"""Slack recap formatting and explicit webhook delivery."""

import json
import os
from urllib import error, request
from urllib.parse import urlsplit


class SlackDeliveryError(Exception):
    """A safe, user-facing Slack posting error."""


def format_recap(items: list[dict[str, str]]) -> str:
    """Build a readable Slack message from reviewed items."""
    if not items:
        raise SlackDeliveryError("There are no action items to post.")
    lines = ["*Meeting action items*"]
    for number, item in enumerate(items, start=1):
        task = str(item.get("task") or "").strip()
        if not task:
            raise SlackDeliveryError("Every action item needs a task description.")
        owner = str(item.get("owner") or "").strip() or "Unassigned"
        due_date = str(item.get("due_date") or "").strip() or "Not specified"
        # Escape Slack formatting characters to avoid unintended mentions/markup.
        def safe(s: str) -> str:
            return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        lines.append(f"{number}. {safe(task)}\n   Owner: {safe(owner)} | Due: {safe(due_date)}")
    return "\n".join(lines)


def post_to_slack(items: list[dict[str, str]]) -> None:
    """Post only when explicitly called by the approved UI button."""
    message = format_recap(items)
    webhook = os.getenv("SLACK_WEBHOOK_URL", "").strip()
    parsed = urlsplit(webhook)
    if parsed.scheme != "https" or parsed.hostname not in ("hooks.slack.com", "hooks.slack-gov.com") or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise SlackDeliveryError("Configure a valid Slack Incoming Webhook URL in Codespaces secrets.")
    payload = json.dumps({"text": message}).encode("utf-8")
    req = request.Request(webhook, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with request.urlopen(req, timeout=20) as response:
            result = response.read().decode("utf-8", errors="replace").strip()
            if response.status != 200 or result != "ok":
                raise SlackDeliveryError("Slack did not confirm delivery. Check the test channel before retrying.")
    except error.HTTPError as exc:
        raise SlackDeliveryError(f"Slack rejected the message (HTTP {exc.code}). Check webhook permissions.") from exc
    except (error.URLError, TimeoutError) as exc:
        raise SlackDeliveryError("Could not reach Slack. Check the connection and test channel before retrying.") from exc
