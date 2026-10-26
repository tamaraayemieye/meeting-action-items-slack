"""Meeting Action Items to Slack — polished Streamlit interface."""

import pandas as pd
import streamlit as st

from extraction import ExtractionError, extract_action_items
from slack_delivery import SlackDeliveryError, format_recap, post_to_slack
from validation import MAX_TRANSCRIPT_CHARS, validate_transcript

st.set_page_config(
    page_title="ActionFlow | Meeting follow-ups",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { color-scheme: dark; }
html, body, [class*="css"], [data-testid="stApp"] { font-family: 'DM Sans', sans-serif; }
[data-testid="stApp"] {
    background: radial-gradient(ellipse at 75% -15%, #172f43 0%, transparent 42%),
                radial-gradient(ellipse at -10% 50%, #132a31 0%, transparent 42%), #0b121b;
    color: #eef4f7;
}
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
.block-container { max-width: 1030px; padding-top: 2.8rem; padding-bottom: 5rem; }
h1,h2,h3 { font-family: 'Manrope', sans-serif; letter-spacing: -.045em; }
.brand { color: #a6f1db; font-size: .82rem; font-weight: 800; letter-spacing: .16em; margin-bottom: 1.2rem; }
.hero-title { font-family: 'Manrope',sans-serif; font-size: clamp(2.2rem,5vw,4rem); font-weight: 800; letter-spacing: -.065em; line-height: 1.14; color: #f3f7fb; margin: 0 0 1rem; }
.hero-title span { color: #86e6c9; }
.hero-copy { font-size: 1.05rem; color: #9eafbd; max-width: 610px; line-height: 1.7; margin-bottom: 2.1rem; }
.stepbar { display: flex; flex-wrap: wrap; gap: .55rem; margin-bottom: 2rem; }
.step { padding: .55rem .85rem; border: 1px solid #2b414b; background: #15232e; border-radius: 999px; font-size: .82rem; color: #c2d2d9; }
.step b { color: #86e6c9; margin-right: .35rem; }
.section-label { font-size: .79rem; letter-spacing: .14em; font-weight: 800; color: #8de8cb; text-transform: uppercase; margin: 1rem 0 .5rem; }
.section-title { font-family: 'Manrope',sans-serif; font-size: 1.65rem; font-weight: 800; letter-spacing: -.045em; margin: 0 0 .5rem; }
.section-copy { color: #a7b8c4; margin-bottom: 1.2rem; }
[data-testid="stForm"] { border: 1px solid #2b414b; border-radius: 20px; background: rgba(21,35,46,.82); padding: 1.45rem 1.55rem 1.25rem; box-shadow: 0 20px 50px #00000022; }
[data-testid="stTextArea"] textarea { background: #0d1923; border: 1px solid #304552; border-radius: 13px; color: #eef4f7; font-size: .98rem; line-height: 1.7; padding: 1rem; }
[data-testid="stTextArea"] textarea:focus { border-color: #81e7c8; box-shadow: 0 0 0 1px #81e7c8; }
[data-testid="stWidgetLabel"] p { color: #e5eff3; font-weight: 700; }
div.stButton > button[kind="primary"], div.stFormSubmitButton > button[kind="primary"] {
    background: #8be7cb; color: #102a2d; border: none; border-radius: 10px;
    font-weight: 800; padding: .75rem 1.3rem; min-height: 2.8rem;
}
div.stButton > button[kind="primary"]:hover, div.stFormSubmitButton > button[kind="primary"]:hover {
    background: #b6f6e3; color: #102a2d;
}
[data-testid="stDataFrame"] { border: 1px solid #2b414b; border-radius: 12px; overflow: hidden; }
[data-testid="stCode"] { border: 1px solid #2b414b; border-radius: 12px; }
hr { border-color: #263d49; margin: 2rem 0; }
.bottom-note { font-size: .82rem; color: #7f98a8; margin-top: 2.5rem; }
@media(max-width:650px) { .block-container { padding-top: 1.5rem; } [data-testid="stForm"] { padding: 1rem; } }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="brand">✦ ACTIONFLOW <span style="color:#64818c"> / MEETING INTELLIGENCE</span></div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">Meetings happen.<br><span>Progress follows.</span></div>', unsafe_allow_html=True)
st.markdown('<div class="hero-copy">Turn messy meeting transcripts into clear, accountable next steps. Review every detail before sharing your recap with Slack.</div>', unsafe_allow_html=True)
st.markdown('<div class="stepbar"><span class="step"><b>01</b> Add transcript</span><span class="step"><b>02</b> Extract tasks</span><span class="step"><b>03</b> Review & edit</span><span class="step"><b>04</b> Send to Slack</span></div>', unsafe_allow_html=True)

if "items" not in st.session_state:
    st.session_state.items = []
if "extracted_from" not in st.session_state:
    st.session_state.extracted_from = None

st.markdown('<div class="section-label">STEP 01 / TRANSCRIPT</div><div class="section-title">Start with your meeting notes</div><div class="section-copy">Paste your transcript below. We’ll identify commitments, owners and deadlines.</div>', unsafe_allow_html=True)
with st.form("transcript_form"):
    transcript = st.text_area(
        "Meeting transcript",
        height=225,
        placeholder="Alex: I'll send the proposal by Friday.\nSam: I'll review it on Monday.",
        help=f"Maximum {MAX_TRANSCRIPT_CHARS:,} characters. Use fictional transcripts while testing.",
    )
    submitted = st.form_submit_button("✦ Extract action items", type="primary")

if submitted:
    st.session_state.items = []
    st.session_state.extracted_from = None
    st.session_state.pop("review_editor", None)
    st.session_state.pop("approve_post", None)
    valid, message = validate_transcript(transcript)
    if not valid:
        st.error(message)
    else:
        try:
            with st.spinner("Finding commitments and owners..."):
                st.session_state.items = extract_action_items(transcript)
            st.session_state.extracted_from = transcript
            st.success("Extraction complete. Review every item before sharing.")
        except ExtractionError as exc:
            st.error(str(exc))

if st.session_state.extracted_from is not None:
    st.divider()
    st.markdown('<div class="section-label">STEP 02 / REVIEW</div><div class="section-title">Make every action count</div><div class="section-copy">Edit, add or remove items before approving the recap.</div>', unsafe_allow_html=True)
    if not st.session_state.items:
        st.info("No clear action items found. You can add a task manually.")

    with st.form("review_and_post"):
        edited = st.data_editor(
            pd.DataFrame(st.session_state.items, columns=["task", "owner", "due_date"]),
            key="review_editor",
            num_rows="dynamic",
            hide_index=True,
            use_container_width=True,
            column_config={
                "task": st.column_config.TextColumn("Action item", required=True),
                "owner": st.column_config.TextColumn("Owner"),
                "due_date": st.column_config.TextColumn("Deadline"),
            },
        )
        st.markdown("**Final approval**")
        approved = st.checkbox(
            "I've reviewed the action items and approve sharing this recap to Slack.",
            key="approve_post",
        )
        send = st.form_submit_button("Send approved recap to Slack →", type="primary")

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

    st.markdown('<div class="section-label">STEP 03 / PREVIEW</div><div class="section-title">Ready for your team</div>', unsafe_allow_html=True)
    if reviewed:
        st.code(format_recap(reviewed), language=None)
    else:
        st.warning("Add at least one task before posting.")

    if send:
        if not approved:
            st.error("Review and approve the recap before posting.")
        elif not reviewed:
            st.error("Add at least one action item before posting.")
        else:
            try:
                post_to_slack(reviewed)
                st.success("Recap posted to Slack successfully.")
            except SlackDeliveryError as exc:
                st.error(str(exc))

st.markdown('<div class="bottom-note">ACTIONFLOW · Human-reviewed meeting follow-ups · Nothing is sent without approval.</div>', unsafe_allow_html=True)
