import argparse
import json
from triage_agent import TriageAgent


def run_demo(input_data: dict):
    agent = TriageAgent()
    out = agent.deliberate(input_data)
    print(json.dumps(out, indent=2))


def sample_input():
    return {
        "age": 45,
        "chief_complaint": "abdominal pain",
        "time_since_onset": "6 hours",
        "consciousness_level": "alert",
        "vital_signs": {
            "heart_rate": 88,
            "respiratory_rate": None,
            "blood_pressure_systolic": 120,
            "blood_pressure_diastolic": 78,
            "temperature": 37.0,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Triage agent demo CLI")
    parser.add_argument("--input-json", help="Path to JSON file with input data")
    parser.add_argument("--sample", action="store_true", help="Run with built-in sample input")
    args = parser.parse_args()

    if args.sample:
        data = sample_input()
    elif args.input_json:
        with open(args.input_json, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        parser.error("Specify --sample or --input-json <file>")

    run_demo(data)


if __name__ == "__main__":
    main()
