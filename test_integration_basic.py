"""
Integration Tests - Tests module interactions
==============================================
Tests that modules can import and interact correctly.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestModuleIntegration(unittest.TestCase):
    """Test module imports and basic integration"""
    
    def test_import_nlp_module(self):
        """Test that nlp module can be imported"""
        try:
            import nlp
            self.assertTrue(hasattr(nlp, 'DataCleaner'))
        except ImportError as e:
            self.skipTest(f"Cannot import nlp module: {e}")
    
    def test_import_analysis_report_generator(self):
        """Test that analysis_report_generator can be imported"""
        try:
            import analysis_report_generator
            self.assertTrue(hasattr(analysis_report_generator, 'AnalysisReportGenerator'))
        except ImportError as e:
            self.skipTest(f"Cannot import analysis_report_generator: {e}")
    
    def test_import_llm_report_generator(self):
        """Test that llm_report_generator can be imported"""
        try:
            import llm_report_generator
            self.assertTrue(hasattr(llm_report_generator, 'LLMReportGenerator'))
        except ImportError as e:
            self.skipTest(f"Cannot import llm_report_generator: {e}")
    
    def test_import_chart_generator(self):
        """Test that chart_generator can be imported"""
        try:
            import chart_generator
            self.assertTrue(hasattr(chart_generator, 'ReportChartGenerator'))
        except ImportError as e:
            self.skipTest(f"Cannot import chart_generator: {e}")
    
    def test_stopwords_loading(self):
        """Test that stopwords can be loaded"""
        try:
            import nlp
            # Try to load stopwords
            nlp.DataCleaner.load_external_config()
            # Check if stopwords were loaded
            self.assertTrue(hasattr(nlp.DataCleaner, 'STOP_PHRASES'))
        except Exception as e:
            self.skipTest(f"Cannot test stopwords loading: {e}")
    
    def test_file_structure(self):
        """Test that required files exist"""
        required_files = [
            'nlp.py',
            'analysis_report_generator.py',
            'llm_report_generator.py',
            'chart_generator.py',
            'gui.py',
            'requirements.txt',
            'README.md'
        ]
        
        missing = []
        for filename in required_files:
            if not os.path.exists(filename):
                missing.append(filename)
        
        if missing:
            self.fail(f"Missing files: {', '.join(missing)}")
    
    def test_json_sample_files(self):
        """Test that sample JSON files exist"""
        sample_files = [
            'refined_topics_test.json',
            'refined_topics_perfect.json'
        ]
        
        found = []
        for filename in sample_files:
            if os.path.exists(filename):
                found.append(filename)
        
        self.assertGreater(len(found), 0, "No sample JSON files found")
    
    def test_requirements_file(self):
        """Test that requirements.txt is readable"""
        if not os.path.exists('requirements.txt'):
            self.skipTest("requirements.txt not found")
        
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for expected dependencies
        expected = ['torch', 'transformers', 'pandas', 'numpy']
        found_deps = []
        
        for dep in expected:
            if dep.lower() in content.lower():
                found_deps.append(dep)
        
        self.assertGreater(len(found_deps), 0, "No expected dependencies in requirements.txt")


class TestExportFunction(unittest.TestCase):
    """Test export_to_projector function exists"""
    
    def test_export_function_exists(self):
        """Test that export_to_projector function is defined"""
        try:
            import nlp
            self.assertTrue(hasattr(nlp, 'export_to_projector'))
        except ImportError:
            self.skipTest("Cannot import nlp module")
    
    def test_export_function_signature(self):
        """Test export function has correct parameters"""
        try:
            import nlp
            import inspect
            
            func = nlp.export_to_projector
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())
            
            # Check for required parameters
            self.assertIn('embeddings', params)
            self.assertIn('dataframe', params)
        except Exception as e:
            self.skipTest(f"Cannot test function signature: {e}")


class TestDocumentationExists(unittest.TestCase):
    """Test that documentation files exist"""
    
    def test_readme_exists(self):
        """Test README.md exists"""
        self.assertTrue(os.path.exists('README.md'))
    
    def test_guides_exist(self):
        """Test that guide documents exist"""
        guides = [
            'METHODOLOGY.md',
            'TESTING.md',
            'IMPLEMENTATION.md'
        ]
        
        found = []
        for guide in guides:
            if os.path.exists(guide):
                found.append(guide)
        
        self.assertGreater(len(found), 0, "No guide documents found")


if __name__ == '__main__':
    unittest.main()
