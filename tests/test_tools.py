import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulator.vmss_simulator import VMSSSimulator
from tools.scale_tool import scale_out, scale_in
from tools.repair_tool import repair_unhealthy_instances
from tools.rebalance_tool import rebalance_zones

sim = VMSSSimulator()
result = scale_out(sim, add_instances=2)
assert result["new_count"] == 8, f"Expected 8, got {result['new_count']}"

result = scale_in(sim, remove_instances=2)
assert result["new_count"] == 6, f"Expected 6, got {result['new_count']}"

sim.apply_scenario("unhealthy_instances")
result = repair_unhealthy_instances(sim)
assert result["count"] == 2, f"Expected 2 repaired, got {result['count']}"

sim.apply_scenario("zone_imbalance")
result = rebalance_zones(sim)
assert result["after"]["zone_1"] == 2
assert result["after"]["zone_2"] == 2
assert result["after"]["zone_3"] == 2

print("Tools OK: scale_out, scale_in, repair, rebalance all working")