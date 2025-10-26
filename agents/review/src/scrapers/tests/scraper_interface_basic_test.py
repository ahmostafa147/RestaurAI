"""
Basic test for scraper_interface.py - tests functionality without API calls
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime

def test_imports():
    """Test if all imports work correctly"""
    print("Testing imports...")
    
    try:
        from scraper_interface import ScraperInterface
        from pull_dataset import Status
        print("OK - All imports successful")
        return True
    except Exception as e:
        print(f"ERROR - Import failed: {e}")
        return False

def test_initialization():
    """Test ScraperInterface initialization"""
    print("Testing ScraperInterface initialization...")
    
    try:
        from scraper_interface import ScraperInterface
        scraper_interface = ScraperInterface()
        print("OK - ScraperInterface initialized successfully")
        print(f"   Google scraper: {type(scraper_interface.google_scraper).__name__}")
        print(f"   Yelp scraper: {type(scraper_interface.yelp_scraper).__name__}")
        print(f"   Pull dataset: {type(scraper_interface.pull_dataset).__name__}")
        print(f"   Saved snapshots: {len(scraper_interface.saved_snapshots)}")
        return scraper_interface
    except Exception as e:
        print(f"ERROR - Initialization failed: {e}")
        return None

def test_datetime_conversion():
    """Test datetime to ISO conversion"""
    print("Testing datetime conversion...")
    
    try:
        from scraper_interface import ScraperInterface
        
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
        
        # Verify the conversion is correct
        assert iso_string == now.isoformat()
        assert iso_specific == specific_date.isoformat()
        print("OK - Datetime conversion works correctly")
        
        return True
    except Exception as e:
        print(f"ERROR - Datetime conversion failed: {e}")
        return False

def test_snapshot_creation():
    """Test Snapshot model creation"""
    print("Testing Snapshot model...")
    
    try:
        from models.snapshot import Snapshot
        
        # Create a test snapshot
        snapshot = Snapshot("test_001", "google", "ready")
        print(f"Snapshot ID: {snapshot.snapshot_id}")
        print(f"Source: {snapshot.source}")
        print(f"Status: {snapshot.status}")
        
        # Test to_dict method
        snapshot_dict = snapshot.to_dict()
        print(f"Dictionary: {snapshot_dict}")
        
        # Test from_dict method
        recreated_snapshot = snapshot.from_dict(snapshot_dict)
        print(f"Recreated snapshot: {recreated_snapshot.snapshot_id}")
        
        assert snapshot.snapshot_id == "test_001"
        assert snapshot.source == "google"
        assert snapshot.status == "ready"
        print("OK - Snapshot model works correctly")
        
        return True
    except Exception as e:
        print(f"ERROR - Snapshot model test failed: {e}")
        return False

def test_status_enum():
    """Test Status enum"""
    print("Testing Status enum...")
    
    try:
        from pull_dataset import Status
        
        print(f"READY: {Status.READY.value}")
        print(f"RUNNING: {Status.RUNNING.value}")
        print(f"FAILED: {Status.FAILED.value}")
        
        # Test enum values
        assert Status.READY.value == "ready"
        assert Status.RUNNING.value == "running"
        assert Status.FAILED.value == "failed"
        
        print("OK - Status enum works correctly")
        return True
    except Exception as e:
        print(f"ERROR - Status enum test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing ScraperInterface (Basic Functionality)")
    print("=" * 50)
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    print()
    
    # Test initialization
    if not test_initialization():
        success = False
    print()
    
    # Test datetime conversion
    if not test_datetime_conversion():
        success = False
    print()
    
    # Test snapshot model
    if not test_snapshot_creation():
        success = False
    print()
    
    # Test status enum
    if not test_status_enum():
        success = False
    print()
    
    if success:
        print("SUCCESS - All basic tests passed!")
        print("The ScraperInterface is working correctly.")
        print("Note: API calls will fail without valid credentials, but the structure is correct.")
    else:
        print("ERROR - Some basic tests failed.")
