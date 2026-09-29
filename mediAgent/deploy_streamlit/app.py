import streamlit as st
import os
import time
import json
from dotenv import load_dotenv
from local_agents.local_researcher import LocalResearcherAgent
from local_agents.local_writer import LocalWriterAgent

load_dotenv()

st.set_page_config(page_title="Medical FullAgent", page_icon="🩺", layout="wide")

if 'activity_log' not in st.session_state:
    st.session_state.activity_log = []

if 'research_data' not in st.session_state:
    st.session_state.research_data = None

if 'report' not in st.session_state:
    st.session_state.report = None


def log_activity(msg: str):
    ts = time.strftime("%H:%M:%S")
    st.session_state.activity_log.append(f"[{ts}] {msg}")


st.title("Medical FullAgent — Local Triage + RAG Research + Report")

with st.sidebar:
    st.header("Configuration")
    use_local = st.checkbox("Use local agents (recommended)", value=True)
    st.markdown("Enable local RAG retrieval using example documents.")
    if st.button("🛸 Antigravity"):
        st.markdown("[xkcd: Antigravity](https://xkcd.com/353/)")

st.markdown("This demo uses local, non-LLM agents so it runs without API keys.")

col1, col2 = st.columns([1, 1])
with col1:
    topic = st.text_input("Enter research topic (or use sample below)")
    start = st.button("Run Full Agent")
    st.markdown("### Samples")
    if st.button("Use sample: high risk"):
        with open(os.path.join("examples", "sample_high_risk.json"), "r", encoding="utf-8") as f:
            sample = json.load(f)
        topic = sample.get('chief_complaint', 'medical')
        st.session_state.research_data = None
        st.session_state.report = None
        st.session_state.activity_log = []
        start = True
    if st.button("Use sample: low risk"):
        with open(os.path.join("examples", "sample_low_risk.json"), "r", encoding="utf-8") as f:
            sample = json.load(f)
        topic = sample.get('chief_complaint', 'medical')
        st.session_state.research_data = None
        st.session_state.report = None
        st.session_state.activity_log = []
        start = True

with col2:
    st.header("Activity")
    if st.session_state.activity_log:
        for l in st.session_state.activity_log[-15:]:
            st.text(l)
    else:
        st.info("No activity yet")

if start and topic:
    st.session_state.research_data = None
    st.session_state.report = None
    st.session_state.activity_log = []

    progress = st.progress(0)
    status = st.empty()

    def update(msg: str):
        log_activity(msg)
        status.text(msg)

    try:
        progress.progress(10)
        update("Initializing researcher...")
        researcher = LocalResearcherAgent(examples_dir=os.path.join(os.getcwd(), "examples"), status_callback=log_activity)
        progress.progress(25)
        update("Searching examples / RAG retrieval...")
        research = researcher.research(topic, status_callback=log_activity)
        st.session_state.research_data = research
        progress.progress(60)
        if not research.get('success'):
            update("Research found no local sources.")
            st.warning("No sources found for the topic in examples/")
        update("Initializing writer...")
        writer = LocalWriterAgent(status_callback=log_activity)
        progress.progress(80)
        update("Generating report...")
        report = writer.create_report(research, triage_result=None, status_callback=log_activity)
        st.session_state.report = report
        progress.progress(100)
        update("Done — report ready")
    except Exception as e:
        st.error(str(e))
        log_activity(f"Error: {e}")

if st.session_state.report:
    st.divider()
    st.header("Report")
    st.markdown(st.session_state.report)
    st.download_button("Download report", data=st.session_state.report, file_name="report.md", mime="text/markdown")
    # Show canonical references separately as clickable links
    with st.expander("References"):
        st.markdown(
            "1. [World Health Organization — Cancer Fact Sheet](https://www.who.int/news-room/fact-sheets/detail/cancer)  \n"
            "2. [National Cancer Institute — What Is Cancer?](https://www.cancer.gov/about-cancer/understanding/what-is-cancer)  \n"
            "3. [Hanahan & Weinberg — Hallmarks of Cancer (PubMed)](https://pubmed.ncbi.nlm.nih.gov/21376230/)"
        )

if st.session_state.research_data:
    st.divider()
    st.header("Research data")
    st.markdown("**Sources**")
    for s in st.session_state.research_data.get('sources', []):
        with st.expander(s.get('title', 'source')):
            st.markdown(f"**URL:** {s.get('url')}")
            st.text(s.get('content', '')[:1000] + "...")

