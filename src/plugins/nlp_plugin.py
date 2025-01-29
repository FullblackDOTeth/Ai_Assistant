"""
Natural Language Processing plugin
"""

from . import Plugin
from typing import Dict, List, Any
import re
import json

class NLPPlugin(Plugin):
    def __init__(self):
        self._name = "nlp"
        self._description = "Natural Language Processing capabilities"
        self._keywords = set()
        self._patterns = {}
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    def initialize(self) -> None:
        """Initialize NLP components"""
        # Load basic keywords and patterns
        self._keywords = {
            "search", "find", "look", "research",
            "explain", "describe", "tell",
            "analyze", "compare", "difference",
            "how", "what", "why", "when", "where"
        }
        
        self._patterns = {
            "question": r"\b(what|how|why|when|where|who)\b.*\?",
            "command": r"\b(search|find|analyze|explain)\b.*",
            "comparison": r"\b(compare|difference|between|vs)\b.*"
        }
        
        print(f"Initialized {self.name} plugin")
    
    def execute(self, text: str, **kwargs) -> Dict[str, Any]:
        """Process text using NLP"""
        result = {
            "type": self._detect_type(text),
            "keywords": self._extract_keywords(text),
            "entities": self._extract_entities(text),
            "sentiment": self._analyze_sentiment(text)
        }
        
        if kwargs.get("include_patterns", False):
            result["patterns"] = self._match_patterns(text)
        
        return result
    
    def _detect_type(self, text: str) -> str:
        """Detect the type of text (question, command, statement)"""
        text = text.lower()
        if re.search(self._patterns["question"], text):
            return "question"
        elif re.search(self._patterns["command"], text):
            return "command"
        elif re.search(self._patterns["comparison"], text):
            return "comparison"
        return "statement"
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        words = set(text.lower().split())
        return list(words.intersection(self._keywords))
    
    def _extract_entities(self, text: str) -> List[Dict[str, str]]:
        """Extract named entities (simple version)"""
        entities = []
        # Look for capitalized words (simple entity detection)
        for word in text.split():
            if word[0].isupper() and len(word) > 1:
                entities.append({
                    "text": word,
                    "type": "unknown"  # In a full implementation, we'd detect the type
                })
        return entities
    
    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Simple sentiment analysis"""
        # This is a very basic implementation
        positive_words = {"good", "great", "excellent", "amazing", "wonderful", "fantastic"}
        negative_words = {"bad", "poor", "terrible", "awful", "horrible", "wrong"}
        
        words = text.lower().split()
        pos_count = sum(1 for w in words if w in positive_words)
        neg_count = sum(1 for w in words if w in negative_words)
        total = len(words)
        
        return {
            "positive": pos_count / total if total > 0 else 0,
            "negative": neg_count / total if total > 0 else 0,
            "neutral": (total - pos_count - neg_count) / total if total > 0 else 1
        }
    
    def _match_patterns(self, text: str) -> Dict[str, bool]:
        """Check text against defined patterns"""
        return {
            name: bool(re.search(pattern, text.lower()))
            for name, pattern in self._patterns.items()
        }
