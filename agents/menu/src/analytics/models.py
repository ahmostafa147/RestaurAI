from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum


class ComplexityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DayPart(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    LATE_NIGHT = "late_night"


class PrepBreakdown(BaseModel):
    ingredient_prep_minutes: float
    cooking_minutes: float
    assembly_minutes: float


class PreparationInsight(BaseModel):
    estimated_prep_time_minutes: float
    complexity_level: ComplexityLevel
    prep_notes: str
    cooking_methods: List[str]
    prep_breakdown: PrepBreakdown
    kitchen_efficiency_notes: str


class DayPartDistribution(BaseModel):
    breakfast: float
    lunch: float
    dinner: float
    late_night: float


class ItemDayPartAnalysis(BaseModel):
    primary_day_part: DayPart
    day_part_distribution: DayPartDistribution
    rationale: str


class OverallDayPartAnalysis(BaseModel):
    primary_day_parts: List[DayPart]
    categorization_rationale: str


class DayPartAnalysis(BaseModel):
    overall_restaurant: OverallDayPartAnalysis
    per_item: Dict[str, ItemDayPartAnalysis]


class SentimentIntegration(BaseModel):
    positive_items: List[str]
    negative_items: List[str]
    improvement_opportunities: List[str]


class LLMInsights(BaseModel):
    preparation_insights: Dict[str, PreparationInsight] = Field(default_factory=dict)
    day_part_analysis: DayPartAnalysis = Field(default_factory=lambda: DayPartAnalysis(
        overall_restaurant=OverallDayPartAnalysis(
            primary_day_parts=[],
            categorization_rationale=""
        ),
        per_item={}
    ))
    trend_observations: List[str] = Field(default_factory=list)
    actionable_suggestions: List[str] = Field(default_factory=list)
    sentiment_integration: SentimentIntegration = Field(default_factory=lambda: SentimentIntegration(
        positive_items=[],
        negative_items=[],
        improvement_opportunities=[]
    ))


class LLMErrorResponse(BaseModel):
    error: str
    preparation_insights: Dict[str, PreparationInsight] = Field(default_factory=dict)
    day_part_analysis: DayPartAnalysis = Field(default_factory=lambda: DayPartAnalysis(
        overall_restaurant=OverallDayPartAnalysis(
            primary_day_parts=[],
            categorization_rationale=""
        ),
        per_item={}
    ))
    trend_observations: List[str] = Field(default_factory=list)
    actionable_suggestions: List[str] = Field(default_factory=list)
    sentiment_integration: SentimentIntegration = Field(default_factory=lambda: SentimentIntegration(
        positive_items=[],
        negative_items=[],
        improvement_opportunities=[]
    ))
