"""
Comprehensive tests for AI learning capabilities
Tests various aspects of learning, adaptation, and knowledge retention
"""

import pytest
import numpy as np
from pathlib import Path
import json
from datetime import datetime
from src.learning.learning_manager import LearningManager
from src.core.module_manager import module_manager

class TestLearningCapabilities:
    @pytest.fixture
    def learning_manager(self):
        """Fixture for learning manager instance"""
        return LearningManager()

    @pytest.fixture
    def sample_data(self):
        """Generate sample training data"""
        return {
            'text_samples': [
                "AI systems need robust testing frameworks",
                "Machine learning requires quality data",
                "Neural networks excel at pattern recognition",
                "Data preprocessing is crucial for model performance"
            ],
            'user_interactions': [
                {"type": "query", "content": "How to improve model accuracy?"},
                {"type": "feedback", "content": "This suggestion was helpful", "rating": 1},
                {"type": "preference", "content": "Prefer detailed technical explanations"}
            ],
            'preferences': {
                'technical_depth': 0.8,
                'response_style': 'detailed',
                'code_examples': True
            }
        }

    def test_topic_modeling(self, learning_manager, sample_data):
        """Test topic modeling capabilities"""
        # Train topic model
        topics = learning_manager.analyze_topics(sample_data['text_samples'])
        
        assert len(topics) > 0
        assert all(isinstance(topic, dict) for topic in topics)
        assert all('keywords' in topic for topic in topics)
        assert all('weight' in topic for topic in topics)

    def test_preference_learning(self, learning_manager, sample_data):
        """Test user preference learning"""
        # Initial preferences
        learning_manager.update_preferences(sample_data['preferences'])
        
        # Add interaction data
        for interaction in sample_data['user_interactions']:
            learning_manager.process_interaction(interaction)
        
        # Get learned preferences
        learned_prefs = learning_manager.get_current_preferences()
        
        assert 'technical_depth' in learned_prefs
        assert 'response_style' in learned_prefs
        assert learned_prefs['technical_depth'] >= 0 and learned_prefs['technical_depth'] <= 1

    def test_semantic_search(self, learning_manager, sample_data):
        """Test semantic search capabilities"""
        # Index sample content
        learning_manager.index_content(sample_data['text_samples'])
        
        # Test search
        query = "model performance"
        results = learning_manager.semantic_search(query, top_k=2)
        
        assert len(results) <= 2
        assert all('content' in result for result in results)
        assert all('score' in result for result in results)

    def test_adaptive_learning(self, learning_manager, sample_data):
        """Test system's ability to adapt to user preferences"""
        # Initial state
        initial_prefs = learning_manager.get_current_preferences()
        
        # Simulate user interactions
        for _ in range(5):
            interaction = {
                "type": "feedback",
                "content": "Need more technical details",
                "rating": 1
            }
            learning_manager.process_interaction(interaction)
        
        # Check adaptation
        adapted_prefs = learning_manager.get_current_preferences()
        assert adapted_prefs['technical_depth'] > initial_prefs.get('technical_depth', 0)

    def test_knowledge_retention(self, learning_manager, sample_data):
        """Test long-term knowledge retention"""
        # Store initial knowledge
        learning_manager.add_knowledge(sample_data['text_samples'])
        
        # Verify retention
        for sample in sample_data['text_samples']:
            relevance = learning_manager.check_knowledge_relevance(sample)
            assert relevance > 0.5

    def test_performance_metrics(self, learning_manager):
        """Test learning performance metrics"""
        metrics = learning_manager.get_performance_metrics()
        
        required_metrics = [
            'topic_model_coherence',
            'preference_learning_accuracy',
            'semantic_search_precision',
            'response_adaptation_rate'
        ]
        
        for metric in required_metrics:
            assert metric in metrics
            assert isinstance(metrics[metric], (int, float))
            assert metrics[metric] >= 0

    def test_error_handling(self, learning_manager):
        """Test error handling in learning processes"""
        # Test with invalid input
        with pytest.raises(ValueError):
            learning_manager.analyze_topics([])
        
        with pytest.raises(ValueError):
            learning_manager.process_interaction({"type": "invalid"})

    def test_resource_efficiency(self, learning_manager, sample_data):
        """Test resource usage during learning"""
        import psutil
        import time
        
        # Measure memory and time
        start_mem = psutil.Process().memory_info().rss
        start_time = time.time()
        
        # Perform learning operations
        learning_manager.analyze_topics(sample_data['text_samples'])
        learning_manager.process_interaction(sample_data['user_interactions'][0])
        
        # Check resource usage
        memory_used = psutil.Process().memory_info().rss - start_mem
        time_taken = time.time() - start_time
        
        # Assert reasonable resource usage
        assert memory_used < 1024 * 1024 * 100  # 100MB max
        assert time_taken < 5.0  # 5 seconds max
