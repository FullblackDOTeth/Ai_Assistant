import pytest
from unittest.mock import Mock, patch
import nltk
from src.setup_nltk import setup_nltk, download_nltk_data
from src.research_methods import ResearchMethods

@pytest.fixture
def nltk_resources():
    """Fixture to ensure NLTK resources are available for testing"""
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('averaged_perceptron_tagger')
    except LookupError:
        download_nltk_data()
    return True

@pytest.fixture
def research_methods():
    """Fixture for ResearchMethods instance"""
    return ResearchMethods()

class TestNLPSetup:
    def test_nltk_setup(self):
        """Test NLTK setup process"""
        with patch('nltk.download') as mock_download:
            setup_nltk()
            mock_download.assert_called()

    def test_nltk_resources_available(self, nltk_resources):
        """Test if required NLTK resources are available"""
        assert nltk_resources == True

class TestResearchMethods:
    def test_text_preprocessing(self, research_methods):
        """Test text preprocessing functionality"""
        test_text = "This is a test sentence! It contains multiple punctuation marks..."
        processed = research_methods._preprocess_text(test_text)
        assert isinstance(processed, str)
        assert "..." not in processed
        assert "!" not in processed

    def test_keyword_extraction(self, research_methods, nltk_resources):
        """Test keyword extraction from text"""
        test_text = "Artificial Intelligence and Machine Learning are transforming technology"
        keywords = research_methods._extract_keywords(test_text)
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        assert any("artificial intelligence" in kw.lower() for kw in keywords)

    @pytest.mark.network
    def test_web_search_integration(self, research_methods):
        """Test web search functionality with NLP preprocessing"""
        query = "Latest developments in AI"
        with patch('duckduckgo_search.ddg') as mock_search:
            mock_search.return_value = [
                {'title': 'AI News', 'link': 'https://example.com', 'snippet': 'Recent AI developments...'}
            ]
            results = research_methods.web_search(query, max_results=1)
            assert isinstance(results, list)
            assert len(results) > 0

    @pytest.mark.network
    def test_wikipedia_search(self, research_methods):
        """Test Wikipedia search with NLP processing"""
        query = "Python programming language"
        with patch('wikipedia.search') as mock_wiki:
            mock_wiki.return_value = ['Python (programming language)']
            results = research_methods.wikipedia_search(query)
            assert isinstance(results, list)
            assert len(results) > 0

    def test_text_similarity(self, research_methods):
        """Test text similarity comparison"""
        text1 = "AI and machine learning"
        text2 = "Artificial intelligence and ML"
        similarity = research_methods._calculate_similarity(text1, text2)
        assert isinstance(similarity, float)
        assert 0 <= similarity <= 1
