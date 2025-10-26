"""
Main entry point for the Restaurant AI Review System
Simple initialization of scraper interface and database functionality
"""

import sys
import os
import json
from typing import Optional, Dict, Any, List

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.scraper_interface import ScraperInterface
from storage.database_handler import DatabaseHandler
from scrapers.pull_dataset import Status
from models.snapshot import Snapshot
from models.review import Review;

class RestaurantReviewAgent:
    def __init__(self, database_path: str):
        self.scraper_interface = ScraperInterface()
        self.database_handler = DatabaseHandler(database_path)
        self.restaurants = self._load_restaurants()
    
    def _load_restaurants(self) -> List[Dict[str, Any]]:
        """Load restaurant configurations from restaurants.json"""
        restaurants_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),'..','..', 'restaurants.json')
        if os.path.exists(restaurants_file):
            with open(restaurants_file, 'r') as f:
                config = json.load(f)
                return config.get('restaurants', [])
        return []
    def pull_reviews(self):
        """Pull reviews for all configured restaurants"""
        if not self.restaurants:
            # Fallback to default scraping for backward compatibility
            google_snapshot = self.scraper_interface.scrape_google_reviews()
            yelp_snapshot = self.scraper_interface.scrape_yelp_reviews(
                unrecommended_reviews=True,
                start_date="2025-03-02T00:00:00.000Z",
                end_date="2025-06-01T00:00:00.000Z",
                sort_by="DATE_DESC"
            )
            self.database_handler.save_snapshot(google_snapshot)
            self.database_handler.save_snapshot(yelp_snapshot)
        else:
            # Scrape reviews for each configured restaurant
            for restaurant in self.restaurants:
                restaurant_id = restaurant['id']
                restaurant_name = restaurant['name']
                
                google_snapshot = self.scraper_interface.scrape_google_reviews(
                    google_url=restaurant['google_url'],
                    restaurant_id=restaurant_id
                )
                yelp_snapshot = self.scraper_interface.scrape_yelp_reviews(
                    unrecommended_reviews=True,
                    start_date="2025-03-02T00:00:00.000Z",
                    end_date="2025-06-01T00:00:00.000Z",
                    sort_by="DATE_DESC",
                    yelp_url=restaurant['yelp_url'],
                    restaurant_id=restaurant_id
                )
                self.database_handler.save_snapshot(google_snapshot)
                self.database_handler.save_snapshot(yelp_snapshot)
    def update_pull_status(self):
        """Update the status of all currently saved snapshots"""
        for snapshot in self.database_handler.get_all_snapshots():
            if snapshot.status == Status.READY.value:
                continue;
            status_enum = self.scraper_interface.check_snapshot_status(snapshot)
            snapshot.status = status_enum.value
            self.database_handler.save_snapshot(snapshot) #Update the status in the database
            if snapshot.status == Status.READY.value:
                reviews = self.scraper_interface.safe_pull_dataset(snapshot)
                if not reviews:
                    raise Exception(f"Snapshot {snapshot.snapshot_id}Status is ready, but cannot be pulled")
                print(f"Pulled {len(reviews)} reviews from snapshot {snapshot.snapshot_id}")
                
                # Get restaurant info from snapshot if available
                restaurant_id = getattr(snapshot, 'restaurant_id', None)
                restaurant_name = None
                if restaurant_id:
                    # Find restaurant name from loaded restaurants
                    for restaurant in self.restaurants:
                        if restaurant['id'] == restaurant_id:
                            restaurant_name = restaurant['name']
                            break
                
                # Create reviews with restaurant info
                review_objects = [
                    Review.from_api_response(
                        review, 
                        snapshot.source, 
                        restaurant_id=restaurant_id,
                        restaurant_name=restaurant_name
                    ) 
                    for review in reviews
                ]
                self.database_handler.save_reviews(review_objects)
    
    def process_reviews_with_llm(self, claude_api_key: Optional[str] = None):
        """Process unanalyzed reviews with LLM extraction"""
        from eval.review_processor import ReviewProcessor
        
        processor = ReviewProcessor(self.database_handler, claude_api_key)
        stats = processor.process_unanalyzed_reviews()
        
        print(f"Processed {stats['processed_count']} reviews")
        print(f"Success: {stats['success_count']}, Failed: {stats['failed_count']}")
        print(f"Total API tokens used: {stats['total_tokens']}")
        
        return stats
    
    def clean_duplicate_reviews(self):
        """Remove duplicate reviews from the database"""
        from eval.review_processor import ReviewProcessor
        
        processor = ReviewProcessor(self.database_handler)
        duplicates_removed = processor.remove_duplicate_reviews()
        
        print(f"Removed {duplicates_removed} duplicate reviews")
        return duplicates_removed
    
    def generate_analytics(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Generate analytics report from processed reviews"""
        from analytics.analytics_engine import AnalyticsEngine
        
        engine = AnalyticsEngine(self.database_handler)
        
        # Use multi-restaurant report by default
        report = engine.generate_multi_restaurant_report()
        
        if output_path:
            # Export multi-restaurant report
            engine.export_report(output_path, multi_restaurant=True)
            print(f"Analytics report exported to {output_path}")
        
        return report