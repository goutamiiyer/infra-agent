import argparse
import json
from simulator.vmss_simulator import VMSSSimulator
from agent.agent import run_agent

SCENARIOS = ["normal", "high_cpu", "unhealthy_instances", "zone_imbalance", "memory_pressure"]

def parse_args():
    parser = argparse.ArgumentParser(
        description="Infra Agent: autonomous infrastructure operations agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agent_cli.py run --scenario high_cpu
  python agent_cli.py run --scenario unhealthy_instances
  python agent_cli.py run --scenario zone_imbalance
  python agent_cli.py simulate --all-scenarios
  python agent_cli.py status
        """
    )

    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    run_parser = subparsers.add_parser("run", help="Run agent on a scenario")
    run_parser.add_argument(
        "--scenario",
        choices=SCENARIOS,
        default="normal",
        help="Scenario to simulate"
    )
    run_parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Save result to JSON file"
    )

    sim_parser = subparsers.add_parser("simulate", help="Run multiple scenarios")
    sim_parser.add_argument(
        "--all-scenarios",
        action="store_true",
        help="Run all scenarios sequentially"
    )

    subparsers.add_parser("status", help="Show current simulated system state")

    return parser.parse_args()

def cmd_run(args):
    sim = VMSSSimulator()
    result = run_agent(sim, scenario=args.scenario)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\nResult saved to {args.output}")

def cmd_simulate(args):
    if args.all_scenarios:
        print("Running all scenarios...\n")
        print("=" * 60)
        for scenario in SCENARIOS:
            sim = VMSSSimulator()
            result = run_agent(sim, scenario=scenario)
            print(f"\nResult: {result['decision']['action']} "
                  f"({result['decision']['priority']} priority)")
            print("=" * 60)

def cmd_status(args):
    sim = VMSSSimulator()
    state = sim.get_state()
    print(json.dumps(state, indent=2))

if __name__ == "__main__":
    args = parse_args()
    commands = {
        "run": cmd_run,
        "simulate": cmd_simulate,
        "status": cmd_status
    }
    commands[args.command](args)