import json
from simulator.vmss_simulator import VMSSSimulator
from agent.planner import decide_action
from tools.scale_tool import scale_out, scale_in
from tools.repair_tool import repair_unhealthy_instances
from tools.rebalance_tool import rebalance_zones
from tools.alert_tool import create_alert

def run_agent(simulator: VMSSSimulator, scenario: str = "normal", verbose: bool = True) -> dict:
    state = simulator.apply_scenario(scenario)

    if verbose:
        print(f"\nScenario: {scenario}")
        print(f"State: avg_cpu={state['avg_cpu']}% | "
              f"unhealthy={state['unhealthy_count']} | "
              f"zones={state['zone_distribution']}")

    decision = decide_action(state)

    if verbose:
        print(f"\nAgent decision: {decision['action']}")
        print(f"Reasoning: {decision['reasoning']}")
        print(f"Priority: {decision['priority']}")

    action_result = execute_action(decision["action"], simulator, state)

    if verbose:
        print(f"\nAction result: {json.dumps(action_result, indent=2)}")

    return {
        "scenario": scenario,
        "initial_state": state,
        "decision": decision,
        "action_result": action_result
    }

def execute_action(action: str, simulator: VMSSSimulator, state: dict) -> dict:
    if action == "scale_out":
        return scale_out(simulator)
    elif action == "scale_in":
        return scale_in(simulator)
    elif action == "repair":
        return repair_unhealthy_instances(simulator)
    elif action == "rebalance":
        return rebalance_zones(simulator)
    elif action == "alert":
        return create_alert(
            severity="high",
            title=f"Infrastructure issue detected in {state['scale_set_name']}",
            description="Agent detected an issue requiring human attention",
            metrics={
                "avg_cpu": state["avg_cpu"],
                "unhealthy_count": state["unhealthy_count"],
                "zone_distribution": state["zone_distribution"]
            }
        )
    else:
        return {"action": "no_action", "reason": "System healthy"}