import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime

# Import with error handling for missing dependencies
from scraper_interface import ScraperInterface
from pull_dataset import Status

def test_scraper_interface_initialization():
    """Test ScraperInterface initialization"""
    print("Testing ScraperInterface initialization...")
    try:
        scraper_interface = ScraperInterface()
        print("OK - ScraperInterface initialized")
        return scraper_interface
    except Exception as e:
        print(f"ERROR - Initialization failed: {e}")
        return None

def test_google_reviews_scraping():
    """Test Google reviews scraping through ScraperInterface"""
    print("Testing Google reviews scraping...")
    scraper_interface = ScraperInterface()
    
    try:
        snapshot = scraper_interface.scrape_google_reviews(days_limit=9)
        print(f"Google scraping result: {snapshot.snapshot_id}")
        print(f"Source: {snapshot.source}")
        print(f"Status: {snapshot.status}")
        return snapshot
    except Exception as e:
        print(f"ERROR - Google scraping failed: {e}")
        return None

def test_yelp_reviews_scraping():
    """Test Yelp reviews scraping through ScraperInterface"""
    print("Testing Yelp reviews scraping...")
    scraper_interface = ScraperInterface()
    
    try:
        snapshot = scraper_interface.scrape_yelp_reviews(
            unrecommended_reviews=True, 
            start_date="2025-03-02T00:00:00.000Z", 
            end_date="2025-06-01T00:00:00.000Z", 
            sort_by="DATE_DESC"
        )
        print(f"Yelp scraping result: {snapshot.snapshot_id}")
        print(f"Source: {snapshot.source}")
        print(f"Status: {snapshot.status}")
        return snapshot
    except Exception as e:
        print(f"ERROR - Yelp scraping failed: {e}")
        return None

def test_snapshot_status_check():
    """Test snapshot status checking"""
    print("Testing snapshot status check...")
    scraper_interface = ScraperInterface()
    
    # First get a snapshot from Google scraping
    google_snapshot = scraper_interface.scrape_google_reviews(days_limit=9)
    
    try:
        # Check status using snapshot object
        status = scraper_interface.check_snapshot_status(google_snapshot)
        print(f"Snapshot status: {status}")
        
        # Check status using snapshot ID string
        status_by_id = scraper_interface.check_snapshot_status(google_snapshot.snapshot_id)
        print(f"Status by ID: {status_by_id}")
        
        return status
    except Exception as e:
        print(f"ERROR - Status check failed: {e}")
        return None

def test_datetime_conversion():
    """Test datetime to ISO conversion"""
    print("Testing datetime conversion...")
    
    try:
        # Test with current datetime
        now = datetime.now()
        iso_string = ScraperInterface.convert_datetime_to_iso(now)
        print(f"Current datetime: {now}")
        print(f"ISO format: {iso_string}")
        
        # Test with specific datetime
        specific_date = datetime(2025, 3, 2, 12, 0, 0)
        iso_specific = ScraperInterface.convert_datetime_to_iso(specific_date)
        print(f"Specific datetime: {specific_date}")
        print(f"ISO format: {iso_specific}")
        
        return True
    except Exception as e:
        print(f"ERROR - Datetime conversion failed: {e}")
        return False

def test_saved_snapshots():
    """Test that snapshots are saved in the interface"""
    print("Testing saved snapshots...")
    scraper_interface = ScraperInterface()
    
    try:
        # Get initial count
        initial_count = len(scraper_interface.saved_snapshots)
        print(f"Initial snapshot count: {initial_count}")
        
        # Scrape Google reviews
        google_snapshot = scraper_interface.scrape_google_reviews(days_limit=9)
        print(f"After Google scraping: {len(scraper_interface.saved_snapshots)} snapshots")
        
        # Scrape Yelp reviews
        yelp_snapshot = scraper_interface.scrape_yelp_reviews(
            unrecommended_reviews=True,
            start_date="2025-03-02T00:00:00.000Z",
            end_date="2025-06-01T00:00:00.000Z"
        )
        print(f"After Yelp scraping: {len(scraper_interface.saved_snapshots)} snapshots")
        
        # Verify snapshots are saved
        assert len(scraper_interface.saved_snapshots) >= 2
        print("OK - Snapshots are being saved correctly")
        
        return True
    except Exception as e:
        print(f"ERROR - Saved snapshots test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing ScraperInterface")
    print("=" * 30)
    
    
        # Test initialization
    test_scraper_interface_initialization()
    print()
    
    # Test Google scraping
    test_google_reviews_scraping()
    print()
    
    # Test Yelp scraping
    test_yelp_reviews_scraping()
    print()
    
    # Test status checking
    test_snapshot_status_check()
    print()
    
    # Test datetime conversion
    test_datetime_conversion()
    print()
    
    # Test saved snapshots
    # test_saved_snapshots()
    print()
    
    print("ScraperInterface tests completed!")
