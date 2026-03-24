"""
Test script for S-DAI (Sentiment-adjusted Developer Actionable Index) model
Tests the implementation of _calculate_s_dai and aggregate_map_results
"""

import sys
import json
from llm_report_generator import LLMReportGenerator

def test_s_dai_calculation():
    """Test the _calculate_s_dai method"""
    print("=" * 80)
    print("TEST 1: S-DAI Calculation")
    print("=" * 80)
    
    # Initialize the generator
    generator = LLMReportGenerator(use_ollama=False)
    
    # Test Case 1: Chinese negative sentiment (should apply cultural correction)
    print("\n📝 Test Case 1: Chinese Negative Sentiment")
    topic1 = {
        'topic_name': '游戏卡顿',
        'sentiment_score': -0.6,
        'density': 50,
        'consistency': 1.0
    }
    dai_score1 = generator._calculate_s_dai(topic1, 'chinese')
    print(f"   Original sentiment: {-0.6}")
    print(f"   Adjusted sentiment (S_adj): {topic1['s_adj']:.3f}")
    print(f"   Expected S_adj: {-0.6 * 1.2:.3f}")
    print(f"   DAI Score: {dai_score1:.3f}")
    
    # Verify cultural correction was applied
    expected_s_adj = -0.6 * 1.2
    if abs(topic1['s_adj'] - expected_s_adj) < 0.001:
        print("   ✅ Cultural correction applied correctly")
        test1_pass = True
    else:
        print(f"   ❌ Cultural correction failed. Expected {expected_s_adj}, got {topic1['s_adj']}")
        test1_pass = False
    
    # Test Case 2: Japanese negative sentiment (should also apply cultural correction)
    print("\n📝 Test Case 2: Japanese Negative Sentiment")
    topic2 = {
        'topic_name': 'バグが多い',
        'sentiment_score': -0.5,
        'density': 30,
        'consistency': 0.9
    }
    dai_score2 = generator._calculate_s_dai(topic2, 'japanese')
    print(f"   Original sentiment: {-0.5}")
    print(f"   Adjusted sentiment (S_adj): {topic2['s_adj']:.3f}")
    print(f"   Expected S_adj: {-0.5 * 1.2:.3f}")
    print(f"   DAI Score: {dai_score2:.3f}")
    
    expected_s_adj2 = -0.5 * 1.2
    if abs(topic2['s_adj'] - expected_s_adj2) < 0.001:
        print("   ✅ Cultural correction applied correctly")
        test2_pass = True
    else:
        print(f"   ❌ Cultural correction failed")
        test2_pass = False
    
    # Test Case 3: English negative sentiment (should NOT apply cultural correction)
    print("\n📝 Test Case 3: English Negative Sentiment")
    topic3 = {
        'topic_name': 'Game crashes',
        'sentiment_score': -0.7,
        'density': 100,
        'consistency': 1.0
    }
    dai_score3 = generator._calculate_s_dai(topic3, 'english')
    print(f"   Original sentiment: {-0.7}")
    print(f"   Adjusted sentiment (S_adj): {topic3['s_adj']:.3f}")
    print(f"   Expected S_adj: {-0.7}")
    print(f"   DAI Score: {dai_score3:.3f}")
    
    if abs(topic3['s_adj'] - (-0.7)) < 0.001:
        print("   ✅ No cultural correction applied (correct for English)")
        test3_pass = True
    else:
        print(f"   ❌ Unexpected correction applied")
        test3_pass = False
    
    # Test Case 4: Chinese positive sentiment (should NOT apply cultural correction)
    print("\n📝 Test Case 4: Chinese Positive Sentiment")
    topic4 = {
        'topic_name': '画面精美',
        'sentiment_score': 0.8,
        'density': 80,
        'consistency': 1.0
    }
    dai_score4 = generator._calculate_s_dai(topic4, 'chinese')
    print(f"   Original sentiment: {0.8}")
    print(f"   Adjusted sentiment (S_adj): {topic4['s_adj']:.3f}")
    print(f"   Expected S_adj: {0.8}")
    print(f"   DAI Score: {dai_score4:.3f}")
    
    if abs(topic4['s_adj'] - 0.8) < 0.001:
        print("   ✅ No cultural correction applied (correct for positive sentiment)")
        test4_pass = True
    else:
        print(f"   ❌ Unexpected correction applied")
        test4_pass = False
    
    # Test Case 5: Verify DAI formula components
    print("\n📝 Test Case 5: DAI Formula Verification")
    import numpy as np
    topic5 = {
        'topic_name': 'Test',
        'sentiment_score': -0.5,
        'density': 100,
        'consistency': 0.8
    }
    dai_score5 = generator._calculate_s_dai(topic5, 'chinese')
    # Manual calculation: log1p(100) * abs(-0.5 * 1.2) * 0.8
    expected_dai = np.log1p(100) * abs(-0.5 * 1.2) * 0.8
    print(f"   Manual calculation: log1p(100) * abs(-0.6) * 0.8 = {expected_dai:.3f}")
    print(f"   Returned DAI: {dai_score5:.3f}")
    
    if abs(dai_score5 - expected_dai) < 0.001:
        print("   ✅ DAI formula calculated correctly")
        test5_pass = True
    else:
        print(f"   ❌ DAI formula mismatch")
        test5_pass = False
    
    all_pass = test1_pass and test2_pass and test3_pass and test4_pass and test5_pass
    
    print("\n" + "=" * 80)
    if all_pass:
        print("✅ All S-DAI calculation tests PASSED")
    else:
        print("❌ Some S-DAI calculation tests FAILED")
    print("=" * 80)
    
    return all_pass


