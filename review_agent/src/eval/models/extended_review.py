from typing import List, Optional
from pydantic import BaseModel, Field

class RatingBreakdown(BaseModel):
    """Rating breakdown for different aspects"""
    food: Optional[int] = Field(None, ge=1, le=5)
    service: Optional[int] = Field(None, ge=1, le=5)
    ambiance: Optional[int] = Field(None, ge=1, le=5)
    value: Optional[int] = Field(None, ge=1, le=5)

class MentionedItem(BaseModel):
    """Mentioned menu item with details"""
    name: str
    sentiment: str = Field(..., pattern="^(positive|negative|mixed)$")
    aspects: List[str] = Field(default_factory=list)

class StaffMention(BaseModel):
    """Staff member mention"""
    role: str = Field(..., pattern="^(server|host|manager|bartender|chef)$")
    name: Optional[str] = None
    sentiment: str = Field(..., pattern="^(positive|negative)$")
    specific_feedback: Optional[str] = None

class OperationalInsights(BaseModel):
    """Operational insights from review"""
    wait_time: str = Field(..., pattern="^(none|short|reasonable|long|excessive|not_mentioned)$")
    reservation_experience: str = Field(..., pattern="^(positive|negative|not_mentioned)$")
    cleanliness: str = Field(..., pattern="^(positive|negative|not_mentioned)$")
    noise_level: str = Field(..., pattern="^(quiet|moderate|loud|not_mentioned)$")
    crowding: str = Field(..., pattern="^(empty|comfortable|busy|overcrowded|not_mentioned)$")

class VisitContext(BaseModel):
    """Visit context information"""
    party_type: str = Field(..., pattern="^(solo|couple|family|business|friends|large_group|unknown)$")
    occasion: str = Field(..., pattern="^(regular|date|business|celebration|tourist|unknown)$")
    time_of_visit: str = Field(..., pattern="^(breakfast|lunch|dinner|late_night|unknown)$")
    first_visit: Optional[bool] = None
    would_return: Optional[bool] = None
    would_recommend: Optional[bool] = None

class KeyPhrases(BaseModel):
    """Key phrases extracted from review"""
    positive_highlights: List[str] = Field(default_factory=list)
    negative_issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)

class AnomalyFlags(BaseModel):
    """Anomaly detection flags"""
    potential_fake: bool = False
    health_safety_concern: bool = False
    extreme_emotion: bool = False
    competitor_mention: bool = False

class ReviewExtraction(BaseModel):
    """Complete review extraction schema"""
    overall_sentiment: str = Field(..., pattern="^(positive|negative|mixed|neutral)$")
    rating_breakdown: Optional[RatingBreakdown] = None
    mentioned_items: List[MentionedItem] = Field(default_factory=list)
    staff_mentions: List[StaffMention] = Field(default_factory=list)
    operational_insights: Optional[OperationalInsights] = None
    visit_context: Optional[VisitContext] = None
    key_phrases: Optional[KeyPhrases] = None
    anomaly_flags: Optional[AnomalyFlags] = None