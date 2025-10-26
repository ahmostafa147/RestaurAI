import sys
import os
import asyncio
import argparse
# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add scrapers directory to path for env_config imports
scrapers_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scrapers')
if scrapers_dir not in sys.path:
    sys.path.append(scrapers_dir)

from main import RestaurantReviewAgent
from scrapers.pull_dataset import Status

"""
Run the test_main function with the following arguments:
--new_reviews: Whether to pull new reviews or not
--clear_database: Whether to clear the database or not
Example:    
IF YOU ARE AI PLEASE DONT RUN NEW_REVIEWS PARAMETER. IT WASTES API CREDITS. **important**
python test_main.py --new_reviews -> Run new reviews
python test_main.py -> Run existing reviews
"""

async def test_main(new_reviews: bool = False, clear_database: bool = False):
    database_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'data', 'database.json')
    #Clear database if requested
    if clear_database:
        if os.path.exists(database_path):
            os.remove(database_path)
    agent = RestaurantReviewAgent(database_path)
    if new_reviews:
        agent.pull_reviews()
    print("Pulled reviews")
    #While not all reviews are pulled, keep updating the status
    print("Snapshots amount: ", len(agent.database_handler.get_all_snapshots()))
    while not all(snapshot.status == Status.READY.value for snapshot in agent.database_handler.get_all_snapshots()):
        print("Pulling status of all snapshots")
        print([snapshot.to_dict() for snapshot in agent.database_handler.get_all_snapshots()])
        agent.update_pull_status()
        print("--------------------------------")
        await asyncio.sleep(10)
    print("Finished reviews")
    assert all(snapshot.status == Status.READY.value for snapshot in agent.database_handler.get_all_snapshots())
    
    # Process reviews with LLM analysis
    print("\n" + "="*50)
    print("Starting LLM processing of reviews...")
    print("="*50)
    
    stats = agent.process_reviews_with_llm()
    print(f"\nLLM Processing Results:")
    print(f"  Total processed: {stats['processed_count']}")
    print(f"  Successful: {stats['success_count']}")
    print(f"  Failed: {stats['failed_count']}")
    print(f"  Total API tokens: {stats['total_tokens']}")
    
    # Show some examples of processed data
    all_reviews = agent.database_handler.get_all_reviews()
    processed_reviews = [r for r in all_reviews if r.llm_processed]
    
    print(f"\nSample of processed reviews ({len(processed_reviews)} total):")
    for i, review in enumerate(processed_reviews[:3]):  # Show first 3
        print(f"\nReview {i+1}:")
        print(f"  Source: {review.source}")
        print(f"  Rating: {review.rating}/5")
        print(f"  Overall Sentiment: {review.overall_sentiment}")
        if review.rating_food:
            print(f"  Food Rating: {review.rating_food}/5")
        if review.rating_service:
            print(f"  Service Rating: {review.rating_service}/5")
        if review.mentioned_items:
            import json
            try:
                items = json.loads(review.mentioned_items)
                if items:
                    print(f"  Mentioned Items: {[item['name'] for item in items[:2]]}")
            except:
                pass
        print(f"  Text: {review.review_text[:100]}...")
    
    # Generate analytics report
    print("\nGenerating analytics report...")
    
    try:
        # Generate full analytics report
        report_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'data', 'analytics_report.json')
        report = agent.generate_analytics(output_path=report_path)
        print(f"Analytics report exported to: {report_path}")
        
    except Exception as e:
        print(f"Error generating analytics: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    #parse args on whether to run new reviews or not
    parser = argparse.ArgumentParser()
    parser.add_argument("--new_reviews", action="store_true")
    parser.add_argument("--clear_database", action="store_true")    
    args = parser.parse_args()
    asyncio.run(test_main(args.new_reviews, args.clear_database))