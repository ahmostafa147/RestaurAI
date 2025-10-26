"""
LLM-based analysis for staff management using Anthropic Claude
"""

import sys
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

try:
    from anthropic import Anthropic
    from dotenv import load_dotenv
except ImportError as e:
    raise ImportError(f"Missing required dependencies: {e}. Please install anthropic and python-dotenv.")

from .models import StaffInsights, AbsenceRecommendation


class LLMAnalyzer:
    """LLM-based analysis for staff scheduling insights and recommendations"""
    
    def __init__(self, anthropic_api_key: Optional[str] = None):
        """
        Initialize the LLM analyzer
        
        Args:
            anthropic_api_key: Anthropic API key. If None, will try to load from .env
        """
        # Load environment variables
        env_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '.env')
        load_dotenv(env_path)
        
        # Get API key
        api_key = anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')
        model = os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')
        
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not provided and not found in environment variables")
        
        # Initialize Anthropic client
        self.client = Anthropic(api_key=api_key)
        self.model = model
    
    def analyze_schedule_weaknesses(self, schedule_data: Dict[str, Any]) -> StaffInsights:
        """
        Analyze schedule data and generate insights about weaknesses
        
        Args:
            schedule_data: Schedule analysis data from ScheduleAnalyzer
            
        Returns:
            StaffInsights with LLM-generated analysis
        """
        try:
            prompt = f"""You are an expert restaurant operations manager analyzing staff scheduling data. 

Please analyze the following schedule data and provide insights about weaknesses, opportunities for improvement, and recommendations.

Schedule Data:
{self._format_schedule_data(schedule_data)}

Please provide:
1. Key weaknesses identified (understaffing, overstaffing, overwork patterns)
2. Root causes of these issues
3. Specific recommendations for improvement
4. Priority levels for each recommendation
5. Expected impact of implementing changes

Focus on practical, actionable insights that a restaurant manager can implement immediately."""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            analysis_text = response.content[0].text
            
            return StaffInsights(
                analysis=analysis_text,
                generated_at=datetime.now().isoformat(),
                confidence_score=0.8,  # High confidence for structured analysis
                recommendations=self._extract_recommendations(analysis_text),
                priority_issues=self._extract_priority_issues(analysis_text)
            )
            
        except Exception as e:
            return StaffInsights(
                analysis=f"Error analyzing schedule: {str(e)}",
                generated_at=datetime.now().isoformat(),
                confidence_score=0.0,
                recommendations=[],
                priority_issues=[]
            )
    
    def suggest_absence_adjustments(self, absence_data: Dict[str, Any]) -> AbsenceRecommendation:
        """
        Suggest adjustments when someone calls in absent
        
        Args:
            absence_data: Data about the absence and available replacements
            
        Returns:
            AbsenceRecommendation with LLM-generated suggestions
        """
        try:
            prompt = f"""You are an expert restaurant manager handling a staff absence. 

Absence Details:
{self._format_absence_data(absence_data)}

Please provide:
1. Immediate action recommendations (who to call first, backup plans)
2. Schedule adjustments needed
3. Impact assessment on service quality
4. Communication strategy for staff and customers
5. Prevention strategies for future absences

Focus on practical steps that can be implemented immediately to minimize service disruption."""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=0.2,  # Lower temperature for more focused recommendations
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            recommendation_text = response.content[0].text
            
            return AbsenceRecommendation(
                recommendations=recommendation_text,
                priority_action=self._extract_priority_action(recommendation_text),
                impact_assessment=self._extract_impact_assessment(recommendation_text),
                generated_at=datetime.now().isoformat(),
                confidence_score=0.9
            )
            
        except Exception as e:
            return AbsenceRecommendation(
                recommendations=f"Error generating recommendations: {str(e)}",
                priority_action="Contact available staff immediately",
                impact_assessment="Unable to assess impact due to analysis error",
                generated_at=datetime.now().isoformat(),
                confidence_score=0.0
            )
    
    def generate_schedule_optimization(self, current_schedule: Dict[str, Any], 
                                     constraints: Dict[str, Any] = None) -> str:
        """
        Generate schedule optimization recommendations
        
        Args:
            current_schedule: Current schedule data
            constraints: Any constraints (budget, staff preferences, etc.)
            
        Returns:
            String with optimization recommendations
        """
        try:
            constraints_text = ""
            if constraints:
                constraints_text = f"\nConstraints: {constraints}"
            
            prompt = f"""You are an expert restaurant scheduling consultant. 

Current Schedule:
{self._format_schedule_data(current_schedule)}
{constraints_text}

Please provide:
1. Optimization opportunities in the current schedule
2. Specific changes to improve efficiency and staff satisfaction
3. Cost-benefit analysis of proposed changes
4. Implementation timeline and steps
5. Metrics to track improvement

Focus on data-driven recommendations that balance operational efficiency with staff well-being."""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.4,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"Error generating optimization recommendations: {str(e)}"
    
    def analyze_staff_performance_patterns(self, performance_data: Dict[str, Any]) -> str:
        """
        Analyze staff performance patterns and suggest improvements
        
        Args:
            performance_data: Staff performance and utilization data
            
        Returns:
            String with performance analysis and recommendations
        """
        try:
            prompt = f"""You are an expert HR consultant analyzing restaurant staff performance patterns.

Performance Data:
{self._format_performance_data(performance_data)}

Please provide:
1. Key performance patterns identified
2. Staff strengths and areas for improvement
3. Training and development recommendations
4. Recognition and motivation strategies
5. Retention strategies for high performers

Focus on actionable insights that can improve staff satisfaction and performance."""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1800,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"Error analyzing performance patterns: {str(e)}"
    
    def _format_schedule_data(self, data: Dict[str, Any]) -> str:
        """Format schedule data for LLM consumption"""
        formatted = []
        
        if "overall_coverage_score" in data:
            formatted.append(f"Overall Coverage Score: {data['overall_coverage_score']:.2f}")
        
        if "understaffed_slots" in data:
            formatted.append("\nUnderstaffed Time Slots:")
            for slot in data["understaffed_slots"]:
                formatted.append(f"  - {slot['day']} {slot['time']}: {slot['staff_count']} staff, roles: {slot['roles']}")
        
        if "overstaffed_slots" in data:
            formatted.append("\nOverstaffed Time Slots:")
            for slot in data["overstaffed_slots"]:
                formatted.append(f"  - {slot['day']} {slot['time']}: {slot['staff_count']} staff, roles: {slot['roles']}")
        
        if "overworked_staff" in data:
            formatted.append("\nOverworked Staff:")
            for staff in data["overworked_staff"]:
                formatted.append(f"  - {staff['name']} ({staff['role']}): {staff['weekly_hours']} hours/week, {staff['consecutive_days']} consecutive days")
        
        if "underutilized_staff" in data:
            formatted.append("\nUnderutilized Staff:")
            for staff in data["underutilized_staff"]:
                formatted.append(f"  - {staff['name']} ({staff['role']}): {staff['weekly_hours']} hours/week")
        
        return "\n".join(formatted)
    
    def _format_absence_data(self, data: Dict[str, Any]) -> str:
        """Format absence data for LLM consumption"""
        formatted = []
        
        if "absent_staff" in data:
            staff = data["absent_staff"]
            formatted.append(f"Absent Staff: {staff['name']} ({staff['role']})")
            formatted.append(f"Absence Date: {staff['date']}")
            formatted.append(f"Shift Details: {staff.get('shift_details', 'Not specified')}")
        
        if "suggested_replacements" in data:
            formatted.append("\nSuggested Replacements:")
            for i, replacement in enumerate(data["suggested_replacements"], 1):
                formatted.append(f"  {i}. {replacement['name']} ({replacement['role']}) - Compatibility: {replacement['compatibility_score']:.2f}, Available: {replacement['is_available']}")
        
        if "impact_assessment" in data:
            formatted.append(f"\nImpact Assessment: {data['impact_assessment']}")
        
        return "\n".join(formatted)
    
    def _format_performance_data(self, data: Dict[str, Any]) -> str:
        """Format performance data for LLM consumption"""
        formatted = []
        
        if "utilization_metrics" in data:
            formatted.append("Staff Utilization:")
            for metric in data["utilization_metrics"]:
                status = "Overworked" if metric.get("is_overworked") else "Underutilized" if metric.get("is_underutilized") else "Normal"
                formatted.append(f"  - {metric['staff_name']} ({metric['role']}): {metric['weekly_hours']} hours/week - {status}")
        
        if "role_distribution" in data:
            formatted.append("\nRole Distribution:")
            for role, count in data["role_distribution"].items():
                formatted.append(f"  - {role}: {count} staff")
        
        return "\n".join(formatted)
    
    def _extract_recommendations(self, analysis_text: str) -> List[str]:
        """Extract specific recommendations from analysis text"""
        recommendations = []
        lines = analysis_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith(('•', '-', '1.', '2.', '3.', '4.', '5.')) or 'recommend' in line.lower():
                recommendations.append(line)
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _extract_priority_issues(self, analysis_text: str) -> List[str]:
        """Extract priority issues from analysis text"""
        issues = []
        lines = analysis_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['urgent', 'critical', 'priority', 'immediate']):
                issues.append(line)
        
        return issues[:3]  # Return top 3 priority issues
    
    def _extract_priority_action(self, recommendation_text: str) -> str:
        """Extract the most important action from recommendations"""
        lines = recommendation_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['first', 'immediately', 'priority', 'urgent']):
                return line
        
        # Fallback to first actionable line
        for line in lines:
            if line.strip() and not line.startswith('#'):
                return line.strip()
        
        return "Contact available staff immediately"
    
    def _extract_impact_assessment(self, recommendation_text: str) -> str:
        """Extract impact assessment from recommendations"""
        lines = recommendation_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if 'impact' in line.lower() or 'effect' in line.lower() or 'consequence' in line.lower():
                return line
        
        return "Impact assessment not available"
