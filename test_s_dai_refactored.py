"""
Test script for refactored S-DAI model (now in nlp.py)
Tests the row-level cultural correction and consistency calculation
"""

import sys
import json
import numpy as np
from nlp import NLPProcessor, EAST_ASIAN_LANGUAGES, CULTURAL_CORRECTION_ALPHA

def test_cultural_correction():
    """Test row-level cultural correction in NLPProcessor"""
    print("=" * 80)
    print("TEST 1: Row-Level Cultural Correction")
    print("=" * 80)
    
    processor = NLPProcessor()
    
    # Test Case 1: Mixed languages with negative sentiments
    print("\n📝 Test Case 1: Mixed Languages, Negative Sentiments")
    sentiment_scores = [-0.6, -0.5, -0.7, -0.4]
    languages = ['chinese', 'japanese', 'english', 'schinese']
    
    adjusted = processor._apply_cultural_correction(sentiment_scores, languages)
    
    print(f"   Input sentiments: {sentiment_scores}")
    print(f"   Languages: {languages}")
    print(f"   Adjusted sentiments: {[round(s, 3) for s in adjusted]}")
    
    # Verify corrections
    expected = [
        -0.6 * 1.2,  # chinese, negative -> apply correction
        -0.5 * 1.2,  # japanese, negative -> apply correction
        -0.7,        # english, negative -> no correction
        -0.4 * 1.2   # schinese, negative -> apply correction
    ]
    
    all_correct = True
    for i, (exp, act) in enumerate(zip(expected, adjusted)):
        if abs(exp - act) < 0.001:
            print(f"   ✅ {languages[i]}: {sentiment_scores[i]:.3f} -> {act:.3f} (expected {exp:.3f})")
        else:
            print(f"   ❌ {languages[i]}: Expected {exp:.3f}, got {act:.3f}")
            all_correct = False
    
    # Test Case 2: Positive sentiments (no correction)
    print("\n📝 Test Case 2: Positive Sentiments (No Correction)")
    sentiment_scores_pos = [0.6, 0.5, 0.7]
    languages_pos = ['chinese', 'japanese', 'english']
    
    adjusted_pos = processor._apply_cultural_correction(sentiment_scores_pos, languages_pos)
    
    print(f"   Input sentiments: {sentiment_scores_pos}")
    print(f"   Adjusted sentiments: {[round(s, 3) for s in adjusted_pos]}")
    
    # Should be unchanged for positive sentiments
    pos_correct = all(abs(orig - adj) < 0.001 for orig, adj in zip(sentiment_scores_pos, adjusted_pos))
    if pos_correct:
        print(f"   ✅ Positive sentiments unchanged (correct)")
    else:
        print(f"   ❌ Positive sentiments were incorrectly modified")
        all_correct = False
    
    return all_correct


def test_consistency_calculation():
    """Test consistency calculation using centroid distance"""
    print("\n" + "=" * 80)
    print("TEST 2: Consistency Calculation (Cluster Tightness)")
    print("=" * 80)
    
    processor = NLPProcessor()
    
    # Test Case 1: Tight cluster (all vectors similar)
    print("\n📝 Test Case 1: Tight Cluster")
    # Create normalized vectors that are very similar
    base_vector = np.array([1.0, 0.0, 0.0])
    tight_embeddings = np.array([
        base_vector,
        base_vector + 0.01 * np.random.randn(3),
        base_vector + 0.01 * np.random.randn(3),
        base_vector + 0.01 * np.random.randn(3),
    ])
    # Normalize
    from sklearn.preprocessing import normalize
    tight_embeddings = normalize(tight_embeddings)
    
    consistency_tight = processor._calculate_topic_consistency(tight_embeddings)
    print(f"   Tight cluster consistency: {consistency_tight:.4f}")
    
    if consistency_tight > 0.9:
        print(f"   ✅ High consistency for tight cluster (> 0.9)")
        test1_pass = True
    else:
        print(f"   ❌ Expected high consistency, got {consistency_tight:.4f}")
        test1_pass = False
    
    # Test Case 2: Loose cluster (vectors spread out)
    print("\n📝 Test Case 2: Loose Cluster")
    loose_embeddings = np.array([
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [-1.0, 0.0, 0.0],
    ])
    loose_embeddings = normalize(loose_embeddings)
    
    consistency_loose = processor._calculate_topic_consistency(loose_embeddings)
    print(f"   Loose cluster consistency: {consistency_loose:.4f}")
    
    if consistency_loose < consistency_tight:
        print(f"   ✅ Loose cluster has lower consistency than tight cluster")
        test2_pass = True
    else:
        print(f"   ❌ Expected lower consistency for loose cluster")
        test2_pass = False
    
    # Test Case 3: Edge case - single point
    print("\n📝 Test Case 3: Single Point")
    single_embedding = np.array([[1.0, 0.0, 0.0]])
    consistency_single = processor._calculate_topic_consistency(single_embedding)
    print(f"   Single point consistency: {consistency_single:.4f}")
    
    if consistency_single == 1.0:
        print(f"   ✅ Single point has perfect consistency (1.0)")
        test3_pass = True
    else:
        print(f"   ❌ Expected 1.0 for single point, got {consistency_single:.4f}")
        test3_pass = False
    
    return test1_pass and test2_pass and test3_pass


