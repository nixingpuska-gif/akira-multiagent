import os
import re
from typing import Any, Dict

from dotenv import load_dotenv
import yaml

ENV_PATTERN = re.compile(r"\$\{([A-Z0-9_]+)(:-([^}]+))?\}")


def load_env() -> None:
    load_dotenv()


def _expand_value(value: Any) -> Any:
    if isinstance(value, str):
        def replace(match: re.Match) -> str:
            key = match.group(1)
            default = match.group(3)
            return os.getenv(key, default or "")
        return ENV_PATTERN.sub(replace, value)
    if isinstance(value, list):
        return [_expand_value(v) for v in value]
    if isinstance(value, dict):
        return {k: _expand_value(v) for k, v in value.items()}
    return value


def load_yaml_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return _expand_value(data)


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)
