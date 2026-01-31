"""
AKIRA 4.0 Key Management System (Key Farm)
Secure storage and management of 1000+ API keys.
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging
from cryptography.fernet import Fernet
import redis

logger = logging.getLogger(__name__)

@dataclass
class APIKey:
    provider: str
    key: str
    added_date: str
    expiry_date: Optional[str] = None
    is_active: bool = True
    rate_limit: int = 0
    usage_count: int = 0
    last_used: Optional[str] = None
    notes: str = ""

class KeyManager:
    """
    Manages API keys with encryption, rotation, and health tracking.
    """
    
    def __init__(self, vault_dir: str = "/home/ubuntu/akira_4_0/vault", redis_host: str = "localhost"):
        self.vault_dir = vault_dir
        self.redis_client = redis.Redis(host=redis_host, decode_responses=True)
        self.keys_file = os.path.join(vault_dir, "keys.json")
        self.metadata_file = os.path.join(vault_dir, "key_metadata.json")
        
        # Initialize vault directory
        os.makedirs(vault_dir, exist_ok=True)
        
        # Load or create encryption key
        self.cipher_suite = self._get_or_create_cipher()
        
        # Load existing keys
        self.keys: Dict[str, List[APIKey]] = self._load_keys()
        
        logger.info(f"Key Manager initialized with vault: {vault_dir}")
    
    def _get_or_create_cipher(self) -> Fernet:
        """Get or create encryption cipher for key storage."""
        key_file = os.path.join(self.vault_dir, ".cipher_key")
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Restrict permissions
        
        return Fernet(key)
    
    def _load_keys(self) -> Dict[str, List[APIKey]]:
        """Load keys from encrypted storage."""
        if not os.path.exists(self.keys_file):
            return {}
        
        try:
            with open(self.keys_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            keys_data = json.loads(decrypted_data)
            
            # Convert to APIKey objects
            keys = {}
            for provider, key_list in keys_data.items():
                keys[provider] = [APIKey(**k) for k in key_list]
            
            logger.info(f"Loaded {sum(len(v) for v in keys.values())} keys from vault")
            return keys
            
        except Exception as e:
            logger.error(f"Failed to load keys: {str(e)}")
            return {}
    
    def _save_keys(self) -> bool:
        """Save keys to encrypted storage."""
        try:
            keys_data = {
                provider: [asdict(k) for k in key_list]
                for provider, key_list in self.keys.items()
            }
            
            json_data = json.dumps(keys_data)
            encrypted_data = self.cipher_suite.encrypt(json_data.encode())
            
            with open(self.keys_file, 'wb') as f:
                f.write(encrypted_data)
            
            os.chmod(self.keys_file, 0o600)  # Restrict permissions
            logger.info("Keys saved to vault")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save keys: {str(e)}")
            return False
    
    def add_key(self, provider: str, key: str, expiry_days: Optional[int] = None, notes: str = "") -> bool:
        """
        Add a new API key to the vault.
        """
        try:
            if provider not in self.keys:
                self.keys[provider] = []
            
            # Calculate expiry date if provided
            expiry_date = None
            if expiry_days:
                expiry_date = (datetime.now() + timedelta(days=expiry_days)).isoformat()
            
            api_key = APIKey(
                provider=provider,
                key=key,
                added_date=datetime.now().isoformat(),
                expiry_date=expiry_date,
                notes=notes
            )
            
            self.keys[provider].append(api_key)
            self._save_keys()
            
            # Update Redis cache
            self.redis_client.hset(f"key_count:{provider}", "total", len(self.keys[provider]))
            
            logger.info(f"Added new key for provider: {provider}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add key: {str(e)}")
            return False
    
    def get_active_key(self, provider: str) -> Optional[str]:
        """
        Get the next active key for a provider.
        Rotates through keys, skipping expired or inactive ones.
        """
        if provider not in self.keys:
            logger.warning(f"No keys found for provider: {provider}")
            return None
        
        now = datetime.now()
        
        for api_key in self.keys[provider]:
            # Check if key is active
            if not api_key.is_active:
                continue
            
            # Check if key is expired
            if api_key.expiry_date:
                expiry = datetime.fromisoformat(api_key.expiry_date)
                if now > expiry:
                    api_key.is_active = False
                    continue
            
            # Update last used timestamp
            api_key.last_used = datetime.now().isoformat()
            api_key.usage_count += 1
            self._save_keys()
            
            logger.debug(f"Returning active key for {provider} (usage: {api_key.usage_count})")
            return api_key.key
        
        logger.warning(f"No active keys available for provider: {provider}")
        return None
    
    def mark_key_as_failed(self, provider: str, key: str) -> bool:
        """
        Mark a key as failed (rate limited or invalid).
        """
        if provider not in self.keys:
            return False
        
        for api_key in self.keys[provider]:
            if api_key.key == key:
                api_key.is_active = False
                self._save_keys()
                logger.warning(f"Marked key as failed for {provider}")
                return True
        
        return False
    
    def get_provider_status(self, provider: str) -> Dict:
        """Get status of all keys for a provider."""
        if provider not in self.keys:
            return {"provider": provider, "total_keys": 0, "active_keys": 0}
        
        keys = self.keys[provider]
        now = datetime.now()
        
        active_count = 0
        expired_count = 0
        
        for api_key in keys:
            if api_key.expiry_date:
                expiry = datetime.fromisoformat(api_key.expiry_date)
                if now > expiry:
                    expired_count += 1
                    continue
            
            if api_key.is_active:
                active_count += 1
        
        return {
            "provider": provider,
            "total_keys": len(keys),
            "active_keys": active_count,
            "expired_keys": expired_count,
            "failed_keys": len(keys) - active_count - expired_count
        }
    
    def get_all_status(self) -> Dict[str, Dict]:
        """Get status of all providers."""
        return {
            provider: self.get_provider_status(provider)
            for provider in self.keys.keys()
        }
    
    def export_key_list(self) -> List[Dict]:
        """Export a list of all keys (for backup or audit)."""
        key_list = []
        for provider, keys in self.keys.items():
            for api_key in keys:
                key_list.append({
                    "provider": provider,
                    "added_date": api_key.added_date,
                    "expiry_date": api_key.expiry_date,
                    "is_active": api_key.is_active,
                    "usage_count": api_key.usage_count,
                    "notes": api_key.notes,
                    # Note: Don't export the actual key value
                    "key_preview": api_key.key[:10] + "***"
                })
        return key_list
    
    def cleanup_expired_keys(self) -> int:
        """Remove expired keys from the vault."""
        now = datetime.now()
        removed_count = 0
        
        for provider in list(self.keys.keys()):
            original_count = len(self.keys[provider])
            
            self.keys[provider] = [
                k for k in self.keys[provider]
                if not k.expiry_date or datetime.fromisoformat(k.expiry_date) > now
            ]
            
            removed_count += original_count - len(self.keys[provider])
        
        if removed_count > 0:
            self._save_keys()
            logger.info(f"Removed {removed_count} expired keys")
        
        return removed_count

# Example usage
if __name__ == "__main__":
    manager = KeyManager()
    
    # Add some test keys
    manager.add_key("OpenAI", "sk-test-123", expiry_days=90, notes="Primary key")
    manager.add_key("OpenAI", "sk-test-456", expiry_days=180, notes="Backup key")
    manager.add_key("Anthropic", "sk-ant-test-789", notes="Claude API key")
    
    # Get status
    print("Provider Status:")
    print(json.dumps(manager.get_all_status(), indent=2))
    
    # Get active key
    active_key = manager.get_active_key("OpenAI")
    print(f"\nActive OpenAI key: {active_key[:10]}***")
    
    # Export key list
    print("\nKey List (for backup):")
    print(json.dumps(manager.export_key_list(), indent=2))
