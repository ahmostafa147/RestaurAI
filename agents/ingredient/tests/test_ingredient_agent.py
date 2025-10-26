#!/usr/bin/env python3
"""
Test script for IngredientAgent functionality
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.ingredient_agent import IngredientAgent


def test_ingredient_agent():
    """Test basic IngredientAgent functionality"""
    
    print("Testing IngredientAgent...")
    
    # Initialize agent
    agent = IngredientAgent()
    
    # Test restaurant key (you may need to adjust this)
    restaurant_key = "2f47a946-d3ca-4257-8c8d-848b58617809"  # Chaos Kitchen with absurd inventory
    
    # Test consumption analysis
    print("\n1. Testing consumption analysis...")
    try:
        consumption_data = agent.analyze_consumption_patterns(restaurant_key)
        if 'error' in consumption_data:
            print(f"   Expected error (no data): {consumption_data['error']}")
        else:
            print(f"   [OK] Consumption analysis successful")
            print(f"   - Total ingredients analyzed: {consumption_data.get('total_tickets_analyzed', 0)}")
            print(f"   - Analysis period: {consumption_data.get('analysis_period_days', 0)} days")
    except Exception as e:
        print(f"   [ERROR] Consumption analysis failed: {e}")
    
    # Test low stock alerts
    print("\n2. Testing low stock alerts...")
    try:
        alerts = agent.get_low_stock_alerts(restaurant_key)
        if alerts and 'error' in alerts[0]:
            print(f"   Expected error (no data): {alerts[0]['error']}")
        else:
            print(f"   [OK] Low stock alerts successful")
            print(f"   - Found {len(alerts)} low stock warnings")
    except Exception as e:
        print(f"   [ERROR] Low stock alerts failed: {e}")
    
    # Test reorder suggestions
    print("\n3. Testing reorder suggestions...")
    try:
        suggestions = agent.get_reorder_suggestions(restaurant_key)
        if suggestions and 'error' in suggestions[0]:
            print(f"   Expected error (no data): {suggestions[0]['error']}")
        else:
            print(f"   [OK] Reorder suggestions successful")
            print(f"   - Generated {len(suggestions)} reorder suggestions")
    except Exception as e:
        print(f"   [ERROR] Reorder suggestions failed: {e}")
    
    # Test inventory report generation
    print("\n4. Testing inventory report generation...")
    try:
        report = agent.generate_inventory_report(restaurant_key)
        if 'error' in report:
            print(f"   Expected error (no data): {report['error']}")
        else:
            print(f"   [OK] Inventory report generation successful")
            print(f"   - Report contains {len(report.get('current_stock', []))} ingredients")
            print(f"   - Generated at: {report.get('metadata', {}).get('generated_at', 'N/A')}")
    except Exception as e:
        print(f"   [ERROR] Inventory report generation failed: {e}")
    
    # Test usage summary
    print("\n5. Testing usage summary...")
    try:
        summary = agent.get_ingredient_usage_summary(restaurant_key)
        if 'error' in summary:
            print(f"   Expected error (no data): {summary['error']}")
        else:
            print(f"   [OK] Usage summary successful")
            print(f"   - Total ingredients: {summary.get('total_ingredients_analyzed', 0)}")
            print(f"   - Total usage: {summary.get('total_usage_analyzed', 0)}")
    except Exception as e:
        print(f"   [ERROR] Usage summary failed: {e}")
    
    # Test available reports
    print("\n6. Testing available reports...")
    try:
        reports = agent.get_available_reports()
        print(f"   [OK] Available reports: {len(reports)} found")
        for report in reports:
            print(f"   - {report}")
    except Exception as e:
        print(f"   [ERROR] Available reports failed: {e}")
    
    print("\nIngredientAgent test completed!")


def test_with_real_data():
    """Test with a restaurant that has real data"""
    print("\n" + "="*50)
    print("Testing with real restaurant data...")
    print("="*50)
    
    # You can modify this to use a restaurant key that has actual data
    restaurant_key = "2f47a946-d3ca-4257-8c8d-848b58617809"  # Chaos Kitchen with absurd inventory
    
    agent = IngredientAgent()
    
    # Generate a full report
    print("Generating comprehensive inventory report...")
    report_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'inventory_report.json')
    report = agent.generate_inventory_report(restaurant_key, report_path)

    if 'error' not in report:
        print("[OK] Report generated successfully!")
        print(f"Report saved to: {report_path}")
        
        # Show summary
        metadata = report.get('metadata', {})
        print(f"\nReport Summary:")
        print(f"- Restaurant: {metadata.get('restaurant_key', 'N/A')}")
        print(f"- Total ingredients: {metadata.get('total_ingredients', 0)}")
        print(f"- Total warnings: {metadata.get('total_warnings', 0)}")
        print(f"- Generated at: {metadata.get('generated_at', 'N/A')}")
        
        # Show warnings if any
        warnings = report.get('warnings', [])
        if warnings:
            print(f"\nLow Stock Warnings ({len(warnings)}):")
            for warning in warnings[:5]:  # Show first 5
                print(f"- {warning.get('ingredient_name', 'Unknown')}: {warning.get('current_quantity', 0)} {warning.get('unit', 'units')} (Severity: {warning.get('severity', 'Unknown')})")
        
        # Show LLM insights if any
        llm_insights = report.get('llm_insights', {})
        reorder_suggestions = llm_insights.get('reorder_suggestions', [])
        if reorder_suggestions:
            print(f"\nReorder Suggestions ({len(reorder_suggestions)}):")
            for suggestion in reorder_suggestions[:3]:  # Show first 3
                print(f"- {suggestion.get('ingredient_name', 'Unknown')}: {suggestion.get('suggested_quantity', 0)} {suggestion.get('unit', 'units')} (Urgency: {suggestion.get('urgency', 'Unknown')})")
    else:
        print(f"[ERROR] Report generation failed: {report['error']}")


if __name__ == "__main__":
    test_ingredient_agent()
    test_with_real_data()
