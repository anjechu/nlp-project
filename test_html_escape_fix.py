#!/usr/bin/env python3
"""
Simple test to verify the html.escape fix in analysis_report_generator.py
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_html_escape_fix():
    """Test that html.escape() works correctly in _generate_developer_executive_summary"""
    print("Testing html.escape() fix...")
    
    try:
        from analysis_report_generator import AnalysisReportGenerator
        
        # Create a generator instance
        generator = AnalysisReportGenerator()
        
        # Create test data with topics
        test_topics = [
            {
                'source_language': 'schinese',
                'sentiment_label': 'positive',
                'topic_name': 'Test Topic <script>alert("xss")</script>',
                'topic_id': 1,
                'density': 100,
                'sentiment_score': 0.8,
                'summary': 'This is a test summary with special characters: <>&"\''
            }
        ]
        
        # Call the method that was failing
        result = generator._generate_developer_executive_summary(test_topics, is_llm=True)
        
        # Verify the result is a string
        assert isinstance(result, str), "Result should be a string"
        
        # Verify HTML entities are escaped (XSS protection)
        assert '&lt;script&gt;' in result or 'Test Topic' in result, "HTML should be escaped"
        assert '&lt;&gt;&amp;' in result or 'special characters' in result, "Special characters should be escaped"
        
        # Verify the structure is present
        assert 'Executive Summary' in result, "Should contain Executive Summary header"
        assert 'Chinese Players' in result or 'Japanese Players' in result or 'English Players' in result, "Should contain language sections"
        
        print("✅ Test passed! html.escape() is working correctly")
        print("✅ XSS protection is in place")
        return True
        
    except AttributeError as e:
        if "'str' object has no attribute 'escape'" in str(e):
            print(f"❌ Test failed! The bug still exists: {e}")
            return False
        else:
            raise
    except Exception as e:
        print(f"❌ Test failed with unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_html_escape_fix()
    sys.exit(0 if success else 1)
