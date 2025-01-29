"""
Text processing utilities for Head AI
Handles text analysis, summarization, and NLP tasks
"""

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from typing import List, Dict, Set, Optional
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class TextProcessor:
    def __init__(self):
        """Initialize TextProcessor and ensure NLTK data is available"""
        self.nltk_data_dir = self._get_nltk_data_dir()
        self._ensure_nltk_data()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))

    def _get_nltk_data_dir(self) -> Path:
        """Get or create NLTK data directory"""
        nltk_dir = Path(os.getenv('NLTK_DATA', Path.home() / 'nltk_data'))
        nltk_dir.mkdir(parents=True, exist_ok=True)
        return nltk_dir

    def _ensure_nltk_data(self):
        """Ensure required NLTK data is downloaded"""
        nltk.data.path.append(str(self.nltk_data_dir))
        required_packages = [
            'punkt',           # For sentence tokenization
            'stopwords',       # For stopword removal
            'averaged_perceptron_tagger',  # For POS tagging
            'wordnet',         # For lemmatization
            'maxent_ne_chunker',  # For named entity recognition
            'words'            # Basic word lists
        ]
        
        for package in required_packages:
            try:
                nltk.data.find(f'tokenizers/{package}')
            except LookupError:
                try:
                    nltk.download(package, download_dir=str(self.nltk_data_dir))
                except Exception as e:
                    logger.error(f"Failed to download NLTK package {package}: {str(e)}")

    def tokenize_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        return sent_tokenize(text)

    def tokenize_words(self, text: str) -> List[str]:
        """Split text into words"""
        return word_tokenize(text)

    def remove_stopwords(self, words: List[str]) -> List[str]:
        """Remove common stopwords from word list"""
        return [word for word in words if word.lower() not in self.stop_words]

    def lemmatize_words(self, words: List[str]) -> List[str]:
        """Convert words to their base form"""
        return [self.lemmatizer.lemmatize(word) for word in words]

    def extract_keywords(self, text: str, top_n: int = 10) -> List[tuple]:
        """
        Extract important keywords from text
        
        Args:
            text: Input text
            top_n: Number of top keywords to return
            
        Returns:
            List of (word, frequency) tuples
        """
        # Tokenize and clean text
        words = self.tokenize_words(text.lower())
        words = self.remove_stopwords(words)
        words = self.lemmatize_words(words)
        
        # Calculate word frequencies
        freq_dist = nltk.FreqDist(words)
        return freq_dist.most_common(top_n)

    def summarize_text(self, text: str, num_sentences: int = 3) -> str:
        """
        Create a summary of the text
        
        Args:
            text: Input text
            num_sentences: Number of sentences in summary
            
        Returns:
            str: Summarized text
        """
        sentences = self.tokenize_sentences(text)
        if len(sentences) <= num_sentences:
            return text

        # Calculate sentence scores based on keyword frequency
        word_freq = dict(self.extract_keywords(text, top_n=100))
        sentence_scores = {}
        
        for sentence in sentences:
            words = self.tokenize_words(sentence.lower())
            score = sum(word_freq.get(word, 0) for word in words)
            sentence_scores[sentence] = score

        # Get top sentences
        top_sentences = sorted(sentences, 
                             key=lambda s: sentence_scores[s], 
                             reverse=True)[:num_sentences]
        
        # Maintain original order
        ordered_summary = [s for s in sentences if s in top_sentences]
        return ' '.join(ordered_summary)

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Basic sentiment analysis of text
        
        Args:
            text: Input text
            
        Returns:
            Dict containing sentiment scores
        """
        try:
            from nltk.sentiment import SentimentIntensityAnalyzer
            sia = SentimentIntensityAnalyzer()
            return sia.polarity_scores(text)
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}")
            return {'compound': 0.0, 'neg': 0.0, 'neu': 1.0, 'pos': 0.0}

    def extract_entities(self, text: str) -> Dict[str, Set[str]]:
        """
        Extract named entities from text
        
        Args:
            text: Input text
            
        Returns:
            Dict mapping entity types to sets of entity values
        """
        entities = {
            'PERSON': set(),
            'ORGANIZATION': set(),
            'LOCATION': set(),
            'DATE': set(),
            'TIME': set(),
            'MONEY': set(),
            'PERCENT': set(),
        }
        
        try:
            # Tokenize and tag
            tokens = nltk.word_tokenize(text)
            tagged = nltk.pos_tag(tokens)
            
            # Extract named entities
            chunks = nltk.ne_chunk(tagged)
            
            for chunk in chunks:
                if hasattr(chunk, 'label'):
                    entity_type = chunk.label()
                    entity_value = ' '.join(c[0] for c in chunk)
                    if entity_type in entities:
                        entities[entity_type].add(entity_value)
        
        except Exception as e:
            logger.error(f"Entity extraction failed: {str(e)}")
        
        return entities
