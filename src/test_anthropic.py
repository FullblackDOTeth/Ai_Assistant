from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def test_anthropic():
    try:
        # Initialize Anthropic client
        anthropic = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        # Create a completion
        completion = anthropic.completions.create(
            model="claude-2.1",
            max_tokens_to_sample=300,
            prompt=f"{HUMAN_PROMPT} Write a haiku about AI assistants.{AI_PROMPT}"
        )
        
        # Print the response
        print("\nAPI Response:")
        print(completion.completion)
        print("\nConnection successful!")
        
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    print("Testing Anthropic connection...")
    test_anthropic()
