"""
API Key Manager - Securely manages API keys for AI providers
"""
from typing import Dict, Optional, List
import os
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass
from functools import lru_cache
import keyring
import json

@dataclass
class APIKeyConfig:
    """Configuration for an API key"""
    name: str
    env_var: str
    required: bool = False
    url: str = ""
    description: str = ""

class APIKeyManager:
    """Manages API keys for different providers"""
    
    # Define known providers and their configurations
    PROVIDERS = {
        'openai': APIKeyConfig(
            name='OpenAI',
            env_var='OPENAI_API_KEY',
            url='https://platform.openai.com/account/api-keys',
            description='Required for OpenAI GPT models'
        ),
        'anthropic': APIKeyConfig(
            name='Anthropic',
            env_var='ANTHROPIC_API_KEY',
            url='https://console.anthropic.com/account/keys',
            description='Required for Claude models'
        ),
        'google': APIKeyConfig(
            name='Google',
            env_var='GOOGLE_API_KEY',
            url='https://makersuite.google.com/app/apikey',
            description='Required for Gemini models'
        ),
        'huggingface': APIKeyConfig(
            name='Hugging Face',
            env_var='HUGGINGFACE_API_KEY',
            url='https://huggingface.co/settings/tokens',
            description='Required for Hugging Face models'
        ),
        'cohere': APIKeyConfig(
            name='Cohere',
            env_var='COHERE_API_KEY',
            url='https://dashboard.cohere.ai/api-keys',
            description='Required for Cohere models'
        )
    }

    def __init__(self):
        """Initialize the API key manager"""
        self.load_env()
        self._api_keys: Dict[str, Optional[str]] = {}
        self._available_providers: Dict[str, bool] = {}
        self._load_api_keys()

    @staticmethod
    def load_env() -> None:
        """Load environment variables from .env file"""
        env_path = Path('.env')
        if env_path.exists():
            load_dotenv(env_path)

    def _load_api_keys(self) -> None:
        """Load API keys from environment variables and system keyring"""
        for provider, config in self.PROVIDERS.items():
            # Try to get key from environment
            key = os.getenv(config.env_var)
            
            # If not in environment, try system keyring
            if not key:
                try:
                    key = keyring.get_password("headai", config.env_var)
                except Exception:
                    key = None
            
            self._api_keys[provider] = key
            self._available_providers[provider] = bool(key)

    def get_key(self, provider: str) -> Optional[str]:
        """
        Get API key for a provider
        
        Args:
            provider: Provider name (e.g., 'openai', 'anthropic')
            
        Returns:
            API key if available, None otherwise
        """
        return self._api_keys.get(provider)

    def set_key(self, provider: str, key: str, save_to_keyring: bool = True) -> None:
        """
        Set API key for a provider
        
        Args:
            provider: Provider name
            key: API key
            save_to_keyring: Whether to save to system keyring
        """
        if provider not in self.PROVIDERS:
            raise ValueError(f"Unknown provider: {provider}")
        
        self._api_keys[provider] = key
        self._available_providers[provider] = bool(key)
        
        if save_to_keyring:
            try:
                keyring.set_password("headai", self.PROVIDERS[provider].env_var, key)
            except Exception as e:
                print(f"Warning: Could not save to keyring: {e}")

    def is_available(self, provider: str) -> bool:
        """Check if a provider is available (has valid API key)"""
        return self._available_providers.get(provider, False)

    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return [p for p, available in self._available_providers.items() if available]

    @property
    def provider_configs(self) -> Dict[str, APIKeyConfig]:
        """Get provider configurations"""
        return self.PROVIDERS

    def get_provider_info(self, provider: str) -> Dict:
        """
        Get information about a provider
        
        Returns:
            Dictionary with provider information including:
            - name: Provider name
            - available: Whether provider is available
            - url: URL for getting API key
            - description: Provider description
        """
        config = self.PROVIDERS.get(provider)
        if not config:
            raise ValueError(f"Unknown provider: {provider}")
            
        return {
            "name": config.name,
            "available": self.is_available(provider),
            "url": config.url,
            "description": config.description
        }

    def to_json(self) -> str:
        """Convert provider status to JSON"""
        status = {
            provider: {
                "name": config.name,
                "available": self.is_available(provider),
                "url": config.url,
                "description": config.description
            }
            for provider, config in self.PROVIDERS.items()
        }
        return json.dumps(status, indent=2)

# Global instance
api_key_manager = APIKeyManager()
