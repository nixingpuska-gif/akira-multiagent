import json
from typing import Optional, Tuple

import httpx


def _build_input(messages: list) -> Tuple[Optional[str], list]:
    system = None
    items = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            if isinstance(content, list):
                system = " ".join([str(c.get("text", "")) for c in content])
            else:
                system = str(content)
            continue
        if isinstance(content, list):
            items.append({"role": role, "content": content})
            continue
        if not isinstance(content, str):
            content = str(content)
        items.append({"role": role, "content": [{"type": "input_text", "text": content}]})
    return system, items


def _extract_text(data: dict) -> str:
    if not isinstance(data, dict):
        return ""

    output_text = data.get("output_text")
    if isinstance(output_text, str) and output_text:
        return output_text

    output = data.get("output")
    if isinstance(output, list):
        chunks = []
        for item in output:
            content = item.get("content", [])
            if isinstance(content, list):
                for part in content:
                    part_type = part.get("type")
                    if part_type in ("output_text", "text"):
                        text = part.get("text")
                        if text:
                            chunks.append(text)
        if chunks:
            return "".join(chunks)

    content = data.get("content")
    if isinstance(content, list):
        chunks = []
        for part in content:
            text = part.get("text")
            if text:
                chunks.append(text)
        if chunks:
            return "".join(chunks)

    return ""


def _extract_text_from_event(data: dict) -> str:
    if "delta" in data and isinstance(data["delta"], str):
        return data["delta"]
    if "output_text" in data and isinstance(data["output_text"], str):
        return data["output_text"]
    if "response" in data and isinstance(data["response"], dict):
        return _extract_text(data["response"])
    if "content" in data and isinstance(data["content"], list):
        return _extract_text({"content": data["content"]})
    return ""


async def complete(base_url: str, api_key: str, request: dict, messages: list) -> str:
    endpoint = request.get("endpoint", "/responses")
    url = base_url.rstrip("/") + endpoint

    instructions, input_items = _build_input(messages)
    payload = {
        "model": request.get("model"),
        "input": input_items,
    }
    if instructions:
        payload["instructions"] = instructions

    if "temperature" in request:
        payload["temperature"] = request.get("temperature", 0.2)

    if "max_output_tokens" in request:
        payload["max_output_tokens"] = request.get("max_output_tokens")
    elif "max_tokens" in request:
        payload["max_output_tokens"] = request.get("max_tokens")

    payload.update(request.get("extra", {}))

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=90) as client:
        async with client.stream("POST", url, json=payload, headers=headers) as response:
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            if "text/event-stream" not in content_type:
                data = await response.json()
                return _extract_text(data)

            chunks = []
            async for line in response.aiter_lines():
                if not line:
                    continue
                if line.startswith("data:"):
                    raw = line[len("data:") :].strip()
                    if raw == "[DONE]":
                        break
                    try:
                        event = json.loads(raw)
                    except json.JSONDecodeError:
                        continue
                    text = _extract_text_from_event(event)
                    if text:
                        chunks.append(text)
            return "".join(chunks)
