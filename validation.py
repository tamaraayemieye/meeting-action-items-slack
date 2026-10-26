"""Pure input-validation helpers for transcript intake."""

MAX_TRANSCRIPT_CHARS = 50_000


def validate_transcript(value: str) -> tuple[bool, str]:
    """Return (valid, message) for pasted meeting transcript text."""
    if not isinstance(value, str) or not value.strip():
        return False, "Paste a meeting transcript before continuing."
    if len(value) > MAX_TRANSCRIPT_CHARS:
        return False, f"Transcript is too long (maximum {MAX_TRANSCRIPT_CHARS:,} characters)."
    return True, "Transcript accepted."
