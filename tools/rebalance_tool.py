from simulator.vmss_simulator import VMSSSimulator

def rebalance_zones(simulator: VMSSSimulator) -> dict:
    zones = [1, 2, 3]
    before = simulator.state.zone_distribution()

    for i, instance in enumerate(simulator.state.instances):
        instance.zone = zones[i % len(zones)]

    after = simulator.state.zone_distribution()

    return {
        "action": "rebalance",
        "before": before,
        "after": after,
        "reason": "Redistributed instances evenly across availability zones"
    }