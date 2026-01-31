import httpx


async def complete(base_url: str, api_key: str, request: dict, messages: list) -> str:
    url = base_url.rstrip("/") + "/v1/messages"
    system = None
    anth_messages = []
    for msg in messages:
        if msg.get("role") == "system":
            system = msg.get("content")
            continue
        anth_messages.append({"role": msg.get("role"), "content": msg.get("content")})

    payload = {
        "model": request.get("model"),
        "max_tokens": request.get("max_tokens", 2000),
        "temperature": request.get("temperature", 0.2),
        "messages": anth_messages,
    }
    if system:
        payload["system"] = system
    payload.update(request.get("extra", {}))

    headers = {
        "x-api-key": api_key,
        "anthropic-version": request.get("anthropic_version", "2023-06-01"),
        "content-type": "application/json",
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    content = data.get("content", [])
    if isinstance(content, list) and content:
        return "".join([part.get("text", "") for part in content])
    return ""
