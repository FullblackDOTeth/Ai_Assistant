"""
AI Provider Manager for Head AI
Manages different AI providers and their configurations
"""

import os
from pathlib import Path
from typing import Dict, Optional, List
import json
import logging
from dotenv import load_dotenv
import openai
from datetime import datetime
from .api_key_manager import APIKeyManager

logger = logging.getLogger(__name__)

class AIProviderManager:
    def __init__(self):
        """Initialize AI Provider Manager"""
        self.api_key_manager = APIKeyManager()
        self.providers = {}
        self.active_provider = None
        self.config_dir = Path(__file__).parent.parent.parent / 'config'
        self.config_dir.mkdir(exist_ok=True)
        
        # Load configurations
        self._load_config()
        self._setup_providers()

    def _load_config(self):
        """Load provider configurations"""
        config_file = self.config_dir / 'ai_providers.json'
        if not config_file.exists():
            # Create default configuration
            default_config = {
                'providers': {
                    'openai': {
                        'enabled': True,
                        'models': ['gpt-4', 'gpt-3.5-turbo'],
                        'default_model': 'gpt-3.5-turbo',
                        'max_tokens': 2000,
                        'temperature': 0.7
                    }
                },
                'default_provider': 'openai'
            }
            config_file.write_text(json.dumps(default_config, indent=4))
            self.config = default_config
        else:
            self.config = json.loads(config_file.read_text())

    def _setup_providers(self):
        """Set up configured AI providers"""
        # Load environment variables
        load_dotenv()
        
        # Set up OpenAI if enabled
        if self.config['providers'].get('openai', {}).get('enabled', False):
            openai_key = self.api_key_manager.get_api_key('OPENAI_API_KEY')
            if openai_key:
                openai.api_key = openai_key
                self.providers['openai'] = self._create_openai_provider()
            else:
                logger.warning("OpenAI API key not found")

        # Set active provider
        default_provider = self.config.get('default_provider')
        if default_provider in self.providers:
            self.active_provider = self.providers[default_provider]

    def _create_openai_provider(self) -> Dict:
        """Create OpenAI provider configuration"""
        config = self.config['providers']['openai']
        return {
            'name': 'openai',
            'client': openai.Client(api_key=openai.api_key),
            'models': config['models'],
            'default_model': config['default_model'],
            'max_tokens': config['max_tokens'],
            'temperature': config['temperature']
        }

    async def generate_response(self, 
                              prompt: str, 
                              provider: str = None, 
                              **kwargs) -> Dict:
        """
        Generate response using specified or default provider
        
        Args:
            prompt: Input prompt
            provider: Provider name (optional)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dict containing response and metadata
        """
        provider = self.providers.get(provider or self.config['default_provider'])
        if not provider:
            raise ValueError("No valid AI provider available")

        try:
            if provider['name'] == 'openai':
                response = await self._generate_openai_response(prompt, **kwargs)
            else:
                raise ValueError(f"Unknown provider: {provider['name']}")

            return {
                'text': response['text'],
                'provider': provider['name'],
                'model': response['model'],
                'timestamp': datetime.now().isoformat(),
                'metadata': response.get('metadata', {})
            }

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise

    async def _generate_openai_response(self, prompt: str, **kwargs) -> Dict:
        """Generate response using OpenAI"""
        provider = self.providers['openai']
        
        # Prepare parameters
        params = {
            'model': kwargs.get('model', provider['default_model']),
            'max_tokens': kwargs.get('max_tokens', provider['max_tokens']),
            'temperature': kwargs.get('temperature', provider['temperature']),
            'messages': [{"role": "user", "content": prompt}]
        }

        # Generate response
        response = await provider['client'].chat.completions.create(**params)
        
        return {
            'text': response.choices[0].message.content,
            'model': params['model'],
            'metadata': {
                'finish_reason': response.choices[0].finish_reason,
                'usage': dict(response.usage)
            }
        }

    def list_providers(self) -> List[Dict]:
        """List all available providers and their status"""
        return [
            {
                'name': name,
                'enabled': True,
                'models': provider['models'],
                'default_model': provider['default_model'],
                'is_active': name == self.config['default_provider']
            }
            for name, provider in self.providers.items()
        ]

    def get_provider_config(self, provider_name: str) -> Optional[Dict]:
        """Get configuration for specific provider"""
        return self.config['providers'].get(provider_name)

    def update_provider_config(self, provider_name: str, config: Dict):
        """Update provider configuration"""
        if provider_name not in self.config['providers']:
            raise ValueError(f"Unknown provider: {provider_name}")
            
        self.config['providers'][provider_name].update(config)
        
        # Save updated config
        config_file = self.config_dir / 'ai_providers.json'
        config_file.write_text(json.dumps(self.config, indent=4))
        
        # Reload providers
        self._setup_providers()

    def set_default_provider(self, provider_name: str):
        """Set default AI provider"""
        if provider_name not in self.providers:
            raise ValueError(f"Provider not available: {provider_name}")
            
        self.config['default_provider'] = provider_name
        
        # Save updated config
        config_file = self.config_dir / 'ai_providers.json'
        config_file.write_text(json.dumps(self.config, indent=4))
        
        self.active_provider = self.providers[provider_name]

# Create singleton instance
ai_provider_manager = AIProviderManager()
