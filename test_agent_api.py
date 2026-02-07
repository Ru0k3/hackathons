import unittest

try:
    from fastapi.testclient import TestClient
    from agent_api import app
    FASTAPI_AVAILABLE = True
except Exception:
    FASTAPI_AVAILABLE = False


@unittest.skipUnless(FASTAPI_AVAILABLE, "fastapi not available in environment")
class TestAgentAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_evaluate_endpoint_accepts_and_returns(self):
        payload = {"data": {"age": 40, "chief_complaint": "cough", "time_since_onset": "1 day", "consciousness_level": "alert", "vital_signs": {"heart_rate": 80, "respiratory_rate": 18, "blood_pressure_systolic": 120, "blood_pressure_diastolic": 80, "o2_saturation": 97, "temperature": 36.8}}}
        r = self.client.post("/evaluate", json=payload)
        self.assertEqual(r.status_code, 200)
        self.assertIn("decision", r.json())


if __name__ == "__main__":
    unittest.main()
