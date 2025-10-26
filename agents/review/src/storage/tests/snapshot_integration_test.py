import sys
import os
import tempfile
import json
from datetime import datetime

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database_handler import DatabaseHandler
from models.snapshot_metadata import SnapshotMetadata

def test_yelp_scraped_data_integration():
    """Test SnapshotMetadata with actual Yelp scraped data"""
    
    # Sample Yelp scraped data (from user's example)
    yelp_scraped_data = [
        {
            "business_id": "causwells-san-francisco-5",
            "Review_auther": {
                "Username": "Charlie H.",
                "URL": "https://www.yelp.com/user_details?userid=4ugITYUTaoA0XYhGiBvP2g",
                "Location": "San Francisco, CA",
                "Friends": 0,
                "Reviews_made": 3,
                "Photos": 0
            },
            "Rating": 1,
            "Date": "29/03/2025",
            "Content": "They have a phone number but no one answers the phone for questions about food. It makes it seems like they don't care about customer service. Food was mediocre at best. I ordered the layered potatoes it came with a pesto mayo which I don't think is the best pairing because it's an oil based condiment for a fried dish. It didn't add any depth of flavor hence the grease bomb. The potatoes were brown on the inside like they had been cut, prepped, and left out too long and oxidized before assembling.",
            "review_order": 3.0,
            "url": "https://www.yelp.com/biz/causwells-san-francisco-5?sort_by=date_desc",
            "recommended_review": False,
            "profile_pic_url": None,
            "review_id": "5PoNLIdwFFyDshO0V6u1Nw",
            "date_iso_format": "2025-03-29T00:00:00.000Z",
            "timestamp": "2025-10-25T03:33:10.861Z",
            "input": {
                "url": "https://www.yelp.com/biz/causwells-san-francisco-5",
                "unrecommended_reviews": True,
                "start_date": "2025-03-02T00:00:00.000Z",
                "end_date": "2025-06-01T00:00:00.000Z",
                "sort_by": "DATE_DESC"
            }
        }
    ]
    
    # Create a temporary database file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Initialize DatabaseHandler
        db_handler = DatabaseHandler(temp_path)
        
        # Test creating SnapshotMetadata from Yelp scraped data
        print("Testing Yelp scraped data integration...")
        
        snapshot_metadata = SnapshotMetadata.from_scraped_data(
            yelp_scraped_data, 
            snapshot_id="yelp_test_001",
            source="yelp",
            status="ready"
        )
        
        # Verify extracted metadata
        assert snapshot_metadata.snapshot_id == "yelp_test_001"
        assert snapshot_metadata.source == "yelp"
        assert snapshot_metadata.business_id == "causwells-san-francisco-5"
        assert snapshot_metadata.records_count == 1
        assert snapshot_metadata.total_reviews_collected == 1
        assert snapshot_metadata.input_params is not None
        assert snapshot_metadata.input_params['url'] == "https://www.yelp.com/biz/causwells-san-francisco-5"
        print("OK - Yelp metadata extracted correctly")
        
        # Test saving to database
        db_handler.save_snapshot_metadata(snapshot_metadata)
        
        # Verify retrieval
        retrieved_snapshot = db_handler.get_snapshot_metadata("yelp_test_001")
        assert retrieved_snapshot is not None
        assert retrieved_snapshot.business_id == "causwells-san-francisco-5"
        print("OK - Yelp snapshot saved and retrieved")
        
        print("SUCCESS - Yelp integration test passed!")
        
    except Exception as e:
        print(f"ERROR - Yelp test failed: {e}")
        raise
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
            print("OK - Yelp test file cleaned up")

