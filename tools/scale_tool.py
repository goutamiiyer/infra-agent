from simulator.vmss_simulator import VMSSSimulator

def scale_out(simulator: VMSSSimulator, add_instances: int = 2) -> dict:
    current_count = len(simulator.state.instances)
    zones = [1, 2, 3]

    from simulator.vmss_simulator import VMInstance
    import random

    for i in range(add_instances):
        new_id = f"vm-{current_count + i:03d}"
        zone = zones[(current_count + i) % len(zones)]
        simulator.state.instances.append(VMInstance(
            instance_id=new_id,
            zone=zone,
            status="healthy",
            cpu_percent=random.uniform(20, 35),
            memory_percent=random.uniform(30, 45)
        ))

    return {
        "action": "scale_out",
        "instances_added": add_instances,
        "new_count": len(simulator.state.instances),
        "reason": f"Scaled from {current_count} to {len(simulator.state.instances)} instances"
    }

def scale_in(simulator: VMSSSimulator, remove_instances: int = 1) -> dict:
    current_count = len(simulator.state.instances)
    if current_count <= 2:
        return {
            "action": "scale_in_blocked",
            "reason": "Cannot scale below 2 instances"
        }

    for _ in range(min(remove_instances, current_count - 2)):
        simulator.state.instances.pop()

    return {
        "action": "scale_in",
        "instances_removed": remove_instances,
        "new_count": len(simulator.state.instances),
        "reason": f"Scaled from {current_count} to {len(simulator.state.instances)} instances"
    }