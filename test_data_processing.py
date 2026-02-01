"""
Data Processing Tests - Requires numpy/pandas
==============================================
Tests data transformation and processing operations.
"""

import unittest
import sys

# Try to import required libraries
try:
    import numpy as np
    import pandas as pd
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False
    print("Skipping data processing tests - numpy/pandas not installed")


@unittest.skipUnless(HAS_DEPS, "Requires numpy and pandas")
class TestDataCleaning(unittest.TestCase):
    """Test data cleaning operations"""
    
    def test_dataframe_creation(self):
        """Test creating DataFrames"""
        data = {
            'text': ['Comment 1', 'Comment 2', 'Comment 3'],
            'score': [0.9, -0.3, 0.5],
            'lang': ['en', 'en', 'zh']
        }
        
        df = pd.DataFrame(data)
        self.assertEqual(len(df), 3)
        self.assertIn('text', df.columns)
    
    def test_dataframe_filtering(self):
        """Test filtering DataFrames"""
        df = pd.DataFrame({
            'text': ['Good', 'Bad', 'Great', 'Terrible'],
            'score': [0.8, -0.7, 0.9, -0.9]
        })
        
        positive = df[df['score'] > 0]
        negative = df[df['score'] < 0]
        
        self.assertEqual(len(positive), 2)
        self.assertEqual(len(negative), 2)
    
    def test_dataframe_sorting(self):
        """Test sorting DataFrames"""
        df = pd.DataFrame({
            'text': ['C', 'A', 'B'],
            'score': [0.5, 0.9, 0.3]
        })
        
        sorted_df = df.sort_values('score', ascending=False)
        self.assertEqual(sorted_df.iloc[0]['text'], 'A')
        self.assertEqual(sorted_df.iloc[-1]['text'], 'B')
    
    def test_missing_value_handling(self):
        """Test handling missing values"""
        df = pd.DataFrame({
            'text': ['A', None, 'C'],
            'score': [0.5, np.nan, 0.7]
        })
        
        # Check for missing values
        has_null = df.isnull().any().any()
        self.assertTrue(has_null)
        
        # Drop missing values
        clean_df = df.dropna()
        self.assertEqual(len(clean_df), 1)
    
    def test_dataframe_grouping(self):
        """Test grouping operations"""
        df = pd.DataFrame({
            'lang': ['en', 'zh', 'en', 'zh'],
            'score': [0.8, 0.9, 0.6, 0.7]
        })
        
        grouped = df.groupby('lang')['score'].mean()
        
        self.assertAlmostEqual(grouped['en'], 0.7)
        self.assertAlmostEqual(grouped['zh'], 0.8)


@unittest.skipUnless(HAS_DEPS, "Requires numpy and pandas")
class TestLanguageDetection(unittest.TestCase):
    """Test language detection logic"""
    
    def test_detect_chinese(self):
        """Test Chinese text detection"""
        texts = [
            '这个游戏很好玩',
            'This is English',
            '日本語テキスト'
        ]
        
        def has_chinese(text):
            return any('\u4e00' <= c <= '\u9fff' for c in text)
        
        results = [has_chinese(t) for t in texts]
        
        self.assertTrue(results[0])  # Chinese
        self.assertFalse(results[1])  # English
        self.assertFalse(results[2])  # Japanese
    
    def test_detect_japanese(self):
        """Test Japanese text detection"""
        texts = [
            '这个游戏很好玩',
            'This is English',
            'これは日本語です'
        ]
        
        def has_japanese(text):
            return any('\u3040' <= c <= '\u30ff' or '\u31f0' <= c <= '\u31ff' for c in text)
        
        results = [has_japanese(t) for t in texts]
        
        self.assertFalse(results[0])  # Chinese
        self.assertFalse(results[1])  # English
        self.assertTrue(results[2])   # Japanese
    
    def test_language_classification(self):
        """Test language classification"""
        def classify_language(text):
            if any('\u4e00' <= c <= '\u9fff' for c in text):
                return 'Chinese'
            elif any('\u3040' <= c <= '\u30ff' or '\u31f0' <= c <= '\u31ff' for c in text):
                return 'Japanese'
            else:
                return 'English'
        
        texts = {
            '游戏': 'Chinese',
            'ゲーム': 'Japanese',
            'Game': 'English'
        }
        
        for text, expected in texts.items():
            result = classify_language(text)
            self.assertEqual(result, expected)


@unittest.skipUnless(HAS_DEPS, "Requires numpy")
class TestNumpyOperations(unittest.TestCase):
    """Test numpy array operations"""
    
    def test_array_creation(self):
        """Test creating numpy arrays"""
        arr = np.array([1, 2, 3, 4, 5])
        self.assertEqual(len(arr), 5)
        self.assertEqual(arr[0], 1)
    
    def test_array_statistics(self):
        """Test statistical operations"""
        arr = np.array([1, 2, 3, 4, 5])
        
        mean = np.mean(arr)
        std = np.std(arr)
        
        self.assertEqual(mean, 3.0)
        self.assertAlmostEqual(std, 1.414, places=2)
    
    def test_array_normalization(self):
        """Test array normalization"""
        arr = np.array([1.0, 2.0, 3.0])
        
        # L2 normalization
        normalized = arr / np.linalg.norm(arr)
        norm = np.linalg.norm(normalized)
        
        self.assertAlmostEqual(norm, 1.0, places=6)
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation"""
        vec1 = np.array([1, 0, 0])
        vec2 = np.array([1, 0, 0])
        vec3 = np.array([0, 1, 0])
        
        # Cosine similarity
        sim_same = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        sim_diff = np.dot(vec1, vec3) / (np.linalg.norm(vec1) * np.linalg.norm(vec3))
        
        self.assertAlmostEqual(sim_same, 1.0)
        self.assertAlmostEqual(sim_diff, 0.0)


if __name__ == '__main__':
    unittest.main()
