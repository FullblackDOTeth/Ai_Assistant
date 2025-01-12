#!/usr/bin/env python3

from headai import Client
from headai.models import TextAnalysis, ImageRecognition
from headai.utils import setup_logging
import asyncio
import json

# Initialize logging
logger = setup_logging()

class HeadAIExample:
    def __init__(self, api_key: str):
        """Initialize Head AI client with API key."""
        self.client = Client(api_key=api_key)
        logger.info("Head AI client initialized")

    async def analyze_text(self, text: str):
        """Analyze text using the Text Analysis model."""
        try:
            # Create text analysis model
            model = TextAnalysis()
            
            # Get predictions
            result = await self.client.predict(
                model=model,
                input=text,
                options={
                    "language": "en",
                    "include_sentiment": True,
                    "include_entities": True
                }
            )
            
            return {
                "sentiment": result.sentiment,
                "entities": result.entities,
                "summary": result.summary
            }
            
        except Exception as e:
            logger.error(f"Text analysis failed: {str(e)}")
            raise

    async def process_image(self, image_path: str):
        """Process image using the Image Recognition model."""
        try:
            # Create image recognition model
            model = ImageRecognition()
            
            # Load and process image
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Get predictions
            result = await self.client.predict(
                model=model,
                input=image_data,
                options={
                    "detect_objects": True,
                    "detect_faces": True,
                    "detect_text": True
                }
            )
            
            return {
                "objects": result.objects,
                "faces": result.faces,
                "text": result.text
            }
            
        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}")
            raise

    async def batch_process(self, items: list):
        """Process multiple items in batch."""
        try:
            # Create processing tasks
            tasks = []
            for item in items:
                if item['type'] == 'text':
                    tasks.append(self.analyze_text(item['content']))
                elif item['type'] == 'image':
                    tasks.append(self.process_image(item['content']))
            
            # Run tasks concurrently
            results = await asyncio.gather(*tasks)
            
            return results
            
        except Exception as e:
            logger.error(f"Batch processing failed: {str(e)}")
            raise

    def save_results(self, results: list, output_file: str):
        """Save processing results to file."""
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Results saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to save results: {str(e)}")
            raise

async def main():
    """Main function demonstrating Head AI usage."""
    try:
        # Initialize client
        example = HeadAIExample(api_key="your_api_key_here")
        
        # Process text
        text_result = await example.analyze_text(
            "Head AI provides powerful artificial intelligence capabilities."
        )
        print("Text Analysis Result:", text_result)
        
        # Process image
        image_result = await example.process_image("example.jpg")
        print("Image Processing Result:", image_result)
        
        # Batch processing
        items = [
            {"type": "text", "content": "First text to analyze"},
            {"type": "text", "content": "Second text to analyze"},
            {"type": "image", "content": "image1.jpg"},
            {"type": "image", "content": "image2.jpg"}
        ]
        
        batch_results = await example.batch_process(items)
        
        # Save results
        example.save_results(batch_results, "results.json")
        
    except Exception as e:
        logger.error(f"Example failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
