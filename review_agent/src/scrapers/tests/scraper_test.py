import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Handle env_config import with fallback
try:
    from ..env_config import token, google_map_url, google_bright_data_url, yelp_url, yelp_bright_data_url
except ImportError:
    from env_config import token, google_map_url, google_bright_data_url, yelp_url, yelp_bright_data_url
from google_scraper import GoogleScraper
from yelp_scraper import YelpScraper

def test_google_scraper():
    google_scraper = GoogleScraper(token, google_map_url, google_bright_data_url)
    snapshot = google_scraper.scrape_reviews(days_limit=9)
    print(snapshot)

def test_yelp_scraper():
    yelp_scraper = YelpScraper(token, yelp_url, yelp_bright_data_url)
    snapshot = yelp_scraper.scrape_reviews(unrecommended_reviews=True, start_date="2025-03-02T00:00:00.000Z", end_date="2025-06-01T00:00:00.000Z", sort_by="DATE_DESC")
    print(snapshot)

if __name__ == "__main__":
    test_google_scraper()
    test_yelp_scraper()