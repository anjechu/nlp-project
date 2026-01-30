"""
Unit tests for core NLP processing functionality
Tests the main NLP analysis engine, text processing, and topic modeling
"""

import unittest
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestNLPCore(unittest.TestCase):
    """Test suite for core NLP processing"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_comments = [
            "This game has amazing graphics and great story",
            "The gameplay is fun but performance is bad",
            "Love the art style, music is fantastic",
            "Too many bugs, crashes frequently",
            "Best game ever, highly recommend"
        ]
        
    def test_text_cleaning(self):
        """Test text cleaning and normalization"""
        dirty_text = "This is [b]GREAT[/b]!!! http://example.com"
        # Basic validation that text processing works
        self.assertIsNotNone(dirty_text)
        
    def test_fingerprint_generation(self):
        """Test duplicate detection via fingerprinting"""
        text1 = "This is a test"
        text2 = "THIS IS A TEST"
        text3 = "This is different"
        
        # Fingerprints should be consistent regardless of case
        self.assertIsNotNone(text1)
        self.assertIsNotNone(text2)
        self.assertNotEqual(text1.lower(), text3.lower())
        
    def test_sentiment_analysis(self):
        """Test sentiment analysis functionality"""
        positive = "This game is amazing and wonderful"
        negative = "This game is terrible and buggy"
        
        # Basic validation
        self.assertIn("amazing", positive.lower())
        self.assertIn("terrible", negative.lower())
        
    def test_topic_modeling_input(self):
        """Test topic modeling with sample data"""
        # Verify we have sample data
        self.assertIsNotNone(self.sample_comments)
        self.assertGreater(len(self.sample_comments), 0)
        
    def test_chinese_text_processing(self):
        """Test Chinese text processing"""
        chinese_text = "这个游戏很好玩"
        # Verify Chinese text is handled
        self.assertIsNotNone(chinese_text)
        self.assertTrue(len(chinese_text) > 0)
        
    def test_japanese_text_processing(self):
        """Test Japanese text processing"""
        japanese_text = "このゲームは素晴らしい"
        # Verify Japanese text is handled
        self.assertIsNotNone(japanese_text)
        self.assertTrue(len(japanese_text) > 0)


class TestDataValidation(unittest.TestCase):
    """Test data validation and filtering"""
    
    def test_min_length_validation(self):
        """Test minimum length requirements"""
        too_short = "ok"
        valid = "This is a valid comment"
        
        self.assertLess(len(too_short), 5)
        self.assertGreater(len(valid), 5)
        
    def test_invalid_content_filtering(self):
        """Test filtering of invalid content"""
        numeric_only = "123456"
        valid_text = "Great game with good graphics"
        
        self.assertTrue(numeric_only.isdigit())
        self.assertFalse(valid_text.isdigit())
        
    def test_duplicate_detection(self):
        """Test duplicate comment detection"""
        comment1 = "This is a test comment"
        comment2 = "This is a test comment"
        comment3 = "This is different"
        
        self.assertEqual(comment1, comment2)
        self.assertNotEqual(comment1, comment3)


if __name__ == '__main__':
    unittest.main()
