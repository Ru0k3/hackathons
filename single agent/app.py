"""
Streamlit App - Multi-Agent Research System
Real-time visualization of agent activities
"""
import streamlit as st
import os
from dotenv import load_dotenv
from researcher_agent import ResearcherAgent
from writer_agent import WriterAgent
# Optional local (non-LLM) agents for offline/testing
try:
    from single_agent.local_researcher import LocalResearcherAgent
    from single_agent.local_writer import LocalWriterAgent
except Exception:
    try:
        from local_researcher import LocalResearcherAgent
        from local_writer import LocalWriterAgent
    except Exception:
        LocalResearcherAgent = None
        LocalWriterAgent = None
import time

# Page configuration
st.set_page_config(
    page_title="Multi-Agent Research System",
    page_icon="🤖",
    layout="wide"
)

# Load environment variables
load_dotenv()

# Initialize session state
if 'research_data' not in st.session_state:
    st.session_state.research_data = None
if 'report' not in st.session_state:
    st.session_state.report = None
if 'activity_log' not in st.session_state:
    st.session_state.activity_log = []

def log_activity(message: str):
    """Add activity to the log with timestamp"""
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.activity_log.append(f"[{timestamp}] {message}")

def main():
    st.title("🤖 Multi-Agent Research System")
    st.markdown("### Real-time Research with Specialized AI Agents")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Keys
            gemini_key = os.getenv("GEMINI_API_KEY", "")
            groq_key = os.getenv("GROQ_API_KEY", "")
            tavily_key = os.getenv("TAVILY_API_KEY", "")

            # Allow using local agents when API keys are missing or when explicitly requested
            env_force_local = os.getenv("USE_LOCAL_AGENTS", "0") == "1"
            use_local_checkbox = st.checkbox("Use local agents (offline/testing)", value=env_force_local)
            use_rag_checkbox = st.checkbox("Enable local RAG retrieval (when using local agents)", value=True)
            use_local = use_local_checkbox or env_force_local or (not gemini_key or not groq_key or not tavily_key)

            if use_local:
                if not (LocalResearcherAgent and LocalWriterAgent):
                    st.error("⚠️ Local agents not available. Ensure local_researcher.py and local_writer.py exist in the single agent folder.")
                else:
                    st.info("Running in local/offline agent mode")
            else:
                st.success("✅ All API keys configured")
            # Antigravity easter-egg
            if st.button("🛸 Antigravity"):
                st.markdown("[xkcd: Antigravity](https://xkcd.com/353/) — enjoy a tiny break!")
        
        st.divider()
        
        st.markdown("""
        ### 🤖 Agent Roles
        
        **Agent A - Researcher** 🔍
        - Uses Gemini AI
        - Searches web via Tavily
        - Analyzes sources
        
        **Agent B - Writer** ✍️
        - Uses Groq AI (Mixtral)
        - Formats research
        - Creates reports
        """)
    
    # Main interface
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📋 Research Topic")
        topic = st.text_input(
            "Enter research topic:",
            placeholder="e.g., Latest developments in quantum computing",
            key="topic_input"
        )
        
        start_research = st.button("🚀 Start Research", type="primary", use_container_width=True)
    
    with col2:
        st.header("📊 System Activity")
        activity_container = st.container(height=150)
        
        with activity_container:
            if st.session_state.activity_log:
                for log in st.session_state.activity_log[-10:]:  # Show last 10 activities
                    st.text(log)
            else:
                st.info("Waiting to start research...")
    
    # Process research
    if start_research and topic:
        if not use_local and (not gemini_key or not groq_key or not tavily_key):
            st.error("Cannot start research without API keys (or enable local agents)!")
            return
        
        # Clear previous results
        st.session_state.research_data = None
        st.session_state.report = None
        st.session_state.activity_log = []
        
            # Create progress containers
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_status(message: str):
            """Update status and log activity"""
            log_activity(message)
            status_text.write(message)
        
            try:
                # Step 1: Research Agent
                progress_bar.progress(10)
                if use_local and LocalResearcherAgent:
                    update_status("🤖 Initializing Local Researcher Agent...")
                    # pass rag flag via examples_dir parameter handled inside local agent (it auto-uses SimpleRAG if available)
                    researcher = LocalResearcherAgent(status_callback=log_activity)
                else:
                    update_status("🤖 Initializing Researcher Agent (Gemini)...")
                    researcher = ResearcherAgent(
                        gemini_api_key=gemini_key,
                        tavily_api_key=tavily_key
                    )
            
            progress_bar.progress(20)
            update_status("🔍 Agent A starting web research...")
            
            research_data = researcher.research(topic, status_callback=log_activity)
            st.session_state.research_data = research_data
            
                progress_bar.progress(60)

                if not research_data.get('success'):
                    st.error("Research failed. Please try again.")
                    return
            
                # Step 2: Writer Agent
                if use_local and LocalWriterAgent:
                    update_status("🤖 Initializing Local Writer Agent...")
                    writer = LocalWriterAgent(status_callback=log_activity)
                else:
                    update_status("🤖 Initializing Writer Agent (Groq)...")
                    writer = WriterAgent(groq_api_key=groq_key)
            
            progress_bar.progress(70)
            update_status("✍️ Agent B creating report...")
            
                report = writer.create_report(research_data, status_callback=log_activity)
            st.session_state.report = report
            
            progress_bar.progress(100)
            update_status("✅ Research and report generation complete!")
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            log_activity(f"❌ Error: {str(e)}")
    
    # Display results
    if st.session_state.research_data and st.session_state.report:
        st.divider()
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["📄 Final Report", "🔬 Research Data", "🔗 Sources"])
        
        with tab1:
            st.markdown(st.session_state.report)
            
            # Download button
            st.download_button(
                label="📥 Download Report",
                data=st.session_state.report,
                file_name=f"research_report_{int(time.time())}.md",
                mime="text/markdown"
            )
        
        with tab2:
            st.subheader("Raw Analysis from Researcher Agent")
            st.markdown(st.session_state.research_data.get('analysis', 'No analysis available'))
        
        with tab3:
            st.subheader("Sources Found")
            sources = st.session_state.research_data.get('sources', [])
            
            for idx, source in enumerate(sources, 1):
                with st.expander(f"Source {idx}: {source.get('title', 'N/A')}"):
                    st.markdown(f"**URL:** {source.get('url', 'N/A')}")
                    st.markdown(f"**Content Preview:**")
                    st.text(source.get('content', 'N/A')[:500] + "...")

if __name__ == "__main__":
    main()