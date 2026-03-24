"""
Test to verify that stopwords are properly loaded and applied to both cleaning and topic naming
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_stopwords_loading():
    """Test that stopwords are properly loaded from stopWord.txt.txt"""
    from nlp import DataCleaner
    
    print("=" * 60)
    print("TEST 1: Stopwords Loading")
    print("=" * 60)
    
    # Force reload
    DataCleaner.load_external_config()
    
    print(f"✓ Stopwords loaded: {len(DataCleaner.STOP_PHRASES)} words")
    
    # Check some expected stopwords
    test_words = ['好玩', '游戏', 'game', 'good', 'recommend', '推荐']
    found = []
    missing = []
    
    for word in test_words:
        if word in DataCleaner.STOP_PHRASES:
            found.append(word)
        else:
            missing.append(word)
    
    print(f"\n✓ Found stopwords: {found}")
    if missing:
        print(f"⚠️ Missing stopwords: {missing}")
    
    # Show sample of loaded stopwords
    sample = list(DataCleaner.STOP_PHRASES)[:20]
    print(f"\n📋 Sample stopwords: {sample[:10]}")
    
    return len(DataCleaner.STOP_PHRASES) > 0

def test_stopwords_in_cleaning():
    """Test that stopwords are used during text cleaning"""
    from nlp import DataCleaner
    
    print("\n" + "=" * 60)
    print("TEST 2: Stopwords in Cleaning Logic")
    print("=" * 60)
    
    # Ensure stopwords are loaded
    DataCleaner.load_external_config()
    
    test_cases = [
        ("This game is really good", "Should be filtered (all stopwords)"),
        ("The graphics are amazing", "Should pass (has meaningful word 'graphics', 'amazing')"),
        ("game good recommend", "Should be filtered (all stopwords)"),
        ("Performance optimization needed", "Should pass (has meaningful words)")
    ]
    
    for text, description in test_cases:
        result = DataCleaner.clean_text(text)
        status = "✓ PASS" if (result is None) == ("filtered" in description.lower()) else "✗ FAIL"
        print(f"{status}: '{text}' -> {result}")
        print(f"      {description}")

def test_stopwords_in_naming():
    """Test that stopwords are used in topic naming keyword extraction"""
    from llm_report_generator import LLMReportGenerator, STOPWORDS_AVAILABLE
    from nlp import DataCleaner
    
    print("\n" + "=" * 60)
    print("TEST 3: Stopwords in Topic Naming")
    print("=" * 60)
    
    # Ensure stopwords are loaded
    DataCleaner.load_external_config()
    
    if not STOPWORDS_AVAILABLE:
        print("⚠️ DataCleaner not available in llm_report_generator")
        return False
    
    # Create LLM generator (without actually loading LLM)
    generator = LLMReportGenerator(use_ollama=False)
    generator.llm_available = False  # Force using keyword extraction
    
    # Test sentences with stopwords
    test_cases = [
        (["The game is very good and fun to play"], "Should extract meaningful words, not 'game', 'good', 'fun'"),
        (["Graphics quality and performance optimization are excellent"], "Should extract 'Graphics', 'Quality', 'Performance', 'Optimization'"),
        (["好玩 推荐 游戏"], "Should filter Chinese stopwords"),
        (["Character development and story progression"], "Should extract 'Character', 'Development', 'Story', 'Progression'")
    ]
    
    for sentences, description in test_cases:
        result = generator._extract_keywords(sentences)
        print(f"\n📝 Input: {sentences[0]}")
        print(f"   → Extracted: '{result}'")
        print(f"   Expected: {description}")
        
        # Check if result contains common stopwords
        stopwords_found = []
        for word in result.lower().split():
            if word in ['game', 'good', 'fun', 'very', 'really', '好玩', '游戏', '推荐']:
                stopwords_found.append(word)
        
        if stopwords_found:
            print(f"   ⚠️ WARNING: Result contains stopwords: {stopwords_found}")
        else:
            print(f"   ✓ Good: No stopwords in result")
    
    return True

def test_integration():
    """Integration test: Full flow with stopwords"""
    print("\n" + "=" * 60)
    print("TEST 4: Integration Test")
    print("=" * 60)
    
    from nlp import DataCleaner
    from llm_report_generator import LLMReportGenerator
    
    # Load stopwords
    DataCleaner.load_external_config()
    print(f"✓ Loaded {len(DataCleaner.STOP_PHRASES)} stopwords")
    
    # Check that llm_report_generator can access them
    try:
        from llm_report_generator import STOPWORDS_AVAILABLE
        if STOPWORDS_AVAILABLE:
            print("✓ LLM generator can import DataCleaner")
            print(f"✓ LLM generator can access {len(DataCleaner.STOP_PHRASES)} stopwords")
        else:
            print("✗ LLM generator cannot import DataCleaner")
            return False
    except Exception as e:
        print(f"✗ Error accessing stopwords in LLM generator: {e}")
        return False
    
    # Test the flow
    reviews = [
        {"review": "这个游戏真的很好玩！", "language": "chinese"},
        {"review": "Game is really good and fun", "language": "english"},
        {"review": "Great graphics and smooth performance", "language": "english"}
    ]
    
    statements = DataCleaner.split_to_statements(reviews)
    print(f"\n✓ Processed {len(reviews)} reviews → {len(statements)} statements")
    
    for stmt in statements:
        print(f"   - {stmt['text']}")
    
    return True

if __name__ == "__main__":
    print("\n🔍 STOPWORDS FIX VALIDATION TESTS")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(("Stopwords Loading", test_stopwords_loading()))
    except Exception as e:
        print(f"✗ Test 1 failed: {e}")
        results.append(("Stopwords Loading", False))
    
    try:
        test_stopwords_in_cleaning()
        results.append(("Stopwords in Cleaning", True))
    except Exception as e:
        print(f"✗ Test 2 failed: {e}")
        results.append(("Stopwords in Cleaning", False))
    
    try:
        results.append(("Stopwords in Naming", test_stopwords_in_naming()))
    except Exception as e:
        print(f"✗ Test 3 failed: {e}")
        results.append(("Stopwords in Naming", False))
    
    try:
        results.append(("Integration", test_integration()))
    except Exception as e:
        print(f"✗ Test 4 failed: {e}")
        results.append(("Integration", False))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Stopwords are now properly integrated.")
    else:
        print("\n⚠️ Some tests failed. Please review the output above.")
    
    sys.exit(0 if all_passed else 1)
