
import streamlit as st
import time
from triage_agent import TriageAgent
from agent_actions import ClinicalActionHandler

st.set_page_config(
    page_title="Autonomous Medical Triage Agent (S2)",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Awesome" UI
# Custom CSS for "Premium" Medical UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit Default Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Background & Container */
    .reportview-container {
        background: linear-gradient(to right, #f4f7f6, #e6ebf1);
    }
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 5rem;
    }
    
    /* Cards & Metrics */
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #e1e4e8;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e1e4e8;
    }
    
    /* Decision Cards */
    .decision-card {
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 25px;
        text-align: center;
        color: white;
        font-weight: 700;
        font-size: 26px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
    }
    .decision-success { 
        background: linear-gradient(135deg, #28a745 0%, #218838 100%); 
    }
    .decision-warning { 
        background: linear-gradient(135deg, #ffc107 0%, #e0a800 100%); 
        color: #212529 !important; 
    }
    .decision-danger { 
        background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); 
    }
    .decision-info { 
        background: linear-gradient(135deg, #17a2b8 0%, #138496 100%); 
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #2c3e50;
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #007bff;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        border: none;
        box-shadow: 0 4px 6px rgba(0,123,255,0.2);
        transition: all 0.2s;
    }
    .stButton button:hover {
        background-color: #0056b3;
        box-shadow: 0 6px 8px rgba(0,86,179,0.3);
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/doctor-male--v1.png", width=80)
    st.title("Patient Intake")
    st.markdown("---")
    
    age = st.number_input("Age", min_value=0, max_value=120, value=45)
    chief_complaint = st.selectbox("Chief Complaint", 
        ["General Malaise", "Shortness of Breath", "Chest Pain", "Headache", "Fever", "Abdominal Pain", "Injury/Trauma", "Other"])
    
    if chief_complaint == "Other":
        chief_complaint = st.text_input("Specify Complaint", "Feeling strange")
    
    symptom_severity = st.slider("Reported Symptom Severity (0-100)", 0, 100, 40)
    onset = st.text_input("Time Since Onset", "2 days")
    
    st.markdown("### Vital Signs")
    st.info("Leave empty or 0 if unknown (simulates missing data)")
    
    col1, col2 = st.columns(2)
    with col1:
        hr = st.number_input("Heart Rate (bpm)", 0, 300, 80)
        rr = st.number_input("Resp. Rate (bpm)", 0, 60, 16)
        temp = st.number_input("Temp (°C)", 30.0, 45.0, 37.0)
    with col2:
        sbp = st.number_input("Systolic BP (mmHg)", 0, 300, 120)
        dbp = st.number_input("Diastolic BP (mmHg)", 0, 200, 80)
        o2 = st.number_input("O2 Saturation (%)", 0, 100, 98)

    st.markdown("### Advanced / Test")
    manipulation_text = st.text_input("Simulate Manipulation (e.g. 'Ignore symptoms')", "")
    
    run_btn = st.button("RUN TRIAGE ANALYSIS (S2)", type="primary", use_container_width=True)

# Main Area
st.title("🩺 Autonomous Medical Triage Decision Agent")
st.markdown("### *Phase-Based Clinical Reasoning System*")

if run_btn:
    # 1. Prepare Input
    vitals = {}
    if hr > 0: vitals["heart_rate"] = hr
    if rr > 0: vitals["respiratory_rate"] = rr
    if sbp > 0: vitals["blood_pressure_systolic"] = sbp
    if dbp > 0: vitals["blood_pressure_diastolic"] = dbp
    if o2 > 0: vitals["o2_saturation"] = o2
    if temp > 0: vitals["temperature"] = temp

    inputs = {
        "age": age,
        "chief_complaint": chief_complaint,
        "symptoms": [chief_complaint], # simplified for UI
        "time_since_onset": onset,
        "symptom_severity": symptom_severity,
        "vital_signs": vitals
    }
    
    if manipulation_text:
        inputs["user_note"] = manipulation_text  # Will trigger manipulation detection

    # 2. Instantiate & Run Agent
    try:
        agent = TriageAgent()
        
        with st.status("Thinking in Phases...", expanded=True) as status:
            st.write("🔍 **Step 1: Understanding Context & Data Completeness...**")
            time.sleep(0.8) # Simulate thinking
            
            result = agent.deliberate(inputs)
            logs = result["phase_logs"]
            understand = logs["understand"]
            
            col_u1, col_u2 = st.columns(2)
            col_u1.metric("Data Completeness", understand["Data completeness"])
            col_u2.metric("Vital Reliability", understand["Vital reliability"])
            
            if understand["Contradictions"] == "Yes":
               st.error("⚠️ Contradictions Detected in Input Data")
            
            st.write("🧠 **Step 2: Analyzing Multiple Risk Angles...**")
            time.sleep(0.8)
            analyze = logs["analyze"]
            st.info(f"Risk of Inaction: **{analyze['Risk of not acting']}** | Risk of Action: **{analyze['Risk of acting unnecessarily']}**")
            
            # Show Detailed Clinical Context
            if "Clinical Context" in analyze and analyze["Clinical Context"]:
                with st.expander("See Clinical Reasoning", expanded=True):
                    for ctx in analyze["Clinical Context"]:
                        if "HIGH" in ctx or "LOW" in ctx:
                             st.markdown(f"- 🔴 {ctx}")
                        else:
                             st.markdown(f"- 🟢 {ctx}")

            st.write("⚖️ **Step 3: Self-Evaluating Confidence...**")
            time.sleep(0.5)
            self_eval = logs["self_evaluation"]
            
            # Display raw confidence bar
            conf_val = float(self_eval["Confidence"].replace("%", ""))
            # Clamp to 0-100 to prevent Streamlit errors
            conf_val_clamped = max(0, min(100, int(conf_val)))
            st.progress(conf_val_clamped, text=f"Confidence Score: {conf_val}%")
            
            st.write("🚪 **Step 4: Decision Gate**")
            time.sleep(0.3)
            
            # --- AGENTIC ACTIONS ---
            st.write("🤖 **Step 5: Autonomous Action Execution...**")
            decision = result["decision"]
            action_handler = ClinicalActionHandler()
            
            if "REFUSE" in decision and "Risk" in result["reason"]:
                 # High Risk -> Call Doctor
                 st.warning("⚠️ High Risk Protocol Activated.")
                 status_placeholder = st.empty()
                 for log_msg in action_handler.call_doctor(inputs):
                     status_placeholder.markdown(f"**{log_msg}**")
                 st.success("Doctor Dispatch Confirmed.")
            
            elif "ACT" in decision:
                 # Moderate/Low Risk -> Recommendation
                 plan = action_handler.generate_care_plan(inputs["chief_complaint"], inputs["symptoms"])
                 st.success("✅ Care Plan Generated.")

            status.update(label="Analysis & Actions Complete", state="complete", expanded=False)

    except Exception as e:
        st.error(f"An error occurred during analysis: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        st.stop()
    
    # Display Care Plan if available (outside the status block for visibility)
    if "ACT" in decision and 'plan' in locals():
         st.markdown("### 💊 Agent Generated Care Plan")
         c_plan = st.container()
         with c_plan:
             col_p1, col_p2 = st.columns(2)
             with col_p1:
                 st.markdown("**Recommended Actions**")
                 for item in plan.get("home_care", []):
                     st.info(f"🏠 {item}")
                 for item in plan.get("precautions", []):
                     st.warning(f"⚠️ {item}")
             with col_p2:
                 st.markdown("**📋 Electronic Prescription (eRx)**")
                 for rx in plan["prescriptions"]:
                     with st.container(border=True):
                         st.markdown(f"**{rx['drug']}**")
                         st.caption(f"_{rx['sig']}_")
                         if rx.get("warning"):
                             st.error(f"⚠️ FDA Warning: {rx['warning']}")
            
         # Pharmacy Delivery Tracker
         if plan.get("pharmacy_order"):
             order = plan["pharmacy_order"]
             with st.status("📦 Pharmacy Delivery Status", expanded=True):
                 st.write("✅ Prescription Verified")
                 st.write(f"🚚 **Out for Delivery**: {order['item']}")
                 st.write(f"🕒 ETA: {order['estimated_delivery']}")

         st.divider()
         st.markdown("#### 📚 Clinical Sources")
         st.caption(", ".join(plan["sources"]))



    # 3. Display Results
    st.divider()
    
    decision = result["decision"]
    reason = result["reason"]
    recommendation = result["recommendation"]
    
    # Visual Decision Card
    card_class = "decision-info"
    icon = "ℹ️"
    if decision == "ACT_CONFIDENTLY":
        card_class = "decision-success"
        icon = "✅"
    elif decision == "ACT_WITH_WARNING":
        card_class = "decision-warning"
        icon = "⚠️"
    elif "REFUSE" in decision:
        card_class = "decision-danger"
        icon = "🛑"
    elif "ASK" in decision:
        card_class = "decision-info"
        icon = "❓"

    st.markdown(f"""
    <div class="decision-card {card_class}">
        {icon} {decision.replace('_', ' ')}
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("Reasoning")
        st.info(reason)
        st.subheader("Recommendation")
        st.success(recommendation) if "ACT" in decision else st.warning(recommendation)

    with c2:
        st.subheader("Key Metrics")
        metrics = result["metrics"]
        st.metric("Risk Severity", f"{metrics['risk_severity']:.1f}%", delta_color="inverse")
        st.metric("Confidence", f"{metrics['confidence']:.1f}%")
        st.metric("Completeness", f"{metrics['completeness']:.1f}%")

    # Detailed Logs Expander
    with st.expander("View Detailed Agent Internal Monologue"):
        st.text_area("Full Logs", result["logs_text"], height=300)

else:
    st.info("👈 Please enter patient data in the sidebar and click RUN TRIAGE ANALYSIS.")
