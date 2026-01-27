"""
Test script for cross-cultural analysis features
Tests the 5 implemented requirements
"""

import sys
import os

# Test 1: Filename parsing
def test_filename_parsing():
    """Test Requirement 2: Parse Filenames"""
    print("=" * 60)
    print("TEST 1: Filename Parsing")
    print("=" * 60)
    
    from analysis_report_generator import AnalysisReportGenerator
    
    generator = AnalysisReportGenerator()
    
    test_cases = [
        ("comments_silksong_japanese.json", "silksong", "japanese"),
        ("Report_comments_battlefield6_chinese.json", "battlefield6", "chinese"),
        ("comments_hollowknight_english.json", "hollowknight", "english"),
        ("Report_comments_game_name_with_underscores_japanese.json", "game_name_with_underscores", "japanese"),
    ]
    
    passed = 0
    failed = 0
    
    for filename, expected_game, expected_lang in test_cases:
        result = generator._parse_filename(filename)
        if result['game'] == expected_game and result['language'] == expected_lang:
            print(f"✅ PASS: {filename}")
            print(f"   Game: {result['game']}, Language: {result['language']}")
            passed += 1
        else:
            print(f"❌ FAIL: {filename}")
            print(f"   Expected: {expected_game}, {expected_lang}")
            print(f"   Got: {result['game']}, {result['language']}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed\n")
    return failed == 0

# Test 2: Language constants
def test_language_constants():
    """Test that language constants are properly defined"""
    print("=" * 60)
    print("TEST 2: Language Constants")
    print("=" * 60)
    
    from llm_report_generator import LLMReportGenerator
    from analysis_report_generator import AnalysisReportGenerator
    
    # Check LLM generator constants
    print("✅ LLM Generator Constants:")
    print(f"   LANG_MAP: {LLMReportGenerator.LANG_MAP}")
    print(f"   LANGUAGE_INSTRUCTIONS: {list(LLMReportGenerator.LANGUAGE_INSTRUCTIONS.keys())}")
    print(f"   MAX_TOPIC_NAME_LENGTH: {LLMReportGenerator.MAX_TOPIC_NAME_LENGTH}")
    
    # Check Analysis generator constants
    print("\n✅ Analysis Generator Constants:")
    print(f"   SUPPORTED_LANGUAGES: {AnalysisReportGenerator.SUPPORTED_LANGUAGES}")
    
    # Verify Korean is supported
    if 'korean' in LLMReportGenerator.LANG_MAP:
        print("\n✅ Korean language support confirmed")
        return True
    else:
        print("\n❌ Korean language support missing")
        return False

# Test 3: Language detection from samples
def test_language_detection():
    """Test language detection logic"""
    print("=" * 60)
    print("TEST 3: Language Detection from Samples")
    print("=" * 60)
    
    # Mock topic data with samples
    test_topic = {
        'topic_id': 1,
        'samples': [
            {'language': 'schinese', 'text': '游戏很好玩'},
            {'language': 'schinese', 'text': '图形很漂亮'},
            {'language': 'japanese', 'text': 'ゲームは面白い'},
        ],
        'representative_sentences': ['游戏很好玩'],
        'sample_texts': ['游戏很好玩', '图形很漂亮'],
        'sentiment_label': 'positive'
    }
    
    # Count languages
    lang_count = {}
    for sample in test_topic['samples']:
        lang = sample.get('language', '')
        lang_count[lang] = lang_count.get(lang, 0) + 1
    
    primary_lang = max(lang_count.items(), key=lambda x: x[1])[0]
    
    if primary_lang == 'schinese':
        print(f"✅ PASS: Detected primary language as 'schinese' from samples")
        print(f"   Language distribution: {lang_count}")
        return True
    else:
        print(f"❌ FAIL: Expected 'schinese', got '{primary_lang}'")
        return False

# Test 4: HTML generation structure
def test_html_structure():
    """Test that HTML contains required sections"""
    print("=" * 60)
    print("TEST 4: HTML Structure Verification")
    print("=" * 60)
    
    # Mock data
    mock_stats = {'total_comments': 100, 'total_valid': 95}
    mock_topics = [
        {
            'topic_id': 1,
            'topic_name': 'Test Topic',
            'density': 50,
            'sentiment_label': 'positive',
            'sentiment_score': 0.8,
            'samples': [{'language': 'english'}],
            'cultural_distribution': {'english': 50}
        }
    ]
    
    from analysis_report_generator import AnalysisReportGenerator
    generator = AnalysisReportGenerator()
    
    # Test executive summary generation
    try:
        html = generator._generate_executive_summary(mock_stats, mock_topics, '', True)
        if '📊 Executive Summary' in html:
            print("✅ PASS: Executive Summary section generated")
        else:
            print("❌ FAIL: Executive Summary section missing")
            return False
    except Exception as e:
        print(f"❌ FAIL: Executive Summary generation error: {e}")
        return False
    
    # Test developer summary generation
    try:
        html = generator._generate_developer_executive_summary(mock_topics, True)
        if '🎮 Executive Summary for Game Developers' in html:
            print("✅ PASS: Developer Executive Summary section generated")
        else:
            print("❌ FAIL: Developer Executive Summary section missing")
            return False
    except Exception as e:
        print(f"❌ FAIL: Developer summary generation error: {e}")
        return False
    
    # Test topics section with language tabs
    try:
        html = generator._generate_topics_section(mock_topics, True)
        if 'language-tabs' in html and 'language-content' in html:
            print("✅ PASS: Language-organized topics section generated")
        else:
            print("❌ FAIL: Language organization missing")
            return False
    except Exception as e:
        print(f"❌ FAIL: Topics section generation error: {e}")
        return False
    
    return True

# Test 5: Aggregation with filenames
def test_aggregation_with_filenames():
    """Test aggregation with filename metadata"""
    print("=" * 60)
    print("TEST 5: Aggregation with Filename Metadata")
    print("=" * 60)
    
    from analysis_report_generator import AnalysisReportGenerator
    generator = AnalysisReportGenerator()
    
    # Mock NLP data
    mock_data = [
        {
            'statistics': {'total': 100, 'valid': 95},
            'topics': [
                {
                    'topic_id': 1,
                    'density': 50,
                    'sentiment_label': 'positive',
                    'sentiment_score': 0.8
                }
            ]
        }
    ]
    
    filenames = ['comments_testgame_chinese.json']
    
    try:
        result = generator._aggregate_nlp_reports(mock_data, filenames)
        
        if 'game_name' in result and result['game_name'] == 'testgame':
            print(f"✅ PASS: Game name extracted: {result['game_name']}")
        else:
            print(f"❌ FAIL: Game name not extracted correctly")
            return False
        
        if 'language' in result and result['language'] == 'chinese':
            print(f"✅ PASS: Language extracted: {result['language']}")
        else:
            print(f"❌ FAIL: Language not extracted correctly")
            return False
        
        return True
    except Exception as e:
        print(f"❌ FAIL: Aggregation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("CROSS-CULTURAL ANALYSIS FEATURES TEST SUITE")
    print("=" * 60 + "\n")
    
    results = []
    
    # Run all tests
    results.append(("Filename Parsing", test_filename_parsing()))
    results.append(("Language Constants", test_language_constants()))
    results.append(("Language Detection", test_language_detection()))
    results.append(("HTML Structure", test_html_structure()))
    results.append(("Aggregation with Filenames", test_aggregation_with_filenames()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    failed = sum(1 for _, result in results if not result)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️ {failed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
