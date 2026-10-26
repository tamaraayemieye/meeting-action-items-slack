"""Meeting Action Items to Slack — Slice 1: transcript intake only."""

import streamlit as st

from validation import MAX_TRANSCRIPT_CHARS, validate_transcript

st.set_page_config(page_title="Meeting Action Items to Slack", page_icon="📝")
st.title("Meeting Action Items to Slack")
st.write("Paste a meeting transcript to prepare it for action-item extraction.")
st.caption("Slice 1: transcript input and validation only. No AI or Slack connection yet.")

with st.form("transcript_form"):
    transcript = st.text_area(
        "Meeting transcript",
        height=260,
        placeholder="Alex: I'll send the proposal by Friday.\nSam: I'll review it on Monday.",
        help=f"Paste up to {MAX_TRANSCRIPT_CHARS:,} characters. Use fictional transcripts for testing.",
    )
    submitted = st.form_submit_button("Extract Action Items", type="primary")

if submitted:
    is_valid, message = validate_transcript(transcript)
    if is_valid:
        st.success(message)
        st.info("Your transcript is ready. Extraction is intentionally not enabled in this slice.")
    else:
        st.error(message)
