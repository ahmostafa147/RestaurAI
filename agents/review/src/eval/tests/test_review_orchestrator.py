"""
Comprehensive tests for review orchestrator functionality
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import List, Dict, Any

from ..review_orchestrator import ReviewOrchestrator, EnrichedReview
from ..llm_wrapper import LLMResponse
from ..models.extended_review import ReviewExtraction, RatingBreakdown, MentionedItem
from ...models.review import Review


class TestReviewOrchestrator:
    """Test cases for ReviewOrchestrator class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.sample_reviews = self._create_sample_reviews()
        # self.mock_api_key = "test-api-key"
        self.mock_api_key = os.getenv('ANTHROPIC_API_KEY')
    
    def _create_sample_reviews(self) -> List[Review]:
        """Create sample Review objects for testing"""
        reviews = []
        
        # Review 1
        review1 = Review(
            source='google',
            review_id='google_001',
            author_name='John Smith',
            rating=4.5,
            review_text='Great food and excellent service! The pasta was amazing.',
            review_date='2024-01-15T10:30:00Z',
            helpful_votes=3,
            verified_purchase=True,
            photos_attached=2,
            fetched_timestamp=datetime.now()
        )
        reviews.append(review1)
        
        # Review 2
        review2 = Review(
            source='yelp',
            review_id='yelp_001',
            author_name='Jane Doe',
            rating=3.0,
            review_text='Food was okay but service was slow.',
            review_date='2024-01-20T19:45:00Z',
            helpful_votes=1,
            verified_purchase=False,
            photos_attached=0,
            fetched_timestamp=datetime.now()
        )
        reviews.append(review2)
        
        return reviews
    
    @patch('fetch_ai_restaurant_agent.src.eval.review_orchestrator.ClaudeWrapper')
    def test_init_with_api_key(self, mock_wrapper_class):
        """Test initialization with provided API key"""
        mock_wrapper = Mock()
        mock_wrapper_class.return_value = mock_wrapper
        
        orchestrator = ReviewOrchestrator(claude_api_key=self.mock_api_key)
        
        mock_wrapper_class.assert_called_once_with(self.mock_api_key)
        assert orchestrator.llm_wrapper == mock_wrapper
    
    @patch('fetch_ai_restaurant_agent.src.eval.review_orchestrator.ClaudeWrapper')
    def test_init_without_api_key(self, mock_wrapper_class):
        """Test initialization without API key (uses environment)"""
        mock_wrapper = Mock()
        mock_wrapper_class.return_value = mock_wrapper
        
        orchestrator = ReviewOrchestrator()
        
        mock_wrapper_class.assert_called_once_with(None)
        assert orchestrator.llm_wrapper == mock_wrapper
    
    @patch('fetch_ai_restaurant_agent.src.eval.review_orchestrator.ClaudeWrapper')
    def test_process_reviews_success(self, mock_wrapper_class):
        """Test successful review processing"""
        # Mock the LLM wrapper
        mock_wrapper = Mock()
        mock_wrapper_class.return_value = mock_wrapper
        
        # Mock LLM responses
        mock_responses = [
            LLMResponse(
                content=json.dumps({
                    "overall_sentiment": "positive",
                    "rating_breakdown": {"food": 5, "service": 4},
                    "mentioned_items": [{"name": "pasta", "sentiment": "positive", "aspects": ["taste"]}],
                    "staff_mentions": [],
                    "operational_insights": None,
                    "visit_context": None,
                    "key_phrases": None,
                    "anomaly_flags": None
                }),
                usage={"input_tokens": 100, "output_tokens": 50},
                model="claude-sonnet-4-5-20250929",
                success=True
            ),
            LLMResponse(
                content=json.dumps({
                    "overall_sentiment": "negative",
                    "rating_breakdown": {"food": 3, "service": 2},
                    "mentioned_items": [],
                    "staff_mentions": [],
                    "operational_insights": None,
                    "visit_context": None,
                    "key_phrases": None,
                    "anomaly_flags": None
                }),
                usage={"input_tokens": 120, "output_tokens": 60},
                model="claude-sonnet-4-5-20250929",
                success=True
            )
        ]
        
        mock_wrapper.batch_extract_reviews.return_value = mock_responses
        
        orchestrator = ReviewOrchestrator(claude_api_key=self.mock_api_key)
        enriched_reviews = orchestrator.process_reviews(self.sample_reviews, batch_size=2)
        
        # Verify results
        assert len(enriched_reviews) == 2
        assert all(isinstance(review, EnrichedReview) for review in enriched_reviews)
        
        # Check first review
        first_review = enriched_reviews[0]
        assert first_review.review_id == 'google_001'
        assert first_review.overall_sentiment == 'positive'
        assert first_review.extraction_success is True
        assert first_review.temporal_metadata is not None
        assert first_review.reviewer_metadata is not None
        assert first_review.platform_metadata is not None
        
        # Check second review
        second_review = enriched_reviews[1]
        assert second_review.review_id == 'yelp_001'
        assert second_review.overall_sentiment == 'negative'
        assert second_review.extraction_success is True
    
    @patch('fetch_ai_restaurant_agent.src.eval.review_orchestrator.ClaudeWrapper')
    def test_process_reviews_with_failures(self, mock_wrapper_class):
        """Test review processing with some failures"""
        mock_wrapper = Mock()
        mock_wrapper_class.return_value = mock_wrapper
        
        # Mock mixed success/failure responses
        mock_responses = [
            LLMResponse(
                content=json.dumps({
                    "overall_sentiment": "positive",
                    "rating_breakdown": None,
                    "mentioned_items": [],
                    "staff_mentions": [],
                    "operational_insights": None,
                    "visit_context": None,
                    "key_phrases": None,
                    "anomaly_flags": None
                }),
                usage={"input_tokens": 100, "output_tokens": 50},
                model="claude-sonnet-4-5-20250929",
                success=True
            ),
            LLMResponse(
                content="",
                usage={"input_tokens": 0, "output_tokens": 0},
                model="claude-sonnet-4-5-20250929",
                success=False,
                error="API Error"
            )
        ]
        
        mock_wrapper.batch_extract_reviews.return_value = mock_responses
        
        orchestrator = ReviewOrchestrator(claude_api_key=self.mock_api_key)
        enriched_reviews = orchestrator.process_reviews(self.sample_reviews, batch_size=2)
        
        # Verify results
        assert len(enriched_reviews) == 2
        
        # First review should be successful
        assert enriched_reviews[0].extraction_success is True
        assert enriched_reviews[0].overall_sentiment == 'positive'
        
        # Second review should have failed extraction
        assert enriched_reviews[1].extraction_success is False
        assert enriched_reviews[1].overall_sentiment is None
    
    def test_review_to_dict(self):
        """Test conversion of Review to dictionary"""
        orchestrator = ReviewOrchestrator(claude_api_key=self.mock_api_key)
        
        review = self.sample_reviews[0]
        review_dict = orchestrator._review_to_dict(review)
        
        assert review_dict['review_id'] == 'google_001'
        assert review_dict['source'] == 'google'
        assert review_dict['rating'] == 4.5
        assert review_dict['review_text'] == 'Great food and excellent service! The pasta was amazing.'
        assert review_dict['helpful_votes'] == 3
        assert review_dict['verified_purchase'] is True
    
    def test_enrich_temporal_metadata(self):
        """Test temporal metadata enrichment"""
        orchestrator = ReviewOrchestrator(claude_api_key=self.mock_api_key)
        
        review = self.sample_reviews[0]
        temporal_metadata = orchestrator._enrich_temporal_metadata(review)
        
        assert temporal_metadata['date'] is not None
        assert temporal_metadata['day_of_week'] in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        assert temporal_metadata['month'] in range(1, 13)
        assert temporal_metadata['quarter'] in range(1, 5)
        assert temporal_metadata['year'] >= 2024
        assert isinstance(temporal_metadata['is_weekend'], bool)
        assert isinstance(temporal_metadata['is_holiday'], bool)
    
    def test_enrich_temporal_metadata_invalid_date(self):
        """Test temporal metadata enrichment with invalid date"""
        orchestrator = ReviewOrchestrator(claude_api_key=self.mock_api_key)
        
        # Create review with invalid date
        review = Review(
            source='google',
            review_id='test_001',
            author_name='Test User',
            rating=4.0,
            review_text='Test review',
            review_date='invalid-date',
            fetched_timestamp=datetime.now()
        )
        
        temporal_metadata = orchestrator._enrich_temporal_metadata(review)
        
        assert temporal_metadata['date'] == 'invalid-date'
        assert temporal_metadata['day_of_week'] == 'unknown'
        assert temporal_metadata['month'] == 'unknown'
        assert temporal_metadata['quarter'] == 'unknown'
        assert temporal_metadata['year'] == 'unknown'
        assert temporal_metadata['is_weekend'] == 'unknown'
        assert temporal_metadata['is_holiday'] == 'unknown'
    
    def test_enrich_reviewer_metadata(self):
        """Test reviewer metadata enrichment"""
        orchestrator = ReviewOrchestrator(claude_api_key=self.mock_api_key)
        
        review = self.sample_reviews[0]
        reviewer_metadata = orchestrator._enrich_reviewer_metadata(review)
        
        assert reviewer_metadata['review_count'] == 3  # helpful_votes
        assert reviewer_metadata['elite_status'] is True  # verified_purchase
        assert isinstance(reviewer_metadata['local_reviewer'], bool)
        assert reviewer_metadata['review_history_with_restaurant'] == 'unknown'
    
    def test_enrich_platform_metadata(self):
        """Test platform metadata enrichment"""
        orchestrator = ReviewOrchestrator(claude_api_key=self.mock_api_key)
        
        review = self.sample_reviews[0]
        platform_metadata = orchestrator._enrich_platform_metadata(review)
        
        assert platform_metadata['source'] == 'google'
        assert platform_metadata['verified_purchase'] is True
        assert platform_metadata['response_exists'] is False  # No owner response
        assert platform_metadata['photos_count'] == 2
        assert platform_metadata['language'] == 'en'
    
    def test_is_likely_local_reviewer(self):
        """Test local reviewer detection"""
        orchestrator = ReviewOrchestrator(claude_api_key=self.mock_api_key)
        
        # Test local indicators
        assert orchestrator._is_likely_local_reviewer("Local Foodie") is True
        assert orchestrator._is_likely_local_reviewer("Neighbor John") is True
        assert orchestrator._is_likely_local_reviewer("Regular Customer") is True
        
        # Test non-local names
        assert orchestrator._is_likely_local_reviewer("John Smith") is False
        assert orchestrator._is_likely_local_reviewer("Anonymous") is False
        assert orchestrator._is_likely_local_reviewer("") is False
        assert orchestrator._is_likely_local_reviewer(None) is False
    
    def test_save_and_load_enriched_reviews(self):
        """Test saving and loading enriched reviews"""
        orchestrator = ReviewOrchestrator(claude_api_key=self.mock_api_key)
        
        # Create sample enriched reviews
        enriched_reviews = [
            EnrichedReview(
                review_id='test_001',
                source='google',
                author_name='Test User',
                rating=4.0,
                review_text='Test review',
                review_date='2024-01-15',
                overall_sentiment='positive',
                extraction_success=True,
                processing_timestamp=datetime.now().isoformat()
            )
        ]
        
        # Test saving
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            orchestrator.save_enriched_reviews(enriched_reviews, temp_path)
            
            # Verify file was created and has content
            assert os.path.exists(temp_path)
            with open(temp_path, 'r') as f:
                data = json.load(f)
                assert len(data) == 1
                assert data[0]['review_id'] == 'test_001'
                assert data[0]['overall_sentiment'] == 'positive'
            
            # Test loading
            loaded_reviews = orchestrator.load_enriched_reviews(temp_path)
            assert len(loaded_reviews) == 1
            assert loaded_reviews[0].review_id == 'test_001'
            assert loaded_reviews[0].overall_sentiment == 'positive'
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_log_processing_stats(self):
        """Test processing statistics logging"""
        orchestrator = ReviewOrchestrator(claude_api_key=self.mock_api_key)
        
        # Create sample enriched reviews
        enriched_reviews = [
            EnrichedReview(
                review_id='test_001',
                source='google',
                author_name='Test User',
                rating=4.0,
                review_text='Test review',
                review_date='2024-01-15',
                extraction_success=True
            ),
            EnrichedReview(
                review_id='test_002',
                source='yelp',
                author_name='Test User 2',
                rating=3.0,
                review_text='Test review 2',
                review_date='2024-01-16',
                extraction_success=False
            )
        ]
        
        # Create sample LLM responses
        llm_responses = [
            LLMResponse("content1", {"input_tokens": 100, "output_tokens": 50}, "model", True),
            LLMResponse("content2", {"input_tokens": 120, "output_tokens": 60}, "model", False, "Error")
        ]
        
        # This should not raise an exception
        orchestrator._log_processing_stats(enriched_reviews, llm_responses)


