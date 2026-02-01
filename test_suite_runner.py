#!/usr/bin/env python3
"""
Comprehensive Test Suite Runner
================================
Runs all unit tests with dependency checking and graceful degradation.

Usage:
    python test_suite_runner.py              # Run all available tests
    python test_suite_runner.py --basic      # Run only basic tests (no ML)
    python test_suite_runner.py --full       # Run all tests including ML
    python test_suite_runner.py --verbose    # Verbose output

Author: NLP Comment Processor Team
"""

import sys
import os
import unittest
import time
from io import StringIO

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

def check_dependencies():
    """Check which dependencies are available"""
    deps = {
        'basic': True,  # Python stdlib always available
        'numpy': False,
        'pandas': False,
        'torch': False,
        'transformers': False,
        'sentence_transformers': False,
        'sklearn': False,
        'hdbscan': False
    }
    
    # Check numpy
    try:
        import numpy
        deps['numpy'] = True
    except ImportError:
        pass
    
    # Check pandas
    try:
        import pandas
        deps['pandas'] = True
    except ImportError:
        pass
    
    # Check torch
    try:
        import torch
        deps['torch'] = True
    except ImportError:
        pass
    
    # Check transformers
    try:
        import transformers
        deps['transformers'] = True
    except ImportError:
        pass
    
    # Check sentence_transformers
    try:
        import sentence_transformers
        deps['sentence_transformers'] = True
    except ImportError:
        pass
    
    # Check sklearn
    try:
        import sklearn
        deps['sklearn'] = True
    except ImportError:
        pass
    
    # Check hdbscan
    try:
        import hdbscan
        deps['hdbscan'] = True
    except ImportError:
        pass
    
    return deps

def run_test_module(module_name, test_class=None, verbose=False):
    """Run a specific test module"""
    try:
        # Import the test module
        test_module = __import__(module_name)
        
        # Create test suite
        if test_class:
            suite = unittest.TestLoader().loadTestsFromTestCase(
                getattr(test_module, test_class)
            )
        else:
            suite = unittest.TestLoader().loadTestsFromModule(test_module)
        
        # Run tests
        if verbose:
            runner = unittest.TextTestRunner(verbosity=2)
        else:
            runner = unittest.TextTestRunner(stream=StringIO(), verbosity=0)
        
        result = runner.run(suite)
        
        return {
            'passed': result.wasSuccessful(),
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'skipped': len(result.skipped)
        }
    
    except Exception as e:
        return {
            'passed': False,
            'tests_run': 0,
            'failures': 0,
            'errors': 1,
            'skipped': 0,
            'exception': str(e)
        }

