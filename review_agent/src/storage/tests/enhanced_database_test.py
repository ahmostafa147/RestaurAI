import sys
import os
import tempfile
import json
from datetime import datetime, timedelta

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database_handler import DatabaseHandler, SnapshotMetadata
from models.review import Review

def test_enhanced_database_handler():
    """Test enhanced DatabaseHandler with snapshot metadata functionality"""
    
    # Create a temporary JSON file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Initialize DatabaseHandler
        db_handler = DatabaseHandler(temp_path)
        
        # Test 1: Snapshot metadata operations
        print("Testing snapshot metadata operations...")
        
        # Create sample snapshot metadata
        snapshot1 = SnapshotMetadata(
            snapshot_id="sd_test001",
            source="google",
            status="ready",
            records_count=15,
            errors_count=0,
            collection_duration=120
        )
        
        snapshot2 = SnapshotMetadata(
            snapshot_id="sd_test002", 
            source="yelp",
            status="running",
            records_count=0,
            errors_count=0,
            collection_duration=0
        )
        
        # Save snapshot metadata
        db_handler.save_snapshot_metadata(snapshot1)
        db_handler.save_snapshot_metadata(snapshot2)
        print("OK - Snapshot metadata saved")
        
        # Test getting all snapshots
        all_snapshots = db_handler.get_all_snapshots()
        assert len(all_snapshots) == 2
        print("OK - All snapshots retrieved")
        
        # Test getting specific snapshot
        retrieved_snapshot = db_handler.get_snapshot_metadata("sd_test001")
        assert retrieved_snapshot is not None
        assert retrieved_snapshot.source == "google"
        assert retrieved_snapshot.status == "ready"
        print("OK - Specific snapshot retrieved")
        
        # Test filtering by source
        google_snapshots = db_handler.get_snapshots_by_source("google")
        assert len(google_snapshots) == 1
        assert google_snapshots[0].snapshot_id == "sd_test001"
        print("OK - Snapshots filtered by source")
        
        # Test filtering by status
        running_snapshots = db_handler.get_snapshots_by_status("running")
        assert len(running_snapshots) == 1
        assert running_snapshots[0].snapshot_id == "sd_test002"
        print("OK - Snapshots filtered by status")
        
        # Test updating snapshot status
        db_handler.update_snapshot_status("sd_test002", "ready", records_count=25, collection_duration=180)
        updated_snapshot = db_handler.get_snapshot_metadata("sd_test002")
        assert updated_snapshot.status == "ready"
        assert updated_snapshot.records_count == 25
        assert updated_snapshot.collection_duration == 180
        print("OK - Snapshot status updated")
        
        # Test 2: Review operations (existing functionality)
        print("\nTesting review operations...")
        
        # Create sample reviews
        review1 = Review(
            source="google",
            review_id="g_001",
            author_name="John Doe",
            rating=4.5,
            review_text="Great food and service!",
            review_date="2024-01-15T10:30:00Z"
        )
        
        review2 = Review(
            source="yelp",
            review_id="y_001",
            author_name="Jane Smith", 
            rating=5.0,
            review_text="Excellent restaurant!",
            review_date="2024-01-20T14:45:00Z"
        )
        
        # Save reviews
        db_handler.save_reviews([review1, review2], overwrite=True)
        all_reviews = db_handler.get_all_reviews()
        assert len(all_reviews) == 2
        print("OK - Reviews saved and retrieved")
        
        # Test 3: Database statistics
        print("\nTesting database statistics...")
        stats = db_handler.get_database_stats()
        assert stats['total_reviews'] == 2
        assert stats['total_snapshots'] == 2
        assert stats['google_snapshots'] == 1
        assert stats['yelp_snapshots'] == 1
        assert stats['ready_snapshots'] == 2  # Both are now ready
        assert stats['running_snapshots'] == 0
        assert stats['failed_snapshots'] == 0
        print("OK - Database statistics calculated correctly")
        
        # Test 4: Recent snapshots
        print("\nTesting recent snapshots...")
        recent_snapshots = db_handler.get_recent_snapshots(days=7)
        assert len(recent_snapshots) == 2  # Both snapshots are recent
        print("OK - Recent snapshots retrieved")
        
        # Test 5: Delete operations
        print("\nTesting delete operations...")
        db_handler.delete_snapshot_metadata("sd_test001")
        remaining_snapshots = db_handler.get_all_snapshots()
        assert len(remaining_snapshots) == 1
        assert remaining_snapshots[0].snapshot_id == "sd_test002"
        print("OK - Snapshot metadata deleted")
        
        db_handler.delete_review("g_001")
        remaining_reviews = db_handler.get_all_reviews()
        assert len(remaining_reviews) == 1
        assert remaining_reviews[0].review_id == "y_001"
        print("OK - Review deleted")
        
        print("\nSUCCESS - All enhanced DatabaseHandler tests passed!")
        
    except Exception as e:
        print(f"ERROR - Test failed with error: {e}")
        raise
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)
            print("OK - Temporary file cleaned up")

