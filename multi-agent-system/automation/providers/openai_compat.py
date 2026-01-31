import httpx


async def complete(base_url: str, api_key: str, request: dict, messages: list) -> str:
    endpoint = request.get("endpoint", "/v1/chat/completions")
    url = base_url.rstrip("/") + endpoint

    payload = {
        "model": request.get("model"),
        "messages": messages,
        "temperature": request.get("temperature", 0.2),
        "max_tokens": request.get("max_tokens", 2000),
    }
    payload.update(request.get("extra", {}))

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    if "choices" in data and data["choices"]:
        choice = data["choices"][0]
        if "message" in choice and choice["message"]:
            return choice["message"].get("content", "") or ""
        return choice.get("text", "") or ""

    return data.get("output_text", "") or ""
