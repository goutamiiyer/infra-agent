from simulator.vmss_simulator import VMSSSimulator
import random

def repair_unhealthy_instances(simulator: VMSSSimulator) -> dict:
    unhealthy = [i for i in simulator.state.instances if i.status != "healthy"]

    if not unhealthy:
        return {
            "action": "repair_skipped",
            "reason": "No unhealthy instances found"
        }

    repaired = []
    for instance in unhealthy:
        instance.status = "healthy"
        instance.cpu_percent = random.uniform(20, 40)
        instance.memory_percent = random.uniform(30, 50)
        repaired.append(instance.instance_id)

    return {
        "action": "repair",
        "repaired_instances": repaired,
        "count": len(repaired),
        "reason": f"Repaired {len(repaired)} unhealthy instances"
    }