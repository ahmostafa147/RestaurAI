"""
Pydantic models for analytics results
"""
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

class MenuItem(BaseModel):
    name: str
    mention_count: int
    positive_count: int
    negative_count: int
    sentiment_score: float  # -1 to 1
    aspects: Dict[str, int]  # aspect -> count
    
class StaffMember(BaseModel):
    name: str
    role: str
    mention_count: int
    positive_count: int
    negative_count: int
    average_sentiment: float
    
class OverallMetrics(BaseModel):
    total_reviews: int
    average_rating: float
    rating_distribution: Dict[str, int]  # "1.0" -> count
    response_rate: float
    reviews_by_platform: Dict[str, int]
    
class AnalyticsResult(BaseModel):
    generated_at: datetime
    overall_metrics: OverallMetrics
    temporal_metrics: Dict[str, Any]
    menu_analytics: List[MenuItem]
    staff_analytics: List[StaffMember]
    operational_metrics: Dict[str, Any]
    customer_insights: Dict[str, Any]
    reputation_insights: Dict[str, Any]
