from simulator.vmss_simulator import VMSSSimulator
from agent.planner import decide_action
import json

sim = VMSSSimulator()
state = sim.apply_scenario("zone_imbalance")

print("State sent to LLM:")
print(json.dumps(state, indent=2))

decision = decide_action(state)
print("\nDecision:")
print(json.dumps(decision, indent=2))