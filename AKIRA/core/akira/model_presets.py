"""
Model Presets Loader
Loads preset models from configuration
"""

import yaml
import os
from typing import Dict, Any, Optional


class ModelPresets:
    """Manages preset models configuration."""

    def __init__(self, config_path: str = "config/models.yaml"):
        self.config_path = config_path
        self.presets: Dict[int, Dict[str, str]] = {}
        self.api_key: Optional[str] = None
        self.load_config()

    def load_config(self):
        """Load presets from YAML config."""
        if not os.path.exists(self.config_path):
            return

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            self.api_key = config.get('openrouter_api_key')
            self.telegram_token = config.get('telegram_bot_token')
            self.presets = config.get('preset_models', {})
        except Exception as e:
            print(f"Error loading model presets: {e}")

    def get_preset(self, number: int) -> Optional[Dict[str, str]]:
        """Get preset by number (1-10)."""
        return self.presets.get(number)

    def get_all_presets(self) -> Dict[int, Dict[str, str]]:
        """Get all presets."""
        return self.presets

    def get_api_key(self) -> Optional[str]:
        """Get OpenRouter API key from config."""
        return self.api_key

    def get_telegram_token(self) -> Optional[str]:
        """Get Telegram bot token from config."""
        return self.telegram_token
