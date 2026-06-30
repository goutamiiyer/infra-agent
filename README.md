# Infra Agent

An autonomous infrastructure operations agent that monitors a simulated
Azure Virtual Machine Scale Set, detects anomalies, and takes corrective
action using an LLM-driven decision loop.

## What it does

Simulates a VMSS experiencing common failure modes (high CPU, unhealthy
instances, zone imbalance, memory pressure), feeds the current state to
an LLM, and lets the LLM decide which remediation action to take from a
fixed set of tools: scale out, scale in, repair, rebalance, or alert.

## Architecture

```
simulator/vmss_simulator.py   simulated VMSS with injectable failure scenarios
agent/planner.py              LLM decides which action to take given current state
agent/agent.py                main loop: state → decision → execution
tools/                        scale, repair, rebalance, alert implementations
eval/scenarios_eval.py        measures decision accuracy across repeated runs
agent_cli.py                  CLI entry point
```

## Eval results

5 scenarios, 3 runs each, fresh simulator state per run:

| Scenario | Expected | Consistency |
|---|---|---|
| normal | no_action | 100% |
| high_cpu | scale_out | 100% |
| unhealthy_instances | repair | 100% |
| zone_imbalance | rebalance | 100% |
| memory_pressure | scale_out | 100% |

**Overall consistency: 100% (5/5 scenarios fully reliable)**

## Key finding: a state representation bug, not a prompt bug

Initial eval showed zone_imbalance failing 0/3 times, consistently
choosing no_action when 6 instances were piled into a single zone.

The cause wasn't the LLM. It was the data it received. The simulator's
`zone_distribution()` method only included zones that had at least one
instance:

```json
{"zone_1": 6}
```

Zones 2 and 3 were absent from the data entirely rather than shown as
zero. The LLM had no way to detect imbalance because it had no evidence
the other zones existed. Fixing the simulator to always report all
zones explicitly, including zero counts, immediately fixed the agent's
decision-making with no prompt changes:

```json
{"zone_1": 6, "zone_2": 0, "zone_3": 0}
```

Lesson: in agentic systems, decision quality is bounded by the
completeness of the state representation the LLM receives. Debugging
an unreliable agent should start with inspecting exactly what data the
LLM sees, not with rewriting the prompt.

## How to run

```bash
git clone https://github.com/YOUR_USERNAME/infra-agent
cd infra-agent
pip install groq python-dotenv httpx
echo "GROQ_API_KEY=your_key_here" > .env

python agent_cli.py status
python agent_cli.py run --scenario high_cpu
python agent_cli.py simulate --all-scenarios
python eval/scenarios_eval.py
```

## CLI commands

```bash
python agent_cli.py status                              # current simulated state
python agent_cli.py run --scenario <name>                # run agent on one scenario
python agent_cli.py run --scenario high_cpu --output result.json
python agent_cli.py simulate --all-scenarios              # run every scenario once
python eval/scenarios_eval.py                              # reliability eval, 3 runs each
```

Available scenarios: `normal`, `high_cpu`, `unhealthy_instances`, `zone_imbalance`, `memory_pressure`

## Tools the agent can invoke

- **scale_out** / **scale_in**: adjust instance count, zone-aware placement
- **repair**: reset unhealthy instances to healthy
- **rebalance**: redistribute instances evenly across availability zones
- **alert**: escalate to a human, optionally opens a GitHub issue if `GITHUB_TOKEN` is set

## Tech stack

- Python 3.12
- Groq API, openai/gpt-oss-20b
- Simulated infrastructure (no real Azure dependency, runs anywhere)

## Why this project

Built on 3 years of Azure Core Compute Platform experience working on
VMSS orchestration. The failure scenarios and remediation logic mirror
real Azure VMSS reliability features: automatic zone balance, automatic
instance repairs, resilient create/delete, documented in the companion
[production-rag-system](https://github.com/YOUR_USERNAME/production-rag-system)
repo's source documents.

## Author

Goutami, software engineer with background in distributed systems and
backend infrastructure at Microsoft Azure, building toward applied AI
engineering roles.