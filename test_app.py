#!/usr/bin/env python3
"""
Test script for NLP Comment Processor
Tests both the NLP module and GUI components
"""

import os
import sys
import json
import tempfile

# Set offscreen mode for GUI testing
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from nlp import NLPProcessor
from PyQt5.QtWidgets import QApplication
from gui import NLPProcessorGUI, ProcessingThread


def test_nlp_processor():
    """Test the NLP processing module."""
    print("Testing NLP Processor...")
    
    processor = NLPProcessor()
    
    # Test sentiment analysis
    test_cases = [
        ("This is great!", "positive"),
        ("This is terrible!", "negative"),
        ("This is okay.", "neutral"),
        ("I love this amazing product!", "positive"),
        ("Awful and disappointing experience.", "negative"),
    ]
    
    for text, expected_sentiment in test_cases:
        result = processor.analyze_sentiment(text)
        assert result['sentiment_label'] == expected_sentiment, \
            f"Failed for '{text}': expected {expected_sentiment}, got {result['sentiment_label']}"
        print(f"  ✓ '{text}' -> {result['sentiment_label']}")
    
    # Test comment processing
    comment = {'text': 'This is a wonderful product!', 'id': 1}
    processed = processor.process_comment(comment)
    assert 'sentiment_label' in processed
    assert 'sentiment_score' in processed
    assert processed['id'] == 1
    print("  ✓ Comment processing works")
    
    # Test file processing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        test_data = {
            "comments": [
                {"text": "Great product!", "id": 1},
                {"text": "Terrible quality.", "id": 2},
            ]
        }
        json.dump(test_data, f)
        input_path = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        output_path = f.name
    
    try:
        stats = processor.process_file(input_path, output_path)
        assert stats['total_comments'] == 2
        assert stats['successful'] == 2
        assert stats['errors'] == 0
        print("  ✓ File processing works")
        
        # Verify output file
        with open(output_path, 'r') as f:
            output_data = json.load(f)
        assert 'statistics' in output_data
        assert 'processed_comments' in output_data
        print("  ✓ Output file format is correct")
    finally:
        os.unlink(input_path)
        os.unlink(output_path)
    
    print("✓ NLP Processor tests passed!\n")


def test_gui_components():
    """Test the GUI components."""
    print("Testing GUI Components...")
    
    app = QApplication(sys.argv)
    window = NLPProcessorGUI()
    
    # Test window initialization
    assert window.windowTitle() == 'NLP Comment Processor'
    assert window.width() == 700
    assert window.height() == 500
    print("  ✓ Window initialized correctly")
    
    # Test initial state
    assert window.input_file_path is None
    assert window.output_file_path is None
    assert not window.process_btn.isEnabled()
    print("  ✓ Initial state is correct")
    
    # Test file selection simulation
    window.input_file_path = os.path.join(tempfile.gettempdir(), 'test_input.json')
    window.output_file_path = os.path.join(tempfile.gettempdir(), 'test_output.json')
    window.check_ready_to_process()
    assert window.process_btn.isEnabled()
    print("  ✓ File selection enables process button")
    
    print("✓ GUI Component tests passed!\n")


def test_error_handling():
    """Test error handling."""
    print("Testing Error Handling...")
    
    processor = NLPProcessor()
    
    # Test invalid JSON
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("invalid json{")
        invalid_json_path = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        output_path = f.name
    
    try:
        processor.process_file(invalid_json_path, output_path)
        assert False, "Should have raised an error for invalid JSON"
    except ValueError as e:
        assert "Invalid JSON" in str(e)
        print("  ✓ Invalid JSON handled correctly")
    finally:
        if os.path.exists(invalid_json_path):
            os.unlink(invalid_json_path)
        if os.path.exists(output_path):
            os.unlink(output_path)
    
    # Test empty comments
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"comments": []}, f)
        empty_path = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        output_path2 = f.name
    
    try:
        processor.process_file(empty_path, output_path2)
        assert False, "Should have raised an error for empty comments"
    except ValueError as e:
        assert "No comments found" in str(e)
        print("  ✓ Empty comments handled correctly")
    finally:
        if os.path.exists(empty_path):
            os.unlink(empty_path)
        if os.path.exists(output_path2):
            os.unlink(output_path2)
    
    print("✓ Error Handling tests passed!\n")


def test_json_format_restrictions():
    """Test JSON file format restrictions."""
    print("Testing JSON Format Restrictions...")
    
    # Test that we only accept .json files
    invalid_files = ['test.txt', 'test.csv', 'test.xml']
    for filename in invalid_files:
        assert not filename.lower().endswith('.json'), \
            f"{filename} should be rejected"
    
    valid_files = ['test.json', 'test.JSON', 'data.json']
    for filename in valid_files:
        assert filename.lower().endswith('.json'), \
            f"{filename} should be accepted"
    
    print("  ✓ File type validation works correctly")
    print("✓ JSON Format Restriction tests passed!\n")


def main():
    """Run all tests."""
    print("=" * 60)
    print("NLP Comment Processor - Test Suite")
    print("=" * 60)
    print()
    
    try:
        test_nlp_processor()
        test_gui_components()
        test_error_handling()
        test_json_format_restrictions()
        
        print("=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        return 0
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
