import time
import random
import requests

API_BASE = "http://localhost:4000/api"

class ClinicalActionHandler:
    """
    Simulates external agentic actions: Doctor Dispatch, RX Generation, Pharmacy Delivery.
    Hybrid mode: Tries Local Node API, falls back to internal simulation if offline.
    """

    def __init__(self):
        self.doctor_registry = [
            {"name": "Dr. Sarah Smith", "specialty": "Emergency Medicine", "status": "Available"},
            {"name": "Dr. James Chen", "specialty": "Internal Medicine", "status": "On Call"},
        ]

    def call_doctor(self, patient_context):
        """
        Simulates an API call to dispatch/contact a doctor.
        """
        yield f"📡 Initiating priority protocol..."
        time.sleep(0.5)
        
        # 1. Query Provider Network
        provider_name = "On-Call Provider"
        try:
            yield f"🔄 Querying Provider Network (Local API)..."
            resp = requests.get(f"{API_BASE}/doctors", params={"specialty": "emergency", "location": "37.773,-122.413"}, timeout=2)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("results"):
                    doc = data["results"][0]
                    if "profile" in doc:
                         p = doc["profile"]
                         provider_name = f"{p.get('first_name')} {p.get('last_name')} ({p.get('title')})"
                    else:
                         provider_name = "Available Specialist"
                    yield f"✅ Network Response: Found provider {provider_name}"
            else:
                yield f"⚠️ API Network unstable. Switching to backup."
        except Exception:
             yield f"⚠️ API Connection Failed (Node server offline?). Switching to internal registry."

        # Fallback
        if provider_name == "On-Call Provider":
             doc = random.choice(self.doctor_registry)
             provider_name = f"{doc['name']} ({doc['specialty']})"

        time.sleep(1.0)
        yield f"📞 Dialing Secure Line: {provider_name}..."
        time.sleep(1.2)
        yield f"✅ CONNECTED. Data packet transferred."
        
        return {
            "action": "call_doctor",
            "status": "success",
            "provider": provider_name,
            "timestamp": time.strftime("%H:%M:%S")
        }

    def generate_care_plan(self, complaint, symptoms):
        """
        Generates a Prescription and Care Plan.
        """
        plan = {
            "prescriptions": [],
            "home_care": [],
            "sources": ["NHS Guidelines", "Mayo Clinic", "openFDA"],
            "pharmacy_order": None,
            "medications": [] # Keep for backwards compatibility if needed
        }
        
        complaint_lower = complaint.lower()
        drug_name = None
        drug_dose = "500mg"
        drug_sig = "Take as needed"
        
        # Clinical Logic for "Prescription"
        if "fever" in complaint_lower:
            drug_name = "acetaminophen"
            drug_dose = "500mg"
            drug_sig = "Take 1 tablet every 4-6 hours for fever > 38.5C"
            plan["home_care"].append("Apply tepid (lukewarm) compresses to forehead")
            plan["home_care"].append("Increase fluid intake (Water, Electrolytes)")
        elif "pain" in complaint_lower or "headache" in complaint_lower:
             drug_name = "ibuprofen"
             drug_dose = "400mg"
             drug_sig = "Take 1 tablet with food every 6-8 hours for pain"
             plan["home_care"].append("Rest in a dark, quiet room")
        elif "infection" in complaint_lower or "redness" in complaint_lower:
             drug_name = "amoxicillin" # Antibiotic simulation
             drug_dose = "500mg"
             drug_sig = "Take 1 capsule every 8 hours for 7 days. Finish full course."
        
        # 2. Fetch Real Drug Info from API or Fallback
        if drug_name:
            warning_text = "Check for allergies before use."
            ingredient = drug_name.title()
            
            try:
                # Try API
                resp = requests.get(f"{API_BASE}/drugs", params={"name": drug_name}, timeout=2)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("active_ingredient"): ingredient = data["active_ingredient"].title()
                    if data.get("warnings"): warning_text = data["warnings"][:150] + "..."
                    if data.get("dosage"): drug_sig = data["dosage"][:100] + "..."
            except:
                pass # Use defaults
            
            # Construct Prescription Object
            rx = {
                "drug": f"{ingredient} {drug_dose}",
                "sig": drug_sig,
                "warning": warning_text,
                "source": "openFDA / Local DB"
            }
            plan["prescriptions"].append(rx)
            plan["medications"].append(f"{rx['drug']} - {rx['sig']}") # Backwards compat
            
            # 3. Create Pharmacy Order
            plan["pharmacy_order"] = {
                "status": "Ready for Delivery",
                "item": rx["drug"],
                "estimated_delivery": "Within 2 hours"
            }

        if not plan["prescriptions"]:
            plan["prescriptions"].append({"drug": "No Medication Indicated", "sig": "Monitor Symptoms", "warning": "None"})
            
        if not plan["home_care"]:
             plan["home_care"].append("Rest and monitor symptoms.")

        return plan
