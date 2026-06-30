import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulator.vmss_simulator import VMSSSimulator

sim = VMSSSimulator()
state = sim.get_state()

assert state["instance_count"] == 6, f"Expected 6 instances, got {state['instance_count']}"
assert state["unhealthy_count"] == 0
assert "zone_1" in state["zone_distribution"]
assert "zone_2" in state["zone_distribution"]
assert "zone_3" in state["zone_distribution"]

state = sim.apply_scenario("zone_imbalance")
assert state["zone_distribution"]["zone_1"] == 6
assert state["zone_distribution"]["zone_2"] == 0
assert state["zone_distribution"]["zone_3"] == 0

state = sim.apply_scenario("high_cpu")
assert state["avg_cpu"] > 80

print("Simulator OK: instance count, zone distribution, and scenarios working")