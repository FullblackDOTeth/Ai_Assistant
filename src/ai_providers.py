client = OpenAI(api_key=self.api_key)  # Python"""
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

load_dotenv()

class AIProvider:
    def __init__(self):
        # Initialize API keys
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.google_key = os.getenv('GOOGLE_API_KEY')
        self.huggingface_key = os.getenv('HUGGINGFACE_API_KEY')
        self.cohere_key = os.getenv('COHERE_API_KEY')
        
        # Initialize clients
        self._init_openai()
        self._init_anthropic()
        self._init_google()
        self._init_huggingface()
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        if self.openai_key:
            openai.api_key = self.openai_key
            self.openai_available = True
        else:
            print("OpenAI API key not found")
            self.openai_available = False
    
    def _init_anthropic(self):
        """Initialize Anthropic client"""
        if self.anthropic_key:
            self.claude = anthropic.Anthropic(api_key=self.anthropic_key)
            self.anthropic_available = True
        else:
            print("Anthropic API key not found")
            self.anthropic_available = False
    
    def _init_google(self):
        """Initialize Google's Gemini client"""
        if self.google_key:
            genai.configure(api_key=self.google_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            self.google_available = True
        else:
            print("Google API key not found")
            self.google_available = False
    
    def _init_huggingface(self):
        """Initialize Hugging Face client"""
        if self.huggingface_key:
            self.hf_client = InferenceClient(token=self.huggingface_key)
            self.huggingface_available = True
        else:
            print("Hugging Face API key not found")
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
                # Try providers in order of preference
                providers = ['openai', 'anthropic', 'google', 'huggingface']
                for p in providers:
                    if hasattr(self, f'{p}_available') and getattr(self, f'{p}_available'):
                        provider = p
                        break
            
            if provider == 'openai' and self.openai_available:
                return await self._get_openai_response(message, context)
            
            elif provider == 'anthropic' and self.anthropic_available:
                return await self._get_anthropic_response(message, context)
            
            elif provider == 'google' and self.google_available:
                return await self._get_google_response(message, context)
            
            elif provider == 'huggingface' and self.huggingface_available:
                return await self._get_huggingface_response(message, context)
            
            else:
                return {
                    'error': 'No AI provider available',
                    'message': 'Please configure at least one AI provider API key'
                }
        
        except Exception as e:
            return {
                'error': str(e),
                'message': 'Error getting AI response'
            }
    
    async def _get_openai_response(self, message: str, context: list = None) -> Dict[str, Any]:
        """Get response from OpenAI"""
        messages = [{"role": "system", "content": "You are a helpful AI assistant."}]
        if context:
            messages.extend(context)
        messages.append({"role": "user", "content": message})
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
        
        return {
            'provider': 'openai',
            'message': response.choices[0].message.content,
            'model': 'gpt-3.5-turbo'
        }
    
    async def _get_anthropic_response(self, message: str, context: list = None) -> Dict[str, Any]:
        """Get response from Anthropic's Claude"""
        system_prompt = "You are Claude, a helpful AI assistant."
        full_message = system_prompt
        
        if context:
            for msg in context:
                full_message += f"\n\n{msg['role']}: {msg['content']}"
        
        full_message += f"\n\nHuman: {message}\n\nAssistant:"
        
        response = await self.claude.messages.create(
            model="claude-2",
            max_tokens=150,
            messages=[{"role": "user", "content": full_message}]
        )
        
        return {
            'provider': 'anthropic',
            'message': response.content[0].text,
            'model': 'claude-2'
        }
    
    async def _get_google_response(self, message: str, context: list = None) -> Dict[str, Any]:
        """Get response from Google's Gemini"""
        chat = self.gemini_model.start_chat(history=[])
        if context:
            for msg in context:
                chat.send_message(msg['content'])
        
        response = chat.send_message(message)
        
        return {
            'provider': 'google',
            'message': response.text,
            'model': 'gemini-pro'
        }
    
    async def _get_huggingface_response(self, message: str, context: list = None) -> Dict[str, Any]:
        """Get response from Hugging Face model"""
        # Using a default model, but you can specify different ones
        model = "microsoft/DialoGPT-medium"
        
        inputs = message
        if context:
            inputs = " ".join([msg['content'] for msg in context]) + " " + message
        
        response = self.hf_client.text_generation(
            inputs,
            model=model,
            max_new_tokens=150
        )
        
        return {
            'provider': 'huggingface',
            'message': response[0]['generated_text'],
            'model': model
        }
