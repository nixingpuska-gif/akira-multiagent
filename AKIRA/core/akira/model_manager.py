"""
AKIRA Model Manager
Manages interactions with different AI models (GPT, Claude, Local)
"""

import os
import json
from typing import Dict, Any, Optional, List
import openai
from config.prompts import PROMPT_MAP
from core.akira.openrouter_client import OpenRouterClient
from core.akira.model_presets import ModelPresets


class ModelManager:
    """
    Manages multiple AI models and routes requests appropriately.
    """

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        # Load API key from config
        presets = ModelPresets()
        config_api_key = presets.get_api_key()

        # Use config key if available, otherwise use env variable
        openrouter_key = config_api_key or os.getenv("OPENROUTER_API_KEY")

        self.openrouter_client = OpenRouterClient(api_key=openrouter_key)
        self.current_provider = "openai"  # Default: openai, openrouter, claude
        self.models_available = self._check_available_models()

    def _check_available_models(self) -> Dict[str, bool]:
        """Check which models are available."""
        available = {
            "gpt-4": bool(self.openai_api_key),
            "gpt-3.5": bool(self.openai_api_key),
            "claude": True,  # Available through terminal
            "local": False  # TODO: Check for local models
        }
        return available

    async def query_model(
        self,
        model_type: str,
        user_message: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Query a specific AI model.

        Args:
            model_type: Type of model (gpt-4, gpt-3.5, claude, local)
            user_message: User's message/request
            system_prompt: Optional system prompt override
            temperature: Model temperature

        Returns:
            Response from the model
        """
        if not self.models_available.get(model_type):
            return {
                "success": False,
                "error": f"Model {model_type} not available"
            }

        # Get appropriate system prompt
        if system_prompt is None:
            system_prompt = PROMPT_MAP.get(model_type, PROMPT_MAP["default"])

        # Check if using OpenRouter
        if self.current_provider == "openrouter":
            return await self._query_openrouter(user_message, system_prompt, temperature)

        try:
            if model_type in ["gpt-4", "gpt-3.5"]:
                return await self._query_openai(model_type, user_message, system_prompt, temperature)
            elif model_type == "claude":
                return await self._query_claude_terminal(user_message)
            elif model_type == "local":
                return await self._query_local_model(user_message, system_prompt)
            else:
                return {"success": False, "error": "Unknown model type"}

        except Exception as e:
            return {
                "success": False,
                "error": f"Error querying {model_type}: {str(e)}"
            }

    async def _query_openai(
        self,
        model: str,
        user_message: str,
        system_prompt: str,
        temperature: float
    ) -> Dict[str, Any]:
        """Query OpenAI models (GPT-4, GPT-3.5)."""
        openai.api_key = self.openai_api_key

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature
        )

        return {
            "success": True,
            "response": response.choices[0].message.content,
            "model": model,
            "usage": response.usage
        }

    async def _query_claude_terminal(self, user_message: str) -> Dict[str, Any]:
        """Query Claude through terminal (claude command)."""
        import subprocess

        try:
            # Run claude command
            result = subprocess.run(
                ["claude", user_message],
                capture_output=True,
                text=True,
                timeout=300
            )

            return {
                "success": result.returncode == 0,
                "response": result.stdout,
                "model": "claude",
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Claude terminal error: {str(e)}"
            }

    async def _query_local_model(
        self,
        user_message: str,
        system_prompt: str
    ) -> Dict[str, Any]:
        """Query local model (placeholder for future implementation)."""
        return {
            "success": False,
            "error": "Local models not yet implemented"
        }

    def get_best_model_for_task(self, task_type: str) -> str:
        """
        Select best available model for a specific task type.

        Args:
            task_type: Type of task (code, analysis, creative, etc.)

        Returns:
            Best model name for the task
        """
        task_preferences = {
            "code": ["gpt-4", "claude", "gpt-3.5"],
            "analysis": ["gpt-4", "claude", "gpt-3.5"],
            "creative": ["gpt-4", "gpt-3.5", "local"],
            "business": ["gpt-4", "gpt-3.5"],
            "default": ["gpt-4", "claude", "gpt-3.5"]
        }

        preferences = task_preferences.get(task_type, task_preferences["default"])

        # Return first available model from preferences
        for model in preferences:
            if self.models_available.get(model):
                return model

        return "gpt-3.5"  # Fallback

    def switch_provider(self, provider: str, model: Optional[str] = None):
        """
        Switch AI provider (openai, openrouter, claude).

        Args:
            provider: Provider name
            model: Optional specific model for OpenRouter
        """
        self.current_provider = provider
        if provider == "openrouter" and model:
            self.openrouter_client.set_model(model)

    async def _query_openrouter(
        self,
        user_message: str,
        system_prompt: str,
        temperature: float
    ) -> Dict[str, Any]:
        """Query through OpenRouter."""
        return await self.openrouter_client.query(
            prompt=user_message,
            system_prompt=system_prompt,
            temperature=temperature
        )
