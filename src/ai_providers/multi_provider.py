import os
from transformers import pipeline
import openai
import cohere
from anthropic import Anthropic

class MultiProvider:
    """Uses multiple AI providers for specialized responses"""
    
    def __init__(self):
        # Initialize Hugging Face for structured content
        self.hf_model = pipeline("text-generation", model="gpt2-large")
        
        # Initialize OpenAI for powerful content
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # Initialize Cohere for empathetic content
        self.cohere_client = cohere.Client(os.getenv("COHERE_API_KEY"))
        
        # Initialize Anthropic as backup
        self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Store conversation history
        self.conversation_history = []
    
    def generate_structured_content(self, prompt):
        """Generate structured content using Hugging Face"""
        try:
            result = self.hf_model(prompt, max_length=200, num_return_sequences=1)
            return result[0]["generated_text"]
        except Exception as e:
            return self._fallback_to_anthropic(prompt, "structured")
    
    def generate_powerful_content(self, prompt):
        """Generate powerful content using OpenAI"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a powerful and direct communicator."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return self._fallback_to_anthropic(prompt, "powerful")
    
    def generate_empathetic_content(self, prompt):
        """Generate empathetic content using Cohere"""
        try:
            response = self.cohere_client.generate(
                model='command',
                prompt=prompt,
                max_tokens=200,
                temperature=0.7
            )
            return response.generations[0].text
        except Exception as e:
            return self._fallback_to_anthropic(prompt, "empathetic")
    
    def _fallback_to_anthropic(self, prompt, style):
        """Fallback to Anthropic Claude if primary provider fails"""
        try:
            style_prompts = {
                "structured": "Organize this content in a clear, structured way:",
                "powerful": "Transform this into powerful, direct content:",
                "empathetic": "Respond with empathy and understanding:"
            }
            
            message = self.anthropic.messages.create(
                model="claude-2",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": f"{style_prompts[style]}\n\n{prompt}"
                }]
            )
            return message.content
        except Exception as e:
            return f"Error: Could not generate response ({str(e)})"
    
    def generate_response(self, prompt, style="all"):
        """Generate a response using the appropriate provider"""
        if style == "structured":
            return self.generate_structured_content(prompt)
        elif style == "powerful":
            return self.generate_powerful_content(prompt)
        elif style == "empathetic":
            return self.generate_empathetic_content(prompt)
        else:
            return {
                "structured": self.generate_structured_content(prompt),
                "powerful": self.generate_powerful_content(prompt),
                "empathetic": self.generate_empathetic_content(prompt)
            }
