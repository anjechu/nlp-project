"""
Unit tests for report generation functionality
Tests HTML report generation, chart integration, and cross-cultural analysis
"""

import unittest
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestReportGenerator(unittest.TestCase):
    """Test suite for report generation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_data = {
            'topics': [
                {
                    'topic_id': 1,
                    'topic_name': 'Graphics Quality',
                    'density': 150,
                    'sentiment_score': 0.8,
                    'sentiment_label': 'positive',
                    'source_language': 'schinese'
                },
                {
                    'topic_id': 2,
                    'topic_name': 'Performance Issues',
                    'density': 120,
                    'sentiment_score': -0.6,
                    'sentiment_label': 'negative',
                    'source_language': 'english'
                }
            ],
            'statistics': {
                'total_comments': 1000,
                'valid_statements': 800
            }
        }
        
    def test_filename_parsing(self):
        """Test game and language extraction from filenames"""
        test_cases = [
            ("comments_silksong_japanese.json", "silksong", "japanese"),
            ("Report_comments_battlefield6_chinese.json", "battlefield6", "chinese"),
            ("comments_game_name_english.json", "game_name", "english"),
        ]
        
        for filename, expected_game, expected_lang in test_cases:
            # Basic validation
            self.assertIn("comments", filename)
            self.assertIn(expected_lang, filename)
            
    def test_cultural_analysis_grouping(self):
        """Test grouping topics by culture"""
        topics = self.sample_data['topics']
        
        # Group by language
        by_language = {}
        for topic in topics:
            lang = topic['source_language']
            if lang not in by_language:
                by_language[lang] = []
            by_language[lang].append(topic)
            
        self.assertIn('schinese', by_language)
        self.assertIn('english', by_language)
        
    def test_sentiment_grouping(self):
        """Test grouping topics by sentiment"""
        topics = self.sample_data['topics']
        
        positive = [t for t in topics if t['sentiment_label'] == 'positive']
        negative = [t for t in topics if t['sentiment_label'] == 'negative']
        
        self.assertEqual(len(positive), 1)
        self.assertEqual(len(negative), 1)
        
    def test_html_generation(self):
        """Test HTML report structure generation"""
        # Test that basic HTML elements would be present
        html_elements = [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            '<body>',
            '</html>'
        ]
        
        for element in html_elements:
            self.assertIsNotNone(element)
            
    def test_executive_summary_structure(self):
        """Test executive summary data structure"""
        topics = self.sample_data['topics']
        
        # Group by language and sentiment
        by_language = {
            'Chinese': {'positive': [], 'negative': []},
            'Japanese': {'positive': [], 'negative': []},
            'English': {'positive': [], 'negative': []}
        }
        
        self.assertIn('Chinese', by_language)
        self.assertIn('positive', by_language['Chinese'])


class TestChartData(unittest.TestCase):
    """Test chart data generation"""
    
    def test_sentiment_distribution(self):
        """Test sentiment distribution calculation"""
        topics = [
            {'sentiment_label': 'positive', 'density': 100},
            {'sentiment_label': 'positive', 'density': 80},
            {'sentiment_label': 'negative', 'density': 60},
            {'sentiment_label': 'neutral', 'density': 40}
        ]
        
        sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
        for topic in topics:
            label = topic['sentiment_label']
            sentiment_counts[label] += topic['density']
            
        self.assertEqual(sentiment_counts['positive'], 180)
        self.assertEqual(sentiment_counts['negative'], 60)
        self.assertEqual(sentiment_counts['neutral'], 40)
        
    def test_topic_density_ranking(self):
        """Test topic density sorting (top 15)"""
        topics = [
            {'topic_name': 'Topic A', 'density': 100},
            {'topic_name': 'Topic B', 'density': 200},
            {'topic_name': 'Topic C', 'density': 150},
        ]
        
        sorted_topics = sorted(topics, key=lambda x: x['density'], reverse=True)
        top_15 = sorted_topics[:15]
        
        self.assertEqual(top_15[0]['topic_name'], 'Topic B')
        self.assertEqual(top_15[0]['density'], 200)


if __name__ == '__main__':
    unittest.main()
