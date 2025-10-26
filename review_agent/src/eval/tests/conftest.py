"""
Pytest configuration and shared fixtures for eval tests
"""

import pytest
import tempfile
import os
from datetime import datetime
from typing import List

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env from the project root (three levels up from this conftest file)
    env_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env')
    load_dotenv(env_path)
except ImportError:
    # dotenv not available, use environment variables directly
    pass

# Handle both relative and absolute imports
try:
    from ...models.review import Review
except ImportError:
    # Fallback to absolute imports when running tests directly
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
    from src.models.review import Review


@pytest.fixture
def sample_reviews() -> List[Review]:
    """Create sample Review objects for testing"""
    reviews = []
    
    # Review 1 - Positive Google review
    review1 = Review(
        source='google',
        review_id='google_001',
        author_name='John Smith',
        rating=4.5,
        review_text='Great food and excellent service! The pasta was amazing and our server Sarah was very attentive. Will definitely come back.',
        review_date='2024-01-15T10:30:00Z',
        helpful_votes=3,
        verified_purchase=True,
        photos_attached=2,
        response_from_owner='Thank you for your kind words!',
        fetched_timestamp=datetime.now()
    )
    reviews.append(review1)
    
    # Review 2 - Negative Yelp review
    review2 = Review(
        source='yelp',
        review_id='yelp_001',
        author_name='Jane Doe',
        rating=3.0,
        review_text='Food was okay but service was slow. The burger was cold when it arrived. Not sure if I would recommend.',
        review_date='2024-01-20T19:45:00Z',
        helpful_votes=1,
        verified_purchase=False,
        photos_attached=0,
        fetched_timestamp=datetime.now()
    )
    reviews.append(review2)
    
    # Review 3 - Mixed sentiment review
    review3 = Review(
        source='google',
        review_id='google_002',
        author_name='Mike Johnson',
        rating=3.5,
        review_text='The ambiance was great and the staff was friendly, but the food took forever to arrive and was just average.',
        review_date='2024-01-25T12:15:00Z',
        helpful_votes=0,
        verified_purchase=True,
        photos_attached=1,
        fetched_timestamp=datetime.now()
    )
    reviews.append(review3)
    
    return reviews


@pytest.fixture
def sample_review_extraction_data():
    """Sample review extraction data for testing"""
    return {
        "overall_sentiment": "positive",
        "rating_breakdown": {
            "food": 5,
            "service": 4,
            "ambiance": 4,
            "value": 3
        },
        "mentioned_items": [
            {
                "name": "pasta",
                "sentiment": "positive",
                "aspects": ["taste", "presentation"]
            },
            {
                "name": "burger",
                "sentiment": "negative",
                "aspects": ["temperature", "taste"]
            }
        ],
        "staff_mentions": [
            {
                "role": "server",
                "name": "Sarah",
                "sentiment": "positive",
                "specific_feedback": "very attentive"
            }
        ],
        "operational_insights": {
            "wait_time": "reasonable",
            "reservation_experience": "positive",
            "cleanliness": "positive",
            "noise_level": "moderate",
            "crowding": "comfortable"
        },
        "visit_context": {
            "party_type": "couple",
            "occasion": "date",
            "time_of_visit": "dinner",
            "first_visit": False,
            "would_return": True,
            "would_recommend": True
        },
        "key_phrases": {
            "positive_highlights": [
                "excellent service",
                "amazing pasta"
            ],
            "negative_issues": [
                "slow service",
                "cold burger"
            ],
            "suggestions": [
                "improve food temperature"
            ]
        },
        "anomaly_flags": {
            "potential_fake": False,
            "health_safety_concern": False,
            "extreme_emotion": False,
            "competitor_mention": False
        }
    }


@pytest.fixture
def temp_file():
    """Create a temporary file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def mock_anthropic_api():
    """Mock Anthropic API for testing"""
    from unittest.mock import Mock, patch
    
    with patch('anthropic.Anthropic') as mock_anthropic:
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_llm_response_success():
    """Mock successful LLM response"""
    from ..llm_wrapper import LLMResponse
    import json
    
    return LLMResponse(
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
    )


@pytest.fixture
def mock_llm_response_failure():
    """Mock failed LLM response"""
    from ..llm_wrapper import LLMResponse
    
    return LLMResponse(
        content="",
        usage={"input_tokens": 0, "output_tokens": 0},
        model="claude-sonnet-4-5-20250929",
        success=False,
        error="API Error"
    )


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables"""
    import os
    
    # Set test environment variables
    # os.environ['ANTHROPIC_API_KEY'] = 'test-api-key'
    os.environ['LOG_LEVEL'] = 'DEBUG'
    
    yield
    
    # Cleanup environment variables
    if 'ANTHROPIC_API_KEY' in os.environ:
        del os.environ['ANTHROPIC_API_KEY']
    if 'LOG_LEVEL' in os.environ:
        del os.environ['LOG_LEVEL']
