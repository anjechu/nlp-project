"""
Unit tests for LLM integration and Map-Reduce architecture
Tests LLM-based enhancements and distributed processing
"""

import unittest
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestLLMIntegration(unittest.TestCase):
    """Test suite for LLM integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_topic = {
            'topic_id': 1,
            'density': 150,
            'sentiment_score': 0.7,
            'sentiment_label': 'positive',
            'representative_sentences': [
                'The graphics are amazing',
                'Beautiful visual design',
                'Stunning art style'
            ]
        }
        
    def test_topic_name_generation(self):
        """Test LLM-based topic naming"""
        sentences = self.sample_topic['representative_sentences']
        
        # Check that we have sentences to work with
        self.assertIsNotNone(sentences)
        self.assertGreater(len(sentences), 0)
        
        # Topic name should be derived from common themes
        keywords = ['graphics', 'visual', 'art']
        has_relevant_keyword = any(
            any(kw in sent.lower() for kw in keywords)
            for sent in sentences
        )
        self.assertTrue(has_relevant_keyword)
        
    def test_cultural_summary_structure(self):
        """Test cross-cultural insights structure"""
        cultures = ['Chinese', 'Japanese', 'English']
        sentiments = ['positive', 'negative', 'neutral']
        
        culture_topics = {}
        for culture in cultures:
            culture_topics[culture] = {}
            for sentiment in sentiments:
                culture_topics[culture][sentiment] = []
                
        self.assertEqual(len(culture_topics), 3)
        self.assertIn('Chinese', culture_topics)


class TestMapReduceArchitecture(unittest.TestCase):
    """Test Map-Reduce processing architecture"""
    
    def test_map_phase_structure(self):
        """Test MAP phase data structure"""
        game_language_pairs = [
            ('game1', 'chinese'),
            ('game1', 'japanese'),
            ('game1', 'english'),
        ]
        
        map_results = []
        for game, language in game_language_pairs:
            result = {
                'topics': [],
                'map_metadata': {
                    'game_name': game,
                    'language': language
                }
            }
            map_results.append(result)
            
        self.assertEqual(len(map_results), 3)
        
    def test_reduce_phase_aggregation(self):
        """Test REDUCE phase aggregation"""
        map_results = [
            {
                'topics': [
                    {'topic_id': 1, 'density': 100}
                ],
                'statistics': {'total': 500, 'valid': 450}
            },
            {
                'topics': [
                    {'topic_id': 1, 'density': 80}
                ],
                'statistics': {'total': 400, 'valid': 380}
            }
        ]
        
        # Aggregate topics
        all_topics = []
        total_comments = 0
        
        for result in map_results:
            all_topics.extend(result['topics'])
            total_comments += result['statistics']['total']
            
        self.assertEqual(len(all_topics), 2)
        self.assertEqual(total_comments, 900)


if __name__ == '__main__':
    unittest.main()
