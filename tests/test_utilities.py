"""
Test suite for Head AI utilities
"""

import unittest
from src.utils.utility_manager import utility_manager
from src.utils.web_scraper import WebScraper
from src.utils.text_processor import TextProcessor

class TestWebScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = WebScraper()
        self.test_url = "https://example.com"

    def test_get_page(self):
        html = self.scraper.get_page(self.test_url)
        self.assertIsNotNone(html)
        self.assertIsInstance(html, str)

    def test_parse_html(self):
        html = self.scraper.get_page(self.test_url)
        soup = self.scraper.parse_html(html)
        self.assertIsNotNone(soup)
        self.assertTrue(hasattr(soup, 'find_all'))

class TestTextProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = TextProcessor()
        self.test_text = """
        Natural language processing (NLP) is a subfield of linguistics, computer science, and artificial intelligence 
        concerned with the interactions between computers and human language. It is used to apply machine learning 
        algorithms to text and speech. The ultimate objective of NLP is to help computers understand language in a way 
        that is valuable.
        """

    def test_tokenization(self):
        sentences = self.processor.tokenize_sentences(self.test_text)
        self.assertIsInstance(sentences, list)
        self.assertTrue(len(sentences) > 0)

        words = self.processor.tokenize_words(self.test_text)
        self.assertIsInstance(words, list)
        self.assertTrue(len(words) > 0)

    def test_keyword_extraction(self):
        keywords = self.processor.extract_keywords(self.test_text)
        self.assertIsInstance(keywords, list)
        self.assertTrue(len(keywords) > 0)
        self.assertIsInstance(keywords[0], tuple)

    def test_summarization(self):
        summary = self.processor.summarize_text(self.test_text)
        self.assertIsInstance(summary, str)
        self.assertTrue(len(summary) > 0)
        self.assertTrue(len(summary) <= len(self.test_text))

class TestUtilityManager(unittest.TestCase):
    def setUp(self):
        self.manager = utility_manager
        self.test_text = "This is a test text for analysis. It contains multiple sentences and some key information."

    def test_text_analysis(self):
        result = self.manager.analyze_text(self.test_text)
        self.assertIsInstance(result, dict)
        self.assertIn('summary', result)
        self.assertIn('keywords', result)
        self.assertIn('entities', result)
        self.assertIn('sentiment', result)

    def test_web_content_processing(self):
        result = self.manager.process_web_content("https://example.com")
        self.assertIsInstance(result, dict)
        self.assertIn('title', result)
        self.assertIn('summary', result)
        self.assertIn('keywords', result)

if __name__ == '__main__':
    unittest.main()
