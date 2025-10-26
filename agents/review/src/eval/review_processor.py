"""
Review Processor for LLM-based analysis
Orchestrates the processing of reviews with Claude LLM extraction
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Handle both relative and absolute imports
try:
    from .llm_wrapper import ClaudeWrapper, LLMResponse
    from .models.extended_review import ReviewExtraction
    from ..models.review import Review
    from ..storage.database_handler import DatabaseHandler
except ImportError:
    # Fallback to absolute imports when running from different directories
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from src.eval.llm_wrapper import ClaudeWrapper, LLMResponse
    from src.eval.models.extended_review import ReviewExtraction
    from src.models.review import Review
    from src.storage.database_handler import DatabaseHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReviewProcessor:
    """
    Orchestrates LLM analysis of restaurant reviews
    """
    
    def __init__(self, database_handler: DatabaseHandler, claude_api_key: Optional[str] = None):
        """
        Initialize the review processor
        
        Args:
            database_handler: Database handler for storing/retrieving reviews
            claude_api_key: Anthropic API key (if None, will try to get from environment)
        """
        self.database = database_handler
        self.llm_wrapper = ClaudeWrapper(api_key=claude_api_key)
        
    def process_unanalyzed_reviews(self) -> Dict[str, Any]:
        """
        Process all reviews that haven't been analyzed yet
        
        Returns:
            Dictionary with processing statistics
        """
        logger.info("Starting review processing for unanalyzed reviews")
        
        # Get all unprocessed reviews
        unprocessed_reviews = self.database.get_unprocessed_reviews()
        
        if not unprocessed_reviews:
            logger.info("No unprocessed reviews found")
            return {
                'processed_count': 0,
                'success_count': 0,
                'failed_count': 0,
                'total_tokens': 0
            }
        
        logger.info(f"Found {len(unprocessed_reviews)} unprocessed reviews")
        
        # Process each review
        success_count = 0
        failed_count = 0
        total_tokens = 0
        
        for i, review in enumerate(unprocessed_reviews, 1):
            logger.info(f"Processing review {i}/{len(unprocessed_reviews)}: {review.review_id}")
            
            try:
                # Process the review
                processed_review = self.process_single_review(review)
                
                # Save the updated review back to database
                # Update the specific review in place instead of overwriting all reviews
                self._update_single_review(processed_review)
                
                success_count += 1
                logger.info(f"Successfully processed review {review.review_id}")
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to process review {review.review_id}: {str(e)}")
                continue
        
        stats = {
            'processed_count': len(unprocessed_reviews),
            'success_count': success_count,
            'failed_count': failed_count,
            'total_tokens': total_tokens
        }
        
        logger.info(f"Processing complete: {success_count} successful, {failed_count} failed")
        return stats
    
    def process_single_review(self, review: Review) -> Review:
        """
        Process a single review and return enriched version
        
        Args:
            review: Review object to process
            
        Returns:
            Updated Review object with LLM-extracted data
        """
        # Build metadata dict for LLM
        metadata = {
            'rating': review.rating,
            'source': review.source,
            'review_date': review.review_date,
            'author_name': review.author_name
        }
        
        # Call LLM wrapper
        response = self.llm_wrapper.extract_review_data(review.review_text, metadata)
        
        if not response.success:
            raise Exception(f"LLM extraction failed: {response.error}")
        
        # Parse the response
        extraction = self.llm_wrapper.parse_extraction_response(response)
        
        if not extraction:
            raise Exception("Failed to parse LLM response")
        
        # Update review with extracted data
        updated_review = self._extraction_to_review_fields(review, extraction)
        
        # Set processing flags
        updated_review.llm_processed = True
        updated_review.llm_processed_date = datetime.now().isoformat()
        
        return updated_review
    
    def _extraction_to_review_fields(self, review: Review, extraction: ReviewExtraction) -> Review:
        """
        Convert ReviewExtraction to Review field updates
        
        Args:
            review: Original review object
            extraction: LLM extraction results
            
        Returns:
            Updated review object
        """
        # Create a copy of the review
        updated_review = Review(
            source=review.source,
            review_id=review.review_id,
            author_name=review.author_name,
            rating=review.rating,
            review_text=review.review_text,
            review_date=review.review_date,
            helpful_votes=review.helpful_votes,
            response_from_owner=review.response_from_owner,
            verified_purchase=review.verified_purchase,
            profile_photo_url=review.profile_photo_url,
            language=review.language,
            fetched_timestamp=review.fetched_timestamp,
            sentiment_score=review.sentiment_score,
            photos_attached=review.photos_attached,
            owner_response_date=review.owner_response_date,
            # Copy existing LLM fields
            llm_processed=review.llm_processed,
            llm_processed_date=review.llm_processed_date,
            overall_sentiment=review.overall_sentiment,
            rating_food=review.rating_food,
            rating_service=review.rating_service,
            rating_ambiance=review.rating_ambiance,
            rating_value=review.rating_value,
            mentioned_items=review.mentioned_items,
            staff_mentions=review.staff_mentions,
            operational_insights=review.operational_insights,
            visit_context=review.visit_context,
            key_phrases=review.key_phrases,
            anomaly_flags=review.anomaly_flags,
            restaurant_id=review.restaurant_id,
            restaurant_name=review.restaurant_name
        )
        
        # Update with new extraction data
        updated_review.overall_sentiment = extraction.overall_sentiment
        
        # Rating breakdown
        if extraction.rating_breakdown:
            updated_review.rating_food = extraction.rating_breakdown.food
            updated_review.rating_service = extraction.rating_breakdown.service
            updated_review.rating_ambiance = extraction.rating_breakdown.ambiance
            updated_review.rating_value = extraction.rating_breakdown.value
        
        # Convert complex objects to JSON strings
        if extraction.mentioned_items:
            updated_review.mentioned_items = json.dumps([item.dict() for item in extraction.mentioned_items])
        
        if extraction.staff_mentions:
            updated_review.staff_mentions = json.dumps([staff.dict() for staff in extraction.staff_mentions])
        
        if extraction.operational_insights:
            updated_review.operational_insights = json.dumps(extraction.operational_insights.dict())
        
        if extraction.visit_context:
            updated_review.visit_context = json.dumps(extraction.visit_context.dict())
        
        if extraction.key_phrases:
            updated_review.key_phrases = json.dumps(extraction.key_phrases.dict())
        
        if extraction.anomaly_flags:
            updated_review.anomaly_flags = json.dumps(extraction.anomaly_flags.dict())
        
        return updated_review
    
    def _update_single_review(self, updated_review: Review) -> None:
        """
        Update a single review in the database without affecting other reviews
        Handles duplicates by updating ALL occurrences of the same review_id
        
        Args:
            updated_review: The review object with updated LLM data
        """
        data = self.database._get_database_data()
        
        # Find and update ALL occurrences of the specific review (handle duplicates)
        updated_count = 0
        for i, review_dict in enumerate(data['reviews']):
            if review_dict['review_id'] == updated_review.review_id:
                data['reviews'][i] = updated_review.to_dict()
                updated_count += 1
        
        if updated_count == 0:
            logger.warning(f"Review {updated_review.review_id} not found in database")
        elif updated_count > 1:
            logger.warning(f"Found and updated {updated_count} duplicate entries for review {updated_review.review_id}")
        
        # Save the updated data
        self.database._save_database_data(data)
    
    def remove_duplicate_reviews(self) -> int:
        """
        Remove duplicate reviews from the database, keeping the most recent one
        
        Returns:
            Number of duplicates removed
        """
        data = self.database._get_database_data()
        reviews = data['reviews']
        
        # Group reviews by review_id
        review_groups = {}
        for review in reviews:
            review_id = review['review_id']
            if review_id not in review_groups:
                review_groups[review_id] = []
            review_groups[review_id].append(review)
        
        # Keep only the most recent review for each review_id
        unique_reviews = []
        duplicates_removed = 0
        
        for review_id, review_list in review_groups.items():
            if len(review_list) > 1:
                # Sort by fetched_timestamp (most recent first)
                review_list.sort(key=lambda x: x.get('fetched_timestamp', ''), reverse=True)
                unique_reviews.append(review_list[0])  # Keep the most recent
                duplicates_removed += len(review_list) - 1
                logger.info(f"Removed {len(review_list) - 1} duplicate(s) for review {review_id}")
            else:
                unique_reviews.append(review_list[0])
        
        # Update database
        data['reviews'] = unique_reviews
        self.database._save_database_data(data)
        
        logger.info(f"Removed {duplicates_removed} duplicate reviews total")
        return duplicates_removed
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Get statistics about processed vs unprocessed reviews
        
        Returns:
            Dictionary with processing statistics
        """
        all_reviews = self.database.get_all_reviews()
        processed_reviews = [r for r in all_reviews if r.llm_processed]
        unprocessed_reviews = [r for r in all_reviews if not r.llm_processed]
        
        return {
            'total_reviews': len(all_reviews),
            'processed_reviews': len(processed_reviews),
            'unprocessed_reviews': len(unprocessed_reviews),
            'processing_rate': len(processed_reviews) / len(all_reviews) if all_reviews else 0
        }
