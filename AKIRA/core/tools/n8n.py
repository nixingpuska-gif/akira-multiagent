import json
import os
from typing import Optional, Any

import httpx


def _workflows_dir(data_dir: str) -> str:
    path = os.path.join(data_dir, "n8n", "workflows")
    os.makedirs(path, exist_ok=True)
    return path


def _normalize_content(content: Any) -> str:
    if isinstance(content, (dict, list)):
        return json.dumps(content, ensure_ascii=False, indent=2)
    if isinstance(content, str):
        try:
            parsed = json.loads(content)
            return json.dumps(parsed, ensure_ascii=False, indent=2)
        except Exception:
            return content
    return json.dumps(content, ensure_ascii=False)


def save_workflow(name: str, content: Any, data_dir: str, mode: str = "safe") -> str:
    if mode != "full":
        return "ERROR: n8n save disabled in safe mode. Set AKIRA_MODE=full."
    if not name.endswith(".json"):
        name = f"{name}.json"
    path = os.path.join(_workflows_dir(data_dir), name)
    content_str = _normalize_content(content)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content_str)
    return path


async def import_workflow(
    content: Any,
    api_base: Optional[str],
    api_key: Optional[str],
    mode: str = "safe",
    timeout_s: float = 60.0,
) -> str:
    if mode != "full":
        return "ERROR: n8n import disabled in safe mode. Set AKIRA_MODE=full."
    if not api_base or not api_key:
        return "ERROR: N8N_API_BASE and N8N_API_KEY are required."
    url = api_base.rstrip("/") + "/api/v1/workflows"
    headers = {"X-N8N-API-KEY": api_key, "Content-Type": "application/json"}
    payload = _normalize_content(content)
    async with httpx.AsyncClient(timeout=timeout_s) as client:
        resp = await client.post(url, headers=headers, data=payload)
        if resp.status_code >= 400:
            return f"ERROR: n8n API {resp.status_code} {resp.text}"
        return resp.text


async def save_and_import_workflow(
    name: str,
    content: Any,
    data_dir: str,
    api_base: Optional[str],
    api_key: Optional[str],
    mode: str = "safe",
) -> str:
    saved = save_workflow(name, content, data_dir, mode=mode)
    if saved.startswith("ERROR:"):
        return saved
    imported = await import_workflow(content, api_base, api_key, mode=mode)
    return f"Saved: {saved}\nImport: {imported}"
