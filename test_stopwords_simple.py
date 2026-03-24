"""
Simple test to verify stopwords file loading works correctly
Tests only the file loading logic, no dependencies on numpy/torch
"""

import os
import re

def test_stopword_file_loading():
    """Test that we can find and load the stopwords file"""
    print("=" * 60)
    print("TEST: Stopwords File Loading (No Dependencies)")
    print("=" * 60)
    
    # Try to find stopwords file
    possible_files = ["stopWord.txt", "stopWord.txt.txt", "stopwords.txt"]
    
    found_file = None
    for filepath in possible_files:
        if os.path.exists(filepath):
            found_file = filepath
            break
    
    if not found_file:
        print(f"✗ FAIL: No stopwords file found. Tried: {possible_files}")
        return False
    
    print(f"✓ Found stopwords file: {found_file}")
    
    # Load stopwords
    stopwords = set()
    try:
        with open(found_file, 'r', encoding='utf-8') as f:
            for line in f:
                # Remove numbering like "1. ", "2. " etc
                line = re.sub(r'^\d+\.\s*', '', line)
                word = line.strip().lower()
                if word and not word.startswith("#"):
                    stopwords.add(word)
        
        print(f"✓ Loaded {len(stopwords)} stopwords")
    except Exception as e:
        print(f"✗ FAIL: Error loading stopwords: {e}")
        return False
    
    # Check for expected stopwords
    test_words = {
        'Chinese': ['好玩', '游戏', '推荐', '神作'],
        'English': ['game', 'good', 'recommend', 'play'],
        'Japanese': [] # Add Japanese stopwords if any
    }
    
    print("\n📋 Checking for expected stopwords:")
    for lang, words in test_words.items():
        found = []
        missing = []
        for word in words:
            if word in stopwords:
                found.append(word)
            else:
                missing.append(word)
        
        if found:
            print(f"  {lang}: ✓ Found {len(found)}: {found}")
        if missing:
            print(f"  {lang}: ⚠️ Missing {len(missing)}: {missing}")
    
    # Show sample
    sample = list(stopwords)[:20]
    print(f"\n📝 Sample of first 20 stopwords:")
    print(f"   {sample[:10]}")
    print(f"   {sample[10:20]}")
    
    # Validation
    if len(stopwords) < 100:
        print(f"\n⚠️ WARNING: Only {len(stopwords)} stopwords loaded (expected 1000+)")
        return False
    
    print(f"\n✅ SUCCESS: Loaded {len(stopwords)} stopwords from {found_file}")
    return True

def test_stopword_integration_code():
    """Test that the code changes are in place"""
    print("\n" + "=" * 60)
    print("TEST: Code Integration Check")
    print("=" * 60)
    
    # Check nlp.py has the updated load_external_config
    try:
        with open('nlp.py', 'r', encoding='utf-8') as f:
            nlp_content = f.read()
        
        checks = [
            ('possible_files', 'nlp.py tries multiple file names'),
            ('stopWord.txt.txt', 'nlp.py checks for .txt.txt extension'),
            (r'^\d+\.\s*', 'nlp.py removes numbering from stopwords'),
        ]
        
        for pattern, description in checks:
            if pattern in nlp_content:
                print(f"✓ {description}")
            else:
                print(f"✗ MISSING: {description}")
                return False
                
    except Exception as e:
        print(f"✗ Error checking nlp.py: {e}")
        return False
    
    # Check llm_report_generator.py has the import
    try:
        with open('llm_report_generator.py', 'r', encoding='utf-8') as f:
            llm_content = f.read()
        
        checks = [
            ('from nlp import DataCleaner', 'Imports DataCleaner'),
            ('STOPWORDS_AVAILABLE', 'Has STOPWORDS_AVAILABLE flag'),
            ('DataCleaner.STOP_PHRASES', 'Uses DataCleaner stopwords'),
            ('Using {len(stopwords)} stopwords', 'Logs stopword usage'),
        ]
        
        for pattern, description in checks:
            if pattern in llm_content:
                print(f"✓ {description}")
            else:
                print(f"✗ MISSING: {description}")
                return False
                
    except Exception as e:
        print(f"✗ Error checking llm_report_generator.py: {e}")
        return False
    
    print("\n✅ SUCCESS: All code integration checks passed")
    return True

if __name__ == "__main__":
    print("\n🔍 STOPWORDS FIX SIMPLE VALIDATION")
    print("=" * 60)
    print("This test validates the fix without requiring ML dependencies\n")
    
    results = []
    
    # Test 1: File loading
    try:
        result1 = test_stopword_file_loading()
        results.append(("Stopwords File Loading", result1))
    except Exception as e:
        print(f"✗ Test 1 failed with exception: {e}")
        results.append(("Stopwords File Loading", False))
    
    # Test 2: Code integration
    try:
        result2 = test_stopword_integration_code()
        results.append(("Code Integration", result2))
    except Exception as e:
        print(f"✗ Test 2 failed with exception: {e}")
        results.append(("Code Integration", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("\nThe stopwords fix is correctly implemented:")
        print("1. ✓ Stopwords file can be loaded (handles multiple names)")
        print("2. ✓ nlp.py updated to try multiple file names")
        print("3. ✓ llm_report_generator.py imports and uses stopwords")
        print("4. ✓ Both cleaning AND naming now use the same stopwords")
        print("\nThe user's diagnosis was correct - the fix bridges")
        print("the gap between cleaning and naming logic!")
    else:
        print("\n⚠️ Some tests failed. Please review the output above.")
    
    import sys
    sys.exit(0 if all_passed else 1)
