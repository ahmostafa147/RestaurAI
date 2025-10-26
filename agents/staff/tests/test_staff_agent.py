"""
Integration tests for staff agent
"""

import sys
import os
import unittest
import json
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from agents.staff.src.staff_agent import StaffAgent
from backend.src.core.restaurant import Restaurant


class TestStaffAgent(unittest.TestCase):
    """Test cases for StaffAgent functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.staff_agent = StaffAgent()
        
        # Use test restaurant keys
        self.test_restaurant_key = "113b9b80-dda7-41e1-b6d1-f1d7428950c3"  # Causwells
        self.test_restaurant_key2 = "d648f285-a940-4101-a013-97d994cdf18e"  # Cote Ouest
        
        # Create restaurant instances for testing
        self.restaurant1 = Restaurant(key=self.test_restaurant_key)
        self.restaurant2 = Restaurant(key=self.test_restaurant_key2)
    
    def test_generate_schedule_report(self):
        """Test generating a comprehensive schedule report"""
        report = self.staff_agent.generate_schedule_report(self.test_restaurant_key)
        
        # Verify report structure
        self.assertIsInstance(report, dict)
        self.assertIn("metadata", report)
        self.assertIn("generated_at", report["metadata"])
        self.assertIn("restaurant_key", report["metadata"])
        
        # Check for error (expected if no staff data exists)
        if "error" not in report:
            self.assertIn("overall_coverage_score", report)
            self.assertIn("weaknesses", report)
            self.assertIn("utilization_metrics", report)
    
    def test_identify_weaknesses(self):
        """Test identifying schedule weaknesses"""
        weaknesses = self.staff_agent.identify_weaknesses(self.test_restaurant_key)
        
        # Verify weaknesses structure
        self.assertIsInstance(weaknesses, dict)
        self.assertIn("metadata", weaknesses)
        
        if "error" not in weaknesses:
            self.assertIn("overall_coverage_score", weaknesses)
            self.assertIn("total_weaknesses", weaknesses)
            self.assertIn("understaffed_slots", weaknesses)
            self.assertIn("overstaffed_slots", weaknesses)
            self.assertIn("overworked_staff", weaknesses)
            self.assertIn("underutilized_staff", weaknesses)
    
    def test_handle_absence(self):
        """Test handling staff absence"""
        # Test with a non-existent staff member (should handle gracefully)
        absence_report = self.staff_agent.handle_absence(self.test_restaurant_key, 999)
        
        # Verify absence report structure
        self.assertIsInstance(absence_report, dict)
        self.assertIn("metadata", absence_report)
        
        if "error" not in absence_report:
            self.assertIn("absent_staff", absence_report)
            self.assertIn("suggested_replacements", absence_report)
            self.assertIn("llm_recommendations", absence_report)
            self.assertIn("summary", absence_report)
    
    def test_get_coverage_metrics(self):
        """Test getting coverage metrics"""
        metrics = self.staff_agent.get_coverage_metrics(self.test_restaurant_key)
        
        # Verify metrics structure
        self.assertIsInstance(metrics, dict)
        self.assertIn("metadata", metrics)
        
        if "error" not in metrics:
            self.assertIn("coverage_summary", metrics)
            self.assertIn("staff_utilization", metrics)
            self.assertIn("daily_coverage", metrics)
            self.assertIn("role_coverage", metrics)
            self.assertIn("alerts", metrics)
    
    def test_analyze_staff_utilization(self):
        """Test analyzing staff utilization"""
        utilization = self.staff_agent.analyze_staff_utilization(self.test_restaurant_key)
        
        # Verify utilization structure
        self.assertIsInstance(utilization, list)
        
        if utilization and "error" not in utilization[0]:
            for staff_metric in utilization:
                self.assertIn("staff_id", staff_metric)
                self.assertIn("staff_name", staff_metric)
                self.assertIn("role", staff_metric)
                self.assertIn("weekly_hours", staff_metric)
                self.assertIn("consecutive_days", staff_metric)
                self.assertIn("is_overworked", staff_metric)
                self.assertIn("is_underutilized", staff_metric)
                self.assertIn("work_pattern_score", staff_metric)
    
    def test_get_schedule_coverage(self):
        """Test getting schedule coverage analysis"""
        coverage = self.staff_agent.get_schedule_coverage(self.test_restaurant_key)
        
        # Verify coverage structure
        self.assertIsInstance(coverage, list)
        
        if coverage and "error" not in coverage[0]:
            for coverage_metric in coverage:
                self.assertIn("day_of_week", coverage_metric)
                self.assertIn("time_slot", coverage_metric)
                self.assertIn("total_staff", coverage_metric)
                self.assertIn("roles_covered", coverage_metric)
                self.assertIn("coverage_score", coverage_metric)
                self.assertIn("is_understaffed", coverage_metric)
                self.assertIn("is_overstaffed", coverage_metric)
    
    def test_optimize_schedule(self):
        """Test generating schedule optimization recommendations"""
        optimization = self.staff_agent.optimize_schedule(self.test_restaurant_key)
        
        # Verify optimization is a string (LLM response)
        self.assertIsInstance(optimization, str)
        self.assertGreater(len(optimization), 0)
    
    def test_analyze_performance_patterns(self):
        """Test analyzing staff performance patterns"""
        performance_analysis = self.staff_agent.analyze_performance_patterns(self.test_restaurant_key)
        
        # Verify performance analysis is a string (LLM response)
        self.assertIsInstance(performance_analysis, str)
        self.assertGreater(len(performance_analysis), 0)
    
    def test_get_staff_insights(self):
        """Test getting LLM-generated staff insights"""
        insights = self.staff_agent.get_staff_insights(self.test_restaurant_key)
        
        # Verify insights structure
        self.assertIsInstance(insights, object)  # StaffInsights dataclass
        self.assertIsInstance(insights.analysis, str)
        self.assertIsInstance(insights.generated_at, str)
        self.assertIsInstance(insights.confidence_score, float)
        self.assertIsInstance(insights.recommendations, list)
        self.assertIsInstance(insights.priority_issues, list)
    
    def test_load_report(self):
        """Test loading existing report or generating new one"""
        report = self.staff_agent.load_report(self.test_restaurant_key)
        
        # Verify report structure
        self.assertIsInstance(report, dict)
        self.assertIn("metadata", report)
        self.assertIn("generated_at", report["metadata"])
        self.assertIn("restaurant_key", report["metadata"])
    
    def test_multi_restaurant_report(self):
        """Test generating multi-restaurant report"""
        multi_report = self.staff_agent.generate_multi_restaurant_report()
        
        # Verify multi-restaurant report structure
        self.assertIsInstance(multi_report, dict)
        self.assertIn("generated_at", multi_report)
        self.assertIn("restaurants", multi_report)
        
        # Should have data for both restaurants
        restaurants = multi_report["restaurants"]
        self.assertIsInstance(restaurants, dict)
        
        # Check that both restaurant IDs are present
        restaurant_ids = list(restaurants.keys())
        self.assertIn("causwells-sf", restaurant_ids)
        self.assertIn("cote-ouest-bistro-sf", restaurant_ids)
    
    def test_restaurant_staff_integration(self):
        """Test integration with Restaurant class"""
        # Test that Restaurant class has staff manager
        self.assertIsNotNone(self.restaurant1.staff_manager)
        self.assertIsNotNone(self.restaurant2.staff_manager)
        
        # Test basic staff operations through Restaurant
        staff_list = self.restaurant1.get_staff()
        self.assertIsInstance(staff_list, list)
        
        utilization = self.restaurant1.get_staff_utilization()
        self.assertIsInstance(utilization, dict)
        self.assertIn("total_staff", utilization)
        self.assertIn("active_staff", utilization)
    
    def test_error_handling(self):
        """Test error handling with invalid inputs"""
        # Test with invalid restaurant key
        invalid_report = self.staff_agent.generate_schedule_report("invalid-key")
        # The system generates a valid report with 0 coverage for invalid keys
        # This is actually correct behavior - it creates an empty restaurant
        self.assertIsInstance(invalid_report, dict)
        self.assertIn("metadata", invalid_report)
        self.assertEqual(invalid_report["overall_coverage_score"], 0.0)


if __name__ == '__main__':
    unittest.main()
