"""
Report generator for staff scheduling analytics
"""

import sys
import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from .schedule_analyzer import ScheduleAnalyzer
from .llm_analyzer import LLMAnalyzer
from .models import ScheduleReport, StaffInsights, AbsenceRecommendation


class ReportGenerator:
    """Generates comprehensive staff scheduling reports"""
    
    def __init__(self, anthropic_api_key: Optional[str] = None):
        """
        Initialize the report generator
        
        Args:
            anthropic_api_key: Anthropic API key for LLM analysis
        """
        self.schedule_analyzer = ScheduleAnalyzer()
        self.llm_analyzer = LLMAnalyzer(anthropic_api_key)
    
    def generate_comprehensive_report(self, restaurant_key: str) -> Dict[str, Any]:
        """
        Generate comprehensive staff scheduling report
        
        Args:
            restaurant_key: Restaurant identifier
            
        Returns:
            Complete schedule report dictionary
        """
        try:
            # Analyze schedule weaknesses
            weaknesses = self.schedule_analyzer.identify_weaknesses(restaurant_key)
            
            # Analyze utilization
            utilization_metrics = self.schedule_analyzer.analyze_utilization(restaurant_key)
            
            # Generate LLM insights
            llm_insights = self.llm_analyzer.analyze_schedule_weaknesses(weaknesses)
            
            # Create comprehensive report
            report = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "restaurant_key": restaurant_key,
                    "report_type": "comprehensive_schedule_analysis"
                },
                "overall_coverage_score": weaknesses.get("overall_coverage_score", 0.0),
                "total_weaknesses": weaknesses.get("total_weaknesses", 0),
                "weaknesses": {
                    "understaffed_slots": weaknesses.get("understaffed_slots", []),
                    "overstaffed_slots": weaknesses.get("overstaffed_slots", []),
                    "overworked_staff": weaknesses.get("overworked_staff", []),
                    "underutilized_staff": weaknesses.get("underutilized_staff", [])
                },
                "utilization_metrics": [
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
                ],
                "llm_insights": {
                    "analysis": llm_insights.analysis,
                    "confidence_score": llm_insights.confidence_score,
                    "recommendations": llm_insights.recommendations,
                    "priority_issues": llm_insights.priority_issues,
                    "generated_at": llm_insights.generated_at
                },
                "summary": {
                    "coverage_status": self._get_coverage_status(weaknesses.get("overall_coverage_score", 0.0)),
                    "staff_utilization_status": self._get_utilization_status(utilization_metrics),
                    "critical_issues": len(weaknesses.get("understaffed_slots", [])) + len(weaknesses.get("overworked_staff", [])),
                    "optimization_opportunities": len(weaknesses.get("overstaffed_slots", [])) + len(weaknesses.get("underutilized_staff", []))
                }
            }
            
            return report
            
        except Exception as e:
            return {
                "error": f"Failed to generate comprehensive report: {str(e)}",
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "restaurant_key": restaurant_key,
                    "error": True
                }
            }
    
    def generate_weakness_report(self, restaurant_key: str) -> Dict[str, Any]:
        """
        Generate focused weakness identification report
        
        Args:
            restaurant_key: Restaurant identifier
            
        Returns:
            Weakness report dictionary
        """
        try:
            weaknesses = self.schedule_analyzer.identify_weaknesses(restaurant_key)
            
            return {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "restaurant_key": restaurant_key,
                    "report_type": "weakness_analysis"
                },
                "overall_coverage_score": weaknesses.get("overall_coverage_score", 0.0),
                "total_weaknesses": weaknesses.get("total_weaknesses", 0),
                "understaffed_slots": weaknesses.get("understaffed_slots", []),
                "overstaffed_slots": weaknesses.get("overstaffed_slots", []),
                "overworked_staff": weaknesses.get("overworked_staff", []),
                "underutilized_staff": weaknesses.get("underutilized_staff", []),
                "priority_issues": self._prioritize_issues(weaknesses)
            }
            
        except Exception as e:
            return {
                "error": f"Failed to generate weakness report: {str(e)}",
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "restaurant_key": restaurant_key,
                    "error": True
                }
            }
    
    def generate_absence_handling_report(self, restaurant_key: str, absent_staff_id: int, 
                                        absence_date: str) -> Dict[str, Any]:
        """
        Generate absence handling report with replacement suggestions
        
        Args:
            restaurant_key: Restaurant identifier
            absent_staff_id: ID of absent staff member
            absence_date: Date of absence
            
        Returns:
            Absence handling report dictionary
        """
        try:
            # Get suggested replacements
            suggestions = self.schedule_analyzer.suggest_absence_replacements(
                restaurant_key, absent_staff_id, absence_date
            )
            
            # Get absent staff member details
            from backend.src.core.staff_manager import StaffManager
            staff_manager = StaffManager(restaurant_key)
            absent_member = staff_manager.get_staff_member(absent_staff_id)
            
            if not absent_member:
                return {
                    "error": f"Staff member with ID {absent_staff_id} not found",
                    "metadata": {
                        "generated_at": datetime.now().isoformat(),
                        "restaurant_key": restaurant_key,
                        "error": True
                    }
                }
            
            # Prepare data for LLM analysis
            absence_data = {
                "absent_staff": {
                    "name": absent_member.name,
                    "role": absent_member.role,
                    "date": absence_date,
                    "shift_details": f"Works on {absence_date}"
                },
                "suggested_replacements": suggestions,
                "impact_assessment": "Moderate impact expected"
            }
            
            # Generate LLM recommendations
            llm_recommendations = self.llm_analyzer.suggest_absence_adjustments(absence_data)
            
            return {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "restaurant_key": restaurant_key,
                    "report_type": "absence_handling"
                },
                "absent_staff": {
                    "staff_id": absent_staff_id,
                    "name": absent_member.name,
                    "role": absent_member.role,
                    "absence_date": absence_date
                },
                "suggested_replacements": suggestions,
                "llm_recommendations": {
                    "recommendations": llm_recommendations.recommendations,
                    "priority_action": llm_recommendations.priority_action,
                    "impact_assessment": llm_recommendations.impact_assessment,
                    "confidence_score": llm_recommendations.confidence_score,
                    "generated_at": llm_recommendations.generated_at
                },
                "summary": {
                    "total_suggestions": len(suggestions),
                    "available_replacements": len([s for s in suggestions if s["is_available"]]),
                    "best_match": suggestions[0] if suggestions else None,
                    "urgency_level": self._assess_urgency(absent_member.role, absence_date)
                }
            }
            
        except Exception as e:
            return {
                "error": f"Failed to generate absence handling report: {str(e)}",
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "restaurant_key": restaurant_key,
                    "error": True
                }
            }
    
    def generate_coverage_metrics(self, restaurant_key: str) -> Dict[str, Any]:
        """
        Generate coverage metrics for dashboard display
        
        Args:
            restaurant_key: Restaurant identifier
            
        Returns:
            Coverage metrics dictionary
        """
        try:
            coverage_metrics = self.schedule_analyzer.analyze_coverage(restaurant_key)
            utilization_metrics = self.schedule_analyzer.analyze_utilization(restaurant_key)
            
            # Calculate summary metrics
            total_slots = len(coverage_metrics)
            understaffed_slots = len([m for m in coverage_metrics if m.is_understaffed])
            overstaffed_slots = len([m for m in coverage_metrics if m.is_overstaffed])
            
            overworked_staff = len([m for m in utilization_metrics if m.is_overworked])
            underutilized_staff = len([m for m in utilization_metrics if m.is_underutilized])
            
            return {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "restaurant_key": restaurant_key,
                    "report_type": "coverage_metrics"
                },
                "coverage_summary": {
                    "total_time_slots": total_slots,
                    "understaffed_slots": understaffed_slots,
                    "overstaffed_slots": overstaffed_slots,
                    "coverage_percentage": ((total_slots - understaffed_slots) / total_slots * 100) if total_slots > 0 else 0
                },
                "staff_utilization": {
                    "total_staff": len(utilization_metrics),
                    "overworked_staff": overworked_staff,
                    "underutilized_staff": underutilized_staff,
                    "optimal_utilization": len(utilization_metrics) - overworked_staff - underutilized_staff
                },
                "daily_coverage": self._summarize_daily_coverage(coverage_metrics),
                "role_coverage": self._summarize_role_coverage(coverage_metrics),
                "alerts": self._generate_coverage_alerts(coverage_metrics, utilization_metrics)
            }
            
        except Exception as e:
            return {
                "error": f"Failed to generate coverage metrics: {str(e)}",
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "restaurant_key": restaurant_key,
                    "error": True
                }
            }
    
    def export_report(self, report: Dict[str, Any], output_path: str) -> bool:
        """
        Export report to JSON file
        
        Args:
            report: Report dictionary to export
            output_path: Path to save the report
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting report: {e}")
            return False
    
    def _get_coverage_status(self, coverage_score: float) -> str:
        """Get human-readable coverage status"""
        if coverage_score >= 0.9:
            return "Excellent"
        elif coverage_score >= 0.8:
            return "Good"
        elif coverage_score >= 0.7:
            return "Fair"
        elif coverage_score >= 0.6:
            return "Poor"
        else:
            return "Critical"
    
    def _get_utilization_status(self, utilization_metrics: List) -> str:
        """Get human-readable utilization status"""
        if not utilization_metrics:
            return "No data"
        
        overworked_count = len([m for m in utilization_metrics if m.is_overworked])
        underutilized_count = len([m for m in utilization_metrics if m.is_underutilized])
        total_count = len(utilization_metrics)
        
        if overworked_count > total_count * 0.3:
            return "Overworked"
        elif underutilized_count > total_count * 0.3:
            return "Underutilized"
        else:
            return "Balanced"
    
    def _prioritize_issues(self, weaknesses: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prioritize issues by severity"""
        issues = []
        
        # Understaffed slots are highest priority
        for slot in weaknesses.get("understaffed_slots", []):
            issues.append({
                "type": "understaffed",
                "priority": "high",
                "description": f"Understaffed on {slot['day']} {slot['time']}",
                "details": slot
            })
        
        # Overworked staff are high priority
        for staff in weaknesses.get("overworked_staff", []):
            issues.append({
                "type": "overworked",
                "priority": "high",
                "description": f"{staff['name']} is overworked ({staff['weekly_hours']} hours/week)",
                "details": staff
            })
        
        # Overstaffed slots are medium priority
        for slot in weaknesses.get("overstaffed_slots", []):
            issues.append({
                "type": "overstaffed",
                "priority": "medium",
                "description": f"Overstaffed on {slot['day']} {slot['time']}",
                "details": slot
            })
        
        # Underutilized staff are low priority
        for staff in weaknesses.get("underutilized_staff", []):
            issues.append({
                "type": "underutilized",
                "priority": "low",
                "description": f"{staff['name']} is underutilized ({staff['weekly_hours']} hours/week)",
                "details": staff
            })
        
        return issues
    
    def _assess_urgency(self, role: str, absence_date: str) -> str:
        """Assess urgency level of absence"""
        # Weekend absences are more urgent
        try:
            date_obj = datetime.strptime(absence_date, "%Y-%m-%d")
            if date_obj.weekday() >= 5:  # Saturday or Sunday
                return "high"
        except:
            pass
        
        # Critical roles are more urgent
        critical_roles = ["chef", "head chef", "manager"]
        if any(critical in role.lower() for critical in critical_roles):
            return "high"
        
        return "medium"
    
    def _summarize_daily_coverage(self, coverage_metrics: List) -> Dict[str, Any]:
        """Summarize coverage by day of week"""
        daily_summary = {}
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for day in days:
            day_metrics = [m for m in coverage_metrics if m.day_of_week == day]
            if day_metrics:
                avg_coverage = sum(m.coverage_score for m in day_metrics) / len(day_metrics)
                understaffed_count = len([m for m in day_metrics if m.is_understaffed])
                daily_summary[day] = {
                    "average_coverage": avg_coverage,
                    "understaffed_slots": understaffed_count,
                    "total_slots": len(day_metrics)
                }
        
        return daily_summary
    
    def _summarize_role_coverage(self, coverage_metrics: List) -> Dict[str, Any]:
        """Summarize coverage by role"""
        role_summary = {}
        
        for metric in coverage_metrics:
            for role in metric.roles_covered:
                if role not in role_summary:
                    role_summary[role] = {"total_slots": 0, "understaffed_slots": 0}
                
                role_summary[role]["total_slots"] += 1
                if metric.is_understaffed:
                    role_summary[role]["understaffed_slots"] += 1
        
        # Calculate coverage percentages
        for role, data in role_summary.items():
            data["coverage_percentage"] = (
                (data["total_slots"] - data["understaffed_slots"]) / data["total_slots"] * 100
                if data["total_slots"] > 0 else 0
            )
        
        return role_summary
    
    def _generate_coverage_alerts(self, coverage_metrics: List, utilization_metrics: List) -> List[Dict[str, Any]]:
        """Generate coverage alerts for dashboard"""
        alerts = []
        
        # Critical understaffing alerts
        critical_understaffed = [
            m for m in coverage_metrics 
            if m.is_understaffed and m.coverage_score < 0.5
        ]
        
        for metric in critical_understaffed:
            alerts.append({
                "type": "critical_understaffing",
                "message": f"Critical understaffing on {metric.day_of_week} {metric.time_slot}",
                "severity": "high",
                "details": metric
            })
        
        # Overwork alerts
        overworked_staff = [m for m in utilization_metrics if m.is_overworked]
        for staff in overworked_staff:
            alerts.append({
                "type": "overwork",
                "message": f"{staff.staff_name} is overworked ({staff.total_hours_per_week} hours/week)",
                "severity": "medium",
                "details": staff
            })
        
        return alerts
