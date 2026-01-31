import asyncio
import json
from typing import Any, List, Dict, Optional

import httpx

try:
    import litellm  # type: ignore
except Exception:  # pragma: no cover
    litellm = None


def _normalize_base_for_litellm(base: str) -> str:
    base = base.rstrip("/")
    if base.endswith("/v1/chat/completions"):
        base = base[: -len("/v1/chat/completions")]
    if base.endswith("/v1"):
        base = base[: -len("/v1")]
    return base


def _build_chat_url(base: str) -> str:
    base = base.rstrip("/")
    if base.endswith("/v1/chat/completions"):
        return base
    if base.endswith("/v1"):
        return f"{base}/chat/completions"
    return f"{base}/v1/chat/completions"


def _build_responses_url(base: str) -> str:
    base = base.rstrip("/")
    if base.endswith("/responses"):
        return base
    if base.endswith("/v1/responses"):
        return base
    if base.endswith("/v1"):
        return f"{base}/responses"
    return f"{base}/responses"


class LLMRouter:
    def __init__(
        self,
        *,
        model: str,
        fallback_model: Optional[str],
        primary_base: str,
        primary_key: str,
        fallback_base: str,
        fallback_key: Optional[str],
        timeout_s: float = 60.0,
        wire_api: str = "chat",
        fallback_wire_api: str = "chat",
        budget_manager: Optional[Any] = None,
    ):
        self.model = model
        self.fallback_model = fallback_model or model
        self.primary_base = primary_base
        self.primary_key = primary_key
        self.fallback_base = fallback_base
        self.fallback_key = fallback_key
        self.timeout_s = timeout_s
        self.wire_api = wire_api
        self.fallback_wire_api = fallback_wire_api
        self.budget_manager = budget_manager

    def set_budget_manager(self, budget_manager: Optional[Any]) -> None:
        self.budget_manager = budget_manager

    def update_config(
        self,
        primary_base: str,
        primary_key: str,
        model: str,
        fallback_base: Optional[str] = None,
        fallback_key: Optional[str] = None,
        fallback_model: Optional[str] = None,
        wire_api: Optional[str] = None,
        fallback_wire_api: Optional[str] = None,
    ) -> None:
        self.primary_base = primary_base
        self.primary_key = primary_key
        self.model = model
        if fallback_base is None:
            fallback_base = self.fallback_base
        self.fallback_base = fallback_base
        self.fallback_key = fallback_key
        self.fallback_model = fallback_model or model
        if wire_api:
            self.wire_api = wire_api
        if fallback_wire_api:
            self.fallback_wire_api = fallback_wire_api

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        if self.wire_api == "responses":
            return await self._chat_responses(messages)
        # Try LiteLLM if available, else use direct HTTP.
        if litellm:
            try:
                return await self._chat_litellm(messages, self.primary_base, self.primary_key)
            except Exception:
                if self.fallback_key:
                    return await self._chat_litellm(messages, self.fallback_base, self.fallback_key)
                raise
        return await self._chat_http(messages)

    async def _chat_litellm(self, messages, base, key) -> str:
        err = self._consume_budget()
        if err:
            return err
        base_norm = _normalize_base_for_litellm(base)

        def _call():
            return litellm.completion(
                model=self.model,
                messages=messages,
                api_base=base_norm,
                api_key=key,
                timeout=self.timeout_s,
            )

        resp = await asyncio.to_thread(_call)
        return resp["choices"][0]["message"]["content"]

    async def _chat_http(self, messages: List[Dict[str, str]]) -> str:
        primary_url = _build_chat_url(self.primary_base)
        fallback_url = _build_chat_url(self.fallback_base)

        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            try:
                return await self._post_chat(client, primary_url, self.primary_key, messages)
            except Exception:
                if self.fallback_key:
                    return await self._post_chat(client, fallback_url, self.fallback_key, messages)
                raise

    async def _chat_responses(self, messages: List[Dict[str, str]]) -> str:
        primary_url = _build_responses_url(self.primary_base)
        fallback_responses_url = _build_responses_url(self.fallback_base)
        fallback_chat_url = _build_chat_url(self.fallback_base)
        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            try:
                text = await self._post_responses(client, primary_url, self.primary_key, messages)
                if not text:
                    raise RuntimeError("Empty response from primary responses API")
                return text
            except Exception:
                if self.fallback_key:
                    if self.fallback_wire_api == "responses":
                        text = await self._post_responses(
                            client,
                            fallback_responses_url,
                            self.fallback_key,
                            messages,
                            model=self.fallback_model,
                        )
                        if not text:
                            raise RuntimeError("Empty response from fallback responses API")
                        return text
                    return await self._post_chat(
                        client,
                        fallback_chat_url,
                        self.fallback_key,
                        messages,
                        model=self.fallback_model,
                    )
                raise

    async def _post_chat(
        self,
        client: httpx.AsyncClient,
        url: str,
        key: str,
        messages,
        model: Optional[str] = None,
    ):
        err = self._consume_budget()
        if err:
            return err
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {"model": model or self.model, "messages": messages}
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"]
        return str(data)

    async def _post_responses(
        self,
        client: httpx.AsyncClient,
        url: str,
        key: str,
        messages,
        model: Optional[str] = None,
    ):
        err = self._consume_budget()
        if err:
            return err
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {"model": model or self.model, "input": messages}
        text_parts: List[str] = []

        async with client.stream("POST", url, headers=headers, json=payload) as resp:
            resp.raise_for_status()

            async for line in resp.aiter_lines():
                if not line:
                    continue
                if line.startswith("data:"):
                    data = line[5:].strip()
                    if not data or data == "[DONE]":
                        continue
                    try:
                        obj = json.loads(data)
                    except Exception:
                        continue
                    typ = obj.get("type", "")
                    if typ.endswith("output_text.delta"):
                        delta = obj.get("delta")
                        if delta:
                            text_parts.append(delta)
                    elif typ.endswith("output_text.done"):
                        text = obj.get("text")
                        if text and not text_parts:
                            text_parts.append(text)

        return "".join(text_parts).strip()

    def _consume_budget(self) -> Optional[str]:
        if self.budget_manager is None:
            return None
        result = self.budget_manager.consume(1)
        if not result.get("ok", False):
            return result.get("error", "ERROR: request budget exceeded.")
        return None