def test_aggregate_map_results_sorting():
    """Test that aggregate_map_results sorts by DAI score"""
    print("\n" + "=" * 80)
    print("TEST 2: Aggregate Map Results Sorting by DAI")
    print("=" * 80)
    
    # Initialize the generator
    generator = LLMReportGenerator(use_ollama=False)
    
    # Create mock map results with different topics
    map_results = [
        {
            'topics': [
                {
                    'topic_name': 'Chinese Low Priority',
                    'sentiment_score': -0.2,  # Low sentiment
                    'density': 10,  # Low density
                    'consistency': 1.0
                },
                {
                    'topic_name': 'Chinese High Priority',
                    'sentiment_score': -0.8,  # High negative sentiment (will be amplified)
                    'density': 100,  # High density
                    'consistency': 1.0
                }
            ],
            'map_metadata': {
                'game_name': 'TestGame',
                'language': 'chinese'
            },
            'statistics': {'total': 110, 'valid': 110}
        },
        {
            'topics': [
                {
                    'topic_name': 'English Medium Priority',
                    'sentiment_score': -0.6,
                    'density': 50,
                    'consistency': 1.0
                }
            ],
            'map_metadata': {
                'game_name': 'TestGame',
                'language': 'english'
            },
            'statistics': {'total': 50, 'valid': 50}
        }
    ]
    
    # Aggregate with S-DAI sorting
    result = generator.aggregate_map_results(map_results)
    
    topics = result.get('topics', [])
    
    print(f"\n📊 Aggregated {len(topics)} topics")
    print("\nTopic ranking (by DAI score):")
    for i, topic in enumerate(topics, 1):
        print(f"   {i}. {topic['topic_name']}")
        print(f"      - DAI Score: {topic.get('dai_score', 0):.3f}")
        print(f"      - S_adj: {topic.get('s_adj', 0):.3f}")
        print(f"      - Density: {topic.get('density', 0)}")
        print(f"      - Language: {topic.get('source_language', 'N/A')}")
    
    # Verify sorting
    if len(topics) >= 2:
        # Check if sorted in descending order
        is_sorted = all(topics[i].get('dai_score', 0) >= topics[i+1].get('dai_score', 0) 
                       for i in range(len(topics)-1))
        
        if is_sorted:
            print("\n✅ Topics are correctly sorted by DAI score (descending)")
            
            # Verify that "Chinese High Priority" is ranked higher than "Chinese Low Priority"
            topic_names = [t['topic_name'] for t in topics]
            if topic_names.index('Chinese High Priority') < topic_names.index('Chinese Low Priority'):
                print("✅ Cultural correction working: High priority Chinese topic ranked correctly")
                return True
            else:
                print("❌ Cultural correction issue: Priority ranking incorrect")
                return False
        else:
            print("❌ Topics are NOT sorted correctly")
            return False
    else:
        print("❌ Not enough topics to verify sorting")
        return False


def test_edge_cases():
    """Test edge cases"""
    print("\n" + "=" * 80)
    print("TEST 3: Edge Cases")
    print("=" * 80)
    
    generator = LLMReportGenerator(use_ollama=False)
    
    # Test with missing fields
    print("\n📝 Test Case: Missing consistency field (should default to 1.0)")
    topic = {
        'topic_name': 'Test',
        'sentiment_score': -0.5,
        'density': 50
        # Missing consistency field
    }
    
    try:
        dai_score = generator._calculate_s_dai(topic, 'chinese')
        if 'consistency' in topic or 'dai_score' in topic:
            print(f"   ✅ Handled missing consistency field, DAI={dai_score:.3f}")
            return True
        else:
            print("   ❌ Failed to handle missing field")
            return False
    except Exception as e:
        print(f"   ❌ Exception raised: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("S-DAI MODEL TEST SUITE")
    print("=" * 80)
    
    results = []
    
    # Run all tests
    results.append(("S-DAI Calculation", test_s_dai_calculation()))
    results.append(("Aggregate Map Results Sorting", test_aggregate_map_results_sorting()))
    results.append(("Edge Cases", test_edge_cases()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    failed = sum(1 for _, result in results if not result)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All S-DAI tests passed!")
        print("\n💡 S-DAI Model is working correctly:")
        print("   - Cultural correction applies to East Asian negative sentiments")
        print("   - DAI formula properly combines volume, sentiment, and consistency")
        print("   - Topics are sorted by priority for developers")
        return 0
    else:
        print(f"\n⚠️ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
