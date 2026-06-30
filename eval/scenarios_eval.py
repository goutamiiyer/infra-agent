import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time

import json
from simulator.vmss_simulator import VMSSSimulator
from agent.agent import run_agent

def load_eval_cases(path: str = "eval/eval_cases.jsonl") -> list[dict]:
    with open(path) as f:
        return [json.loads(line) for line in f]

def run_single_eval(case: dict, runs_per_scenario: int = 3) -> dict:
    results = []

    for run_num in range(runs_per_scenario):
        sim = VMSSSimulator()
        result = run_agent(sim, scenario=case["scenario"], verbose=False)
        actual_action = result["decision"]["action"]
        correct = actual_action == case["expected_action"]

        results.append({
            "run": run_num + 1,
            "actual_action": actual_action,
            "correct": correct,
            "reasoning": result["decision"]["reasoning"]
        })

        time.sleep(3)

    correct_count = sum(1 for r in results if r["correct"])
    consistency = correct_count / runs_per_scenario

    return {
        "scenario": case["scenario"],
        "expected_action": case["expected_action"],
        "runs": results,
        "correct_count": correct_count,
        "total_runs": runs_per_scenario,
        "consistency": consistency
    }

def run_full_eval(runs_per_scenario: int = 3) -> list[dict]:
    cases = load_eval_cases()
    all_results = []

    print(f"\n--- Agent Evaluation ({runs_per_scenario} runs per scenario) ---\n")

    for case in cases:
        result = run_single_eval(case, runs_per_scenario)
        all_results.append(result)

        status = "RELIABLE" if result["consistency"] == 1.0 else "UNRELIABLE" if result["consistency"] > 0 else "BROKEN"

        print(f"Scenario: {result['scenario']}")
        print(f"  Expected: {result['expected_action']}")
        print(f"  Status: {status} ({result['correct_count']}/{result['total_runs']} correct)")

        actions_taken = [r["actual_action"] for r in result["runs"]]
        print(f"  Actions taken: {actions_taken}")
        print()

    overall_consistency = sum(r["consistency"] for r in all_results) / len(all_results)
    fully_reliable = sum(1 for r in all_results if r["consistency"] == 1.0)

    print(f"Scenarios fully reliable: {fully_reliable}/{len(all_results)}")
    print(f"Overall consistency score: {overall_consistency:.0%}")

    return all_results

if __name__ == "__main__":
    run_full_eval()