def test_google_scraped_data_integration():
    """Test SnapshotMetadata with actual Google scraped data"""
    
    # Sample Google scraped data (from user's example)
    google_scraped_data = [
        {
            "url": "https://www.google.com/maps/place/Causwells/@37.8012624,-122.4428722,17z/data=!4m6!3m5!1s0x808580d439f7c8ef:0x4535d182f05476fe!8m2!3d37.8003429!4d-122.4420181!16s%2Fg%2F1q66z5g1s?entry=ttu",
            "place_id": "ChIJ78j3OdSAhYAR_nZU8ILRNUU",
            "place_name": "Causwells",
            "country": "US",
            "address": "2346 Chestnut St, San Francisco, CA 94123",
            "review_id": "Ci9DQUlRQUNvZENodHljRjlvT21ORGRVVXhXSE5MVkdWUVdEZHJhVlJLUlZvNGVuYxAB",
            "reviewer_name": "Marsha Bien-Aime",
            "reviews_by_reviewer": 3,
            "photos_by_reviewer": None,
            "reviewer_url": "https://www.google.com/maps/contrib/108182113952284568845/reviews?hl=en",
            "local_guide": False,
            "review_rating": 5,
            "review": "Byron made the best espresso martini I've ever tasted in my life! 🍸 Causwells is officially #1 on my list.",
            "review_date": "2025-10-17T01:18:09.697Z",
            "number_of_likes": 0,
            "response_of_owner": None,
            "response_date": None,
            "photos": None,
            "review_details": [
                {"title": "Food", "value": "5"},
                {"title": "Service", "value": "5"},
                {"title": "Atmosphere", "value": "5"}
            ],
            "profile_pic_url": "https://lh3.googleusercontent.com/a/ACg8ocKO8Wp1wjHGpQk9tXaPrwfTMnJsb5mWPXxlKUiJuFdHT8lkbw=s120-c-rp-mo-br100",
            "place_general_rating": 4.3,
            "overall_place_riviews": 911,
            "questions_answers": [
                {
                    "question": "How is the parking around Causwells?",
                    "answers": ["You'll be able to find a spot on a weekday or weeknight. For weekends there are two nearby garages"]
                }
            ],
            "fid_location": "0x808580d439f7c8ef:0x4535d182f05476fe",
            "category": "American restaurant",
            "timestamp": "2025-10-25T03:27:43.907Z",
            "input": {
                "url": "https://www.google.com/maps/place/Causwells/@37.8012624,-122.4428722,17z/data=!4m6!3m5!1s0x808580d439f7c8ef:0x4535d182f05476fe!8m2!3d37.8003429!4d-122.4420181!16s%2Fg%2F1q66z5g1s?entry=ttu",
                "days_limit": 18
            }
        }
    ]
    
    # Create a temporary database file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Initialize DatabaseHandler
        db_handler = DatabaseHandler(temp_path)
        
        # Test creating SnapshotMetadata from Google scraped data
        print("Testing Google scraped data integration...")
        
        snapshot_metadata = SnapshotMetadata.from_scraped_data(
            google_scraped_data,
            snapshot_id="google_test_001", 
            source="google",
            status="ready"
        )
        
        # Verify extracted metadata
        assert snapshot_metadata.snapshot_id == "google_test_001"
        assert snapshot_metadata.source == "google"
        assert snapshot_metadata.place_id == "ChIJ78j3OdSAhYAR_nZU8ILRNUU"
        assert snapshot_metadata.place_name == "Causwells"
        assert snapshot_metadata.address == "2346 Chestnut St, San Francisco, CA 94123"
        assert snapshot_metadata.category == "American restaurant"
        assert snapshot_metadata.records_count == 1
        assert snapshot_metadata.input_params is not None
        assert snapshot_metadata.input_params['days_limit'] == 18
        print("OK - Google metadata extracted correctly")
        
        # Test saving to database
        db_handler.save_snapshot_metadata(snapshot_metadata)
        
        # Verify retrieval
        retrieved_snapshot = db_handler.get_snapshot_metadata("google_test_001")
        assert retrieved_snapshot is not None
        assert retrieved_snapshot.place_name == "Causwells"
        assert retrieved_snapshot.category == "American restaurant"
        print("OK - Google snapshot saved and retrieved")
        
        print("SUCCESS - Google integration test passed!")
        
    except Exception as e:
        print(f"ERROR - Google test failed: {e}")
        raise
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
            print("OK - Google test file cleaned up")

def test_snapshot_metadata_methods():
    """Test SnapshotMetadata utility methods"""
    
    print("Testing SnapshotMetadata utility methods...")
    
    # Create a snapshot with test data
    snapshot = SnapshotMetadata(
        snapshot_id="test_001",
        source="google",
        status="ready",
        records_count=10,
        errors_count=2,
        collection_duration=300  # 5 minutes
    )
    
    # Update the collection results to set the proper fields
    snapshot.update_collection_results(10, 2, 300)
    
    # Test success rate calculation
    success_rate = snapshot.get_success_rate()
    expected_rate = 8 / 10  # 8 successful out of 10 total
    assert abs(success_rate - expected_rate) < 0.001
    print("OK - Success rate calculation works")
    
    # Test collection efficiency
    efficiency = snapshot.get_collection_efficiency()
    expected_efficiency = (10 * 60) / 300  # 10 reviews * 60 seconds / 300 seconds = 2 reviews/minute
    assert abs(efficiency - expected_efficiency) < 0.001
    print("OK - Collection efficiency calculation works")
    
    # Test is_recent method
    is_recent = snapshot.is_recent(days=7)
    assert is_recent == True  # Just created, should be recent
    print("OK - Recent check works")
    
    # Test update_collection_results
    snapshot.update_collection_results(15, 1, 600)
    assert snapshot.records_count == 15
    assert snapshot.errors_count == 1
    assert snapshot.collection_duration == 600
    assert snapshot.total_reviews_collected == 15
    assert snapshot.successful_reviews == 14
    assert snapshot.failed_reviews == 1
    print("OK - Collection results update works")
    
    print("SUCCESS - SnapshotMetadata methods test passed!")

def test_database_handler_new_method():
    """Test the new save_snapshot_from_scraped_data method"""
    
    # Create a temporary database file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Initialize DatabaseHandler
        db_handler = DatabaseHandler(temp_path)
        
        # Test data
        test_scraped_data = [
            {
                "business_id": "test-business",
                "review_id": "test-review-1",
                "Rating": 5,
                "Content": "Great food!",
                "input": {"url": "https://test.com", "days_limit": 7}
            }
        ]
        
        # Test the new method
        print("Testing save_snapshot_from_scraped_data method...")
        db_handler.save_snapshot_from_scraped_data(
            test_scraped_data,
            snapshot_id="test_001",
            source="yelp",
            status="ready"
        )
        
        # Verify the snapshot was saved
        retrieved_snapshot = db_handler.get_snapshot_metadata("test_001")
        assert retrieved_snapshot is not None
        assert retrieved_snapshot.source == "yelp"
        assert retrieved_snapshot.business_id == "test-business"
        assert retrieved_snapshot.records_count == 1
        print("OK - save_snapshot_from_scraped_data works")
        
        print("SUCCESS - DatabaseHandler new method test passed!")
        
    except Exception as e:
        print(f"ERROR - DatabaseHandler test failed: {e}")
        raise
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
            print("OK - DatabaseHandler test file cleaned up")

if __name__ == "__main__":
    print("Starting SnapshotMetadata integration tests...\n")
    test_yelp_scraped_data_integration()
    test_google_scraped_data_integration()
    test_snapshot_metadata_methods()
    test_database_handler_new_method()
    print("\nSUCCESS - All integration tests completed successfully!")
