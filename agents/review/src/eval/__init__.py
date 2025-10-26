"""
Eval module for LLM-based restaurant review analysis
Contains LLM wrapper for comprehensive review data extraction.
"""

# Import with error handling for missing dependencies
try:
    from .llm_wrapper import ClaudeWrapper, LLMResponse
    from .models.extended_review import (
        ReviewExtraction,
        RatingBreakdown,
        MentionedItem,
        StaffMention,
        OperationalInsights,
        VisitContext,
        KeyPhrases,
        AnomalyFlags
    )
    _eval_available = True
except ImportError as e:
    # Handle case where dependencies are not available
    _eval_available = False
    ClaudeWrapper = LLMResponse = None
    ReviewExtraction = RatingBreakdown = MentionedItem = StaffMention = None
    OperationalInsights = VisitContext = KeyPhrases = AnomalyFlags = None

if _eval_available:
    __all__ = [
        'ClaudeWrapper',
        'LLMResponse',
        'ReviewExtraction',
        'RatingBreakdown',
        'MentionedItem',
        'StaffMention',
        'OperationalInsights',
        'VisitContext',
        'KeyPhrases',
        'AnomalyFlags'
    ]
else:
    __all__ = []
