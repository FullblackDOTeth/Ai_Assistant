"""
AI Providers Module - Handles different AI API integrations
"""
import os
from typing import Dict, Any
import openai
import anthropic
import google.generativeai as genai
from huggingface_hub import InferenceClient
import requests
from dotenv import load_dotenv
from .ai_providers.api_key_manager import api_key_manager

class AIProvider:
    def __init__(self):
        """Initialize AI provider with available services"""
        self._init_providers()
    
    def _init_providers(self):
        """Initialize all available AI providers"""
        # OpenAI
        if api_key_manager.is_available('openai'):
            openai.api_key = api_key_manager.get_key('openai')
            self.openai_available = True
        else:
            self.openai_available = False
        
        # Anthropic
        if api_key_manager.is_available('anthropic'):
            self.claude = anthropic.Anthropic(api_key=api_key_manager.get_key('anthropic'))
            self.anthropic_available = True
        else:
            self.anthropic_available = False
        
        # Google
        if api_key_manager.is_available('google'):
            genai.configure(api_key=api_key_manager.get_key('google'))
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            self.google_available = True
        else:
            self.google_available = False
        
        # Hugging Face
        if api_key_manager.is_available('huggingface'):
            self.hf_client = InferenceClient(token=api_key_manager.get_key('huggingface'))
            self.huggingface_available = True
        else:
            self.huggingface_available = False
    
    async def get_response(self, message: str, provider: str = 'auto', context: list = None) -> Dict[str, Any]:
        """
        Get response from specified AI provider
        
        Args:
            message: User message
            provider: AI provider to use ('openai', 'anthropic', 'google', 'huggingface', or 'auto')
            context: Previous conversation context
        
        Returns:
            Dictionary containing response and metadata
        """
        try:
            if provider == 'auto':
                # Get available providers in order of preference
                available = api_key_manager.get_available_providers()
                if not available:
                    return {
                        'error': True,
                        'message': 'No AI providers available. Please configure at least one provider.',
                        'provider_info': api_key_manager.to_json()
                    }
                provider = available[0]
            
            if provider == 'openai' and self.openai_available:
                return await self._get_openai_response(message, context)
            
            elif provider == 'anthropic' and self.anthropic_available:
                return await self._get_anthropic_response(message, context)
            
            elif provider == 'google' and self.google_available:
                return await self._get_google_response(message, context)
            
            elif provider == 'huggingface' and self.huggingface_available:
                return await self._get_huggingface_response(message, context)
            
            else:
                provider_info = api_key_manager.get_provider_info(provider)
                return {
                    'error': True,
                    'message': f'Provider {provider} is not available',
                    'provider_info': provider_info
                }
                
        except Exception as e:
            return {
                'error': True,
                'message': f'Error getting response: {str(e)}',
                'provider': provider
            }

    async def _get_openai_response(self, message: str, context: list = None) -> Dict[str, Any]:
        """Get response from OpenAI"""
        try:
            response = await openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    *([{"role": "user", "content": c} for c in context] if context else []),
                    {"role": "user", "content": message}
                ]
            )
            return {
                'error': False,
                'message': response.choices[0].message.content,
                'provider': 'openai',
                'model': 'gpt-4'
            }
        except Exception as e:
            return {
                'error': True,
                'message': f'OpenAI error: {str(e)}',
                'provider': 'openai'
            }

    async def _get_anthropic_response(self, message: str, context: list = None) -> Dict[str, Any]:
        """Get response from Anthropic's Claude"""
        try:
            system_prompt = "You are Claude, a helpful AI assistant."
            messages = [{"role": "system", "content": system_prompt}]
            if context:
                messages.extend([{"role": "user", "content": c} for c in context])
            messages.append({"role": "user", "content": message})
            
            response = await self.claude.messages.create(
                model="claude-2.1",
                max_tokens=2000,
                messages=messages
            )
            return {
                'error': False,
                'message': response.content[0].text,
                'provider': 'anthropic',
                'model': 'claude-2.1'
            }
        except Exception as e:
            return {
                'error': True,
                'message': f'Anthropic error: {str(e)}',
                'provider': 'anthropic'
            }

    async def _get_google_response(self, message: str, context: list = None) -> Dict[str, Any]:
        """Get response from Google's Gemini"""
        try:
            chat = self.gemini_model.start_chat(history=[])
            if context:
                for c in context:
                    chat.send_message(c)
            response = chat.send_message(message)
            return {
                'error': False,
                'message': response.text,
                'provider': 'google',
                'model': 'gemini-pro'
            }
        except Exception as e:
            return {
                'error': True,
                'message': f'Google error: {str(e)}',
                'provider': 'google'
            }

    async def _get_huggingface_response(self, message: str, context: list = None) -> Dict[str, Any]:
        """Get response from Hugging Face"""
        try:
            # Use Hugging Face's endpoint
            response = self.hf_client.text_generation(
                prompt=message,
                model="meta-llama/Llama-2-70b-chat-hf",
                max_new_tokens=500
            )
            return {
                'error': False,
                'message': response,
                'provider': 'huggingface',
                'model': 'llama-2-70b'
            }
        except Exception as e:
            return {
                'error': True,
                'message': f'Hugging Face error: {str(e)}',
                'provider': 'huggingface'
            }
