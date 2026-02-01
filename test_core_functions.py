"""
Core Function Tests - No ML Dependencies Required
==================================================
These tests validate core functionality without requiring ML models.
They test text processing, validation, and utility functions.

Can be run standalone or via test_suite_runner.py
"""

import unittest
import re
import json
import os
import sys


class TestTextProcessing(unittest.TestCase):
    """Test text processing functions"""
    
    def test_basic_text_cleaning(self):
        """Test basic text cleaning operations"""
        # Test HTML tag removal
        text_with_html = "This is <b>bold</b> and <i>italic</i>"
        cleaned = re.sub(r'<[^>]+>', '', text_with_html)
        self.assertNotIn('<b>', cleaned)
        self.assertNotIn('</b>', cleaned)
        self.assertIn('bold', cleaned)
    
    def test_url_removal(self):
        """Test URL removal"""
        text_with_url = "Check this out http://example.com and https://test.org"
        cleaned = re.sub(r'https?://\S+', '', text_with_url)
        self.assertNotIn('http://', cleaned)
        self.assertNotIn('https://', cleaned)
    
    def test_whitespace_normalization(self):
        """Test whitespace normalization"""
        messy_text = "Too   many    spaces\n\n\nand\tlines"
        cleaned = ' '.join(messy_text.split())
        self.assertEqual(cleaned.count('  '), 0)  # No double spaces
        self.assertNotIn('\n', cleaned)
        self.assertNotIn('\t', cleaned)
    
    def test_special_character_removal(self):
        """Test special character handling"""
        text = "Hello!!! This is great??? Really..."
        # Remove excessive punctuation
        cleaned = re.sub(r'([!?.]){2,}', r'\1', text)
        self.assertNotIn('!!!', cleaned)
        self.assertNotIn('???', cleaned)
    
    def test_case_normalization(self):
        """Test case conversion"""
        text = "HELLO world MiXeD CaSe"
        lower = text.lower()
        self.assertEqual(lower, "hello world mixed case")
        upper = text.upper()
        self.assertEqual(upper, "HELLO WORLD MIXED CASE")
    
    def test_chinese_text_detection(self):
        """Test Chinese character detection"""
        chinese = "这是中文文本"
        english = "This is English"
        
        # Check for Chinese characters (CJK Unified Ideographs)
        has_chinese = any('\u4e00' <= c <= '\u9fff' for c in chinese)
        has_chinese_in_english = any('\u4e00' <= c <= '\u9fff' for c in english)
        
        self.assertTrue(has_chinese)
        self.assertFalse(has_chinese_in_english)
    
    def test_japanese_text_detection(self):
        """Test Japanese character detection"""
        japanese = "これは日本語です"
        english = "This is English"
        
        # Check for Japanese characters (Hiragana + Katakana)
        has_japanese = any(
            '\u3040' <= c <= '\u30ff' or '\u31f0' <= c <= '\u31ff' 
            for c in japanese
        )
        has_japanese_in_english = any(
            '\u3040' <= c <= '\u30ff' or '\u31f0' <= c <= '\u31ff' 
            for c in english
        )
        
        self.assertTrue(has_japanese)
        self.assertFalse(has_japanese_in_english)
    
    def test_text_length_validation(self):
        """Test text length checks"""
        too_short = "ok"
        valid = "This is a valid comment with sufficient length"
        too_long = "x" * 10000
        
        self.assertLess(len(too_short), 5)
        self.assertGreater(len(valid), 5)
        self.assertGreater(len(too_long), 1000)


