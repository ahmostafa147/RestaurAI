"""
Pydantic models for ingredient agent structured output
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class SeverityLevel(str, Enum):
    """Severity levels for stock warnings"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class StockWarning(BaseModel):
    """Individual ingredient warning with severity and predicted runout time"""
    ingredient_id: int
    ingredient_name: str
    current_quantity: float
    unit: str
    severity: SeverityLevel
    predicted_runout: datetime
    consumption_rate: float  # units per hour
    days_remaining: float
    supplier: str
    cost_per_unit: float


class ReorderSuggestion(BaseModel):
    """LLM recommendation for reorder quantity, timing, and reasoning"""
    ingredient_id: int
    ingredient_name: str
    suggested_quantity: float
    unit: str
    reasoning: str
    urgency: SeverityLevel
    estimated_cost: float
    supplier: str = ""
    delivery_time_days: Optional[int] = None
    storage_considerations: Optional[str] = None


class ConsumptionForecast(BaseModel):
    """Predicted usage rate for next 24-48 hours"""
    ingredient_id: int
    ingredient_name: str
    predicted_usage_24h: float
    predicted_usage_48h: float
    confidence_level: float  # 0.0 to 1.0
    peak_usage_hours: List[int]  # Hours of day with highest usage
    seasonal_factor: Optional[float] = None


class IngredientInsight(BaseModel):
    """Per-ingredient analysis combining algorithmic and LLM insights"""
    ingredient_id: int
    ingredient_name: str
    current_stock: float
    unit: str
    consumption_volatility: float  # Standard deviation of usage
    optimal_reorder_threshold: float
    reorder_suggestion: Optional[ReorderSuggestion] = None
    consumption_forecast: Optional[ConsumptionForecast] = None
    critical_for_menu_items: List[str]  # Menu items that use this ingredient
    cost_impact: float  # Total cost if this ingredient runs out


class LLMInsights(BaseModel):
    """Complete LLM analysis output"""
    reorder_suggestions: List[ReorderSuggestion] = Field(default_factory=list)
    critical_items: List[int] = Field(default_factory=list)  # Ingredient IDs that are most critical
    optimization_tips: List[str] = Field(default_factory=list)
    seasonal_recommendations: List[str] = Field(default_factory=list)
    cost_optimization_suggestions: List[str] = Field(default_factory=list)
    supplier_analysis: Dict[str, Any] = Field(default_factory=dict)  # Analysis of supplier performance
    inventory_turnover_insights: List[str] = Field(default_factory=list)


class InventoryReport(BaseModel):
    """Complete inventory report structure"""
    metadata: Dict[str, Any]
    current_stock: List[Dict[str, Any]]
    warnings: List[StockWarning]
    consumption_analysis: Dict[str, Any]
    llm_insights: LLMInsights
    generated_at: datetime = Field(default_factory=datetime.now)


class LLMErrorResponse(BaseModel):
    """Error response from LLM"""
    error: str
    fallback_data: Optional[Dict[str, Any]] = None
