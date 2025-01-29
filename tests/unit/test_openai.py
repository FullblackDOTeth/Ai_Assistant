import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def test_openai():
    try:
        # Set API key
        openai.api_key = os.getenv('OPENAI_API_KEY')
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Test completion with a simpler model
        completion = openai.Completion.create(
            model="text-davinci-003",
            prompt="Write a haiku about recursion in programming.",
            max_tokens=50
        )
        
        # Print the response
        print("\nAPI Response:")
        print(completion.choices[0].text.strip())
        print("\nConnection successful!")
        
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    print("Testing OpenAI connection...")
    test_openai()
