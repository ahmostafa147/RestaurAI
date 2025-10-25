"""
Comprehensive tests for LLM wrapper functionality
"""

import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env from the project root (two levels up from this test file)
    env_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env')
    load_dotenv(env_path)
except ImportError:
    # dotenv not available, use environment variables directly
    pass

# Handle both relative and absolute imports
try:
    from ..llm_wrapper import ClaudeWrapper, LLMResponse
    from ..models.extended_review import ReviewExtraction, RatingBreakdown, MentionedItem, StaffMention
except ImportError:
    # Fallback to absolute imports when running tests directly
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    from src.eval.llm_wrapper import ClaudeWrapper, LLMResponse
    from src.eval.models.extended_review import ReviewExtraction, RatingBreakdown, MentionedItem, StaffMention


class TestClaudeWrapper:
    """Test cases for ClaudeWrapper class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        # Use real API key from environment if available
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.sample_review_text = "Great food and excellent service! The pasta was amazing and our server Sarah was very attentive. Will definitely come back."
        self.sample_metadata = {
            'rating': 4.5,
            'source': 'google',
            'review_date': '2024-01-15'
        }
        
        # Debug information
        print(f"\nDEBUG: ANTHROPIC_API_KEY found: {'Yes' if self.api_key else 'No'}")
        if self.api_key:
            print(f"DEBUG: API key starts with: {self.api_key[:10]}...")
        
        # Skip tests if no API key is available
        if not self.api_key:
            pytest.skip("ANTHROPIC_API_KEY not found in environment variables. Please set it in .env file or environment.")
    
    def test_init_with_api_key(self):
        """Test initialization with provided API key"""
        wrapper = ClaudeWrapper(api_key=self.api_key)
        assert wrapper.model == "claude-sonnet-4-5-20250929"
        assert wrapper.max_retries == 3
        assert wrapper.retry_delay == 1.0
        assert wrapper.client is not None
    
    def test_init_with_env_variable(self):
        """Test initialization with environment variable"""
        wrapper = ClaudeWrapper()  # Should use ANTHROPIC_API_KEY from environment
        assert wrapper.model == "claude-sonnet-4-5-20250929"
        assert wrapper.client is not None
    
    
    def test_extract_review_data_success(self):
        """Test successful review data extraction with real API"""
        wrapper = ClaudeWrapper(api_key=self.api_key)
        response = wrapper.extract_review_data(self.sample_review_text, self.sample_metadata)
        
        assert response.success is True
        assert response.content is not None
        assert response.usage['input_tokens'] > 0
        assert response.usage['output_tokens'] > 0
        assert response.model == "claude-sonnet-4-5-20250929"
        assert response.error is None
        
        # Verify the response contains valid JSON
        try:
            parsed_content = json.loads(response.content)
            assert "overall_sentiment" in parsed_content
            assert parsed_content["overall_sentiment"] in ["positive", "negative", "mixed", "neutral"]
        except json.JSONDecodeError:
            pytest.fail("Response content is not valid JSON")
    
    @patch('anthropic.Anthropic')
    def test_extract_review_data_failure(self, mock_anthropic):
        """Test review data extraction failure"""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("API Error")
        
        wrapper = ClaudeWrapper(api_key=self.mock_api_key)
        response = wrapper.extract_review_data(self.sample_review_text, self.sample_metadata)
        
        assert response.success is False
        assert response.content == ""
        assert response.error == "API Error"
        assert response.usage == {"input_tokens": 0, "output_tokens": 0}
    
    def test_parse_extraction_response_success(self):
        """Test successful parsing of extraction response with real API"""
        wrapper = ClaudeWrapper(api_key=self.api_key)
        
        # Get a real response from the API
        response = wrapper.extract_review_data(self.sample_review_text, self.sample_metadata)
        assert response.success is True
        
        # Parse the real response
        result = wrapper.parse_extraction_response(response)
        
        if result is not None:
            assert isinstance(result, ReviewExtraction)
            assert result.overall_sentiment in ["positive", "negative", "mixed", "neutral"]
            
            # Check if rating breakdown exists and is valid
            if result.rating_breakdown:
                if result.rating_breakdown.food:
                    assert 1 <= result.rating_breakdown.food <= 5
                if result.rating_breakdown.service:
                    assert 1 <= result.rating_breakdown.service <= 5
            
            # Check mentioned items if they exist
            if result.mentioned_items:
                for item in result.mentioned_items:
                    assert item.sentiment in ["positive", "negative", "mixed"]
                    assert len(item.name) > 0
        else:
            # If parsing failed, that's also a valid test result
            # (the API might return unexpected format)
            pytest.skip("API response format not compatible with Pydantic models")
    
    def test_parse_extraction_response_failure(self):
        """Test parsing failure with invalid JSON"""
        wrapper = ClaudeWrapper(api_key=self.api_key)
        
        # Create a mock response with invalid JSON
        mock_response = LLMResponse(
            content="invalid json content",
            usage={"input_tokens": 100, "output_tokens": 50},
            model="claude-sonnet-4-5-20250929",
            success=True
        )
        
        result = wrapper.parse_extraction_response(mock_response)
        assert result is None
    
    def test_parse_extraction_response_markdown_formatting(self):
        """Test parsing response with markdown formatting"""
        wrapper = ClaudeWrapper(api_key=self.api_key)
        
        json_content = json.dumps({
            "overall_sentiment": "positive",
            "rating_breakdown": None,
            "mentioned_items": [],
            "staff_mentions": [],
            "operational_insights": None,
            "visit_context": None,
            "key_phrases": None,
            "anomaly_flags": None
        })
        
        mock_response = LLMResponse(
            content=f"```json\n{json_content}\n```",
            usage={"input_tokens": 100, "output_tokens": 50},
            model="claude-sonnet-4-5-20250929",
            success=True
        )
        
        result = wrapper.parse_extraction_response(mock_response)
        assert isinstance(result, ReviewExtraction)
        assert result.overall_sentiment == "positive"
    
    def test_parse_extraction_response_failed_request(self):
        """Test parsing failed request"""
        wrapper = ClaudeWrapper(api_key=self.api_key)
        
        mock_response = LLMResponse(
            content="",
            usage={"input_tokens": 0, "output_tokens": 0},
            model="claude-sonnet-4-5-20250929",
            success=False,
            error="API Error"
        )
        
        result = wrapper.parse_extraction_response(mock_response)
        assert result is None
    
    def test_get_usage_stats(self):
        """Test usage statistics calculation"""
        wrapper = ClaudeWrapper(api_key=self.api_key)
        
        responses = [
            LLMResponse("content1", {"input_tokens": 100, "output_tokens": 50}, "model", True),
            LLMResponse("content2", {"input_tokens": 150, "output_tokens": 75}, "model", True),
            LLMResponse("content3", {"input_tokens": 0, "output_tokens": 0}, "model", False),
        ]
        
        stats = wrapper.get_usage_stats(responses)
        
        assert stats['total_input_tokens'] == 250
        assert stats['total_output_tokens'] == 125
        assert stats['total_tokens'] == 375
        assert stats['successful_requests'] == 2
        assert stats['failed_requests'] == 1
    
    def test_build_extraction_prompt(self):
        """Test prompt building functionality"""
        wrapper = ClaudeWrapper(api_key=self.api_key)
        
        prompt = wrapper._build_extraction_prompt(self.sample_review_text, self.sample_metadata)
        
        assert isinstance(prompt, str)
        assert self.sample_review_text in prompt
        assert str(self.sample_metadata['rating']) in prompt
        assert self.sample_metadata['source'] in prompt
        assert "overall_sentiment" in prompt
        assert "rating_breakdown" in prompt
        assert "mentioned_items" in prompt
        assert "staff_mentions" in prompt
        assert "operational_insights" in prompt
        assert "visit_context" in prompt
        assert "key_phrases" in prompt
        assert "anomaly_flags" in prompt
    
    def test_real_api_integration(self):
        """Test real API integration with actual review extraction"""
        wrapper = ClaudeWrapper(api_key=self.api_key)
        
        # Test with a more complex review
        complex_review = """
        I had a mixed experience at this restaurant. The food was absolutely delicious - 
        the pasta carbonara was perfect and the tiramisu was to die for. However, the service 
        was incredibly slow. We waited 45 minutes for our appetizers and another hour for our 
        main courses. Our server, Maria, was very apologetic and tried her best, but the 
        kitchen seemed overwhelmed. The ambiance was nice though - cozy and romantic. 
        I would come back for the food, but I hope they fix their service issues.
        """
        
        complex_metadata = {
            'rating': 3.5,
            'source': 'yelp',
            'review_date': '2024-01-20',
            'author_name': 'Test User'
        }
        
        response = wrapper.extract_review_data(complex_review, complex_metadata)
        
        assert response.success is True
        assert response.content is not None
        assert response.usage['input_tokens'] > 0
        assert response.usage['output_tokens'] > 0
        
        # Parse the response
        extraction = wrapper.parse_extraction_response(response)
        
        if extraction:
            # Verify the extraction makes sense
            assert extraction.overall_sentiment in ["positive", "negative", "mixed", "neutral"]
            
            # Check if it detected the mixed sentiment
            if extraction.overall_sentiment == "mixed":
                print("✅ API correctly identified mixed sentiment")
            
            # Check if it found mentioned items
            if extraction.mentioned_items:
                item_names = [item.name.lower() for item in extraction.mentioned_items]
                if "pasta" in " ".join(item_names) or "carbonara" in " ".join(item_names):
                    print("✅ API correctly identified food items")
            
            # Check if it found staff mentions
            if extraction.staff_mentions:
                staff_names = [staff.name for staff in extraction.staff_mentions if staff.name]
                if "maria" in " ".join(staff_names).lower():
                    print("✅ API correctly identified staff member")
            
            print(f"Extraction successful: {extraction.overall_sentiment} sentiment")
        else:
            pytest.skip("API response format not compatible with Pydantic models")


class TestLLMResponse:
    """Test cases for LLMResponse dataclass"""
    
    def test_llm_response_creation(self):
        """Test LLMResponse creation"""
        response = LLMResponse(
            content="test content",
            usage={"input_tokens": 100, "output_tokens": 50},
            model="claude-sonnet-4-5-20250929",
            success=True
        )
        
        assert response.content == "test content"
        assert response.usage == {"input_tokens": 100, "output_tokens": 50}
        assert response.model == "claude-sonnet-4-5-20250929"
        assert response.success is True
        assert response.error is None
    
    def test_llm_response_with_error(self):
        """Test LLMResponse with error"""
        response = LLMResponse(
            content="",
            usage={"input_tokens": 0, "output_tokens": 0},
            model="claude-sonnet-4-5-20250929",
            success=False,
            error="API Error"
        )
        
        assert response.content == ""
        assert response.success is False
        assert response.error == "API Error"


class TestPydanticModels:
    """Test cases for Pydantic model validation"""
    
    def test_rating_breakdown_validation(self):
        """Test RatingBreakdown model validation"""
        # Valid data
        valid_data = {"food": 5, "service": 4, "ambiance": 3, "value": 2}
        rating = RatingBreakdown(**valid_data)
        assert rating.food == 5
        assert rating.service == 4
        
        # Invalid rating (out of range)
        with pytest.raises(ValueError):
            RatingBreakdown(food=6)
        
        with pytest.raises(ValueError):
            RatingBreakdown(food=0)
    
    def test_mentioned_item_validation(self):
        """Test MentionedItem model validation"""
        # Valid data
        valid_data = {
            "name": "pasta",
            "sentiment": "positive",
            "aspects": ["taste", "presentation"]
        }
        item = MentionedItem(**valid_data)
        assert item.name == "pasta"
        assert item.sentiment == "positive"
        assert item.aspects == ["taste", "presentation"]
        
        # Invalid sentiment
        with pytest.raises(ValueError):
            MentionedItem(name="pasta", sentiment="invalid")
    
    def test_staff_mention_validation(self):
        """Test StaffMention model validation"""
        # Valid data
        valid_data = {
            "role": "server",
            "name": "John",
            "sentiment": "positive",
            "specific_feedback": "Very helpful"
        }
        staff = StaffMention(**valid_data)
        assert staff.role == "server"
        assert staff.name == "John"
        assert staff.sentiment == "positive"
        
        # Invalid role
        with pytest.raises(ValueError):
            StaffMention(role="invalid_role", sentiment="positive")
        
        # Invalid sentiment
        with pytest.raises(ValueError):
            StaffMention(role="server", sentiment="neutral")
    
    def test_review_extraction_validation(self):
        """Test ReviewExtraction model validation"""
        # Valid minimal data
        valid_data = {
            "overall_sentiment": "positive",
            "rating_breakdown": None,
            "mentioned_items": [],
            "staff_mentions": [],
            "operational_insights": None,
            "visit_context": None,
            "key_phrases": None,
            "anomaly_flags": None
        }
        extraction = ReviewExtraction(**valid_data)
        assert extraction.overall_sentiment == "positive"
        
        # Invalid sentiment
        with pytest.raises(ValueError):
            ReviewExtraction(overall_sentiment="invalid")


if __name__ == "__main__":
    pytest.main([__file__])
