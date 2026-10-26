"""Meeting Action Items to Slack — Slice 2: AI extraction preview."""

import streamlit as st

from extraction import ExtractionError, extract_action_items
from validation import MAX_TRANSCRIPT_CHARS, validate_transcript

st.set_page_config(page_title="Meeting Action Items to Slack", page_icon="📝")
st.title("Meeting Action Items to Slack")
st.write("Paste a meeting transcript to identify tasks, owners and deadlines.")
st.caption("Slice 2: AI extraction preview only. Editing and Slack posting come later.")

with st.form("transcript_form"):
    transcript = st.text_area(
        "Meeting transcript",
        height=260,
        placeholder="Alex: I'll send the proposal by Friday.\nSam: I'll review it on Monday.",
        help=f"Paste up to {MAX_TRANSCRIPT_CHARS:,} characters. Use fictional transcripts for testing.",
    )
    submitted = st.form_submit_button("Extract Action Items", type="primary")

if submitted:
    valid, message = validate_transcript(transcript)
    if not valid:
        st.error(message)
    else:
        try:
            with st.spinner("Extracting action items..."):
                st.session_state["extracted_items"] = extract_action_items(transcript)
            st.success("Extraction complete.")
        except ExtractionError as exc:
            st.session_state.pop("extracted_items", None)
            st.error(str(exc))

if "extracted_items" in st.session_state:
    items = st.session_state["extracted_items"]
    if items:
        st.subheader("Extracted action items")
        st.dataframe(items, hide_index=True, use_container_width=True)
        st.info("Read-only preview. Review and editing will be added in Slice 3. Nothing has been sent to Slack.")
    else:
        st.info("No clear action items were found in this transcript.")
