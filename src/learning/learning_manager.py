"""
Advanced Learning Manager for Head AI
Implements user preference learning, topic modeling, and interest tracking
"""

import numpy as np
from pathlib import Path
import json
import pickle
from datetime import datetime
from typing import Dict, List, Set, Optional, Union
import logging
from gensim import models, corpora
from gensim.models.ldamodel import LdaModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from sentence_transformers import SentenceTransformer
import torch
import faiss
import pandas as pd
from collections import defaultdict

logger = logging.getLogger(__name__)

class LearningManager:
    def __init__(self):
        """Initialize the learning system"""
        self.data_dir = Path(__file__).parent.parent.parent / 'data' / 'learning'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize models
        self.topic_model = None
        self.dictionary = None
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.preference_index = None
        
        # Load or initialize data structures
        self.user_preferences = self._load_preferences()
        self.interest_graph = self._load_interest_graph()
        self.interaction_history = self._load_interaction_history()
        
        # Initialize topic modeling
        self._init_topic_modeling()
        
        # Initialize FAISS index for semantic search
        self._init_preference_index()

    def _load_preferences(self) -> Dict:
        """Load user preferences from disk"""
        pref_file = self.data_dir / 'preferences.json'
        if pref_file.exists():
            return json.loads(pref_file.read_text())
        return {
            'topics': defaultdict(float),
            'categories': defaultdict(float),
            'entities': defaultdict(float),
            'sentiment': defaultdict(float)
        }

    def _load_interest_graph(self) -> Dict:
        """Load interest graph from disk"""
        graph_file = self.data_dir / 'interest_graph.pkl'
        if graph_file.exists():
            with open(graph_file, 'rb') as f:
                return pickle.load(f)
        return {
            'nodes': set(),
            'edges': defaultdict(set),
            'weights': defaultdict(float)
        }

    def _load_interaction_history(self) -> List[Dict]:
        """Load interaction history from disk"""
        history_file = self.data_dir / 'interactions.json'
        if history_file.exists():
            return json.loads(history_file.read_text())
        return []

    def _init_topic_modeling(self):
        """Initialize or load topic model"""
        model_file = self.data_dir / 'topic_model.pkl'
        dict_file = self.data_dir / 'dictionary.pkl'
        
        if model_file.exists() and dict_file.exists():
            self.topic_model = LdaModel.load(str(model_file))
            self.dictionary = corpora.Dictionary.load(str(dict_file))
        else:
            # Will be initialized when first document is processed
            self.topic_model = None
            self.dictionary = None

    def _init_preference_index(self):
        """Initialize FAISS index for preference matching"""
        index_file = self.data_dir / 'preference_index.faiss'
        if index_file.exists():
            self.preference_index = faiss.read_index(str(index_file))
        else:
            # Create empty index
            embedding_size = self.encoder.get_sentence_embedding_dimension()
            self.preference_index = faiss.IndexFlatIP(embedding_size)

    def update_preferences(self, text: str, interaction_type: str, metadata: Dict = None):
        """
        Update user preferences based on interaction
        
        Args:
            text: Interaction text
            interaction_type: Type of interaction (query, response, click, etc.)
            metadata: Additional metadata about the interaction
        """
        # Encode text
        embedding = self.encoder.encode([text])[0]
        
        # Update topic model
        self._update_topic_model(text)
        
        # Extract topics
        topics = self._extract_topics(text)
        
        # Update preference index
        if self.preference_index.ntotal > 0:
            # Find similar previous interactions
            D, I = self.preference_index.search(
                embedding.reshape(1, -1).astype('float32'), 
                k=5
            )
            # Update weights based on similarities
            for sim, idx in zip(D[0], I[0]):
                if sim > 0.8:  # High similarity threshold
                    self._strengthen_preference(idx, sim)
        
        # Add new embedding to index
        self.preference_index.add(embedding.reshape(1, -1).astype('float32'))
        
        # Update interest graph
        self._update_interest_graph(topics, interaction_type)
        
        # Record interaction
        self.interaction_history.append({
            'text': text,
            'type': interaction_type,
            'timestamp': datetime.now().isoformat(),
            'topics': topics,
            'metadata': metadata or {}
        })
        
        # Save updates
        self._save_state()

    def _update_topic_model(self, text: str):
        """Update topic model with new text"""
        if not self.dictionary:
            # Initialize on first document
            texts = [[word.lower() for word in text.split()]]
            self.dictionary = corpora.Dictionary(texts)
            corpus = [self.dictionary.doc2bow(text) for text in texts]
            self.topic_model = LdaModel(
                corpus=corpus,
                id2word=self.dictionary,
                num_topics=20,
                update_every=1,
                passes=1
            )
        else:
            # Update existing model
            bow = self.dictionary.doc2bow(text.lower().split())
            self.topic_model.update([bow])

    def _extract_topics(self, text: str) -> List[tuple]:
        """Extract topics from text"""
        if not self.topic_model:
            return []
            
        bow = self.dictionary.doc2bow(text.lower().split())
        return self.topic_model.get_document_topics(bow)

    def _strengthen_preference(self, index: int, similarity: float):
        """Strengthen preference based on similarity"""
        # Update topic weights
        for topic_id, weight in self.topic_model.get_document_topics(
            self.interaction_history[index]['text']
        ):
            self.user_preferences['topics'][str(topic_id)] += weight * similarity

    def _update_interest_graph(self, topics: List[tuple], interaction_type: str):
        """Update interest graph based on topics"""
        # Add topic nodes
        for topic_id, weight in topics:
            topic_node = f'topic_{topic_id}'
            self.interest_graph['nodes'].add(topic_node)
            
            # Connect related topics
            for other_id, other_weight in topics:
                if topic_id != other_id:
                    other_node = f'topic_{other_id}'
                    self.interest_graph['edges'][topic_node].add(other_node)
                    self.interest_graph['weights'][(topic_node, other_node)] += (
                        weight * other_weight
                    )

    def get_recommendations(self, context: str = None, n: int = 5) -> List[Dict]:
        """
        Get personalized recommendations based on user preferences
        
        Args:
            context: Optional context to consider
            n: Number of recommendations
            
        Returns:
            List of recommended topics/items
        """
        if not self.interaction_history:
            return []
            
        # Encode context if provided
        if context:
            context_embedding = self.encoder.encode([context])[0]
            
            # Search for similar interactions
            D, I = self.preference_index.search(
                context_embedding.reshape(1, -1).astype('float32'),
                k=n
            )
            
            recommendations = []
            for sim, idx in zip(D[0], I[0]):
                if sim > 0:  # Only include positive similarities
                    interaction = self.interaction_history[idx]
                    recommendations.append({
                        'text': interaction['text'],
                        'similarity': float(sim),
                        'topics': interaction['topics'],
                        'timestamp': interaction['timestamp']
                    })
            
            return recommendations
            
        # Without context, return top topics based on preferences
        sorted_topics = sorted(
            self.user_preferences['topics'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {
                'topic_id': topic_id,
                'weight': float(weight),
                'related_topics': list(
                    self.interest_graph['edges'].get(f'topic_{topic_id}', set())
                )
            }
            for topic_id, weight in sorted_topics[:n]
        ]

    def get_interest_analysis(self) -> Dict:
        """Get analysis of user interests"""
        return {
            'top_topics': dict(
                sorted(
                    self.user_preferences['topics'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            ),
            'topic_clusters': self._get_topic_clusters(),
            'interest_evolution': self._get_interest_evolution(),
            'interaction_stats': self._get_interaction_stats()
        }

    def _get_topic_clusters(self) -> List[Dict]:
        """Get clusters of related topics"""
        if not self.interest_graph['nodes']:
            return []
            
        # Create similarity matrix from graph
        nodes = list(self.interest_graph['nodes'])
        n = len(nodes)
        similarity_matrix = np.zeros((n, n))
        
        for i, node1 in enumerate(nodes):
            for j, node2 in enumerate(nodes):
                similarity_matrix[i, j] = self.interest_graph['weights'].get(
                    (node1, node2),
                    0
                )
        
        # Cluster topics
        clustering = DBSCAN(eps=0.5, min_samples=2)
        clusters = clustering.fit_predict(similarity_matrix)
        
        # Group topics by cluster
        topic_clusters = defaultdict(list)
        for node, cluster in zip(nodes, clusters):
            if cluster >= 0:  # Ignore noise points
                topic_clusters[int(cluster)].append(node)
        
        return [
            {
                'cluster_id': cluster_id,
                'topics': topics,
                'strength': float(np.mean([
                    self.user_preferences['topics'].get(
                        topic.split('_')[1],
                        0
                    )
                    for topic in topics
                ]))
            }
            for cluster_id, topics in topic_clusters.items()
        ]

    def _get_interest_evolution(self) -> List[Dict]:
        """Get evolution of interests over time"""
        if not self.interaction_history:
            return []
            
        # Convert timestamps to datetime objects
        df = pd.DataFrame(self.interaction_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Group by day and calculate topic distributions
        daily_topics = df.groupby(df['timestamp'].dt.date).agg({
            'topics': lambda x: self._merge_topic_distributions(list(x))
        })
        
        return [
            {
                'date': date.isoformat(),
                'topics': topics
            }
            for date, topics in daily_topics.itertuples()
        ]

    def _merge_topic_distributions(self, topic_lists: List[List[tuple]]) -> Dict[str, float]:
        """Merge multiple topic distributions"""
        merged = defaultdict(float)
        for topics in topic_lists:
            for topic_id, weight in topics:
                merged[str(topic_id)] += weight
        return dict(merged)

    def _get_interaction_stats(self) -> Dict:
        """Get interaction statistics"""
        if not self.interaction_history:
            return {}
            
        df = pd.DataFrame(self.interaction_history)
        
        return {
            'total_interactions': len(df),
            'interaction_types': df['type'].value_counts().to_dict(),
            'unique_topics': len(self.user_preferences['topics']),
            'most_active_day': df.groupby(
                pd.to_datetime(df['timestamp']).dt.date
            ).size().idxmax().isoformat()
        }

    def _save_state(self):
        """Save current state to disk"""
        # Save preferences
        pref_file = self.data_dir / 'preferences.json'
        pref_file.write_text(json.dumps(self.user_preferences))
        
        # Save interest graph
        graph_file = self.data_dir / 'interest_graph.pkl'
        with open(graph_file, 'wb') as f:
            pickle.dump(self.interest_graph, f)
        
        # Save interaction history
        history_file = self.data_dir / 'interactions.json'
        history_file.write_text(json.dumps(self.interaction_history))
        
        # Save topic model
        if self.topic_model:
            self.topic_model.save(str(self.data_dir / 'topic_model.pkl'))
            self.dictionary.save(str(self.data_dir / 'dictionary.pkl'))
        
        # Save FAISS index
        if self.preference_index:
            faiss.write_index(
                self.preference_index,
                str(self.data_dir / 'preference_index.faiss')
            )

# Create singleton instance
learning_manager = LearningManager()
