from typing import Any, Dict, List


def build_agents(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    agents: List[Dict[str, Any]] = []
    for spec in config.get("agents", []):
        role = spec["role"]
        count = int(spec.get("count", 1))
        provider = spec["provider"]
        system_prompt = spec.get("system_prompt", "")
        for idx in range(1, count + 1):
            name = f"{role}-{idx:02d}" if count > 1 else role
            agents.append(
                {
                    "name": name,
                    "role": role,
                    "provider": provider,
                    "system_prompt": system_prompt,
                }
            )
    return agents
