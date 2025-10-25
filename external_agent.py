"""
API Test Script for Restaurant Review Service
This script tests all the REST API endpoints to ensure they work correctly.
"""

import os
import asyncio
import requests
import logging
import time
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "default-api-key")

# Headers for API requests
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

class APITester:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
        self.test_results = []
    
    def make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make an API request and return the response"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.info(f"Making {method.upper()} request to {endpoint}")
            
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"✅ {method.upper()} {endpoint} - Status: {response.status_code}")
            return {"success": True, "data": result, "status_code": response.status_code}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ {method.upper()} {endpoint} - Request failed: {e}")
            return {"success": False, "error": str(e), "status_code": getattr(e.response, 'status_code', None)}
        except Exception as e:
            logger.error(f"❌ {method.upper()} {endpoint} - Unexpected error: {e}")
            return {"success": False, "error": str(e)}
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        logger.info("🔍 Testing root endpoint...")
        result = self.make_request("GET", "/")
        self.test_results.append(("GET /", result))
        return result
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        logger.info("🔍 Testing health endpoint...")
        result = self.make_request("GET", "/health")
        self.test_results.append(("GET /health", result))
        return result
    
    def test_trigger_pull(self):
        """Test the trigger pull endpoint"""
        logger.info("🔍 Testing trigger pull endpoint...")
        result = self.make_request("POST", "/api/trigger-pull")
        self.test_results.append(("POST /api/trigger-pull", result))
        return result
    
    def test_status_endpoint(self):
        """Test the status endpoint"""
        logger.info("🔍 Testing status endpoint...")
        result = self.make_request("GET", "/api/status")
        self.test_results.append(("GET /api/status", result))
        return result
    
    def test_analytics_endpoint(self):
        """Test the analytics endpoint"""
        logger.info("🔍 Testing analytics endpoint...")
        result = self.make_request("GET", "/api/analytics")
        self.test_results.append(("GET /api/analytics", result))
        return result
    
    def test_authentication(self):
        """Test authentication with invalid API key"""
        logger.info("🔍 Testing authentication (should fail)...")
        invalid_headers = {
            "X-API-Key": "invalid-key",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(f"{self.base_url}/api/status", headers=invalid_headers, timeout=30)
            if response.status_code == 401:
                logger.info("✅ Authentication test passed - correctly rejected invalid key")
                self.test_results.append(("Authentication Test", {"success": True, "message": "Correctly rejected invalid key"}))
            else:
                logger.error(f"❌ Authentication test failed - expected 401, got {response.status_code}")
                self.test_results.append(("Authentication Test", {"success": False, "message": f"Expected 401, got {response.status_code}"}))
        except Exception as e:
            logger.error(f"❌ Authentication test error: {e}")
            self.test_results.append(("Authentication Test", {"success": False, "error": str(e)}))
    
    async def test_full_workflow(self):
        """Test the complete workflow: trigger -> status -> analytics"""
        logger.info("🚀 Starting full workflow test...")
        
        # Step 1: Trigger review pull
        logger.info("Step 1: Triggering review pull...")
        trigger_result = self.test_trigger_pull()
        
        if not trigger_result.get("success"):
            logger.error("❌ Failed to trigger review pull, stopping workflow test")
            return False
        
        # Step 2: Monitor status
        logger.info("Step 2: Monitoring status...")
        max_checks = 10  # Reduced for testing
        check_count = 0
        
        while check_count < max_checks:
            logger.info(f"Status check {check_count + 1}/{max_checks}...")
            
            status_result = self.test_status_endpoint()
            
            if not status_result.get("success"):
                logger.error("❌ Status check failed")
                break
            
            # Check if processing is complete (simplified check)
            data = status_result.get("data", {})
            snapshots_status = data.get("snapshots_status", [])
            
            logger.info(f"Status: {data.get('total_reviews', 0)} total reviews, "
                       f"{data.get('processed_reviews', 0)} processed, "
                       f"{len(snapshots_status)} snapshots")
            
            # For testing, we'll just wait a bit and then proceed
            await asyncio.sleep(2)
            check_count += 1
        
        # Step 3: Get analytics
        logger.info("Step 3: Getting analytics...")
        analytics_result = self.test_analytics_endpoint()
        
        if analytics_result.get("success"):
            logger.info("✅ Full workflow test completed successfully")
            return True
        else:
            logger.error("❌ Analytics retrieval failed")
            return False
    
    def print_summary(self):
        """Print test results summary"""
        logger.info("\n" + "="*60)
        logger.info("📊 TEST RESULTS SUMMARY")
        logger.info("="*60)
        
        passed = 0
        failed = 0
        
        for endpoint, result in self.test_results:
            if result.get("success"):
                logger.info(f"✅ {endpoint} - PASSED")
                passed += 1
            else:
                logger.error(f"❌ {endpoint} - FAILED")
                if result.get("error"):
                    logger.error(f"   Error: {result['error']}")
                failed += 1
        
        logger.info("="*60)
        logger.info(f"Total: {passed + failed} | Passed: {passed} | Failed: {failed}")
        logger.info("="*60)
        
        return failed == 0

async def main():
    """Main test function"""
    logger.info("🧪 Starting Restaurant Review API Tests")
    logger.info(f"API Base URL: {API_BASE_URL}")
    logger.info(f"API Key: {'*' * len(API_KEY) if API_KEY else 'Not set'}")
    logger.info("-" * 60)
    
    tester = APITester(API_BASE_URL, API_KEY)
    
    # Test individual endpoints
    logger.info("🔍 Testing individual endpoints...")
    tester.test_root_endpoint()
    tester.test_health_endpoint()
    tester.test_status_endpoint()
    tester.test_analytics_endpoint()
    tester.test_authentication()
    
    # Test trigger pull (this will start background processing)
    logger.info("\n🔍 Testing trigger pull...")
    tester.test_trigger_pull()
    
    # Wait a moment for processing to start
    logger.info("⏳ Waiting 5 seconds for processing to start...")
    await asyncio.sleep(5)
    
    # Test full workflow
    logger.info("\n🚀 Testing full workflow...")
    await tester.test_full_workflow()
    
    # Print summary
    all_passed = tester.print_summary()
    
    if all_passed:
        logger.info("🎉 All tests passed! API is working correctly.")
    else:
        logger.error("💥 Some tests failed. Check the logs above for details.")
    
    return all_passed

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⏹️  Tests interrupted by user")
        exit(1)
    except Exception as e:
        logger.error(f"💥 Test script error: {e}")
        exit(1)
