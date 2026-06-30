import random
import time
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class VMInstance:
    instance_id: str
    zone: int
    status: str = "healthy"
    cpu_percent: float = 0.0
    memory_percent: float = 0.0

    def to_dict(self) -> dict:
        return {
            "instance_id": self.instance_id,
            "zone": self.zone,
            "status": self.status,
            "cpu_percent": round(self.cpu_percent, 1),
            "memory_percent": round(self.memory_percent, 1)
        }

@dataclass
class VMSSState:
    scale_set_name: str
    region: str
    instances: list[VMInstance] = field(default_factory=list)
    timestamp: str = ""

    def to_dict(self) -> dict:
        return {
            "scale_set_name": self.scale_set_name,
            "region": self.region,
            "timestamp": self.timestamp,
            "instance_count": len(self.instances),
            "instances": [i.to_dict() for i in self.instances],
            "zone_distribution": self.zone_distribution(),
            "unhealthy_count": self.unhealthy_count(),
            "avg_cpu": self.avg_cpu(),
            "avg_memory": self.avg_memory()
        }

    def zone_distribution(self) -> dict:
        dist = {"zone_1": 0, "zone_2": 0, "zone_3": 0}
        for instance in self.instances:
            zone_key = f"zone_{instance.zone}"
            dist[zone_key] = dist.get(zone_key, 0) + 1
        return dist

    def unhealthy_count(self) -> int:
        return sum(1 for i in self.instances if i.status != "healthy")

    def avg_cpu(self) -> float:
        if not self.instances:
            return 0.0
        return round(sum(i.cpu_percent for i in self.instances) / len(self.instances), 1)

    def avg_memory(self) -> float:
        if not self.instances:
            return 0.0
        return round(sum(i.memory_percent for i in self.instances) / len(self.instances), 1)


class VMSSSimulator:
    def __init__(self, name: str = "prod-vmss", region: str = "eastus", instance_count: int = 6):
        self.name = name
        self.region = region
        self.instance_count = instance_count
        self.state = self._initialize()

    def _initialize(self) -> VMSSState:
        instances = []
        zones = [1, 2, 3]
        for i in range(self.instance_count):
            zone = zones[i % len(zones)]
            instances.append(VMInstance(
                instance_id=f"vm-{i:03d}",
                zone=zone,
                status="healthy",
                cpu_percent=random.uniform(20, 40),
                memory_percent=random.uniform(30, 50)
            ))
        return VMSSState(
            scale_set_name=self.name,
            region=self.region,
            instances=instances,
            timestamp=datetime.utcnow().isoformat()
        )

    def get_state(self) -> dict:
        self.state.timestamp = datetime.utcnow().isoformat()
        return self.state.to_dict()

    def apply_scenario(self, scenario: str) -> dict:
        if scenario == "high_cpu":
            for instance in self.state.instances:
                instance.cpu_percent = random.uniform(85, 98)

        elif scenario == "unhealthy_instances":
            unhealthy = random.sample(self.state.instances, k=2)
            for instance in unhealthy:
                instance.status = "unhealthy"
                instance.cpu_percent = 0.0

        elif scenario == "zone_imbalance":
            for instance in self.state.instances:
                instance.zone = 1

        elif scenario == "memory_pressure":
            for instance in self.state.instances:
                instance.memory_percent = random.uniform(88, 97)

        elif scenario == "normal":
            for instance in self.state.instances:
                instance.status = "healthy"
                instance.cpu_percent = random.uniform(20, 40)
                instance.memory_percent = random.uniform(30, 50)
                instance.zone = [1, 2, 3][self.state.instances.index(instance) % 3]

        return self.get_state()


if __name__ == "__main__":
    sim = VMSSSimulator()

    print("Normal state:")
    import json
    state = sim.get_state()
    print(json.dumps(state, indent=2))

    print("\nAfter high CPU scenario:")
    state = sim.apply_scenario("high_cpu")
    print(f"Avg CPU: {state['avg_cpu']}%")
    print(f"Unhealthy: {state['unhealthy_count']}")

    print("\nAfter zone imbalance scenario:")
    state = sim.apply_scenario("zone_imbalance")
    print(f"Zone distribution: {state['zone_distribution']}")