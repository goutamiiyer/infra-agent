import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from simulator.vmss_simulator import VMSSSimulator
from agent.agent import run_agent

test_scenarios = [
    {"scenario": "unhealthy_instances", "expected": "repair"},
    {"scenario": "zone_imbalance", "expected": "rebalance"},
]

print("Running CI agent subset (2 scenarios)...")

for case in test_scenarios:
    sim = VMSSSimulator()
    result = run_agent(sim, scenario=case["scenario"], verbose=False)
    actual = result["decision"]["action"]
    status = "PASS" if actual == case["expected"] else "FAIL"
    print(f"{status}: {case['scenario']} -> {actual} (expected {case['expected']})")
    time.sleep(3)

print("Agent CI subset OK")