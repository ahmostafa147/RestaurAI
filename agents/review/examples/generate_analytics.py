#!/usr/bin/env python3
"""
Example script for generating analytics from processed reviews
"""
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import RestaurantReviewAgent

def main():
    """Generate analytics report from processed reviews"""
    print("Restaurant Analytics Generator")
    print("=" * 40)
    
    # Initialize agent
    database_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'database.json')
    agent = RestaurantReviewAgent(database_path)

    # Generate full analytics report
    print("Generating analytics report...")
    report_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'analytics_report.json')
    report = agent.generate_analytics(output_path=report_path)
    
    # Print summary
    metadata = report.get('metadata', {})
    basic_metrics = report.get('basic_metrics', {})
    overall_perf = basic_metrics.get('overall_performance', {})
    
    print(f"\n📊 Analytics Summary:")
    print(f"Total reviews analyzed: {metadata.get('processed_reviews', 0)}")
    print(f"Processing coverage: {metadata.get('processing_coverage', 0)}%")
    print(f"Average rating: {overall_perf.get('average_rating', 0):.2f}")
    print(f"Review velocity: {overall_perf.get('review_velocity', 0):.2f} reviews/week")
    
    # Menu analytics summary
    menu_analytics = report.get('menu_analytics', {})
    items = menu_analytics.get('items', [])
    print(f"Menu items mentioned: {len(items)}")
    
    if items:
        print(f"Top mentioned item: {items[0]['name']} ({items[0]['mention_count']} mentions)")
    
    # Staff analytics summary
    staff_analytics = report.get('staff_analytics', {})
    staff_by_person = staff_analytics.get('by_person', [])
    print(f"Staff members mentioned: {len(staff_by_person)}")
    
    if staff_by_person:
        print(f"Most mentioned staff: {staff_by_person[0]['name']} ({staff_by_person[0]['mention_count']} mentions)")
    
    # Customer insights summary
    customer_insights = report.get('customer_insights', {})
    segmentation = customer_insights.get('segmentation', {})
    segments = segmentation.get('segments', {})
    print(f"Customer segments identified: {len(segments)}")
    
    # Reputation insights summary
    reputation = report.get('reputation_insights', {})
    anomaly_flags = reputation.get('anomaly_flags', {})
    print(f"Potential fake reviews: {anomaly_flags.get('potential_fake', 0)}")
    print(f"Health/safety concerns: {anomaly_flags.get('health_safety_concern', 0)}")
    
    print(f"\n✅ Full report exported to: {report_path}")
    print(f"📈 Report contains {len(report)} main sections with detailed metrics")

if __name__ == "__main__":
    main()
