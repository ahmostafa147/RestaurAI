#!/usr/bin/env python3
"""
Test script for LLM wrapper with real API integration
"""

import os
import sys

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, use environment variables directly
    pass

def test_llm_wrapper():
    """Test LLM wrapper with real API"""
    
    # Check if API key is available
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not found in environment variables")
        print("Please set your API key in .env file or environment variables")
        return False
    
    print("Testing LLM Wrapper with Real API")
    print("=" * 50)
    
    try:
        # Import the wrapper
        from src.eval.llm_wrapper import ClaudeWrapper, LLMResponse
        from src.eval.models.extended_review import ReviewExtraction
        
        # Initialize wrapper
        print("1. Initializing Claude wrapper...")
        wrapper = ClaudeWrapper(api_key=api_key)
        print("PASSED: Wrapper initialized successfully")
        
        # Test review extraction
        print("\n2. Testing review extraction...")
        sample_review = """
        Great food and excellent service! The pasta was amazing and our server Sarah was very attentive. 
        Will definitely come back. The ambiance was perfect for a date night.
        """
        
        sample_metadata = {
            'rating': 4.5,
            'source': 'google',
            'review_date': '2024-01-15',
            'author_name': 'Test User'
        }
        
        response = wrapper.extract_review_data(sample_review, sample_metadata)
        
        if response.success:
            print("PASSED: Review extraction successful")
            print(f"   Input tokens: {response.usage['input_tokens']}")
            print(f"   Output tokens: {response.usage['output_tokens']}")
            print(f"   Total tokens: {response.usage['input_tokens'] + response.usage['output_tokens']}")
        else:
            print(f"FAILED: Review extraction failed: {response.error}")
            return False
        
        # Test response parsing
        print("\n3. Testing response parsing...")
        extraction = wrapper.parse_extraction_response(response)
        
        if extraction:
            print("PASSED: Response parsing successful")
            print(f"   Overall sentiment: {extraction.overall_sentiment}")
            
            if extraction.rating_breakdown:
                print("   Rating breakdown:")
                if extraction.rating_breakdown.food:
                    print(f"     Food: {extraction.rating_breakdown.food}/5")
                if extraction.rating_breakdown.service:
                    print(f"     Service: {extraction.rating_breakdown.service}/5")
            
            if extraction.mentioned_items:
                print(f"   Mentioned items: {len(extraction.mentioned_items)}")
                for item in extraction.mentioned_items[:2]:  # Show first 2
                    print(f"     - {item.name} ({item.sentiment})")
            
            if extraction.staff_mentions:
                print(f"   Staff mentions: {len(extraction.staff_mentions)}")
                for staff in extraction.staff_mentions:
                    print(f"     - {staff.role}: {staff.name or 'Unknown'} ({staff.sentiment})")
            
            if extraction.operational_insights:
                print("   Operational insights:")
                print(f"     Wait time: {extraction.operational_insights.wait_time}")
                print(f"     Cleanliness: {extraction.operational_insights.cleanliness}")
            
            if extraction.visit_context:
                print("   Visit context:")
                print(f"     Party type: {extraction.visit_context.party_type}")
                print(f"     Occasion: {extraction.visit_context.occasion}")
                print(f"     Time: {extraction.visit_context.time_of_visit}")
            
            if extraction.key_phrases:
                if extraction.key_phrases.positive_highlights:
                    print(f"   Positive highlights: {extraction.key_phrases.positive_highlights}")
                if extraction.key_phrases.negative_issues:
                    print(f"   Negative issues: {extraction.key_phrases.negative_issues}")
            
            if extraction.anomaly_flags:
                print("   Anomaly flags:")
                print(f"     Potential fake: {extraction.anomaly_flags.potential_fake}")
                print(f"     Health concern: {extraction.anomaly_flags.health_safety_concern}")
        else:
            print("WARNING: Response parsing failed - API response format not compatible")
            print("   Raw response preview:")
            print(f"   {response.content[:200]}...")
        
        # Test usage statistics
        print("\n4. Testing usage statistics...")
        stats = wrapper.get_usage_stats([response])
        print(f"PASSED: Usage stats calculated:")
        print(f"   Total tokens: {stats['total_tokens']}")
        print(f"   Successful requests: {stats['successful_requests']}")
        print(f"   Failed requests: {stats['failed_requests']}")
        
        print("\nSUCCESS: All tests passed! LLM wrapper is working correctly.")
        return True
        
    except ImportError as e:
        print(f"FAILED: Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("  pip install anthropic pydantic python-dotenv")
        return False
    except Exception as e:
        print(f"FAILED: Unexpected error: {e}")
        return False

def main():
    """Main test function"""
    success = test_llm_wrapper()
    
    if success:
        print("\nSUCCESS: LLM Wrapper test completed successfully!")
        print("The wrapper is ready for production use.")
    else:
        print("\nFAILED: LLM Wrapper test failed!")
        print("Please check your API key and dependencies.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
