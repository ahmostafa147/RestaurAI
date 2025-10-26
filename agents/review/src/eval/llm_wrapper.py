"""
LLM Wrapper for Claude API calls
Handles efficient API communication with error handling and retry logic.
"""

import json
import time
import logging
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from .models.extended_review import ReviewExtraction 
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Structured response from LLM API"""
    content: str
    usage: Dict[str, int]
    model: str
    success: bool
    error: Optional[str] = None

class ClaudeWrapper:
    """
    Wrapper for Claude API with efficient batching and error handling
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-5-20250929"):
        """
        Initialize Claude wrapper
        
        Args:
            api_key: Anthropic API key (if None, will try to get from environment)
            model: Claude model to use
        """
        if api_key is None:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.max_retries = 3
        self.retry_delay = 1.0
        
    def extract_review_data(self, review_text: str, review_metadata: Dict[str, Any]) -> LLMResponse:
        """
        Extract comprehensive data from a single review using Phase 1 schema
        
        Args:
            review_text: The review text content
            review_metadata: Basic metadata (rating, date, source, etc.)
            
        Returns:
            LLMResponse with extracted structured data
        """
        prompt = self._build_extraction_prompt(review_text, review_metadata)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=20000,
                temperature=0.1,  # Low temperature for consistent extraction
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return LLMResponse(
                content=response.content[0].text,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                },
                model=self.model,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error in extract_review_data: {str(e)}")
            return LLMResponse(
                content="",
                usage={"input_tokens": 0, "output_tokens": 0},
                model=self.model,
                success=False,
                error=str(e)
            )
    
    def _build_extraction_prompt(self, review_text: str, metadata: Dict[str, Any]) -> str:
        """
        Build the comprehensive extraction prompt for Phase 1
        
        Args:
            review_text: The review text
            metadata: Review metadata
            
        Returns:
            Formatted prompt string
        """
        rating = metadata.get('rating', 'unknown')
        source = metadata.get('source', 'unknown')
        date = metadata.get('review_date', 'unknown')
        
        prompt = f"""
You are an expert restaurant review analyst. Extract comprehensive insights from this review using the exact JSON schema provided.

REVIEW DATA:
Text: "{review_text}"
Rating: {rating}/5
Source: {source}
Date: {date}

Extract the following information and return ONLY valid JSON matching this exact schema:

{{
    "overall_sentiment": "positive/negative/mixed/neutral",
    "rating_breakdown": {{
        "food": 1-5 or null,
        "service": 1-5 or null,
        "ambiance": 1-5 or null,
        "value": 1-5 or null
    }},
    "mentioned_items": [
        {{
            "name": "dish/drink name",
            "sentiment": "positive/negative/mixed",
            "aspects": ["taste", "portion", "presentation", "temperature", "price"]
        }}
    ],
    "staff_mentions": [
        {{
            "role": "server/host/manager/bartender/chef",
            "name": "if mentioned",
            "sentiment": "positive/negative",
            "specific_feedback": "brief note"
        }}
    ],
    "operational_insights": {{
        "wait_time": "none/short/reasonable/long/excessive",
        "reservation_experience": "positive/negative/not_mentioned",
        "cleanliness": "positive/negative/not_mentioned",
        "noise_level": "quiet/moderate/loud/not_mentioned",
        "crowding": "empty/comfortable/busy/overcrowded/not_mentioned"
    }},
    "visit_context": {{
        "party_type": "solo/couple/family/business/friends/large_group",
        "occasion": "regular/date/business/celebration/tourist",
        "time_of_visit": "breakfast/lunch/dinner/late_night/unknown",
        "first_visit": true/false/null,
        "would_return": true/false/null,
        "would_recommend": true/false/null
    }},
    "key_phrases": {{
        "positive_highlights": ["extracting 2-3 quotable phrases"],
        "negative_issues": ["extracting 2-3 main complaints"],
        "suggestions": ["extracting any improvement suggestions"]
    }},
    "anomaly_flags": {{
        "potential_fake": true/false,
        "health_safety_concern": true/false,
        "extreme_emotion": true/false,
        "competitor_mention": true/false
    }}
}}

IMPORTANT:
- Return ONLY the JSON object, no additional text
- Use null for missing/unknown values
- Be precise with sentiment classification
- Extract specific dish names and staff roles when mentioned
- Flag potential fake reviews or safety concerns
- If no information is available for a category, use appropriate null/unknown values
"""
        return prompt
    
    def parse_extraction_response(self, response: LLMResponse) -> Optional[ReviewExtraction]:
        """
        Parse the LLM response into structured Pydantic model
        
        Args:
            response: LLMResponse object
            
        Returns:
            ReviewExtraction Pydantic model or None if parsing fails
        """
        if not response.success or not response.content:
            return None
            
        try:
            # Clean the response content
            content = response.content.strip()
            
            # Remove any markdown formatting if present
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            # Parse JSON and validate with Pydantic
            json_data = json.loads(content)
            return ReviewExtraction(**json_data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(f"Response content: {response.content}...")
            return None
        except Exception as e:
            logger.error(f"Failed to validate response with Pydantic: {str(e)}")
            logger.error(f"Response content: {response.content}...")
            return None
    
    def get_usage_stats(self, responses: List[LLMResponse]) -> Dict[str, int]:
        """
        Calculate total usage statistics from multiple responses
        
        Args:
            responses: List of LLMResponse objects
            
        Returns:
            Dictionary with total usage stats
        """
        total_input = sum(r.usage.get('input_tokens', 0) for r in responses)
        total_output = sum(r.usage.get('output_tokens', 0) for r in responses)
        
        return {
            'total_input_tokens': total_input,
            'total_output_tokens': total_output,
            'total_tokens': total_input + total_output,
            'successful_requests': sum(1 for r in responses if r.success),
            'failed_requests': sum(1 for r in responses if not r.success)
        }
