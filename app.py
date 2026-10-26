"""Meeting Action Items to Slack — review, approve, and send."""

import pandas as pd
import streamlit as st

from extraction import ExtractionError, extract_action_items
from slack_delivery import SlackDeliveryError, format_recap, post_to_slack
from validation import MAX_TRANSCRIPT_CHARS, validate_transcript

st.set_page_config(page_title="Meeting Action Items to Slack", page_icon="📝")
st.title("Meeting Action Items to Slack")
st.write("Turn a meeting transcript into a reviewed Slack recap.")
st.caption("Extract → review and edit → approve → post.")

if "items" not in st.session_state:
    st.session_state.items = []
if "extracted_from" not in st.session_state:
    st.session_state.extracted_from = None

with st.form("transcript_form"):
    transcript = st.text_area(
        "Meeting transcript",
        height=260,
        placeholder="Alex: I'll send the proposal by Friday.\nSam: I'll review it on Monday.",
        help=f"Paste up to {MAX_TRANSCRIPT_CHARS:,} characters. Use fictional transcripts for testing.",
    )
    submitted = st.form_submit_button("Extract Action Items", type="primary")

if submitted:
    # A new extraction invalidates all previous approval and review state.
    st.session_state.items = []
    st.session_state.extracted_from = None
    st.session_state.pop("review_editor", None)
    st.session_state.pop("approve_post", None)
    valid, message = validate_transcript(transcript)
    if not valid:
        st.error(message)
    else:
        try:
            with st.spinner("Extracting action items..."):
                st.session_state.items = extract_action_items(transcript)
            st.session_state.extracted_from = transcript
            st.success("Extraction complete. Review every item before posting.")
        except ExtractionError as exc:
            st.error(str(exc))

if st.session_state.extracted_from is not None:
    st.subheader("Review action items")
    if not st.session_state.items:
        st.info("No clear action items found. You can add a task manually below.")
    st.write("Edit cells, add rows or delete incorrect items. Changes are not sent until you approve.")
    edited = st.data_editor(
        pd.DataFrame(st.session_state.items, columns=["task", "owner", "due_date"]),
        key="review_editor",
        num_rows="dynamic",
        hide_index=True,
        use_container_width=True,
        column_config={
            "task": st.column_config.TextColumn("Task", required=True),
            "owner": st.column_config.TextColumn("Owner"),
            "due_date": st.column_config.TextColumn("Deadline"),
        },
    )
    reviewed = []
    for row in edited.to_dict("records"):
        task = str(row.get("task") or "").strip()
        owner = str(row.get("owner") or "").strip()
        due_date = str(row.get("due_date") or "").strip()
        if task:
            reviewed.append({
                "task": task,
                "owner": owner if owner and owner.lower() != "nan" else "Unassigned",
                "due_date": due_date if due_date and due_date.lower() != "nan" else "Not specified",
            })

    st.subheader("Slack recap preview")
    if reviewed:
        st.code(format_recap(reviewed), language=None)
    else:
        st.warning("Add at least one task before posting.")

    approved = st.checkbox(
        "I have reviewed the action items and approve posting this recap to Slack.",
        key="approve_post",
    )
    if st.button("Post approved recap to Slack", disabled=not approved or not reviewed, type="primary"):
        try:
            post_to_slack(reviewed)
            st.success("Recap posted to Slack successfully.")
            st.session_state.approve_post = False
        except SlackDeliveryError as exc:
            st.error(str(exc))