def test_snapshot_metadata_model():
    """Test SnapshotMetadata model functionality"""
    
    print("\nTesting SnapshotMetadata model...")
    
    # Test creation with all parameters
    snapshot = SnapshotMetadata(
        snapshot_id="test_001",
        source="google",
        status="ready",
        records_count=10,
        errors_count=1,
        collection_duration=300
    )
    
    # Test to_dict conversion
    snapshot_dict = snapshot.to_dict()
    assert snapshot_dict['snapshot_id'] == "test_001"
    assert snapshot_dict['source'] == "google"
    assert snapshot_dict['status'] == "ready"
    assert snapshot_dict['records_count'] == 10
    print("OK - SnapshotMetadata to_dict works")
    
    # Test from_dict conversion
    recreated_snapshot = SnapshotMetadata.from_dict(snapshot_dict)
    assert recreated_snapshot.snapshot_id == "test_001"
    assert recreated_snapshot.source == "google"
    assert recreated_snapshot.status == "ready"
    assert recreated_snapshot.records_count == 10
    print("OK - SnapshotMetadata from_dict works")
    
    # Test with minimal data
    minimal_snapshot = SnapshotMetadata(
        snapshot_id="min_001",
        source="yelp", 
        status="running"
    )
    minimal_dict = minimal_snapshot.to_dict()
    assert minimal_dict['records_count'] == 0
    assert minimal_dict['errors_count'] == 0
    assert minimal_dict['collection_duration'] == 0
    print("OK - Minimal SnapshotMetadata works")
    
    print("OK - SnapshotMetadata model tests passed!")

def test_database_migration():
    """Test database structure migration from old format"""
    
    print("\nTesting database migration...")
    
    # Create a temporary file with old format (list of reviews)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Write old format data
        old_data = [
            {
                'source': 'google',
                'review_id': 'g_migration',
                'author_name': 'Migration Test',
                'rating': 4.0,
                'review_text': 'Test review for migration',
                'review_date': '2024-01-01T00:00:00Z'
            }
        ]
        
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(old_data, f, indent=2)
        
        # Initialize DatabaseHandler (should trigger migration)
        db_handler = DatabaseHandler(temp_path)
        
        # Verify migration worked
        all_reviews = db_handler.get_all_reviews()
        assert len(all_reviews) == 1
        assert all_reviews[0].review_id == "g_migration"
        
        # Verify new structure has snapshots array
        data = db_handler._get_database_data()
        assert 'reviews' in data
        assert 'snapshots' in data
        assert isinstance(data['reviews'], list)
        assert isinstance(data['snapshots'], list)
        
        print("OK - Database migration successful")
        
    except Exception as e:
        print(f"ERROR - Migration test failed: {e}")
        raise
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
            print("OK - Migration test file cleaned up")

if __name__ == "__main__":
    print("Starting Enhanced DatabaseHandler tests...\n")
    test_enhanced_database_handler()
    test_snapshot_metadata_model()
    test_database_migration()
    print("\nSUCCESS - All enhanced tests completed successfully!")