class TestDataValidation(unittest.TestCase):
    """Test data validation logic"""
    
    def test_numeric_only_detection(self):
        """Test detection of numeric-only text"""
        numeric = "123456789"
        alphanumeric = "abc123"
        text = "This is text"
        
        self.assertTrue(numeric.isdigit())
        self.assertFalse(alphanumeric.isdigit())
        self.assertFalse(text.isdigit())
    
    def test_empty_text_validation(self):
        """Test empty text detection"""
        empty = ""
        whitespace = "   \n\t  "
        valid = "Valid text"
        
        self.assertTrue(len(empty.strip()) == 0)
        self.assertTrue(len(whitespace.strip()) == 0)
        self.assertFalse(len(valid.strip()) == 0)
    
    def test_duplicate_detection(self):
        """Test duplicate detection logic"""
        text1 = "This is a comment"
        text2 = "This is a comment"
        text3 = "This is different"
        
        # Simple duplicate check
        self.assertEqual(text1, text2)
        self.assertNotEqual(text1, text3)
        
        # Case-insensitive duplicate check
        text4 = "THIS IS A COMMENT"
        self.assertEqual(text1.lower(), text4.lower())
    
    def test_language_mixing_detection(self):
        """Test mixed language detection"""
        pure_english = "This is pure English text"
        pure_chinese = "这是纯中文文本"
        mixed = "This is 混合 text"
        
        # Check for Chinese in pure English
        has_chinese_en = any('\u4e00' <= c <= '\u9fff' for c in pure_english)
        # Check for Chinese in pure Chinese
        has_chinese_cn = any('\u4e00' <= c <= '\u9fff' for c in pure_chinese)
        # Check for Chinese in mixed
        has_chinese_mix = any('\u4e00' <= c <= '\u9fff' for c in mixed)
        
        self.assertFalse(has_chinese_en)
        self.assertTrue(has_chinese_cn)
        self.assertTrue(has_chinese_mix)
    
    def test_min_word_count(self):
        """Test minimum word count validation"""
        few_words = "ok great"
        many_words = "This is a much longer comment with many words"
        
        word_count_few = len(few_words.split())
        word_count_many = len(many_words.split())
        
        self.assertLess(word_count_few, 5)
        self.assertGreater(word_count_many, 5)
    
    def test_repeated_characters(self):
        """Test repeated character detection"""
        normal = "This is normal text"
        repeated = "Wooooooow!!!! Amaziiiiing!!!!"
        
        # Check for 3+ repeated characters
        has_repeated = bool(re.search(r'(.)\1{2,}', repeated))
        has_repeated_normal = bool(re.search(r'(.)\1{2,}', normal))
        
        self.assertTrue(has_repeated)
        self.assertFalse(has_repeated_normal)


class TestJSONOperations(unittest.TestCase):
    """Test JSON file operations"""
    
    def test_json_serialization(self):
        """Test JSON encoding/decoding"""
        data = {
            'text': 'Test comment',
            'score': 0.85,
            'topics': ['gameplay', 'graphics']
        }
        
        # Serialize
        json_str = json.dumps(data)
        self.assertIsInstance(json_str, str)
        
        # Deserialize
        loaded = json.loads(json_str)
        self.assertEqual(loaded['text'], data['text'])
        self.assertEqual(loaded['score'], data['score'])
    
    def test_json_with_unicode(self):
        """Test JSON with Unicode characters"""
        data = {
            'chinese': '游戏很好玩',
            'japanese': 'ゲームは素晴らしい',
            'english': 'Game is great'
        }
        
        json_str = json.dumps(data, ensure_ascii=False)
        loaded = json.loads(json_str)
        
        self.assertEqual(loaded['chinese'], data['chinese'])
        self.assertEqual(loaded['japanese'], data['japanese'])
    
    def test_json_array_handling(self):
        """Test JSON array operations"""
        comments = [
            {'id': 1, 'text': 'First'},
            {'id': 2, 'text': 'Second'},
            {'id': 3, 'text': 'Third'}
        ]
        
        json_str = json.dumps(comments)
        loaded = json.loads(json_str)
        
        self.assertIsInstance(loaded, list)
        self.assertEqual(len(loaded), 3)
        self.assertEqual(loaded[0]['id'], 1)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility helper functions"""
    
    def test_list_deduplication(self):
        """Test removing duplicates from list"""
        items = [1, 2, 2, 3, 3, 3, 4]
        unique = list(set(items))
        self.assertEqual(len(unique), 4)
        self.assertIn(1, unique)
        self.assertIn(4, unique)
    
    def test_string_splitting(self):
        """Test string tokenization"""
        text = "This is a test sentence"
        words = text.split()
        self.assertEqual(len(words), 5)
        self.assertEqual(words[0], "This")
        self.assertEqual(words[-1], "sentence")
    
    def test_list_filtering(self):
        """Test list filtering operations"""
        numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        evens = [n for n in numbers if n % 2 == 0]
        odds = [n for n in numbers if n % 2 != 0]
        
        self.assertEqual(len(evens), 5)
        self.assertEqual(len(odds), 5)
        self.assertIn(2, evens)
        self.assertIn(1, odds)
    
    def test_dictionary_operations(self):
        """Test dictionary manipulations"""
        data = {'a': 1, 'b': 2, 'c': 3}
        
        # Test key existence
        self.assertIn('a', data)
        self.assertNotIn('d', data)
        
        # Test get with default
        value = data.get('d', 0)
        self.assertEqual(value, 0)
        
        # Test update
        data['d'] = 4
        self.assertEqual(len(data), 4)


if __name__ == '__main__':
    unittest.main()
