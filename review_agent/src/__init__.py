"""
Restaurant review system package
"""

from .models import Review
from .storage import DatabaseHandler

# Import scrapers with error handling to avoid env_config issues
try:
    from .scrapers import BaseScraper, GoogleScraper, YelpScraper
    _scrapers_available = True
except ImportError as e:
    # Handle case where env_config is not available
    _scrapers_available = False
    BaseScraper = GoogleScraper = YelpScraper = None

__all__ = [
    'Review',
    'DatabaseHandler',
]

# Only add scrapers if they're available
if _scrapers_available:
    __all__.extend(['BaseScraper', 'GoogleScraper', 'YelpScraper'])