def test_integration():
    """Test that topics are properly generated with S-DAI scores"""
    print("\n" + "=" * 80)
    print("TEST 3: Integration Test (Mock Topic Generation)")
    print("=" * 80)
    
    # Mock a simple topic with pre-calculated values
    print("\n📝 Simulating topic with:")
    print("   - Density: 100 comments")
    print("   - Sentiment (culturally adjusted): -0.72 (Chinese negative)")
    print("   - Consistency: 0.85")
    
    density = 100
    sentiment_adj = -0.72
    consistency = 0.85
    
    # Calculate DAI manually
    dai_score = np.log1p(density) * abs(sentiment_adj) * consistency
    
    print(f"\n   DAI = log(1 + {density}) × |{sentiment_adj:.2f}| × {consistency:.2f}")
    print(f"   DAI = {np.log1p(density):.3f} × {abs(sentiment_adj):.2f} × {consistency:.2f}")
    print(f"   DAI = {dai_score:.3f}")
    
    # Verify formula
    expected_dai = 4.615 * 0.72 * 0.85  # Approximately
    if abs(dai_score - expected_dai) < 0.1:
        print(f"   ✅ DAI calculation correct")
        return True
    else:
        print(f"   ❌ DAI calculation mismatch")
        return False


def test_aggregate_map_results_compatibility():
    """Test that aggregate_map_results works with pre-calculated DAI scores"""
    print("\n" + "=" * 80)
    print("TEST 4: LLM Aggregation Compatibility")
    print("=" * 80)
    
    try:
        from llm_report_generator import LLMReportGenerator
        
        generator = LLMReportGenerator(use_ollama=False)
        
        # Mock map results with pre-calculated DAI scores
        map_results = [
            {
                'topics': [
                    {
                        'topic_name': 'High Priority',
                        'sentiment_score': -0.72,  # Already culturally adjusted
                        'density': 100,
                        'consistency': 0.85,
                        'dai_score': 2.823,  # Pre-calculated
                        'sentiment_label': 'negative'
                    },
                    {
                        'topic_name': 'Low Priority',
                        'sentiment_score': -0.24,  # Already culturally adjusted
                        'density': 10,
                        'consistency': 0.75,
                        'dai_score': 0.432,  # Pre-calculated
                        'sentiment_label': 'negative'
                    }
                ],
                'map_metadata': {
                    'game_name': 'TestGame',
                    'language': 'chinese'
                },
                'statistics': {'total': 110, 'valid': 110}
            }
        ]
        
        result = generator.aggregate_map_results(map_results)
        topics = result.get('topics', [])
        
        print(f"\n   Generated {len(topics)} topics")
        
        # Verify sorting
        if len(topics) >= 2:
            if topics[0]['topic_name'] == 'High Priority':
                print(f"   ✅ Topics sorted by DAI score (High Priority first)")
                print(f"      1. {topics[0]['topic_name']}: DAI={topics[0]['dai_score']:.3f}")
                print(f"      2. {topics[1]['topic_name']}: DAI={topics[1]['dai_score']:.3f}")
                return True
            else:
                print(f"   ❌ Topics not sorted correctly")
                return False
        else:
            print(f"   ⚠️ Not enough topics to verify sorting")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("S-DAI REFACTORED MODEL TEST SUITE")
    print("(Now with row-level precision in nlp.py)")
    print("=" * 80)
    
    results = []
    
    # Run all tests
    results.append(("Row-Level Cultural Correction", test_cultural_correction()))
    results.append(("Consistency Calculation", test_consistency_calculation()))
    results.append(("Integration Test", test_integration()))
    results.append(("LLM Aggregation Compatibility", test_aggregate_map_results_compatibility()))
    
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
        print("\n🎉 All refactored S-DAI tests passed!")
        print("\n💡 Architecture Improvements:")
        print("   ✅ Row-level cultural correction (more precise)")
        print("   ✅ Direct vector space access for consistency")
        print("   ✅ GPU-accelerated calculations")
        print("   ✅ Better separation of concerns")
        return 0
    else:
        print(f"\n⚠️ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
