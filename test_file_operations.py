"""
File Operations Tests - Tests file I/O without ML dependencies
===============================================================
Tests JSON loading/saving, file validation, and path operations.
"""

import unittest
import json
import os
import tempfile
import shutil


class TestFileOperations(unittest.TestCase):
    """Test file I/O operations"""
    
    def setUp(self):
        """Create temporary directory for tests"""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, 'test.json')
    
    def tearDown(self):
        """Clean up temporary files"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_json_file_write_read(self):
        """Test writing and reading JSON files"""
        data = {
            'comments': [
                {'text': 'Great game!', 'score': 0.9},
                {'text': 'Too buggy', 'score': -0.5}
            ]
        }
        
        # Write
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        self.assertTrue(os.path.exists(self.test_file))
        
        # Read
        with open(self.test_file, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        
        self.assertEqual(len(loaded['comments']), 2)
        self.assertEqual(loaded['comments'][0]['text'], 'Great game!')
    
    def test_unicode_file_handling(self):
        """Test handling files with Unicode content"""
        data = {
            'chinese': '这个游戏很好玩',
            'japanese': 'ゲームは素晴らしい',
            'korean': '게임이 훌륭합니다'
        }
        
        # Write with Unicode
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        
        # Read back
        with open(self.test_file, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        
        self.assertEqual(loaded['chinese'], data['chinese'])
        self.assertEqual(loaded['japanese'], data['japanese'])
        self.assertEqual(loaded['korean'], data['korean'])
    
    def test_file_existence_check(self):
        """Test file existence validation"""
        # Non-existent file
        self.assertFalse(os.path.exists('nonexistent_file.json'))
        
        # Create file
        with open(self.test_file, 'w') as f:
            f.write('{}')
        
        # Now it exists
        self.assertTrue(os.path.exists(self.test_file))
    
    def test_directory_creation(self):
        """Test creating directories"""
        new_dir = os.path.join(self.test_dir, 'subdir', 'nested')
        
        # Create nested directories
        os.makedirs(new_dir, exist_ok=True)
        
        self.assertTrue(os.path.exists(new_dir))
        self.assertTrue(os.path.isdir(new_dir))
    
    def test_file_size_check(self):
        """Test file size validation"""
        # Write some data
        data = {'test': 'x' * 1000}
        with open(self.test_file, 'w') as f:
            json.dump(data, f)
        
        # Check size
        file_size = os.path.getsize(self.test_file)
        self.assertGreater(file_size, 0)
        self.assertGreater(file_size, 1000)  # Should be > 1KB
    
    def test_empty_json_handling(self):
        """Test handling empty JSON files"""
        # Write empty object
        with open(self.test_file, 'w') as f:
            json.dump({}, f)
        
        # Read back
        with open(self.test_file, 'r') as f:
            loaded = json.load(f)
        
        self.assertIsInstance(loaded, dict)
        self.assertEqual(len(loaded), 0)
    
    def test_json_array_file(self):
        """Test JSON array file operations"""
        comments = [
            'First comment',
            'Second comment',
            'Third comment'
        ]
        
        with open(self.test_file, 'w') as f:
            json.dump(comments, f)
        
        with open(self.test_file, 'r') as f:
            loaded = json.load(f)
        
        self.assertIsInstance(loaded, list)
        self.assertEqual(len(loaded), 3)


class TestPathOperations(unittest.TestCase):
    """Test path manipulation"""
    
    def test_path_joining(self):
        """Test joining path components"""
        path = os.path.join('dir', 'subdir', 'file.txt')
        self.assertIn('dir', path)
        self.assertIn('file.txt', path)
    
    def test_path_splitting(self):
        """Test splitting paths"""
        path = '/home/user/data/file.json'
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)
        
        self.assertEqual(dirname, '/home/user/data')
        self.assertEqual(basename, 'file.json')
    
    def test_file_extension_extraction(self):
        """Test extracting file extensions"""
        filename = 'analysis_report.json'
        name, ext = os.path.splitext(filename)
        
        self.assertEqual(name, 'analysis_report')
        self.assertEqual(ext, '.json')
    
    def test_absolute_path_conversion(self):
        """Test converting to absolute path"""
        relative = 'test.txt'
        absolute = os.path.abspath(relative)
        
        self.assertTrue(os.path.isabs(absolute))
        self.assertIn('test.txt', absolute)


class TestCSVOperations(unittest.TestCase):
    """Test CSV file operations (using simple text operations)"""
    
    def setUp(self):
        """Create temporary directory"""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, 'test.csv')
    
    def tearDown(self):
        """Clean up"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_tsv_write_read(self):
        """Test TSV (tab-separated values) operations"""
        # Write TSV
        lines = [
            "id\ttext\tscore",
            "1\tGreat game\t0.9",
            "2\tToo buggy\t-0.5"
        ]
        
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        # Read TSV
        with open(self.test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn('\t', content)
        self.assertIn('Great game', content)
        
        # Parse lines
        lines_read = content.strip().split('\n')
        self.assertEqual(len(lines_read), 3)
        
        # Parse first data row
        row = lines_read[1].split('\t')
        self.assertEqual(row[0], '1')
        self.assertEqual(row[1], 'Great game')
    
    def test_tsv_unicode_handling(self):
        """Test TSV with Unicode content"""
        lines = [
            "text\tlanguage",
            "这是中文\tChinese",
            "これは日本語\tJapanese"
        ]
        
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        with open(self.test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn('这是中文', content)
        self.assertIn('これは日本語', content)


if __name__ == '__main__':
    unittest.main()
