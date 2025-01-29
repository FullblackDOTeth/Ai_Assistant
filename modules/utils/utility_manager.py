"""
Utility Manager for Head AI
Provides centralized access to all utility functions
"""

import logging
from typing import Optional, Dict, Any
from .web_scraper import WebScraper
from .text_processor import TextProcessor

logger = logging.getLogger(__name__)

class UtilityManager:
    def __init__(self):
        """Initialize all utility components"""
        self.web_scraper = WebScraper()
        self.text_processor = TextProcessor()
        logger.info("Utility Manager initialized")

    def process_web_content(self, url: str) -> Dict[str, Any]:
        """
        Process web content: fetch, scrape, and analyze
        
        Args:
            url: URL to process
            
        Returns:
            Dict containing processed data
        """
        # Scrape webpage
        scrape_result = self.web_scraper.scrape_page(url)
        if scrape_result.get('error'):
            return scrape_result

        text_content = scrape_result['text']
        
        # Process text
        result = {
            'url': url,
            'title': scrape_result['title'],
            'links': scrape_result['links'],
            'summary': self.text_processor.summarize_text(text_content),
            'keywords': self.text_processor.extract_keywords(text_content),
            'entities': self.text_processor.extract_entities(text_content),
            'sentiment': self.text_processor.analyze_sentiment(text_content)
        }

        return result

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text content
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict containing analysis results
        """
        return {
            'summary': self.text_processor.summarize_text(text),
            'keywords': self.text_processor.extract_keywords(text),
            'entities': self.text_processor.extract_entities(text),
            'sentiment': self.text_processor.analyze_sentiment(text)
        }

# Create a singleton instance
utility_manager = UtilityManager()
