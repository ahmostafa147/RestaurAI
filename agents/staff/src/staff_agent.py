"""
Main orchestrator for staff agent analytics
"""

import sys
import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from .analytics.schedule_analyzer import ScheduleAnalyzer
from .analytics.llm_analyzer import LLMAnalyzer
from .analytics.report_generator import ReportGenerator
from .analytics.models import StaffInsights, AbsenceRecommendation


class StaffAgent:
    """Main orchestrator for staff analytics and scheduling management"""
    
    def __init__(self, anthropic_api_key: Optional[str] = None):
        """
        Initialize the staff agent with analyzers
        
        Args:
            anthropic_api_key: Anthropic API key for LLM analysis
        """
        self.schedule_analyzer = ScheduleAnalyzer()
        self.llm_analyzer = LLMAnalyzer(anthropic_api_key)
        self.report_generator = ReportGenerator(anthropic_api_key)
        self.restaurants = self._load_restaurants()
    
    def _load_restaurants(self) -> List[Dict[str, Any]]:
        """Load restaurant configurations from unified restaurants.json"""
        restaurants_file = os.path.join(os.path.dirname(__file__), '..', '..', 'restaurants.json')
        if os.path.exists(restaurants_file):
            with open(restaurants_file, 'r') as f:
                config = json.load(f)
                return config.get('restaurants', [])
        print(f"File not found in restaurants.json: {restaurants_file}")
        return []
    
    def generate_schedule_report(self, restaurant_key: str, 
                               output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate comprehensive schedule analytics report
        
        Args:
            restaurant_key: Restaurant identifier
            output_path: Optional path to save report as JSON file
            
        Returns:
            Complete schedule report dictionary
        """
        try:
            # Generate the comprehensive report
            report = self.report_generator.generate_comprehensive_report(restaurant_key)
            
            # Save to file if output path provided
            if output_path and 'error' not in report:
                success = self.report_generator.export_report(report, output_path)
                if success:
                    report['metadata']['saved_to'] = output_path
            
            return report
            
        except Exception as e:
            return {
                'error': f"Failed to generate schedule report: {str(e)}",
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'restaurant_key': restaurant_key,
                    'error': True
                }
            }
    
    def identify_weaknesses(self, restaurant_key: str) -> Dict[str, Any]:
        """
        Identify schedule weaknesses and coverage gaps
        
        Args:
            restaurant_key: Restaurant identifier
            
        Returns:
            Weakness analysis data
        """
        try:
            return self.report_generator.generate_weakness_report(restaurant_key)
        except Exception as e:
            return {'error': f"Failed to identify weaknesses: {str(e)}"}
    
    def handle_absence(self, restaurant_key: str, staff_id: int, 
                      absence_date: str = None) -> Dict[str, Any]:
        """
        Handle staff absence and suggest replacements
        
        Args:
            restaurant_key: Restaurant identifier
            staff_id: ID of absent staff member
            absence_date: Date of absence (defaults to today)
            
        Returns:
            Absence handling data with replacement suggestions
        """
        try:
            if absence_date is None:
                absence_date = datetime.now().strftime("%Y-%m-%d")
            
            return self.report_generator.generate_absence_handling_report(
                restaurant_key, staff_id, absence_date
            )
        except Exception as e:
            return {'error': f"Failed to handle absence: {str(e)}"}
    
    def suggest_adjustments(self, restaurant_key: str, absence_info: Dict[str, Any]) -> AbsenceRecommendation:
        """
        Generate LLM-powered adjustment suggestions for absence
        
        Args:
            restaurant_key: Restaurant identifier
            absence_info: Information about the absence
            
        Returns:
            LLM-generated recommendations
        """
        try:
            return self.llm_analyzer.suggest_absence_adjustments(absence_info)
        except Exception as e:
            return AbsenceRecommendation(
                recommendations=f"Error generating suggestions: {str(e)}",
                priority_action="Contact available staff immediately",
                impact_assessment="Unable to assess impact",
                generated_at=datetime.now().isoformat(),
                confidence_score=0.0
            )
    
    def get_coverage_metrics(self, restaurant_key: str) -> Dict[str, Any]:
        """
        Get coverage metrics for dashboard display
        
        Args:
            restaurant_key: Restaurant identifier
            
        Returns:
            Coverage metrics data
        """
        try:
            return self.report_generator.generate_coverage_metrics(restaurant_key)
        except Exception as e:
            return {'error': f"Failed to get coverage metrics: {str(e)}"}
    
    def analyze_staff_utilization(self, restaurant_key: str) -> List[Dict[str, Any]]:
        """
        Analyze individual staff utilization patterns
        
        Args:
            restaurant_key: Restaurant identifier
            
        Returns:
            List of utilization metrics for each staff member
        """
        try:
            utilization_metrics = self.schedule_analyzer.analyze_utilization(restaurant_key)
            
            return [
                {
                    "staff_id": metric.staff_id,
                    "staff_name": metric.staff_name,
                    "role": metric.role,
                    "weekly_hours": metric.total_hours_per_week,
                    "consecutive_days": metric.consecutive_days,
                    "is_overworked": metric.is_overworked,
                    "is_underutilized": metric.is_underutilized,
                    "work_pattern_score": metric.work_pattern_score
                }
                for metric in utilization_metrics
            ]
        except Exception as e:
            return [{'error': f"Failed to analyze utilization: {str(e)}"}]
    
    def get_schedule_coverage(self, restaurant_key: str) -> List[Dict[str, Any]]:
        """
        Get schedule coverage analysis for all time slots
        
        Args:
            restaurant_key: Restaurant identifier
            
        Returns:
            List of coverage metrics for each day/time combination
        """
        try:
            coverage_metrics = self.schedule_analyzer.analyze_coverage(restaurant_key)
            
            return [
                {
                    "day_of_week": metric.day_of_week,
                    "time_slot": metric.time_slot,
                    "total_staff": metric.total_staff,
                    "roles_covered": metric.roles_covered,
                    "coverage_score": metric.coverage_score,
                    "is_understaffed": metric.is_understaffed,
                    "is_overstaffed": metric.is_overstaffed
                }
                for metric in coverage_metrics
            ]
        except Exception as e:
            return [{'error': f"Failed to get schedule coverage: {str(e)}"}]
    
    def optimize_schedule(self, restaurant_key: str, constraints: Dict[str, Any] = None) -> str:
        """
        Generate schedule optimization recommendations
        
        Args:
            restaurant_key: Restaurant identifier
            constraints: Optional constraints for optimization
            
        Returns:
            LLM-generated optimization recommendations
        """
        try:
            # Get current schedule data
            current_schedule = self.schedule_analyzer.identify_weaknesses(restaurant_key)
            
            return self.llm_analyzer.generate_schedule_optimization(current_schedule, constraints)
        except Exception as e:
            return f"Error generating optimization recommendations: {str(e)}"
    
    def analyze_performance_patterns(self, restaurant_key: str) -> str:
        """
        Analyze staff performance patterns and suggest improvements
        
        Args:
            restaurant_key: Restaurant identifier
            
        Returns:
            LLM-generated performance analysis
        """
        try:
            # Get performance data
            utilization_metrics = self.schedule_analyzer.analyze_utilization(restaurant_key)
            
            # Get staff utilization summary
            from backend.src.core.staff_manager import StaffManager
            staff_manager = StaffManager(restaurant_key)
            utilization_summary = staff_manager.get_staff_utilization()
            
            performance_data = {
                "utilization_metrics": [
                    {
                        "staff_name": metric.staff_name,
                        "role": metric.role,
                        "weekly_hours": metric.total_hours_per_week,
                        "is_overworked": metric.is_overworked,
                        "is_underutilized": metric.is_underutilized,
                        "work_pattern_score": metric.work_pattern_score
                    }
                    for metric in utilization_metrics
                ],
                "role_distribution": utilization_summary.get("role_distribution", {}),
                "total_staff": utilization_summary.get("total_staff", 0),
                "active_staff": utilization_summary.get("active_staff", 0)
            }
            
            return self.llm_analyzer.analyze_staff_performance_patterns(performance_data)
        except Exception as e:
            return f"Error analyzing performance patterns: {str(e)}"
    
    def get_staff_insights(self, restaurant_key: str) -> StaffInsights:
        """
        Get LLM-generated insights about staff scheduling
        
        Args:
            restaurant_key: Restaurant identifier
            
        Returns:
            StaffInsights with analysis and recommendations
        """
        try:
            # Get weakness analysis
            weaknesses = self.schedule_analyzer.identify_weaknesses(restaurant_key)
            
            return self.llm_analyzer.analyze_schedule_weaknesses(weaknesses)
        except Exception as e:
            return StaffInsights(
                analysis=f"Error generating insights: {str(e)}",
                generated_at=datetime.now().isoformat(),
                confidence_score=0.0,
                recommendations=[],
                priority_issues=[]
            )
    
    def load_report(self, restaurant_key: str) -> Optional[Dict[str, Any]]:
        """
        Load a report for a restaurant by restaurant_key.
        If no report exists, generates a new one.
        
        Args:
            restaurant_key: Restaurant identifier
            
        Returns:
            Report dictionary or None if generation fails
        """
        # First try to load from the multi-restaurant schedule report
        data_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data')
        schedule_report_path = os.path.join(data_dir, 'schedule_report.json')
        
        if os.path.exists(schedule_report_path):
            try:
                with open(schedule_report_path, 'r') as f:
                    multi_report = json.load(f)
                
                # Find the restaurant in the multi-report
                restaurants = multi_report.get('restaurants', {})
                for restaurant_id, restaurant_data in restaurants.items():
                    if restaurant_data.get('analytics', {}).get('metadata', {}).get('restaurant_key') == restaurant_key:
                        return restaurant_data.get('analytics')
                
                print(f"Restaurant {restaurant_key} not found in multi-restaurant report")
            except Exception as e:
                print(f"Error loading multi-restaurant report: {e}")
        
        # Fallback: Look for individual report files
        report_files = []
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.startswith(restaurant_key) and filename.endswith('.json'):
                    file_path = os.path.join(data_dir, filename)
                    try:
                        stat = os.stat(file_path)
                        report_files.append({
                            'path': file_path,
                            'time': stat.st_mtime
                        })
                    except:
                        continue
        
        # If we found individual reports, return the most recent one
        if report_files:
            latest = max(report_files, key=lambda x: x['time'])
            try:
                with open(latest['path'], 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading report from {latest['path']}: {e}")
        
        # If no report found, generate a new one
        print(f"No existing report found for {restaurant_key}, generating new report...")
        return self.generate_schedule_report(restaurant_key)
    
    def generate_multi_restaurant_report(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Generate analytics report for all configured restaurants"""
        restaurants_report = {}
        
        for restaurant in self.restaurants:
            restaurant_id = restaurant['id']
            restaurant_name = restaurant['name']
            secure_key = restaurant['secure_key']
            
            try:
                # Generate analytics for this restaurant
                analytics = self.generate_schedule_report(secure_key)
                
                restaurants_report[restaurant_id] = {
                    "id": restaurant_id,
                    "name": restaurant_name,
                    "analytics": analytics
                }
            except Exception as e:
                restaurants_report[restaurant_id] = {
                    "id": restaurant_id,
                    "name": restaurant_name,
                    "error": f"Failed to generate analytics: {str(e)}"
                }
        
        # Save multi-restaurant report if output path provided
        if output_path:
            with open(output_path, 'w') as f:
                json.dump({
                    "generated_at": datetime.now().isoformat(),
                    "restaurants": restaurants_report
                }, f, indent=2)
        
        return {
            "generated_at": datetime.now().isoformat(),
            "restaurants": restaurants_report
        }
    
    def get_available_reports(self) -> List[str]:
        """
        Get list of available staff reports
        
        Returns:
            List of report file paths
        """
        try:
            import glob
            data_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data')
            
            # Look for schedule_report.json (multi-restaurant report)
            schedule_report_path = os.path.join(data_dir, 'schedule_report.json')
            reports = []
            
            if os.path.exists(schedule_report_path):
                reports.append('schedule_report.json')
            
            # Also look for individual restaurant reports
            report_pattern = os.path.join(data_dir, 'staff_report*.json')
            individual_reports = glob.glob(report_pattern)
            reports.extend([os.path.basename(report) for report in individual_reports])
            
            return reports
        except Exception as e:
            return []
