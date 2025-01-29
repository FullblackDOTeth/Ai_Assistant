import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def test_gemini():
    try:
        # Configure API key
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        
        # Load model
        model = genai.GenerativeModel('gemini-pro')
        
        # Generate content
        response = model.generate_content(
            "Write a haiku about artificial intelligence.",
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=100,
                top_p=0.8,
                top_k=40
            ),
            safety_settings={
                "HARASSMENT": "block_none",
                "HATE_SPEECH": "block_none",
                "SEXUALLY_EXPLICIT": "block_none",
                "DANGEROUS_CONTENT": "block_none"
            }
        )
        
        print("\nAPI Response:")
        print(response.text)
        print("\nConnection successful!")
        
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    print("Testing Google Gemini...")
    test_gemini()
