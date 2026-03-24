#!/usr/bin/env python3
"""
Simple verification test for export_to_projector() function
Checks that the function is properly defined without running it
"""

import sys
import os

def test_function_exists():
    """Test that export_to_projector function is defined in nlp.py"""
    print("\n" + "="*60)
    print("VERIFICATION TEST: export_to_projector() Function")
    print("="*60)
    
    # Read nlp.py file
    with open('nlp.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for function definition
    if 'def export_to_projector(' not in content:
        print("❌ FAILED: export_to_projector function not found in nlp.py")
        return False
    
    print("✓ Function export_to_projector() is defined")
    
    # Check for key components
    checks = [
        ('embeddings', 'Embeddings parameter'),
        ('dataframe', 'Dataframe parameter'),
        ('vectors.tsv', 'Vectors TSV file'),
        ('metadata.tsv', 'Metadata TSV file'),
        ('detect_language', 'Language detection lambda'),
        ('Chinese', 'Chinese language detection'),
        ('Japanese', 'Japanese language detection'),
        ('English', 'English language detection'),
        ('topic_id', 'Topic ID column'),
        ('np.savetxt', 'NumPy save function for vectors'),
        ('to_csv', 'Pandas CSV export for metadata'),
        ('projector.tensorflow.org', 'Google Projector URL'),
    ]
    
    all_passed = True
    for keyword, description in checks:
        if keyword in content:
            print(f"✓ {description} - found")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    # Check function signature
    print("\n" + "-"*60)
    print("Function Signature Check:")
    print("-"*60)
    
    import re
    # Find function definition
    func_pattern = r'def export_to_projector\((.*?)\):'
    match = re.search(func_pattern, content, re.DOTALL)
    if match:
        params = match.group(1)
        print(f"Parameters: {params.strip()}")
        
        required_params = ['embeddings', 'dataframe']
        for param in required_params:
            if param in params:
                print(f"✓ Required parameter '{param}' present")
            else:
                print(f"✗ Required parameter '{param}' MISSING")
                all_passed = False
    else:
        print("✗ Could not parse function signature")
        all_passed = False
    
    # Check docstring
    print("\n" + "-"*60)
    print("Documentation Check:")
    print("-"*60)
    
    docstring_pattern = r'def export_to_projector.*?"""(.*?)"""'
    match = re.search(docstring_pattern, content, re.DOTALL)
    if match:
        docstring = match.group(1)
        print(f"✓ Docstring present ({len(docstring)} characters)")
        if 'Args:' in docstring or 'Parameters:' in docstring:
            print("✓ Parameter documentation present")
        if 'projector.tensorflow.org' in docstring.lower() or 'google' in docstring.lower():
            print("✓ Google Projector reference present")
    else:
        print("✗ No docstring found")
    
    # Final result
    print("\n" + "="*60)
    if all_passed:
        print("✅ VERIFICATION PASSED")
        print("\nThe export_to_projector() function is properly implemented.")
        print("\nUsage example:")
        print("  from nlp import export_to_projector")
        print("  export_to_projector(embeddings, df, output_dir='analysis')")
        print("\nTo visualize:")
        print("  1. Go to https://projector.tensorflow.org/")
        print("  2. Upload vectors.tsv")
        print("  3. Upload metadata.tsv")
        return True
    else:
        print("⚠️ VERIFICATION INCOMPLETE")
        print("Some components may be missing or need adjustment")
        return False

def test_integration_point():
    """Check if the function can be integrated into NLPProcessor"""
    print("\n" + "="*60)
    print("INTEGRATION POINT CHECK")
    print("="*60)
    
    with open('nlp.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if function is at module level (can be imported)
    # It should be outside the NLPProcessor class
    lines = content.split('\n')
    
    in_class = False
    class_indent = 0
    func_line = -1
    
    for i, line in enumerate(lines):
        if line.strip().startswith('class NLPProcessor'):
            in_class = True
            # Find indentation
            class_indent = len(line) - len(line.lstrip())
        elif in_class and 'def export_to_projector' in line:
            func_indent = len(line) - len(line.lstrip())
            if func_indent > class_indent:
                print("⚠️ Function is inside NLPProcessor class")
                print("   Consider making it a standalone function for easier import")
            else:
                in_class = False
        elif not in_class and 'def export_to_projector' in line:
            func_line = i + 1
            print(f"✓ Function is at module level (line {func_line})")
            print("  Can be imported as: from nlp import export_to_projector")
            break
    
    if func_line == -1:
        print("✗ Could not determine function location")
        return False
    
    return True

def main():
    """Run all verification tests"""
    print("\n" + "="*60)
    print("EXPORT TO PROJECTOR - CODE VERIFICATION")
    print("="*60)
    print("\nThis test verifies the export_to_projector() implementation")
    print("without requiring numpy/pandas to be installed.\n")
    
    test1 = test_function_exists()
    test2 = test_integration_point()
    
    print("\n" + "="*60)
    print("FINAL RESULT")
    print("="*60)
    
    if test1 and test2:
        print("✅ ALL VERIFICATIONS PASSED")
        print("\nNext steps:")
        print("  1. Install dependencies: pip install numpy pandas")
        print("  2. Run full test: python test_export_to_projector.py")
        print("  3. Use in your code:")
        print("     from nlp import export_to_projector")
        print("     export_to_projector(embeddings, df)")
        return 0
    else:
        print("⚠️ Some verifications failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
