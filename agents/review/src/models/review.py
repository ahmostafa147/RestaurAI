"""
Review data model for restaurant reviews
This module defines the Review data structure with comprehensive fields.
"""

from dataclasses import dataclass
from typing import Optional, Union
from datetime import datetime
import json

@dataclass
class Review:
    """
    Comprehensive data structure for restaurant reviews
    
    This class captures all relevant information from both Google and Yelp reviews
    with standardized fields for consistent processing and storage.
    """
    # Core identification
    source: str  # 'google' or 'yelp'
    review_id: str  # Unique identifier from the source platform
    author_name: str  # Name of the reviewer
    
    # Review content
    rating: float  # Rating on 5-star scale (normalized)
    review_text: str  # Full text of the review
    review_date: str  # Date when review was posted (ISO format)
    
    # Additional metadata
    helpful_votes: Optional[int] = None  # Number of helpful votes (Yelp)
    response_from_owner: Optional[str] = None  # Owner response to review
    verified_purchase: bool = False  # Whether review is verified
    profile_photo_url: Optional[str] = None  # URL to reviewer's profile photo
    language: str = "en"  # Language of the review
    
    # System fields
    fetched_timestamp: datetime = None  # When this review was fetched
    sentiment_score: Optional[float] = None  # Computed sentiment score (-1 to 1)
    photos_attached: int = 0  # Number of photos attached to review
    owner_response_date: Optional[str] = None  # Date of owner response
    
    # LLM-extracted fields
    llm_processed: bool = False  # Flag to track if review has been analyzed
    llm_processed_date: Optional[str] = None  # When LLM processing occurred
    overall_sentiment: Optional[str] = None  # positive/negative/mixed/neutral
    rating_food: Optional[int] = None  # 1-5
    rating_service: Optional[int] = None  # 1-5
    rating_ambiance: Optional[int] = None  # 1-5
    rating_value: Optional[int] = None  # 1-5
    mentioned_items: Optional[str] = None  # JSON string of mentioned menu items
    staff_mentions: Optional[str] = None  # JSON string of staff mentions
    operational_insights: Optional[str] = None  # JSON string of operational data
    visit_context: Optional[str] = None  # JSON string of visit context
    key_phrases: Optional[str] = None  # JSON string of key phrases
    anomaly_flags: Optional[str] = None  # JSON string of anomaly flags
    
    # Restaurant identification (moved to end to fix dataclass ordering)
    restaurant_id: str = None  # Restaurant identifier
    restaurant_name: str = None  # Restaurant name
    
    def __post_init__(self):
        """Post-initialization processing"""
        if self.fetched_timestamp is None:
            self.fetched_timestamp = datetime.now()
    
    def to_dict(self) -> dict:
        """
        Convert Review to dictionary for CSV storage
        
        Returns:
            Dictionary representation of the review
        """
        result = {
            'source': self.source,
            'review_id': self.review_id,
            'author_name': self.author_name,
            'rating': self.rating,
            'review_text': self.review_text,
            'review_date': self.review_date,
            'helpful_votes': self.helpful_votes,
            'response_from_owner': self.response_from_owner,
            'verified_purchase': self.verified_purchase,
            'profile_photo_url': self.profile_photo_url,
            'language': self.language,
            'fetched_timestamp': self.fetched_timestamp.isoformat() if self.fetched_timestamp else None,
            'sentiment_score': self.sentiment_score,
            'photos_attached': self.photos_attached,
            'owner_response_date': self.owner_response_date,
            # LLM-extracted fields
            'llm_processed': self.llm_processed,
            'llm_processed_date': self.llm_processed_date,
            'overall_sentiment': self.overall_sentiment,
            'rating_food': self.rating_food,
            'rating_service': self.rating_service,
            'rating_ambiance': self.rating_ambiance,
            'rating_value': self.rating_value,
            'mentioned_items': self.mentioned_items,
            'staff_mentions': self.staff_mentions,
            'operational_insights': self.operational_insights,
            'visit_context': self.visit_context,
            'key_phrases': self.key_phrases,
            'anomaly_flags': self.anomaly_flags
        }
        if self.restaurant_id is not None:
            result['restaurant_id'] = self.restaurant_id
        if self.restaurant_name is not None:
            result['restaurant_name'] = self.restaurant_name
        return result
    
    @classmethod
    def from_google_maps(cls, data: dict, restaurant_id: str = None, restaurant_name: str = None) -> 'Review':
        """
        Create Review from Google Maps API data
        
        Args:
            data: Dictionary containing Google Maps review data
            restaurant_id: Optional restaurant identifier
            restaurant_name: Optional restaurant name
            
        Returns:
            Review instance
        """
        # Parse timestamp if it exists
        fetched_timestamp = None
        if data.get('timestamp'):
            try:
                fetched_timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
            except (ValueError, TypeError):
                fetched_timestamp = None
        
        # Handle review_date format
        review_date = data.get('review_date', '')
        if review_date and not review_date.startswith('20'):
            # If it's a relative date like "a week ago", use timestamp
            review_date = data.get('timestamp', review_date)
        
        # Count photos if they exist
        photos_count = 0
        if data.get('photos'):
            if isinstance(data['photos'], list):
                photos_count = len(data['photos'])
            elif isinstance(data['photos'], int):
                photos_count = data['photos']
        
        return cls(
            source='google',
            review_id=data['review_id'],
            author_name=data['reviewer_name'],
            rating=float(data['review_rating']),
            review_text=data.get('review', '') or '',  # Handle None values
            review_date=review_date,
            helpful_votes=data.get('number_of_likes', 0),
            response_from_owner=data.get('response_of_owner'),
            verified_purchase=data.get('local_guide', False),  # Local guides are somewhat verified
            profile_photo_url=data.get('profile_pic_url'),
            language='en',  # Google doesn't provide this, assume English
            fetched_timestamp=fetched_timestamp,
            sentiment_score=None,  # Will be computed separately
            photos_attached=photos_count,
            owner_response_date=data.get('response_date'),
            restaurant_id=restaurant_id,
            restaurant_name=restaurant_name
        )
    
    @classmethod
    def from_yelp(cls, data: dict, restaurant_id: str = None, restaurant_name: str = None) -> 'Review':
        """
        Create Review from Yelp API data
        
        Args:
            data: Dictionary containing Yelp review data
            restaurant_id: Optional restaurant identifier
            restaurant_name: Optional restaurant name
            
        Returns:
            Review instance
        """
        # Parse timestamp if it exists
        fetched_timestamp = None
        if data.get('timestamp'):
            try:
                fetched_timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
            except (ValueError, TypeError):
                fetched_timestamp = None
        
        # Use ISO format date if available, otherwise use Date field
        review_date = data.get('date_iso_format', data.get('Date', ''))
        
        # Handle the typo in "Review_auther"
        author_info = data.get('Review_auther', {})
        
        # Get photos count from author info
        photos_count = 0
        if isinstance(author_info.get('Photos'), (int, str)):
            try:
                photos_count = int(author_info['Photos'])
            except (ValueError, TypeError):
                photos_count = 0
        
        return cls(
            source='yelp',
            review_id=data['review_id'],
            author_name=author_info.get('Username', 'Anonymous'),
            rating=float(data['Rating']),
            review_text=data.get('Content', ''),
            review_date=review_date,
            helpful_votes=author_info.get('Reviews_made'),  # Not exactly helpful votes, but related
            response_from_owner=None,  # Yelp data doesn't include this in your format
            verified_purchase=data.get('recommended_review', False),
            profile_photo_url=data.get('profile_pic_url'),
            language='en',  # Yelp doesn't provide this, assume English
            fetched_timestamp=fetched_timestamp,
            sentiment_score=None,  # Will be computed separately
            photos_attached=photos_count,
            owner_response_date=None,  # Not in Yelp data
            restaurant_id=restaurant_id,
            restaurant_name=restaurant_name
        )
    
    @classmethod
    def from_api_response(cls, data: dict, source: str = None, restaurant_id: str = None, restaurant_name: str = None) -> 'Review':
        """
        Smart factory method that detects the source and creates Review accordingly
        
        Args:
            data: Dictionary containing review data
            source: Optional source hint ('google' or 'yelp')
            restaurant_id: Optional restaurant identifier
            restaurant_name: Optional restaurant name
            
        Returns:
            Review instance
        """
        # Try to auto-detect source if not provided
        if source is None:
            if 'reviewer_name' in data and 'review_rating' in data:
                source = 'google'
            elif 'Review_auther' in data or 'Rating' in data:
                source = 'yelp'
            elif 'source' in data:
                # It's already in Review format
                return cls.from_dict(data)
            else:
                raise ValueError(f"Cannot determine source from data keys: {list(data.keys())[:10]}")
        
        if source == 'google':
            return cls.from_google_maps(data, restaurant_id, restaurant_name)
        elif source == 'yelp':
            return cls.from_yelp(data, restaurant_id, restaurant_name)
        else:
            raise ValueError(f"Unknown source: {source}")

    # Keep the existing from_dict method for loading from storage
    @classmethod
    def from_dict(cls, data: Union[dict, str]) -> 'Review':
        """
        Create Review from dictionary (for loading from storage)
        
        Args:
            data: Dictionary containing review data in standard format
            
        Returns:
            Review instance
        """
        if isinstance(data, str):
            data = json.loads(data)
        
        # Check if this is API data that needs conversion
        if 'source' not in data:
            # This is raw API data, use the smart factory
            return cls.from_api_response(data)
        
        # Parse fetched_timestamp if it exists
        fetched_timestamp = None
        if data.get('fetched_timestamp'):
            try:
                fetched_timestamp = datetime.fromisoformat(data['fetched_timestamp'])
            except ValueError:
                fetched_timestamp = None
        
        return cls(
            source=data['source'],
            review_id=data['review_id'],
            author_name=data['author_name'],
            rating=float(data['rating']),
            review_text=data['review_text'],
            review_date=data['review_date'],
            helpful_votes=data.get('helpful_votes'),
            response_from_owner=data.get('response_from_owner'),
            verified_purchase=bool(data.get('verified_purchase', False)),
            profile_photo_url=data.get('profile_photo_url'),
            language=data.get('language', 'en'),
            fetched_timestamp=fetched_timestamp,
            sentiment_score=data.get('sentiment_score'),
            photos_attached=int(data.get('photos_attached', 0)),
            owner_response_date=data.get('owner_response_date'),
            # LLM-extracted fields
            llm_processed=bool(data.get('llm_processed', False)),
            llm_processed_date=data.get('llm_processed_date'),
            overall_sentiment=data.get('overall_sentiment'),
            rating_food=data.get('rating_food'),
            rating_service=data.get('rating_service'),
            rating_ambiance=data.get('rating_ambiance'),
            rating_value=data.get('rating_value'),
            mentioned_items=data.get('mentioned_items'),
            staff_mentions=data.get('staff_mentions'),
            operational_insights=data.get('operational_insights'),
            visit_context=data.get('visit_context'),
            key_phrases=data.get('key_phrases'),
            anomaly_flags=data.get('anomaly_flags'),
            restaurant_id=data.get('restaurant_id'),
            restaurant_name=data.get('restaurant_name')
        )
    
    def normalize_rating(self, source_scale: int = 5) -> float:
        """
        Normalize rating to 5-star scale
        
        Args:
            source_scale: Original scale of the rating
            
        Returns:
            Normalized rating (0-5)
        """
        if source_scale == 5:
            return self.rating
        elif source_scale == 10:
            return self.rating / 2.0
        else:
            # Assume it's already normalized
            return min(5.0, max(0.0, self.rating))
    
    def is_recent(self, days: int = 30) -> bool:
        """
        Check if review is recent
        
        Args:
            days: Number of days to consider as recent
            
        Returns:
            True if review is within the specified days
        """
        try:
            review_date = datetime.fromisoformat(self.review_date.replace('Z', '+00:00'))
            days_ago = datetime.now().replace(tzinfo=review_date.tzinfo) - review_date
            return days_ago.days <= days
        except (ValueError, AttributeError):
            return False
    
    def has_owner_response(self) -> bool:
        """
        Check if review has owner response
        
        Returns:
            True if owner has responded to this review
        """
        return self.response_from_owner is not None and len(self.response_from_owner.strip()) > 0
    
    def get_word_count(self) -> int:
        """
        Get word count of review text
        
        Returns:
            Number of words in review text
        """
        return len(self.review_text.split()) if self.review_text else 0
    
    def is_helpful(self, threshold: int = 5) -> bool:
        """
        Check if review is considered helpful based on votes
        
        Args:
            threshold: Minimum helpful votes to consider helpful
            
        Returns:
            True if review has enough helpful votes
        """
        return self.helpful_votes is not None and self.helpful_votes >= threshold
