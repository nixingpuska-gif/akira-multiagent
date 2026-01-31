"""
OpenRouter Integration
Unified API for multiple AI models
"""

import os
import aiohttp
from typing import Dict, Any, Optional, List


class OpenRouterClient:
    """
    Client for OpenRouter API.
    Provides access to multiple models through unified interface.
    """

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.current_model = "openai/gpt-4"  # Default model

    async def query(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Query OpenRouter API.

        Args:
            prompt: User prompt
            system_prompt: System prompt
            model: Model to use (e.g., "openai/gpt-4", "anthropic/claude-3")
            temperature: Temperature
            max_tokens: Max tokens

        Returns:
            Response dict
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "OpenRouter API key not set"
            }

        model = model or self.current_model

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "response": data["choices"][0]["message"]["content"],
                            "model": model,
                            "usage": data.get("usage", {})
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"OpenRouter error: {error_text}"
                        }

        except Exception as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}"
            }

    def set_model(self, model: str):
        """Set current model."""
        self.current_model = model

    def get_available_models(self) -> List[str]:
        """Get list of popular available models."""
        return [
            "openai/gpt-4",
            "openai/gpt-3.5-turbo",
            "anthropic/claude-3-opus",
            "anthropic/claude-3-sonnet",
            "meta-llama/llama-3-70b",
            "google/gemini-pro"
        ]

    async def get_all_models(self) -> Dict[str, Any]:
        """
        Get full list of all available models from OpenRouter API.

        Returns:
            Dict with success status and list of models
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "OpenRouter API key not set",
                "models": []
            }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://openrouter.ai/api/v1/models",
                    headers={
                        "Authorization": f"Bearer {self.api_key}"
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get("data", [])

                        # Extract model IDs and names
                        model_list = [
                            {
                                "id": model.get("id"),
                                "name": model.get("name", model.get("id")),
                                "context_length": model.get("context_length", 0)
                            }
                            for model in models
                        ]

                        return {
                            "success": True,
                            "models": model_list,
                            "count": len(model_list)
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"API error: {response.status}",
                            "models": []
                        }

        except Exception as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}",
                "models": []
            }
