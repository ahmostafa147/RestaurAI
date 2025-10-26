#!/usr/bin/env python3
"""
Simple test script for MenuAgent functionality
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from menu_agent.src.menu_agent import MenuAgent


def test_menu_agent():
    """Test basic MenuAgent functionality"""
    
    print("Testing MenuAgent...")
    
    # Initialize agent
    agent = MenuAgent()
    
    # Test report generation (this will fail without real data, but tests the structure)
    try:
        print("Testing report generation...")
        report = agent.generate_analytics_report(
            "3c3da43d-9f97-4e62-8945-b03cde626dfd",
            review_analytics_path="review_agent/sample_analytics_report.json"
        )
        
        if 'error' in report:
            print(f"Expected error (no data): {report['error']}")
        else:
            print("Report generated successfully!")
            print(f"Report contains {len(report.get('menu_items', []))} menu items")
        
    except Exception as e:
        print(f"Test failed with exception: {e}")
    
    # Test report listing
    print("\nTesting report listing...")
    reports = agent.get_available_reports()
    print(f"Found {len(reports)} existing reports")
    print("\nMenuAgent test completed!")


if __name__ == "__main__":
    test_menu_agent()
