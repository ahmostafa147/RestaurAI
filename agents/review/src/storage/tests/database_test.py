import sys
import os
import tempfile
import json
from datetime import datetime

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database_handler import DatabaseHandler
from models.review import Review

def test_database_handler():
    """Test DatabaseHandler functionality"""
    
    # Create a temporary CSV file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Initialize DatabaseHandler
        db_handler = DatabaseHandler(temp_path)
        
        # Create sample reviews
        review1 = Review(
            source="google",
            review_id="g_001",
            author_name="John Doe",
            rating=4.5,
            review_text="Great food and service! The pasta was amazing.",
            review_date="2024-01-15T10:30:00Z",
            helpful_votes=3,
            verified_purchase=True,
            language="en"
        )
        
        review2 = Review(
            source="yelp",
            review_id="y_001", 
            author_name="Jane Smith",
            rating=5.0,
            review_text="Excellent restaurant with friendly staff. Highly recommend!",
            review_date="2024-01-20T14:45:00Z",
            helpful_votes=7,
            response_from_owner="Thank you for your kind words!",
            verified_purchase=False,
            language="en"
        )
        
        # Test saving reviews (overwrite mode)
        print("Testing save_reviews (overwrite mode)...")
        db_handler.save_reviews([review1, review2], overwrite=True)
        
        # Test getting all reviews
        print("Testing get_all_reviews...")
        all_reviews = db_handler.get_all_reviews()
        print(f"Retrieved {len(all_reviews)} reviews")
        
        # Verify review data
        assert len(all_reviews) == 2
        assert all_reviews[0].review_id == "g_001"
        assert all_reviews[1].review_id == "y_001"
        print("OK - All reviews retrieved correctly")
        
        # Test getting specific review
        print("Testing get_reviews...")
        specific_review = db_handler.get_reviews(0)
        assert specific_review.review_id == "g_001"
        assert specific_review.author_name == "John Doe"
        print("OK - Specific review retrieved correctly")
        
        # Test appending reviews
        print("Testing save_reviews (append mode)...")
        review3 = Review(
            source="google",
            review_id="g_002",
            author_name="Mike Johnson",
            rating=3.0,
            review_text="Food was okay, but service was slow.",
            review_date="2024-01-25T19:20:00Z",
            language="en"
        )
        
        db_handler.save_reviews([review3], overwrite=False)
        all_reviews_after_append = db_handler.get_all_reviews()
        assert len(all_reviews_after_append) == 3
        print("OK - Review appended successfully")
        
        # Test deleting review
        print("Testing delete_review...")
        db_handler.delete_review("g_001")
        remaining_reviews = db_handler.get_all_reviews()
        assert len(remaining_reviews) == 2
        assert remaining_reviews[0].review_id == "y_001"  # First review should be deleted
        print("OK - Review deleted successfully")
        
        # Test Review model methods
        print("Testing Review model methods...")
        test_review = remaining_reviews[0]
        
        # Test is_recent method
        is_recent = test_review.is_recent(days=30)
        print(f"Review is recent (within 30 days): {is_recent}")
        
        # Test has_owner_response method
        has_response = test_review.has_owner_response()
        print(f"Review has owner response: {has_response}")
        
        # Test get_word_count method
        word_count = test_review.get_word_count()
        print(f"Review word count: {word_count}")
        
        # Test is_helpful method
        is_helpful = test_review.is_helpful(threshold=5)
        print(f"Review is helpful (>=5 votes): {is_helpful}")
        
        # Test normalize_rating method
        normalized_rating = test_review.normalize_rating()
        print(f"Normalized rating: {normalized_rating}")
        
        print("\nSUCCESS - All DatabaseHandler tests passed!")
        
    except Exception as e:
        print(f"ERROR - Test failed with error: {e}")
        raise
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)
            print("OK - Temporary file cleaned up")

def test_review_model_edge_cases():
    """Test Review model with edge cases"""
    
    print("\nTesting Review model edge cases...")
    
    # Test with minimal data
    minimal_review = Review(
        source="google",
        review_id="min_001",
        author_name="Anonymous",
        rating=2.5,
        review_text="",
        review_date="2024-01-01T00:00:00Z"
    )
    
    # Test methods with minimal data
    assert minimal_review.get_word_count() == 0
    assert not minimal_review.has_owner_response()
    assert minimal_review.normalize_rating() == 2.5
    
    # Test with invalid date
    invalid_date_review = Review(
        source="yelp",
        review_id="inv_001",
        author_name="Test User",
        rating=4.0,
        review_text="Test review",
        review_date="invalid-date"
    )
    
    # Should handle invalid dates gracefully
    assert not invalid_date_review.is_recent()
    
    print("OK - Edge case tests passed!")

if __name__ == "__main__":
    print("Starting DatabaseHandler tests...\n")
    test_database_handler()
    test_review_model_edge_cases()
    print("\nSUCCESS - All tests completed successfully!")
