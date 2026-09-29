"""
Flask API Backend for Multi-Agent Triage System
Exposes the LangChain multi-agent system via REST API for React frontend
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from triage_agent import TriageAgent

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

agent = TriageAgent()

@app.route('/api/triage', methods=['POST'])
def triage():
    """Main triage endpoint - accepts patient data and returns decision"""
    try:
        data = request.json
        
        # Convert React format to Python format
        inputs = {
            "age": data.get("age"),
            "chief_complaint": data.get("chief_complaint"),
            "symptoms": [data.get("chief_complaint")],
            "time_since_onset": data.get("duration", "unknown"),
            "symptom_severity": data.get("severity", 50),
            "vital_signs": data.get("vitals", {})
        }
        
        # Run multi-agent deliberation
        result = agent.deliberate(inputs)
        
        # Return formatted response
        return jsonify({
            "decision": result["decision"],
            "reason": result["reason"],
            "recommendation": result["recommendation"],
            "narrative": result["phase_logs"]["analyze"]["Clinical Context"],
            "metrics": result["metrics"],
            "riskContext": result["phase_logs"]["analyze"]["Clinical Context"],
            "shouldCallDoctor": result["metrics"]["risk_severity"] > 70,
            "plan": _generate_care_plan(inputs) if result["decision"] == "ACT_CONFIDENTLY" or result["decision"] == "ACT_WITH_WARNING" else None
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def _generate_care_plan(inputs):
    """Generate care plan (simplified from agent_actions.py)"""
    sx = inputs.get("chief_complaint", "").lower()
    plan = {
        "rx": [],
        "dos": ["Rest thoroughly", "Stay hydrated"],
        "donts": ["Ignore worsening symptoms", "Self-medicate without advice"],
        "delivery": {"status": "Preparing", "eta": "2 hours"}
    }
    
    if "fever" in sx:
        plan["rx"].append({"name": "Acetaminophen 500mg", "dose": "1 tab q6h", "warn": "Max 4g/day"})
        plan["dos"].extend(["Monitor temperature every 4 hours", "Wear loose clothing"])
    elif "pain" in sx or "headache" in sx:
        plan["rx"].append({"name": "Ibuprofen 400mg", "dose": "1 tab q8h", "warn": "Take with food"})
        plan["dos"].append("Use ice/heat pack as needed")
        plan["donts"].append("Stare at screens (if headache)")
    
    return plan

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "Multi-Agent System Active", "agents": 4})

if __name__ == '__main__':
    print("Starting Multi-Agent Triage API Server...")
    print("React UI should connect to: http://localhost:5000/api/triage")
    app.run(debug=False, port=5000, threaded=True)
