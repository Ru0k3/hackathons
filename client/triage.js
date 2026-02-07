/**
 * Autonomous Medical Triage Logic (JavaScript Port)
 * Handles Understand, Analyze, Self-Evaluate, Decision.
 */

class TriageAgent2 {
    constructor() {
        this.config = {
            min_confidence: 50.0,
            max_risk: 70.0,
            completeness_threshold: 60.0
        };
    }

    // --- STEP 1: UNDERSTAND ---
    calculateCompleteness(inputs) {
        const required = ["age", "chief_complaint", "symptoms", "time"];
        let present = 0;
        required.forEach(f => { if (inputs[f]) present++; });

        const vitals = inputs.vitals || {};
        const vitalKeys = ["hr", "rr", "bp_sys", "o2", "temp"];
        let vitalsPresent = 0;
        vitalKeys.forEach(k => { if (vitals[k] > 0) vitalsPresent++; });

        const score = ((present + vitalsPresent) / (required.length + vitalKeys.length)) * 100;
        return Math.min(100, score);
    }

    // --- STEP 2: ANALYZE ---
    analyzeRisk(inputs) {
        const v = inputs.vitals || {};
        let score = 0;
        const context = [];

        // Heart Rate Analysis
        const hr = v.hr || v.heart_rate;
        if (hr) {
            if (hr < 40) {
                score += 40;
                context.push(`Heart Rate is CRITICALLY LOW (${hr} bpm < 40)`);
            } else if (hr > 120) {
                score += 40;
                context.push(`Heart Rate is HIGH (${hr} bpm > 120)`);
            } else if (hr > 100) {
                score += 20;
                context.push(`Heart Rate is Elevated (${hr} bpm)`);
            } else {
                context.push(`Heart Rate is Normal (${hr} bpm)`);
            }
        }

        // O2 Saturation
        const o2 = v.o2 || v.o2_saturation;
        if (o2) {
            if (o2 < 90) {
                score += 50;
                context.push(`O2 Saturation is CRITICALLY LOW (${o2}% < 90%)`);
            } else if (o2 < 94) {
                score += 25;
                context.push(`O2 Saturation is LOW (${o2}%)`);
            } else {
                context.push(`O2 Saturation is Normal (${o2}%)`);
            }
        }

        // Blood Pressure
        const bp = v.bp_sys || v.blood_pressure_systolic;
        if (bp) {
            if (bp > 180) {
                score += 40;
                context.push(`Blood Pressure is CRITICALLY HIGH (${bp} mmHg)`);
            } else if (bp < 90) {
                score += 40;
                context.push(`Blood Pressure is LOW (${bp} mmHg)`);
            } else if (bp > 140) {
                score += 20;
                context.push(`Blood Pressure is Elevated (${bp} mmHg)`);
            } else {
                context.push(`Blood Pressure is Normal (${bp} mmHg)`);
            }
        }

        // Temperature
        const temp = v.temp || v.temperature;
        if (temp) {
            if (temp > 39) {
                score += 30;
                context.push(`Temperature is HIGH (${temp}°C)`);
            } else if (temp > 37.5) {
                score += 15;
                context.push(`Temperature is Elevated (${temp}°C)`);
            } else if (temp < 35) {
                score += 25;
                context.push(`Temperature is LOW (${temp}°C)`);
            } else {
                context.push(`Temperature is Normal (${temp}°C)`);
            }
        }

        // Respiratory Rate
        const rr = v.rr || v.respiratory_rate;
        if (rr) {
            if (rr > 24) {
                score += 25;
                context.push(`Respiratory Rate is HIGH (${rr} breaths/min)`);
            } else if (rr < 12) {
                score += 25;
                context.push(`Respiratory Rate is LOW (${rr} breaths/min)`);
            } else {
                context.push(`Respiratory Rate is Normal (${rr} breaths/min)`);
            }
        }

        // Symptom severity
        const severity = inputs.severity || 0;
        if (severity > 8) {
            score += 30;
            context.push(`Symptom Severity is HIGH (${severity}/10)`);
        } else if (severity > 5) {
            score += 15;
            context.push(`Symptom Severity is Moderate (${severity}/10)`);
        }

        // Symptoms
        const sx = (inputs.chief_complaint || "").toLowerCase();
        if (sx.includes("chest pain") || sx.includes("chest")) { score += 50; context.push("Chest Pain context"); }
        if (sx.includes("breath")) { score += 40; context.push("Respiratory distress context"); }

        return { score: Math.min(100, score), context };
    }

