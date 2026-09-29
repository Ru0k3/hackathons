"""
FullAgent: orchestrates triage, research, and report writing.
Uses `TriageAgent` for medical triage and local researcher/writer fallbacks
when LLM-based agents are not available.
"""
from typing import Dict, Any, Optional, Callable
from triage_agent import TriageAgent
import importlib.util
from pathlib import Path


def _load_class_from_file(class_name: str, filename: str):
    # Try several candidate locations: package folder `single_agent`, folder with space `single agent`, or same dir
    base = Path(__file__).parent
    candidates = [base / 'single_agent' / filename, base / 'single agent' / filename, base / filename]
    for p in candidates:
        if p.exists():
            spec = importlib.util.spec_from_file_location(p.stem, str(p))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return getattr(mod, class_name, None)
    return None


LocalResearcherAgent = _load_class_from_file('LocalResearcherAgent', 'local_researcher.py')
LocalWriterAgent = _load_class_from_file('LocalWriterAgent', 'local_writer.py')

# Prefer package `local_agents` when available (zipapp-friendly)
try:
    from local_agents.local_researcher import LocalResearcherAgent as _LR
    from local_agents.local_writer import LocalWriterAgent as _LW
    LocalResearcherAgent = _LR
    LocalWriterAgent = _LW
except Exception:
    pass


class FullAgent:
    def __init__(self, researcher=None, writer=None, triage_agent: Optional[TriageAgent] = None, status_callback: Optional[Callable[[str], None]] = None):
        self.status = status_callback
        self.triage = triage_agent or TriageAgent()
        self.researcher = researcher or LocalResearcherAgent(status_callback=self.status)
        self.writer = writer or LocalWriterAgent(status_callback=self.status)

    def _log(self, msg: str):
        if self.status:
            self.status(msg)

    def analyze_case(self, patient_input: Dict[str, Any], run_research: bool = True) -> Dict[str, Any]:
        """Run triage on patient input, optionally perform topic research and produce a report.

        Returns a dictionary with keys: `triage`, `research` (optional), `report` (optional).
        """
        self._log("Running triage analysis...")
        triage_result = self.triage.deliberate(patient_input)

        research_result = None
        report = None

        if run_research:
            topic = patient_input.get('chief_complaint', 'general')
            self._log(f"Running research on topic: {topic}")
            research_result = self.researcher.research(topic, status_callback=self.status)

            self._log("Generating report from research and triage result")
            report = self.writer.create_report(research_result, triage_result, status_callback=self.status)

        return {
            'triage': triage_result,
            'research': research_result,
            'report': report,
        }


def demo():
    fa = FullAgent()
    sample_patient = {
        "age": 68,
        "chief_complaint": "shortness of breath",
        "time_since_onset": "2 hours",
        "consciousness_level": "alert",
        "vital_signs": {
            "heart_rate": 110,
            "respiratory_rate": 28,
            "blood_pressure_systolic": 140,
            "blood_pressure_diastolic": 85,
            "o2_saturation": 88,
            "temperature": 36.8,
        },
    }
    out = fa.analyze_case(sample_patient)
    import json

    print(json.dumps({
        'triage_decision': out['triage'].get('decision'),
        'research_success': bool(out['research'] and out['research'].get('success')),
    }, indent=2))


if __name__ == '__main__':
    demo()
