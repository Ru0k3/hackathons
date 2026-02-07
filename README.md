# Autonomous Medical Triage Deliberation Agent (S2)

This repository contains a single autonomous deliberation agent designed to assess whether it is safe to provide autonomous guidance in high-stakes medical triage contexts. The agent does NOT diagnose or provide treatment. It decides one of: ACT_CONFIDENTLY, ACT_WITH_WARNING, ASK_FOR_MORE_INFORMATION, or REFUSE_AUTONOMOUS_ACTION.

Files of interest:
- `triage_agent.py` — the agent implementation (four-phase reasoning pipeline).
- `triage_demo.py` — CLI demo to run the agent with `--sample` or `--input-json`.
- `test_triage_agent.py` — basic unit tests covering key decision paths.
- `examples/` — example JSON inputs you can use with the demo.

Quick start

Run the sample demo:

```bash
python triage_demo.py --sample
```

Run the demo with an example input:

```bash
python triage_demo.py --input-json examples/sample_low_risk.json
```

Run tests:

```bash
python -m unittest discover -v
```

Safety notes

- The agent intentionally emphasizes uncertainty, self-evaluation, and refusal when appropriate. It is not a clinical decision tool and must not be used as a substitute for care by qualified clinicians.
- If the agent returns `REFUSE_AUTONOMOUS_ACTION` or `ASK_FOR_MORE_INFORMATION`, escalate to human clinical staff.

License & attribution

This is example code for demonstration and development purposes only.
