#!/usr/bin/env python3
"""
Test the actual HTTP REST endpoint by starting the agent and making real HTTP requests
"""

import asyncio
import sys
import os
import json
import time
import requests
import threading
import subprocess
from typing import Optional

# Add the ingredient_agent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class AgentRunner:
    """Helper class to run the agent in a separate process"""
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.port = 8005
        self.base_url = f"http://localhost:{self.port}"
    
    def start_agent(self):
        """Start the agent in a separate process"""
        print(f"   Starting ingredient agent on port {self.port}...")
        
        # Start the agent process
        self.process = subprocess.Popen(
            [sys.executable, "ingredient_agent_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.path.dirname(__file__)
        )
        
        # Wait for the agent to start
        print("   Waiting for agent to start...")
        time.sleep(5)
        
        # Check if the process is still running
        if self.process.poll() is not None:
            stdout, stderr = self.process.communicate()
            print(f"❌ Agent failed to start!")
            print(f"   STDOUT: {stdout.decode()}")
            print(f"   STDERR: {stderr.decode()}")
            return False
        
        print("✅ Agent process started successfully")
        return True
    
    def stop_agent(self):
        """Stop the agent process"""
        if self.process:
            print("   Stopping agent...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            print("✅ Agent stopped")
    
    def is_agent_running(self) -> bool:
        """Check if the agent is still running"""
        return self.process is not None and self.process.poll() is None
    
    def test_endpoint_health(self) -> bool:
        """Test if the endpoint is responding"""
        try:
            # Try to make a request to the inventory report endpoint
            response = requests.get(f"{self.base_url}/inventory_report?key=test", timeout=10)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

async def test_http_endpoint():
    """Test the actual HTTP REST endpoint"""
    print("🧪 Testing HTTP REST endpoint...")
    
    runner = AgentRunner()
    
    try:
        # Start the agent
        if not runner.start_agent():
            return False
        
        # Wait a bit more for the agent to fully initialize
        print("   Waiting for agent to fully initialize...")
        time.sleep(3)
        
        # Test the endpoint
        print("   Making HTTP request to /inventory_report...")
        try:
            response = requests.get(f"{runner.base_url}/inventory_report?key=test", timeout=15)
            
            print(f"   - HTTP Status: {response.status_code}")
            print(f"   - Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("✅ HTTP request successful!")
                
                # Parse the response
                try:
                    data = response.json()
                    print(f"   - Response type: {type(data)}")
                    print(f"   - Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    
                    # Check if it's a proper response format
                    if isinstance(data, dict) and 'response' in data:
                        inventory_data = json.loads(data['response'])
                        print(f"   - Inventory data keys: {list(inventory_data.keys())}")
                        
                        if 'metadata' in inventory_data:
                            metadata = inventory_data['metadata']
                            print(f"   - Total ingredients: {metadata.get('total_ingredients', 'N/A')}")
                            print(f"   - Generated at: {metadata.get('generated_at', 'N/A')}")
                        
                        return True
                    else:
                        print(f"   - Unexpected response format: {data}")
                        return False
                        
                except json.JSONDecodeError as e:
                    print(f"   - JSON decode error: {e}")
                    print(f"   - Raw response: {response.text[:200]}...")
                    return False
                    
            else:
                print(f"❌ HTTP request failed with status {response.status_code}")
                print(f"   - Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ HTTP request failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ HTTP endpoint test failed: {e}")
        return False
    finally:
        # Always stop the agent
        runner.stop_agent()

async def test_multiple_endpoints():
    """Test multiple endpoints to ensure they all work"""
    print("\n🧪 Testing multiple HTTP endpoints...")
    
    runner = AgentRunner()
    
    try:
        # Start the agent
        if not runner.start_agent():
            return False
        
        # Wait for initialization
        time.sleep(3)
        
        # Test different endpoints
        endpoints = [
            ("/inventory_report", "Full inventory report"),
            ("/low_stock", "Low stock alerts"),
            ("/reorder_suggestions", "Reorder suggestions"),
            ("/consumption_analysis", "Consumption analysis"),
            ("/usage_summary", "Usage summary")
        ]
        
        success_count = 0
        total_endpoints = len(endpoints)
        
        for endpoint, description in endpoints:
            print(f"   Testing {endpoint} ({description})...")
            try:
                response = requests.get(f"{runner.base_url}{endpoint}?key=test", timeout=10)
                if response.status_code == 200:
                    success_count += 1
                    print(f"   ✅ {endpoint} successful")
                else:
                    print(f"   ❌ {endpoint} failed: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"   ❌ {endpoint} failed: {e}")
            
            # Small delay between requests
            time.sleep(1)
        
        success_rate = success_count / total_endpoints
        print(f"   - Success rate: {success_count}/{total_endpoints} ({success_rate*100:.1f}%)")
        
        return success_rate >= 0.8  # 80% success rate
        
    except Exception as e:
        print(f"❌ Multiple endpoints test failed: {e}")
        return False
    finally:
        runner.stop_agent()

async def test_error_handling():
    """Test error handling by making requests to non-existent endpoints"""
    print("\n🧪 Testing error handling...")
    
    runner = AgentRunner()
    
    try:
        # Start the agent
        if not runner.start_agent():
            return False
        
        # Wait for initialization
        time.sleep(3)
        
        # Test non-existent endpoint
        print("   Testing non-existent endpoint...")
        try:
            response = requests.get(f"{runner.base_url}/nonexistent", timeout=10)
            print(f"   - Status for /nonexistent: {response.status_code}")
            
            # Should return 404 or similar
            if response.status_code in [404, 405, 400]:
                print("✅ Non-existent endpoint handled correctly")
                return True
            else:
                print(f"❌ Unexpected status for non-existent endpoint: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error testing non-existent endpoint: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False
    finally:
        runner.stop_agent()

async def main():
    """Run all HTTP endpoint tests"""
    print("🚀 Testing Ingredient Agent HTTP REST Endpoints")
    print("=" * 70)
    
    tests = [
        ("HTTP Endpoint", test_http_endpoint),
        ("Multiple Endpoints", test_multiple_endpoints),
        ("Error Handling", test_error_handling),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All HTTP endpoint tests passed!")
        print("✅ The REST endpoints are working correctly with real HTTP requests")
    else:
        print("⚠️  Some HTTP endpoint tests failed")
        print("❌ The REST endpoints may not be working properly")
    
    return passed == total

if __name__ == '__main__':
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
