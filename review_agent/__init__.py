"""
RestaurAI - Restaurant Review Processing Pipeline
A comprehensive system for scraping, processing, and analyzing restaurant reviews using LLM technology.
"""

# Import main functionality from eval module with error handling
try:
    from .src.eval import (
        ReviewOrchestrator,
        EnrichedReview,
        ClaudeWrapper,
        LLMResponse,
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
    # Handle case where eval module dependencies are not available
    _eval_available = False
    ReviewOrchestrator = EnrichedReview = ClaudeWrapper = LLMResponse = None
    ReviewExtraction = RatingBreakdown = MentionedItem = StaffMention = None
    OperationalInsights = VisitContext = KeyPhrases = AnomalyFlags = None

# Import core models
from .src.models.review import Review

# Import scrapers with error handling to avoid env_config issues
try:
    from .src.scrapers import BaseScraper, GoogleScraper, YelpScraper
    _scrapers_available = True
except ImportError:
    _scrapers_available = False
    BaseScraper = GoogleScraper = YelpScraper = None

__version__ = "1.0.0"
__author__ = "RestaurAI Team"
__description__ = "Restaurant Review Processing Pipeline with LLM Analysis"

__all__ = [
    # Core models (always available)
    'Review',
    
    # Package metadata
    '__version__',
    '__author__',
    '__description__'
]

# Only add eval components if they're available
if _eval_available:
    __all__.extend([
        'ReviewOrchestrator',
        'EnrichedReview',
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
    ])

# Only add scrapers if they're available
if _scrapers_available:
    __all__.extend(['BaseScraper', 'GoogleScraper', 'YelpScraper'])

# Package information
PACKAGE_INFO = {
    'name': 'RestaurAI',
    'version': __version__,
    'description': __description__,
    'author': __author__,
    'main_module': 'src.eval',
    'entry_point': 'ReviewOrchestrator'
}

def get_version():
    """Get the package version"""
    return __version__

def get_info():
    """Get package information"""
    return PACKAGE_INFO.copy()

def quick_start():
    """
    Quick start guide for using RestaurAI
    
    Returns:
        str: Quick start instructions
    """
    return """
🚀 RestaurAI Quick Start Guide

1. Set up your environment:
   - Copy env_template.txt to .env
   - Add your ANTHROPIC_API_KEY to .env

2. Basic usage:
   ```python
   from restaurAI import ReviewOrchestrator, Review
   
   # Initialize orchestrator
   orchestrator = ReviewOrchestrator()
   
   # Process your reviews
   enriched_reviews = orchestrator.process_reviews(your_reviews)
   
   # Save results
   orchestrator.save_enriched_reviews(enriched_reviews, 'output.json')
   ```

3. For more details, see the documentation in src/eval/tests/README.md
"""

# Example usage function
def example_usage():
    """
    Example of how to use RestaurAI
    
    Returns:
        dict: Example usage dictionary
    """
    return {
        'basic_usage': '''
# Basic review processing
from restaurAI import ReviewOrchestrator, Review

# Create orchestrator (uses ANTHROPIC_API_KEY from .env)
orchestrator = ReviewOrchestrator()

# Process reviews through LLM pipeline
enriched_reviews = orchestrator.process_reviews(reviews, batch_size=5)

# Save enriched results
orchestrator.save_enriched_reviews(enriched_reviews, 'enriched_reviews.json')
        ''',
        'advanced_usage': '''
# Advanced usage with custom configuration
from restaurAI import ReviewOrchestrator, Review, ClaudeWrapper

# Custom LLM wrapper
llm_wrapper = ClaudeWrapper()  # Uses environment variables
orchestrator = ReviewOrchestrator()

# Process with custom batch size
enriched_reviews = orchestrator.process_reviews(reviews, batch_size=3)

# Analyze results
for review in enriched_reviews:
    print(f"Sentiment: {review.overall_sentiment}")
    print(f"Mentioned items: {len(review.mentioned_items or [])}")
    print(f"Staff mentions: {len(review.staff_mentions or [])}")
        ''',
        'data_structures': '''
# Working with enriched review data
enriched_review = enriched_reviews[0]

# LLM extracted data
print(f"Overall sentiment: {enriched_review.overall_sentiment}")
print(f"Rating breakdown: {enriched_review.rating_breakdown}")
print(f"Mentioned items: {enriched_review.mentioned_items}")
print(f"Staff mentions: {enriched_review.staff_mentions}")

# Metadata enrichment
print(f"Temporal data: {enriched_review.temporal_metadata}")
print(f"Reviewer data: {enriched_review.reviewer_metadata}")
print(f"Platform data: {enriched_review.platform_metadata}")
        '''
    }
