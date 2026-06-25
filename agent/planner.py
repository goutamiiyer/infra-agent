import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

TOOLS = {
    "scale_out": "Add more VM instances to handle increased load",
    "scale_in": "Remove VM instances when load is low",
    "repair": "Repair unhealthy VM instances",
    "rebalance": "Redistribute instances evenly across availability zones",
    "alert": "Create an alert for critical issues requiring human attention",
    "no_action": "System is healthy, no action needed"
}

def decide_action(state: dict) -> dict:
    tools_description = "\n".join([f"- {k}: {v}" for k, v in TOOLS.items()])

    prompt = f"""You are an infrastructure operations agent monitoring an Azure Virtual Machine Scale Set.

Current system state:
{json.dumps(state, indent=2)}

Available actions:
{tools_description}

Analyze the state and decide what single action to take.
Consider:
- CPU above 80% means high load, consider scale_out
- More than 1 unhealthy instance means repair is needed
- Zone imbalance (one zone has more than double another) means rebalance
- Memory above 85% means memory pressure, consider scale_out
- CPU below 20% with many instances means scale_in
- Critical issues that can't be auto-remediated need alert

Respond in exactly this JSON format:
{{
    "action": "one of the available action names",
    "reasoning": "one sentence explaining why",
    "priority": "low, medium, high, or critical"
}}"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    text = response.choices[0].message.content.strip()
    decision = json.loads(text)

    return decision