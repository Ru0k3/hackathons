import unittest
from triage_agent import TriageAgent


class TestTriageAgent(unittest.TestCase):

    def setUp(self):
        self.agent = TriageAgent()

    def test_missing_information_asks_for_more(self):
        inp = {"age": 30, "chief_complaint": "headache"}
        out = self.agent.deliberate(inp)
        self.assertEqual(out.get("decision"), "ASK_FOR_MORE_INFORMATION")

    def test_high_risk_refuses(self):
        inp = {
            "age": 70,
            "chief_complaint": "shortness of breath",
            "time_since_onset": "1 hour",
            "consciousness_level": "alert",
            "vital_signs": {
                "heart_rate": 140,
                "respiratory_rate": 30,
                "blood_pressure_systolic": 85,
                "blood_pressure_diastolic": 50,
                "o2_saturation": 82,
                "temperature": 37.5,
            },
        }
        out = self.agent.deliberate(inp)
        self.assertEqual(out.get("decision"), "REFUSE_AUTONOMOUS_ACTION")

    def test_confident_action_for_complete_low_risk(self):
        inp = {
            "age": 25,
            "chief_complaint": "sprained ankle",
            "time_since_onset": "2 hours",
            "consciousness_level": "alert",
            "vital_signs": {
                "heart_rate": 78,
                "respiratory_rate": 16,
                "blood_pressure_systolic": 118,
                "blood_pressure_diastolic": 76,
                "o2_saturation": 98,
                "temperature": 36.7,
            },
        }
        out = self.agent.deliberate(inp)
        self.assertEqual(out.get("decision"), "ACT_CONFIDENTLY")


if __name__ == "__main__":
    unittest.main()

