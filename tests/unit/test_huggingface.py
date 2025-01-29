from transformers import pipeline
from dotenv import load_dotenv
import os

def test_huggingface():
    try:
        # Initialize a text generation pipeline
        generator = pipeline('text-generation', model='gpt2')
        
        # Generate text
        prompt = "AI assistants are"
        result = generator(prompt, max_length=50, num_return_sequences=1)
        
        print("\nAPI Response:")
        print(result[0]['generated_text'])
        print("\nConnection successful!")
        
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    print("Testing Hugging Face...")
    test_huggingface()
