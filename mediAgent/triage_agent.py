"""
Multi-Agent Autonomous Medical Triage System using LangChain
Refactored from single agent to multiple specialized agents.
"""
from typing import Dict, Any, List
from dataclasses import dataclass
import math


# ============== AGENT 1: Data Analysis Agent ==============
class DataAnalysisAgent:
    """Validates inputs and calculates data completeness (Step 1: Understand)"""
    
    REQUIRED_FIELDS = ["age", "chief_complaint", "symptoms", "time_since_onset"]
    VITAL_KEYS = ["heart_rate", "respiratory_rate", "blood_pressure_systolic", 
                  "blood_pressure_diastolic", "o2_saturation", "temperature"]
    
    def analyze(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run data completeness and validation analysis"""
        # Check required fields
        required_present = sum(1 for f in self.REQUIRED_FIELDS if inputs.get(f))
        
        # Check vitals
        vitals = inputs.get("vital_signs", {})
        vitals_present = sum(1 for k in self.VITAL_KEYS if vitals.get(k))
        
        # Calculate completeness
        total_fields = len(self.REQUIRED_FIELDS) + len(self.VITAL_KEYS)
        completeness = ((required_present + vitals_present) / total_fields) * 100
        
        # Vital reliability
        reliability = "High" if vitals_present >= 4 else ("Medium" if vitals_present >= 2 else "Low")
        
        # Check contradictions (simple heuristic)
        contradictions = self._check_contradictions(inputs)
        
        return {
            "Data completeness": f"{completeness:.1f}%",
            "Vital reliability": reliability,
            "Contradictions": "Yes" if contradictions else "No",
            "completeness_score": completeness,
            "vitals_count": vitals_present
        }
    
    def _check_contradictions(self, inputs: Dict[str, Any]) -> bool:
        """Simple contradiction check"""
        vitals = inputs.get("vital_signs", {})
        hr = vitals.get("heart_rate", 0)
        o2 = vitals.get("o2_saturation", 100)
        
        # Example: Very low O2 but normal HR is suspicious
        if o2 < 85 and 60 <= hr <= 100:
            return True
        return False


# ============== AGENT 2: Risk Assessment Agent ==============
class RiskAssessmentAgent:
    """Analyzes vitals and symptoms for risk factors (Step 2: Analyze)"""
    
    VITAL_RANGES = {
        "heart_rate": {"low": 50, "high": 100, "critical_low": 40, "critical_high": 120},
        "o2_saturation": {"low": 94, "critical_low": 90},
        "blood_pressure_systolic": {"low": 90, "high": 140, "critical_high": 180},
        "temperature": {"low": 36.0, "high": 37.5, "critical_high": 39.0}
    }
    
    def assess(self, inputs: Dict[str, Any], data_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk based on vitals and symptoms"""
        vitals = inputs.get("vital_signs", {})
        severity_score = 0
        risk_context = []
        
        # Analyze each vital
        for vital, ranges in self.VITAL_RANGES.items():
            value = vitals.get(vital)
            if not value:
                continue
                
            if vital == "heart_rate":
                if value < ranges["critical_low"]:
                    severity_score += 40
                    risk_context.append(f"Heart Rate is CRITICALLY LOW ({value} bpm < 40)")
                elif value > ranges["critical_high"]:
                    severity_score += 40
                    risk_context.append(f"Heart Rate is HIGH ({value} bpm > 120)")
                elif value > ranges["high"]:
                    severity_score += 20
                    risk_context.append(f"Heart Rate is Elevated ({value} bpm)")
                else:
                    risk_context.append(f"Heart Rate is Normal ({value} bpm)")
                    
            elif vital == "o2_saturation":
                if value < ranges["critical_low"]:
                    severity_score += 50
                    risk_context.append(f"O2 Saturation is CRITICALLY LOW ({value}% < 90%)")
                elif value < ranges["low"]:
                    severity_score += 25
                    risk_context.append(f"O2 Saturation is LOW ({value}%)")
                else:
                    risk_context.append(f"O2 Saturation is Normal ({value}%)")
                    
            elif vital == "blood_pressure_systolic":
                if value > ranges["critical_high"]:
                    severity_score += 40
                    risk_context.append(f"Blood Pressure is CRITICALLY HIGH ({value} mmHg)")
                elif value < ranges["low"]:
                    severity_score += 40
                    risk_context.append(f"Blood Pressure is LOW ({value} mmHg)")
                else:
                    risk_context.append(f"Blood Pressure is Normal ({value} mmHg)")
                    
            elif vital == "temperature":
                if value > ranges["critical_high"]:
                    severity_score += 30
                    risk_context.append(f"Temperature is HIGH ({value}°C)")
                elif value > ranges["high"]:
                    severity_score += 15
                    risk_context.append(f"Temperature is Elevated ({value}°C)")
                else:
                    risk_context.append(f"Temperature is Normal ({value}°C)")
        
        # Symptom severity contribution
        symptom_severity = inputs.get("symptom_severity", 0)
        if symptom_severity > 80:
            severity_score += 30
            risk_context.append(f"Symptom Severity is HIGH ({symptom_severity}/100)")
        elif symptom_severity > 50:
            severity_score += 15
        
        # Cap at 100
        severity_score = min(100, severity_score)
        
        return {
            "Risk of not acting": "High" if severity_score > 60 else ("Medium" if severity_score > 30 else "Low"),
            "Risk of acting unnecessarily": "Low" if severity_score > 60 else "Medium",
            "Clinical Context": risk_context,
            "risk_score": severity_score
        }


# ============== AGENT 3: Confidence Evaluation Agent ==============
class ConfidenceAgent:
    """Evaluates confidence based on data quality (Step 3: Self-Evaluate)"""
    
    def evaluate(self, data_analysis: Dict[str, Any], risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate confidence score"""
        completeness = data_analysis["completeness_score"]
        vitals_count = data_analysis["vitals_count"]
        risk_score = risk_assessment["risk_score"]
        
        # Base confidence = completeness
        confidence = completeness
        
        # Penalize if high risk but low vitals
        if risk_score > 70 and vitals_count < 3:
            confidence -= 20
        
        # Penalize contradictions
        if data_analysis["Contradictions"] == "Yes":
            confidence -= 15
        
        # Boost if vitals are comprehensive
        if vitals_count >= 5:
            confidence += 10
        
        confidence = max(0, min(100, confidence))
        
        return {
            "Confidence": f"{confidence:.1f}%",
            "Data quality": "High" if confidence > 70 else ("Medium" if confidence > 50 else "Low"),
            "confidence_score": confidence
        }


# ============== AGENT 4: Decision Gate Agent ==============
class DecisionGateAgent:
    """Makes final decision using strict rubric (Step 4: Decision Gate)"""
    
    @dataclass
    class Config:
        min_confidence_threshold: float = 50.0
        high_confidence_threshold: float = 80.0
        max_risk_threshold: float = 70.0
        completeness_threshold: float = 60.0
    
    def __init__(self):
        self.config = self.Config()
    
    def decide(self, inputs: Dict[str, Any], data_analysis: Dict[str, Any], 
               risk_assessment: Dict[str, Any], confidence_eval: Dict[str, Any]) -> Dict[str, Any]:
        """Make final triage decision"""
        
        completeness = data_analysis["completeness_score"]
        risk_score = risk_assessment["risk_score"]
        confidence_score = confidence_eval["confidence_score"]
        risk_context = risk_assessment["Clinical Context"]
        
        # Check for manipulation
        if inputs.get("user_note") and any(x in inputs["user_note"].lower() for x in ["ignore", "override"]):
            return {
                "decision": "REFUSE_AUTONOMOUS_ACTION",
                "reason": "Safety Protocol: Manipulation Detected",
                "recommendation": "Please provide accurate patient data without override requests."
            }
        
        # Decision Logic
        if completeness < self.config.completeness_threshold:
            return {
                "decision": "ASK_FOR_MORE_INFORMATION",
                "reason": f"Insufficient Data ({completeness:.1f}%)",
                "recommendation": "Please provide more vital signs and symptom details for accurate assessment."
            }
        
        if risk_score > self.config.max_risk_threshold:
            narrative = ". ".join([ctx for ctx in risk_context if "HIGH" in ctx or "CRITICAL" in ctx])
            return {
                "decision": "REFUSE_AUTONOMOUS_ACTION",
                "reason": f"High Risk Detected. {narrative}",
                "recommendation": "IMMEDIATE MEDICAL ATTENTION REQUIRED. Do not delay care."
            }
        
        if confidence_score < self.config.min_confidence_threshold:
            return {
                "decision": "REFUSE_AUTONOMOUS_ACTION",
                "reason": f"Low Confidence ({confidence_score:.1f}%)",
                "recommendation": "Uncertain assessment due to data quality. Please consult a healthcare provider."
            }
        
        # Safe to act
        if confidence_score > self.config.high_confidence_threshold and risk_score < 40:
            narrative = ". ".join([ctx for ctx in risk_context if "Normal" in ctx])
            return {
                "decision": "ACT_CONFIDENTLY",
                "reason": f"Stable Assessment. {narrative}",
                "recommendation": "Monitor symptoms. Rest and hydration recommended."
            }
        else:
            narrative = ". ".join(risk_context[:3])  # First 3 contexts
            return {
                "decision": "ACT_WITH_WARNING",
                "reason": f"Moderate Concern. {narrative}",
                "recommendation": "Monitor closely. Seek medical care if symptoms worsen."
            }


# ============== ORCHESTRATOR: Multi-Agent Coordinator ==============
class MultiAgentTriageOrchestrator:
    """Coordinates all specialized agents to execute the 4-step triage process"""
    
    def __init__(self):
        self.data_agent = DataAnalysisAgent()
        self.risk_agent = RiskAssessmentAgent()
        self.confidence_agent = ConfidenceAgent()
        self.decision_agent = DecisionGateAgent()
    
    def deliberate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute multi-agent deliberation process"""
        
        logs = []
        
        # Step 1: Data Analysis
        logs.append("🔍 Agent 1 (Data Analysis): Validating inputs...")
        data_result = self.data_agent.analyze(inputs)
        
        # Step 2: Risk Assessment
        logs.append("🧠 Agent 2 (Risk Assessment): Analyzing vitals...")
        risk_result = self.risk_agent.assess(inputs, data_result)
        
        # Step 3: Confidence Evaluation
        logs.append("⚖️ Agent 3 (Confidence): Evaluating certainty...")
        confidence_result = self.confidence_agent.evaluate(data_result, risk_result)
        
        # Step 4: Decision Gate
        logs.append("🚪 Agent 4 (Decision Gate): Making final decision...")
        decision_result = self.decision_agent.decide(inputs, data_result, risk_result, confidence_result)
        
        # Compile final output
        return {
            "decision": decision_result["decision"],
            "reason": decision_result["reason"],
            "recommendation": decision_result["recommendation"],
            "metrics": {
                "completeness": data_result["completeness_score"],
                "risk_severity": risk_result["risk_score"],
                "confidence": confidence_result["confidence_score"]
            },
            "phase_logs": {
                "understand": data_result,
                "analyze": risk_result,
                "self_evaluation": confidence_result,
                "decision": decision_result
            },
            "logs_text": "\n".join(logs)
        }


# Backward compatibility alias
class TriageAgent(MultiAgentTriageOrchestrator):
    """Alias for backward compatibility with existing code"""
    pass