class TestEnrichedReview:
    """Test cases for EnrichedReview dataclass"""
    
    def test_enriched_review_creation(self):
        """Test EnrichedReview creation"""
        enriched_review = EnrichedReview(
            review_id='test_001',
            source='google',
            author_name='Test User',
            rating=4.0,
            review_text='Test review',
            review_date='2024-01-15',
            overall_sentiment='positive',
            extraction_success=True,
            processing_timestamp=datetime.now().isoformat()
        )
        
        assert enriched_review.review_id == 'test_001'
        assert enriched_review.source == 'google'
        assert enriched_review.author_name == 'Test User'
        assert enriched_review.rating == 4.0
        assert enriched_review.review_text == 'Test review'
        assert enriched_review.review_date == '2024-01-15'
        assert enriched_review.overall_sentiment == 'positive'
        assert enriched_review.extraction_success is True
        assert enriched_review.processing_timestamp is not None
    
    def test_enriched_review_minimal_creation(self):
        """Test EnrichedReview creation with minimal data"""
        enriched_review = EnrichedReview(
            review_id='test_001',
            source='google',
            author_name='Test User',
            rating=4.0,
            review_text='Test review',
            review_date='2024-01-15'
        )
        
        assert enriched_review.review_id == 'test_001'
        assert enriched_review.overall_sentiment is None
        assert enriched_review.extraction_success is False
        assert enriched_review.processing_timestamp is None


if __name__ == "__main__":
    pytest.main([__file__])
