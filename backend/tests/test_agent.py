"""
Test script for the Restaurant Review Agent
This script tests the agent locally before AgentVerse deployment.
"""

import os
import sys
import json
import asyncio
from datetime import datetime

# Add review_agent/src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'review_agent', 'src'))

def test_imports():
    """Test that all required imports work"""
    print("Testing imports...")
    
    try:
        from main import RestaurantReviewAgent
        print("+ RestaurantReviewAgent import successful")
    except ImportError as e:
        print(f"- RestaurantReviewAgent import failed: {e}")
        return False
    
    try:
        from scrapers.pull_dataset import Status
        print("+ Status import successful")
    except ImportError as e:
        print(f"- Status import failed: {e}")
        return False
    
    return True

def test_restaurant_agent():
    """Test the RestaurantReviewAgent initialization"""
    print("\nTesting RestaurantReviewAgent initialization...")
    
    try:
        from main import RestaurantReviewAgent
        
        # Use test database path
        test_db_path = os.path.join(os.path.dirname(__file__), 'review_agent', 'database.json')
        agent = RestaurantReviewAgent(test_db_path)
        
        print("+ RestaurantReviewAgent initialized successfully")
        return True
    except Exception as e:
        print(f"- RestaurantReviewAgent initialization failed: {e}")
        return False

def test_analytics_report():
    """Test that analytics report exists and is valid JSON"""
    print("\nTesting analytics report...")
    
    report_path = os.path.join(os.path.dirname(__file__), 'review_agent', 'analytics_report.json')
    
    if not os.path.exists(report_path):
        print("! Analytics report not found - this is expected for first run")
        return True
    
    try:
        with open(report_path, 'r') as f:
            report = json.load(f)
        
        print("+ Analytics report is valid JSON")
        print(f"   Total reviews: {report.get('metadata', {}).get('total_reviews', 'unknown')}")
        return True
    except Exception as e:
        print(f"- Analytics report validation failed: {e}")
        return False

def test_agent_structure():
    """Test the agent structure without running it"""
    print("\nTesting agent structure...")
    
    try:
        # Read the agent file
        agent_file = os.path.join(os.path.dirname(__file__), 'review_agent', 'restaurant_review_agent.py')
        
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Check for required components
        required_components = [
            'REFRESH_INTERVAL_SECONDS = 86400',
            '@protocol.on_message(ChatMessage)',
            '@agent.on_interval(period=REFRESH_INTERVAL_SECONDS)',
            'agent.include(protocol, publish_manifest=True)',
            'agent.run()'
        ]
        
        missing_components = []
        for component in required_components:
            if component not in content:
                missing_components.append(component)
        
        if missing_components:
            print(f"- Missing required components: {missing_components}")
            return False
        
        print("+ Agent structure validation passed")
        return True
        
    except Exception as e:
        print(f"- Agent structure test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Starting Restaurant Review Agent Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_restaurant_agent,
        test_analytics_report,
        test_agent_structure
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"- Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print("TEST RESULTS")
    print("=" * 50)
    print(f"Total: {passed + failed} | Passed: {passed} | Failed: {failed}")
    
    if failed == 0:
        print("All tests passed! Agent is ready for AgentVerse deployment.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r review_agent/requirements.txt")
        print("2. Set environment variables (ANTHROPIC_API_KEY, etc.)")
        print("3. Deploy to AgentVerse platform")
    else:
        print("Some tests failed. Check the errors above.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
