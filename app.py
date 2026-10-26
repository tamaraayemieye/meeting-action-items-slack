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
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');
:root { color-scheme: light; }
html, body, [data-testid="stApp"], [class*="css"] { font-family: 'DM Sans', sans-serif; }
[data-testid="stApp"] { background: #f6f3ec; color: #24231f; }
header[data-testid="stHeader"] { background: #f6f3ec; }
#MainMenu, footer { visibility: hidden; }
.block-container { max-width: 1120px; padding-top: 2.5rem; padding-bottom: 5rem; }
.brand { color: #27241f; font-size: .86rem; font-weight: 800; letter-spacing: .16em; padding: 0 0 1.15rem; border-bottom: 1px solid #c9c5bb; margin-bottom: 3.1rem; }
.hero-title { font-family: 'Playfair Display', Georgia, serif; font-size: clamp(3rem, 7vw, 6.2rem); font-weight: 600; letter-spacing: -.065em; line-height: 1.03; color: #25231f; margin: 0 0 1.5rem; }
.hero-title span { color: #d05b39; font-style: italic; }
.hero-copy { font-size: 1.08rem; color: #655f57; max-width: 620px; line-height: 1.8; margin-bottom: 2.4rem; }
.stepbar { display: flex; flex-wrap: wrap; gap: 0; border-top: 1px solid #c9c5bb; border-bottom: 1px solid #c9c5bb; padding: 1rem 0; margin-bottom: 3rem; }
.step { padding: .5rem 1.1rem .5rem 0; margin-right: 1.2rem; font-size: .86rem; color: #49443d; }
.step b { color: #c75231; margin-right: .45rem; }
.section-label { font-size: .76rem; letter-spacing: .15em; font-weight: 800; color: #b44b2d; text-transform: uppercase; margin: 1.5rem 0 .7rem; }
.section-title { font-family: 'Playfair Display', Georgia, serif; font-size: clamp(1.8rem,3.4vw,2.7rem); font-weight: 600; letter-spacing: -.04em; color: #28251f; margin: 0 0 .55rem; }
.section-copy { color: #6d665e; margin-bottom: 1.4rem; }
[data-testid="stForm"] { border: 1px solid #d5cfc4; border-radius: 4px; background: #fffdf9; padding: 1.6rem 1.7rem 1.4rem; box-shadow: 7px 8px 0 #e5ded2; }
[data-testid="stTextArea"] textarea { background: #f9f6f0; border: 1px solid #d4cbbd; border-radius: 3px; color: #24231f; font-size: 1rem; line-height: 1.75; padding: 1.1rem; }
[data-testid="stTextArea"] textarea:focus { border-color: #c65335; box-shadow: 0 0 0 1px #c65335; }
[data-testid="stWidgetLabel"] p, [data-testid="stMarkdownContainer"] p { color: #39352f; }
div.stButton > button[kind="primary"], div.stFormSubmitButton > button[kind="primary"] {
    background: #24231f; color: #fffdf7; border: 1px solid #24231f; border-radius: 2px;
    font-weight: 700; padding: .8rem 1.5rem; min-height: 3rem;
}
div.stButton > button[kind="primary"]:hover, div.stFormSubmitButton > button[kind="primary"]:hover { background: #c65335; color: #fff; border-color: #c65335; }
[data-testid="stDataFrame"] { border: 1px solid #d5cfc4; border-radius: 4px; overflow: hidden; }
[data-testid="stCode"] { border: 1px solid #d5cfc4; border-radius: 4px; }
hr { border-color: #d5cfc4; margin: 3rem 0; }
.bottom-note { font-size: .82rem; color: #7a7167; margin-top: 3.5rem; border-top: 1px solid #c9c5bb; padding-top: 1.5rem; }
@media(max-width:650px) { .block-container { padding-top: 1rem; } .brand { margin-bottom: 2rem; } [data-testid="stForm"] { padding: 1rem; } .step { margin-right: .4rem; } }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="brand">ACTIONFLOW <span style="color:#8b8174"> / MEETING INTELLIGENCE</span></div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">Less meeting admin.<br><span>More meaningful work.</span></div>', unsafe_allow_html=True)
st.markdown('<div class="hero-copy">The good ideas deserve follow-through. Turn conversations into clear next steps, thoughtfully reviewed and ready for your team.</div>', unsafe_allow_html=True)
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
    submitted = st.form_submit_button("Extract action items →", type="primary")

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
