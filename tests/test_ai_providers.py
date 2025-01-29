"""
Test suite for AI Provider Manager
"""

import unittest
import asyncio
from pathlib import Path
import json
import os
from unittest.mock import patch, MagicMock
from src.ai_providers.provider_manager import AIProviderManager
from src.ai_providers.api_key_manager import APIKeyManager

class TestAIProviderManager(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        # Create test config directory
        self.test_config_dir = Path('test_config')
        self.test_config_dir.mkdir(exist_ok=True)
        
        # Create test environment file
        self.test_env_file = self.test_config_dir / '.env.test'
        self.test_env_file.write_text('''
        OPENAI_API_KEY=test_key_123
        '''.strip())
        
        # Mock environment variables
        self.env_patcher = patch.dict('os.environ', {
            'OPENAI_API_KEY': 'test_key_123'
        })
        self.env_patcher.start()
        
        # Initialize manager
        self.manager = AIProviderManager()

    def tearDown(self):
        """Clean up test environment"""
        # Remove test files
        if self.test_env_file.exists():
            self.test_env_file.unlink()
        if self.test_config_dir.exists():
            self.test_config_dir.rmdir()
            
        # Stop environment patcher
        self.env_patcher.stop()

    def test_initialization(self):
        """Test manager initialization"""
        self.assertIsNotNone(self.manager)
        self.assertIsInstance(self.manager.api_key_manager, APIKeyManager)
        self.assertIsInstance(self.manager.config, dict)
        self.assertIn('providers', self.manager.config)
        self.assertIn('default_provider', self.manager.config)

    def test_provider_configuration(self):
        """Test provider configuration loading"""
        openai_config = self.manager.get_provider_config('openai')
        self.assertIsNotNone(openai_config)
        self.assertIn('enabled', openai_config)
        self.assertIn('models', openai_config)
        self.assertIn('default_model', openai_config)

    def test_list_providers(self):
        """Test listing available providers"""
        providers = self.manager.list_providers()
        self.assertIsInstance(providers, list)
        if providers:  # If any providers are configured
            first_provider = providers[0]
            self.assertIn('name', first_provider)
            self.assertIn('enabled', first_provider)
            self.assertIn('models', first_provider)
            self.assertIn('is_active', first_provider)

    @patch('openai.Client')
    async def test_generate_response(self, mock_client):
        """Test response generation"""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(content="Test response"),
                finish_reason="stop"
            )
        ]
        mock_response.usage = {
            'prompt_tokens': 10,
            'completion_tokens': 20,
            'total_tokens': 30
        }
        
        # Setup mock client
        mock_client.return_value.chat.completions.create.return_value = mock_response
        
        # Test response generation
        response = await self.manager.generate_response(
            "Test prompt",
            provider="openai"
        )
        
        self.assertIsInstance(response, dict)
        self.assertIn('text', response)
        self.assertIn('provider', response)
        self.assertIn('model', response)
        self.assertIn('timestamp', response)
        self.assertIn('metadata', response)
        
        # Verify response content
        self.assertEqual(response['text'], "Test response")
        self.assertEqual(response['provider'], "openai")
        self.assertIn('usage', response['metadata'])

    def test_update_provider_config(self):
        """Test updating provider configuration"""
        new_config = {
            'temperature': 0.8,
            'max_tokens': 1500
        }
        
        self.manager.update_provider_config('openai', new_config)
        
        # Verify changes
        updated_config = self.manager.get_provider_config('openai')
        self.assertEqual(updated_config['temperature'], 0.8)
        self.assertEqual(updated_config['max_tokens'], 1500)

    def test_set_default_provider(self):
        """Test setting default provider"""
        # Ensure OpenAI is available
        if 'openai' in self.manager.providers:
            self.manager.set_default_provider('openai')
            self.assertEqual(self.manager.config['default_provider'], 'openai')
            self.assertIs(self.manager.active_provider, self.manager.providers['openai'])

def async_test(coro):
    """Decorator for async test methods"""
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro(*args, **kwargs))
    return wrapper

if __name__ == '__main__':
    unittest.main()
