"""
Data models for staff analytics
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class StaffInsights:
    """LLM-generated insights about staff scheduling"""
    analysis: str
    generated_at: str
    confidence_score: float  # 0-1 scale
    recommendations: List[str]
    priority_issues: List[str]


@dataclass
class AbsenceRecommendation:
    """LLM-generated recommendations for handling staff absences"""
    recommendations: str
    priority_action: str
    impact_assessment: str
    generated_at: str
    confidence_score: float  # 0-1 scale


@dataclass
class ScheduleReport:
    """Comprehensive schedule analysis report"""
    restaurant_key: str
    generated_at: str
    overall_coverage_score: float
    weaknesses: dict
    utilization_metrics: List[dict]
    llm_insights: Optional[StaffInsights]
    recommendations: List[str]


@dataclass
class AbsenceHandling:
    """Data structure for absence handling analysis"""
    absent_staff_id: int
    absent_staff_name: str
    absence_date: str
    suggested_replacements: List[dict]
    impact_assessment: str
    recommendations: AbsenceRecommendation
