# Simple and reliable import strategy
import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Handle env_config import with fallback
try:
    from .env_config import token, google_map_url, google_bright_data_url, yelp_url, yelp_bright_data_url
except ImportError:
    from env_config import token, google_map_url, google_bright_data_url, yelp_url, yelp_bright_data_url
from google_scraper import GoogleScraper
from yelp_scraper import YelpScraper
from pull_dataset import PullDataset, Status

from typing import Dict, Any, Union
from datetime import datetime

# Handle models import
try:
    from models.snapshot import Snapshot
except ImportError:
    # Fallback when running from scrapers directory
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from models.snapshot import Snapshot
#Wrapper for all scraper / database interactions
class ScraperInterface:
    def __init__(self):
        # Keep default scrapers for backward compatibility
        self.default_google_scraper = GoogleScraper(token, google_map_url, google_bright_data_url)
        self.default_yelp_scraper = YelpScraper(token, yelp_url, yelp_bright_data_url)
        self.pull_dataset = PullDataset()
        self.saved_snapshots = []
    
    def _create_google_scraper(self, google_url: str):
        """Create a Google scraper for a specific URL"""
        return GoogleScraper(token, google_url, google_bright_data_url)
    
    def _create_yelp_scraper(self, yelp_url: str):
        """Create a Yelp scraper for a specific URL"""
        return YelpScraper(token, yelp_url, yelp_bright_data_url)
    
    def scrape_google_reviews(self, days_limit: int = 9, google_url: str = None, restaurant_id: str = None) -> Snapshot:
        # Use specific scraper if URL provided, otherwise use default
        google_scraper = self._create_google_scraper(google_url) if google_url else self.default_google_scraper
        
        snapshot_id = google_scraper.scrape_reviews(days_limit)
        snapshot = Snapshot(snapshot_id['snapshot_id'], "google", self.pull_dataset.check_snapshot_status(snapshot_id).value, restaurant_id=restaurant_id)
        self.saved_snapshots.append(snapshot)
        return snapshot
    
    def scrape_yelp_reviews(self, unrecommended_reviews: bool, start_date: Union[str, datetime], end_date: Union[str, datetime], sort_by: str = "DATE_DESC", yelp_url: str = None, restaurant_id: str = None) -> Snapshot:
        # Use specific scraper if URL provided, otherwise use default
        yelp_scraper = self._create_yelp_scraper(yelp_url) if yelp_url else self.default_yelp_scraper
        
        if isinstance(start_date, datetime):
            start_date = self.convert_datetime_to_iso(start_date)
        if isinstance(end_date, datetime):
            end_date = self.convert_datetime_to_iso(end_date)
        if start_date is None or end_date is None:
            raise ValueError("Start and end date must be provided")
        snapshot_id = yelp_scraper.scrape_reviews(unrecommended_reviews, start_date, end_date, sort_by)
        snapshot = Snapshot(snapshot_id['snapshot_id'], "yelp", self.pull_dataset.check_snapshot_status(snapshot_id).value, restaurant_id=restaurant_id)
        self.saved_snapshots.append(snapshot)
        return snapshot
    def check_snapshot_status(self, snapshot_id: Union[str, Snapshot]) -> Status:
        if isinstance(snapshot_id, Snapshot):
            snapshot_id = snapshot_id.snapshot_id
        return self.pull_dataset.check_snapshot_status(snapshot_id)
    def safe_pull_dataset(self, snapshot_id: Union[str, Snapshot]) -> Dict[str, Any]:
        if isinstance(snapshot_id, Snapshot):
            snapshot_id = snapshot_id.snapshot_id
        return self.pull_dataset.safe_pull_dataset(snapshot_id)
        
    @staticmethod
    def convert_datetime_to_iso(datetime: datetime) -> str:
        return datetime.isoformat()