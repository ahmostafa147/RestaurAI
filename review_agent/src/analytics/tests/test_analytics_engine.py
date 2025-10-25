"""
Tests for analytics engine
"""
import pytest
import json
import tempfile
import os
from datetime import datetime

# Handle imports with proper path resolution
try:
    from ..analytics_engine import AnalyticsEngine
    from ...models.review import Review
    from ...storage.database_handler import DatabaseHandler
except ImportError:
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    grandparent_dir = os.path.dirname(parent_dir)
    sys.path.append(grandparent_dir)
    from analytics.analytics_engine import AnalyticsEngine
    from models.review import Review
    from storage.database_handler import DatabaseHandler

class TestAnalyticsEngine:
    """Test cases for AnalyticsEngine"""
    
    def setup_method(self):
        """Set up test data"""
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()
        
        # Initialize database with test data
        test_data = {
            "reviews": [
                {
                    "source": "google",
                    "review_id": "test1",
                    "author_name": "Test User 1",
                    "rating": 5.0,
                    "review_text": "Great food and service!",
                    "review_date": "2025-01-01T00:00:00.000Z",
                    "helpful_votes": 0,
                    "response_from_owner": None,
                    "verified_purchase": True,
                    "profile_photo_url": None,
                    "language": "en",
                    "fetched_timestamp": "2025-01-01T00:00:00.000Z",
                    "sentiment_score": None,
                    "photos_attached": 0,
                    "owner_response_date": None,
                    "llm_processed": True,
                    "llm_processed_date": "2025-01-01T00:00:00.000Z",
                    "overall_sentiment": "positive",
                    "rating_food": 5,
                    "rating_service": 5,
                    "rating_ambiance": 4,
                    "rating_value": 5,
                    "mentioned_items": '[{"name": "pizza", "sentiment": "positive", "aspects": ["taste", "presentation"]}]',
                    "staff_mentions": '[{"role": "server", "name": "John", "sentiment": "positive", "specific_feedback": "excellent service"}]',
                    "operational_insights": '{"wait_time": "short", "cleanliness": "positive", "noise_level": "moderate"}',
                    "visit_context": '{"party_type": "couple", "occasion": "date", "time_of_visit": "dinner", "first_visit": true, "would_return": true, "would_recommend": true}',
                    "key_phrases": '{"positive_highlights": ["great food", "excellent service"], "negative_issues": [], "suggestions": []}',
                    "anomaly_flags": '{"potential_fake": false, "health_safety_concern": false, "extreme_emotion": false, "competitor_mention": false}'
                },
                {
                    "source": "yelp",
                    "review_id": "test2",
                    "author_name": "Test User 2",
                    "rating": 2.0,
                    "review_text": "Poor service and cold food",
                    "review_date": "2025-01-02T00:00:00.000Z",
                    "helpful_votes": 1,
                    "response_from_owner": "We apologize for the poor experience",
                    "verified_purchase": False,
                    "profile_photo_url": None,
                    "language": "en",
                    "fetched_timestamp": "2025-01-02T00:00:00.000Z",
                    "sentiment_score": None,
                    "photos_attached": 0,
                    "owner_response_date": "2025-01-03T00:00:00.000Z",
                    "llm_processed": True,
                    "llm_processed_date": "2025-01-02T00:00:00.000Z",
                    "overall_sentiment": "negative",
                    "rating_food": 1,
                    "rating_service": 2,
                    "rating_ambiance": 3,
                    "rating_value": 2,
                    "mentioned_items": '[{"name": "burger", "sentiment": "negative", "aspects": ["temperature", "taste"]}]',
                    "staff_mentions": '[{"role": "server", "name": "Jane", "sentiment": "negative", "specific_feedback": "slow service"}]',
                    "operational_insights": '{"wait_time": "long", "cleanliness": "negative", "noise_level": "loud"}',
                    "visit_context": '{"party_type": "family", "occasion": "regular", "time_of_visit": "lunch", "first_visit": false, "would_return": false, "would_recommend": false}',
                    "key_phrases": '{"positive_highlights": [], "negative_issues": ["poor service", "cold food"], "suggestions": ["improve service speed"]}',
                    "anomaly_flags": '{"potential_fake": false, "health_safety_concern": true, "extreme_emotion": false, "competitor_mention": false}'
                }
            ],
            "snapshots": []
        }
        
        with open(self.temp_db_path, 'w') as f:
            json.dump(test_data, f)
        
        # Initialize database handler and analytics engine
        self.db_handler = DatabaseHandler(self.temp_db_path)
        self.analytics_engine = AnalyticsEngine(self.db_handler)
    
    def teardown_method(self):
        """Clean up test data"""
        if os.path.exists(self.temp_db_path):
            os.unlink(self.temp_db_path)
    
    def test_generate_full_report(self):
        """Test full report generation"""
        report = self.analytics_engine.generate_full_report()
        
        # Check metadata
        assert 'metadata' in report
        metadata = report['metadata']
        assert metadata['total_reviews'] == 2
        assert metadata['processed_reviews'] == 2
        assert metadata['processing_coverage'] == 100.0
        
        # Check all sections are present
        assert 'basic_metrics' in report
        assert 'menu_analytics' in report
        assert 'staff_analytics' in report
        assert 'temporal_analysis' in report
        assert 'operational_metrics' in report
        assert 'customer_insights' in report
        assert 'reputation_insights' in report
    
    def test_basic_metrics(self):
        """Test basic metrics calculation"""
        report = self.analytics_engine.generate_full_report()
        basic_metrics = report['basic_metrics']
        
        # Check overall performance
        overall_perf = basic_metrics['overall_performance']
        assert overall_perf['total_reviews'] == 2
        assert overall_perf['processed_reviews'] == 2
        assert overall_perf['average_rating'] == 3.5  # (5.0 + 2.0) / 2
        
        # Check platform comparison
        platform_comp = basic_metrics['platform_comparison']
        assert 'platforms' in platform_comp
        assert 'google' in platform_comp['platforms']
        assert 'yelp' in platform_comp['platforms']
    
    def test_menu_analytics(self):
        """Test menu analytics calculation"""
        report = self.analytics_engine.generate_full_report()
        menu_analytics = report['menu_analytics']
        
        # Check items
        items = menu_analytics['items']
        assert len(items) == 2  # pizza and burger
        
        # Find pizza item
        pizza_item = next((item for item in items if item['name'].lower() == 'pizza'), None)
        assert pizza_item is not None
        assert pizza_item['mention_count'] == 1
        assert pizza_item['positive_count'] == 1
        assert pizza_item['sentiment_score'] == 1.0  # positive sentiment
    
    def test_staff_analytics(self):
        """Test staff analytics calculation"""
        report = self.analytics_engine.generate_full_report()
        staff_analytics = report['staff_analytics']
        
        # Check by person
        by_person = staff_analytics['by_person']
        assert len(by_person) == 2  # John and Jane
        
        # Find John
        john = next((staff for staff in by_person if staff['name'] == 'John'), None)
        assert john is not None
        assert john['mention_count'] == 1
        assert john['positive_count'] == 1
        assert john['average_sentiment'] == 1.0  # positive sentiment
    
    def test_operational_metrics(self):
        """Test operational metrics calculation"""
        report = self.analytics_engine.generate_full_report()
        operational_metrics = report['operational_metrics']
        
        # Check ambiance ratings
        ambiance = operational_metrics['ambiance_ratings']
        assert ambiance['average_rating'] == 3.5  # (4 + 3) / 2
        assert ambiance['total_ratings'] == 2
        
        # Check wait time patterns
        wait_times = operational_metrics['wait_time_patterns']
        assert wait_times['total_mentions'] == 2
        assert 'short' in wait_times['distribution']
        assert 'long' in wait_times['distribution']
    
    def test_customer_insights(self):
        """Test customer insights calculation"""
        report = self.analytics_engine.generate_full_report()
        customer_insights = report['customer_insights']
        
        # Check segmentation
        segmentation = customer_insights['segmentation']
        segments = segmentation['segments']
        assert 'couple' in segments
        assert 'family' in segments
        
        # Check loyalty metrics
        loyalty = customer_insights['loyalty_metrics']
        assert 'loyalty_data' in loyalty
        assert 'loyalty_percentages' in loyalty
    
    def test_export_report(self):
        """Test report export functionality"""
        output_path = tempfile.mktemp(suffix='.json')
        
        try:
            self.analytics_engine.export_report(output_path)
            
            # Check file was created and contains valid JSON
            assert os.path.exists(output_path)
            with open(output_path, 'r') as f:
                exported_data = json.load(f)
            
            assert 'metadata' in exported_data
            assert exported_data['metadata']['total_reviews'] == 2
            
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_get_summary(self):
        """Test summary generation"""
        summary = self.analytics_engine.get_summary()
        
        assert 'total_reviews' in summary
        assert 'processed_reviews' in summary
        assert 'average_rating' in summary
        assert 'menu_items_mentioned' in summary
        assert 'staff_members_mentioned' in summary
        assert 'processing_coverage' in summary
        
        assert summary['total_reviews'] == 2
        assert summary['processed_reviews'] == 2
        assert summary['average_rating'] == 3.5
