"""
Command Line Interface for managing AI providers
"""

import asyncio
import argparse
import json
from pathlib import Path
from ai_providers.provider_manager import ai_provider_manager
from ai_providers.api_key_manager import api_key_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AICLI:
    def __init__(self):
        self.provider_manager = ai_provider_manager
        self.api_manager = api_key_manager

    def list_providers(self):
        """List all available AI providers"""
        providers = self.provider_manager.list_providers()
        print("\nAvailable AI Providers:")
        print("=" * 50)
        for provider in providers:
            status = "✓ ACTIVE" if provider['is_active'] else "INACTIVE"
            print(f"\n{provider['name'].upper()} [{status}]")
            print("-" * 30)
            print(f"Models: {', '.join(provider['models'])}")
            print(f"Default Model: {provider['default_model']}")

    def show_api_keys(self):
        """Show API key status"""
        print("\nAPI Key Status:")
        print("=" * 50)
        for provider in self.api_manager.PROVIDERS.values():
            key = self.api_manager.get_api_key(provider.env_var)
            status = "✓ SET" if key else "NOT SET"
            print(f"\n{provider.name}")
            print("-" * 30)
            print(f"Status: {status}")
            if provider.url:
                print(f"Get key at: {provider.url}")
            if provider.description:
                print(f"Note: {provider.description}")

    async def test_provider(self, provider_name: str, prompt: str):
        """Test an AI provider with a prompt"""
        try:
            print(f"\nTesting {provider_name.upper()}...")
            print("-" * 50)
            print(f"Prompt: {prompt}")
            print("\nGenerating response...")
            
            response = await self.provider_manager.generate_response(
                prompt, 
                provider=provider_name
            )
            
            print("\nResponse:")
            print("-" * 50)
            print(response['text'])
            print("\nMetadata:")
            print("-" * 50)
            print(json.dumps(response['metadata'], indent=2))
            
        except Exception as e:
            logger.error(f"Error testing provider: {str(e)}")

    def update_config(self, provider: str, model: str = None, temperature: float = None):
        """Update provider configuration"""
        try:
            config = {}
            if model:
                config['default_model'] = model
            if temperature is not None:
                config['temperature'] = temperature
                
            if config:
                self.provider_manager.update_provider_config(provider, config)
                print(f"\nUpdated {provider} configuration:")
                print(json.dumps(config, indent=2))
        except Exception as e:
            logger.error(f"Error updating config: {str(e)}")

async def main():
    parser = argparse.ArgumentParser(description='AI Provider Management CLI')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # List providers command
    subparsers.add_parser('list', help='List available AI providers')

    # Show API keys command
    subparsers.add_parser('keys', help='Show API key status')

    # Test provider command
    test_parser = subparsers.add_parser('test', help='Test an AI provider')
    test_parser.add_argument('provider', help='Provider name (e.g., openai)')
    test_parser.add_argument('prompt', help='Test prompt')

    # Update config command
    config_parser = subparsers.add_parser('config', help='Update provider configuration')
    config_parser.add_argument('provider', help='Provider name (e.g., openai)')
    config_parser.add_argument('--model', help='Set default model')
    config_parser.add_argument('--temperature', type=float, help='Set temperature (0.0-1.0)')

    args = parser.parse_args()
    cli = AICLI()

    if args.command == 'list':
        cli.list_providers()
    elif args.command == 'keys':
        cli.show_api_keys()
    elif args.command == 'test':
        await cli.test_provider(args.provider, args.prompt)
    elif args.command == 'config':
        cli.update_config(args.provider, args.model, args.temperature)
    else:
        parser.print_help()

if __name__ == '__main__':
    asyncio.run(main())