    // --- MAIN DELIBERATION ---
    deliberate(inputs) {
        // 1. Understand
        const completeness = this.calculateCompleteness(inputs);

        // 2. Analyze
        const riskAnalysis = this.analyzeRisk(inputs);
        const riskSeverity = riskAnalysis.score;

        // 3. Self-Evaluate
        // Simple heuristic for demo
        let confidence = completeness;
        if (riskSeverity > 80) confidence -= 10; // High risk makes us cautious

        // 4. Decision Gate
        let decision = "WAIT";
        let summary = "";
        let recommendation = "";

        const narrative = riskAnalysis.context.join(". ");

        if (inputs.manipulation) {
            decision = "REFUSE";
            summary = "Safety Protocol Limit";
            recommendation = "Manipulation detected. Please provide accurate data.";
        } else if (completeness < this.config.completeness_threshold) {
            decision = "ASK_INFO";
            summary = `Insufficient Data (${completeness.toFixed(1)}%)`;
            recommendation = "Please provide more vital signs for an accurate assessment.";
        } else if (riskSeverity > this.config.max_risk) {
            decision = "REFUSE_RISK";
            summary = `High Risk Detected (${riskSeverity}%)`;
            recommendation = "IMMEDIATE ESCALATION. Calling Emergency Services...";
        } else if (confidence < this.config.min_confidence) {
            decision = "REFUSE_CONFIDENCE";
            summary = `Low Confidence (${confidence.toFixed(1)}%)`;
            recommendation = "Uncertain assessment. Please see a doctor.";
        } else {
            decision = "ACT";
            summary = "Stable Assessment";
            recommendation = "Monitor symptoms. " + narrative;
        }

        return {
            decision,
            reason: summary,
            narrative,
            recommendation,
            metrics: { completeness, riskSeverity, confidence },
            riskContext: riskAnalysis.context,
            shouldCallDoctor: riskSeverity > this.config.max_risk // Trigger Action
        };
    }

    // --- AGENTIC ACTIONS ---
    generateCarePlan(inputs) {
        const sx = (inputs.chief_complaint || "").toLowerCase();
        let plan = {
            rx: [],
            care: [],
            dos: ["Rest thoroughly", "Stay hydrated"],
            donts: ["Ignore worsening symptoms", "Self-medicate without advice"]
        };

        if (sx.includes("fever")) {
            plan.rx.push({ name: "Acetaminophen 500mg", dose: "1 tab q6h", warn: "Max 4g/day" });
            plan.care.push("Cool compress to forehead");
            plan.dos.push("Monitor temperature every 4 hours", "Wear loose clothing");
            plan.donts.push("Overdress (traps heat)");
        } else if (sx.includes("pain") || sx.includes("headache")) {
            plan.rx.push({ name: "Ibuprofen 400mg", dose: "1 tab q8h", warn: "Take with food" });
            plan.care.push("Rest in a dark/quiet room");
            plan.dos.push("Use ice/heat pack as needed");
            plan.donts.push("Stare at screens (if headache)", "Do heavy lifting");
        } else if (sx.includes("chest") || sx.includes("breath")) {
            plan.care.push("Sit upright");
            plan.dos.push("Keep airways clear", "Loosen tight clothing");
            plan.donts.push("Lie flat on back", "Exert yourself");
        } else {
            // Generic/Other
            plan.care.push("Monitor symptoms for changes");
            plan.dos.push("Keep a symptom log");
        }

        // Simulating Pharmacy
        plan.delivery = { status: "Preparing", eta: "2 hours" };

        return plan;
    }
}

window.TriageAgent = new TriageAgent2();