def main():
    """Main test runner"""
    # Parse arguments
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    verbose = '--verbose' in args or '-v' in args
    basic_only = '--basic' in args
    full_mode = '--full' in args
    
    print_header("NLP Comment Processor - Test Suite Runner")
    
    # Check dependencies
    print_info("Checking dependencies...")
    deps = check_dependencies()
    
    print(f"\n{Colors.BOLD}Available Dependencies:{Colors.RESET}")
    for dep, available in deps.items():
        status = f"{Colors.GREEN}✓ Installed{Colors.RESET}" if available else f"{Colors.RED}✗ Not installed{Colors.RESET}"
        print(f"  • {dep:25s} {status}")
    
    # Determine which test categories to run
    can_run_numpy = deps['numpy']
    can_run_pandas = deps['pandas']
    can_run_ml = deps['torch'] and deps['transformers']
    
    print(f"\n{Colors.BOLD}Test Categories:{Colors.RESET}")
    print(f"  • Basic tests (no deps):     {Colors.GREEN}✓ Available{Colors.RESET}")
    print(f"  • NumPy tests:               {Colors.GREEN if can_run_numpy else Colors.RED}{'✓ Available' if can_run_numpy else '✗ Unavailable'}{Colors.RESET}")
    print(f"  • Pandas tests:              {Colors.GREEN if can_run_pandas else Colors.RED}{'✓ Available' if can_run_pandas else '✗ Unavailable'}{Colors.RESET}")
    print(f"  • ML tests (full pipeline):  {Colors.GREEN if can_run_ml else Colors.RED}{'✓ Available' if can_run_ml else '✗ Unavailable'}{Colors.RESET}")
    
    # Start testing
    print_header("Running Tests")
    
    start_time = time.time()
    total_tests = 0
    total_passed = 0
    total_failed = 0
    total_errors = 0
    total_skipped = 0
    
    test_results = []
    
    # Category 1: Basic tests (always run)
    print(f"\n{Colors.BOLD}Category 1: Basic Tests (No Dependencies){Colors.RESET}")
    print("-" * 70)
    
    basic_tests = [
        ('test_core_functions', 'TestTextProcessing'),
        ('test_core_functions', 'TestDataValidation'),
        ('test_file_operations', 'TestFileOperations'),
    ]
    
    for module, test_class in basic_tests:
        try:
            print(f"\nRunning {module}.{test_class}...")
            result = run_test_module(module, test_class, verbose)
            test_results.append((f"{module}.{test_class}", result))
            
            total_tests += result['tests_run']
            if result['passed']:
                total_passed += result['tests_run']
                print_success(f"PASSED: {result['tests_run']} tests")
            else:
                total_failed += result['failures']
                total_errors += result['errors']
                print_error(f"FAILED: {result['failures']} failures, {result['errors']} errors")
        except Exception as e:
            print_error(f"Could not run {module}.{test_class}: {e}")
    
    # Category 2: Data processing tests (needs numpy/pandas)
    if can_run_numpy and can_run_pandas and not basic_only:
        print(f"\n{Colors.BOLD}Category 2: Data Processing Tests{Colors.RESET}")
        print("-" * 70)
        
        data_tests = [
            ('test_data_processing', 'TestDataCleaning'),
            ('test_data_processing', 'TestLanguageDetection'),
        ]
        
        for module, test_class in data_tests:
            try:
                print(f"\nRunning {module}.{test_class}...")
                result = run_test_module(module, test_class, verbose)
                test_results.append((f"{module}.{test_class}", result))
                
                total_tests += result['tests_run']
                if result['passed']:
                    total_passed += result['tests_run']
                    print_success(f"PASSED: {result['tests_run']} tests")
                else:
                    total_failed += result['failures']
                    total_errors += result['errors']
                    print_error(f"FAILED: {result['failures']} failures, {result['errors']} errors")
            except Exception as e:
                print_error(f"Could not run {module}.{test_class}: {e}")
    
    # Category 3: Integration tests
    if not basic_only:
        print(f"\n{Colors.BOLD}Category 3: Integration Tests{Colors.RESET}")
        print("-" * 70)
        
        integration_tests = [
            ('test_integration_basic', 'TestModuleIntegration'),
        ]
        
        for module, test_class in integration_tests:
            try:
                print(f"\nRunning {module}.{test_class}...")
                result = run_test_module(module, test_class, verbose)
                test_results.append((f"{module}.{test_class}", result))
                
                total_tests += result['tests_run']
                if result['passed']:
                    total_passed += result['tests_run']
                    print_success(f"PASSED: {result['tests_run']} tests")
                else:
                    total_failed += result['failures']
                    total_errors += result['errors']
                    print_error(f"FAILED: {result['failures']} failures, {result['errors']} errors")
            except Exception as e:
                print_error(f"Could not run {module}.{test_class}: {e}")
    
    # Summary
    elapsed_time = time.time() - start_time
    
    print_header("Test Summary")
    
    print(f"{Colors.BOLD}Results:{Colors.RESET}")
    print(f"  Total tests run:    {total_tests}")
    print(f"  Passed:             {Colors.GREEN}{total_passed}{Colors.RESET}")
    print(f"  Failed:             {Colors.RED}{total_failed}{Colors.RESET}")
    print(f"  Errors:             {Colors.RED}{total_errors}{Colors.RESET}")
    print(f"  Execution time:     {elapsed_time:.2f} seconds")
    
    # Success rate
    if total_tests > 0:
        success_rate = (total_passed / total_tests) * 100
        if success_rate == 100:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! (100%){Colors.RESET}")
        elif success_rate >= 80:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ MOSTLY PASSING ({success_rate:.1f}%){Colors.RESET}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}✗ TESTS FAILING ({success_rate:.1f}%){Colors.RESET}")
    
    # Recommendations
    print(f"\n{Colors.BOLD}Recommendations:{Colors.RESET}")
    if not can_run_ml and not basic_only:
        print_warning("Install ML dependencies for full testing:")
        print("  pip install torch transformers sentence-transformers")
    
    if not can_run_numpy:
        print_warning("Install numpy for data processing tests:")
        print("  pip install numpy pandas")
    
    if total_tests == 0:
        print_error("No tests were run! Check test file existence.")
        return 1
    
    # Return exit code
    if total_failed > 0 or total_errors > 0:
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
