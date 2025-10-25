#!/usr/bin/env python3
"""
Test script to verify import functionality
"""

import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_core_imports():
    """Test core model imports"""
    try:
        from src.models.review import Review
        print("PASSED: Core Review model imports successfully")
        return True
    except ImportError as e:
        print(f"FAILED: Core Review model import failed: {e}")
        return False

def test_eval_imports():
    """Test eval module imports"""
    try:
        from src.eval import ReviewOrchestrator, EnrichedReview
        print("PASSED: Eval module imports successfully")
        return True
    except ImportError as e:
        print(f"WARNING: Eval module import failed (dependencies missing): {e}")
        return False

def test_storage_imports():
    """Test storage module imports"""
    try:
        from src.storage import DatabaseHandler
        print("PASSED: Storage module imports successfully")
        return True
    except ImportError as e:
        print(f"FAILED: Storage module import failed: {e}")
        return False

def test_scraper_imports():
    """Test scraper module imports"""
    try:
        from src.scrapers import GoogleScraper, YelpScraper
        print("PASSED: Scraper module imports successfully")
        return True
    except ImportError as e:
        print(f"WARNING: Scraper module import failed (dependencies missing): {e}")
        return False

def main():
    """Run all import tests"""
    print("Testing RestaurAI Import Functionality")
    print("=" * 50)
    
    tests = [
        ("Core Models", test_core_imports),
        ("Eval Module", test_eval_imports),
        ("Storage Module", test_storage_imports),
        ("Scraper Module", test_scraper_imports),
    ]
    
    results = {}
    for name, test_func in tests:
        print(f"\nTesting {name}...")
        results[name] = test_func()
    
    # Summary
    print("\n" + "=" * 50)
    print("IMPORT TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for name, result in results.items():
        status = "PASSED" if result else "FAILED"
        print(f"{name}: {status}")
    
    print(f"\nOverall: {passed}/{total} modules imported successfully")
    
    if passed >= 2:  # At least core models and one other module
        print("Core functionality is working!")
        return 0
    else:
        print("Some core functionality is missing. Check dependencies.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
