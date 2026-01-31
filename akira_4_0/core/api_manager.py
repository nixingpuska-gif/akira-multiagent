"""
AKIRA 4.0 API Manager
Intelligent fallback chain with health checks and SOS mechanism.
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import redis
import logging

logger = logging.getLogger(__name__)

class ProviderStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNKNOWN = "unknown"

@dataclass
class APIProvider:
    name: str
    api_key: str
    priority: int
    health_check_url: str
    rate_limit: int
    timeout: int = 30

class APIManager:
    """
    Manages multiple API providers with intelligent fallback chain.
    """
    
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.providers: Dict[str, APIProvider] = {}
        self.provider_status: Dict[str, ProviderStatus] = {}
        self.fallback_chain: List[str] = []
        self.health_check_interval = 300  # 5 minutes
        self.last_health_check = {}
        
    def add_provider(self, provider: APIProvider) -> None:
        """Add a new API provider to the system."""
        self.providers[provider.name] = provider
        self.provider_status[provider.name] = ProviderStatus.UNKNOWN
        self.last_health_check[provider.name] = 0
        self._rebuild_fallback_chain()
        logger.info(f"Added provider: {provider.name} (priority: {provider.priority})")
    
    def remove_provider(self, provider_name: str) -> None:
        """Remove an API provider."""
        if provider_name in self.providers:
            del self.providers[provider_name]
            del self.provider_status[provider_name]
            self._rebuild_fallback_chain()
            logger.info(f"Removed provider: {provider_name}")
    
    def _rebuild_fallback_chain(self) -> None:
        """Rebuild the fallback chain based on provider priorities."""
        sorted_providers = sorted(
            self.providers.items(),
            key=lambda x: x[1].priority
        )
        self.fallback_chain = [name for name, _ in sorted_providers]
        logger.debug(f"Fallback chain rebuilt: {self.fallback_chain}")
    
    async def health_check(self, provider_name: str) -> ProviderStatus:
        """
        Perform a lightweight health check on a provider.
        Returns the provider's status.
        """
        if provider_name not in self.providers:
            return ProviderStatus.UNKNOWN
        
        # Check cache first
        cache_key = f"health_check:{provider_name}"
        cached_status = self.redis_client.get(cache_key)
        
        if cached_status:
            self.provider_status[provider_name] = ProviderStatus(cached_status)
            return self.provider_status[provider_name]
        
        provider = self.providers[provider_name]
        
        try:
            # Perform a minimal health check (e.g., token count estimation for LLMs)
            # This is provider-specific
            status = await self._check_provider_health(provider)
            
            # Cache the result
            self.redis_client.setex(cache_key, self.health_check_interval, status.value)
            self.provider_status[provider_name] = status
            self.last_health_check[provider_name] = time.time()
            
            logger.debug(f"Health check for {provider_name}: {status.value}")
            return status
            
        except Exception as e:
            logger.error(f"Health check failed for {provider_name}: {str(e)}")
            self.provider_status[provider_name] = ProviderStatus.FAILED
            return ProviderStatus.FAILED
    
    async def _check_provider_health(self, provider: APIProvider) -> ProviderStatus:
        """
        Perform provider-specific health check.
        This is a placeholder; actual implementation depends on the provider.
        """
        # For now, assume all providers are healthy
        # In production, this would make actual API calls
        return ProviderStatus.HEALTHY
    
    async def get_next_available_provider(self) -> Optional[str]:
        """
        Get the next available provider from the fallback chain.
        Performs health checks and returns the first healthy provider.
        """
        for provider_name in self.fallback_chain:
            status = await self.health_check(provider_name)
            
            if status == ProviderStatus.HEALTHY:
                logger.info(f"Selected provider: {provider_name}")
                return provider_name
            elif status == ProviderStatus.DEGRADED:
                # Try degraded provider if no healthy ones available
                logger.warning(f"Using degraded provider: {provider_name}")
                return provider_name
        
        # All providers failed
        logger.critical("All API providers are unavailable!")
        return None
    
    async def execute_with_fallback(self, task_func, *args, **kwargs):
        """
        Execute a task with automatic fallback chain.
        If the primary provider fails, automatically tries the next one.
        """
        for provider_name in self.fallback_chain:
            try:
                logger.info(f"Attempting task with provider: {provider_name}")
                provider = self.providers[provider_name]
                
                # Inject provider into kwargs
                kwargs['provider'] = provider
                
                result = await task_func(*args, **kwargs)
                logger.info(f"Task succeeded with provider: {provider_name}")
                return result
                
            except Exception as e:
                logger.warning(f"Task failed with {provider_name}: {str(e)}")
                # Mark provider as degraded
                self.provider_status[provider_name] = ProviderStatus.DEGRADED
                continue
        
        # All providers failed
        logger.critical("Task failed with all providers. Triggering SOS.")
        await self.trigger_sos()
        return None
    
    async def trigger_sos(self) -> None:
        """
        Trigger SOS mechanism when all providers are exhausted.
        Sends emergency notification to user's Telegram account.
        """
        sos_message = self._generate_sos_message()
        logger.critical(f"SOS triggered: {sos_message}")
        
        # Store SOS in Redis for Telegram client to pick up
        self.redis_client.lpush("sos_queue", json.dumps({
            "timestamp": time.time(),
            "message": sos_message,
            "provider_status": {k: v.value for k, v in self.provider_status.items()}
        }))
    
    def _generate_sos_message(self) -> str:
        """Generate SOS message with provider status."""
        status_report = "\n".join([
            f"- {name}: {status.value}"
            for name, status in self.provider_status.items()
        ])
        
        return (
            f"🚨 CRITICAL: All API providers are down!\n\n"
            f"Provider Status:\n{status_report}\n\n"
            f"Please add new API keys immediately.\n"
            f"Respond with: /addkey <provider> <key>"
        )
    
    def get_status_report(self) -> Dict:
        """Get a complete status report of all providers."""
        return {
            "timestamp": time.time(),
            "providers": {
                name: {
                    "status": self.provider_status[name].value,
                    "priority": self.providers[name].priority,
                    "last_check": self.last_health_check.get(name, 0)
                }
                for name in self.providers.keys()
            },
            "fallback_chain": self.fallback_chain
        }

# Example usage
if __name__ == "__main__":
    manager = APIManager()
    
    # Add providers
    manager.add_provider(APIProvider(
        name="OpenAI",
        api_key="sk-...",
        priority=1,
        health_check_url="https://api.openai.com/v1/models",
        rate_limit=3500
    ))
    
    manager.add_provider(APIProvider(
        name="Anthropic",
        api_key="sk-ant-...",
        priority=2,
        health_check_url="https://api.anthropic.com/v1/models",
        rate_limit=1000
    ))
    
    manager.add_provider(APIProvider(
        name="OpenRouter",
        api_key="sk-or-...",
        priority=999,  # Last resort
        health_check_url="https://openrouter.ai/api/v1/models",
        rate_limit=500
    ))
    
    print("API Manager initialized with providers:")
    print(json.dumps(manager.get_status_report(), indent=2))
