#!/usr/bin/env python3
"""
Test the actual HTTP REST endpoint by starting the menu agent and making real HTTP requests
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

# Add the menu_agent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class MenuAgentRunner:
    """Helper class to run the menu agent in a separate process"""
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.port = 8006
        self.base_url = f"http://localhost:{self.port}"
    
    def start_agent(self):
        """Start the menu agent in a separate process"""
        print(f"   Starting menu agent on port {self.port}...")
        
        # Start the agent process
        self.process = subprocess.Popen(
            [sys.executable, "menu_agent_server.py"],
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
            print(f"ERROR: Menu agent failed to start!")
            print(f"   STDOUT: {stdout.decode()}")
            print(f"   STDERR: {stderr.decode()}")
            return False
        
        print("SUCCESS: Menu agent process started successfully")
        return True
    
    def stop_agent(self):
        """Stop the menu agent process"""
        if self.process:
            print("   Stopping menu agent...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            print("SUCCESS: Menu agent stopped")
    
    def is_agent_running(self) -> bool:
        """Check if the menu agent is still running"""
        return self.process is not None and self.process.poll() is None
    
    def test_endpoint_health(self) -> bool:
        """Test if the endpoint is responding"""
        try:
            # Try to make a request to the menu analytics endpoint
            response = requests.get(f"{self.base_url}/menu_analytics", timeout=10)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

async def test_menu_analytics_endpoint():
    """Test the main menu analytics endpoint"""
    print("Testing menu analytics HTTP endpoint...")
    
    runner = MenuAgentRunner()
    
    try:
        # Start the agent
        if not runner.start_agent():
            return False
        
        # Wait a bit more for the agent to fully initialize
        print("   Waiting for menu agent to fully initialize...")
        time.sleep(3)
        
        # Test the endpoint
        print("   Making HTTP request to /menu_analytics...")
        try:
            response = requests.get(f"{runner.base_url}/menu_analytics", timeout=15)
            
            print(f"   - HTTP Status: {response.status_code}")
            print(f"   - Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("SUCCESS: HTTP request successful!")
                
                # Parse the response
                try:
                    data = response.json()
                    print(f"   - Response type: {type(data)}")
                    print(f"   - Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    
                    # Check if it's a proper response format
                    if isinstance(data, dict) and 'response' in data:
                        menu_data = json.loads(data['response'])
                        print(f"   - Menu analytics data keys: {list(menu_data.keys())}")
                        
                        if 'metadata' in menu_data:
                            metadata = menu_data['metadata']
                            print(f"   - Restaurant key: {metadata.get('restaurant_key', 'N/A')}")
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
                print(f"ERROR: HTTP request failed with status {response.status_code}")
                print(f"   - Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"ERROR: HTTP request failed: {e}")
            return False
            
    except Exception as e:
        print(f"ERROR: Menu analytics endpoint test failed: {e}")
        return False
    finally:
        # Always stop the agent
        runner.stop_agent()

async def test_multiple_menu_endpoints():
    """Test multiple menu endpoints to ensure they all work"""
    print("\nTEST: Testing multiple menu HTTP endpoints...")
    
    runner = MenuAgentRunner()
    
    try:
        # Start the agent
        if not runner.start_agent():
            return False
        
        # Wait for initialization
        time.sleep(3)
        
        # Test different endpoints
        endpoints = [
            ("/menu_analytics", "Full menu analytics report"),
            ("/menu_performance", "Menu performance metrics"),
            ("/popular_items", "Popular menu items analysis"),
            ("/profit_analysis", "Profit analysis"),
            ("/menu_recommendations", "Menu recommendations"),
            ("/revenue_analysis", "Revenue analysis"),
            ("/available_reports", "Available reports list")
        ]
        
        success_count = 0
        total_endpoints = len(endpoints)
        
        for endpoint, description in endpoints:
            print(f"   Testing {endpoint} ({description})...")
            try:
                response = requests.get(f"{runner.base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    success_count += 1
                    print(f"   SUCCESS: {endpoint} successful")
                    
                    # Try to parse JSON response
                    try:
                        data = response.json()
                        if isinstance(data, dict) and 'response' in data:
                            print(f"   - Response contains data")
                        else:
                            print(f"   - Response format: {type(data)}")
                    except json.JSONDecodeError:
                        print(f"   - Non-JSON response")
                        
                else:
                    print(f"   ERROR: {endpoint} failed: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"   ERROR: {endpoint} failed: {e}")
            
            # Small delay between requests
            time.sleep(1)
        
        success_rate = success_count / total_endpoints
        print(f"   - Success rate: {success_count}/{total_endpoints} ({success_rate*100:.1f}%)")
        
        return success_rate >= 0.8  # 80% success rate
        
    except Exception as e:
        print(f"ERROR: Multiple menu endpoints test failed: {e}")
        return False
    finally:
        runner.stop_agent()

async def test_menu_error_handling():
    """Test error handling by making requests to non-existent endpoints"""
    print("\nTEST: Testing menu agent error handling...")
    
    runner = MenuAgentRunner()
    
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
                print("SUCCESS: Non-existent endpoint handled correctly")
                return True
            else:
                print(f"ERROR: Unexpected status for non-existent endpoint: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Error testing non-existent endpoint: {e}")
            return False
            
    except Exception as e:
        print(f"ERROR: Menu error handling test failed: {e}")
        return False
    finally:
        runner.stop_agent()

async def test_menu_data_validation():
    """Test that menu endpoints return valid data structures"""
    print("\nTEST: Testing menu data validation...")
    
    runner = MenuAgentRunner()
    
    try:
        # Start the agent
        if not runner.start_agent():
            return False
        
        # Wait for initialization
        time.sleep(3)
        
        # Test menu analytics endpoint for data structure
        print("   Testing menu analytics data structure...")
        try:
            response = requests.get(f"{runner.base_url}/menu_analytics", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'response' in data:
                    menu_data = json.loads(data['response'])
                    
                    # Check for expected structure
                    expected_keys = ['metadata', 'summary_metrics', 'item_analytics']
                    found_keys = [key for key in expected_keys if key in menu_data]
                    
                    print(f"   - Found expected keys: {found_keys}")
                    
                    if len(found_keys) >= 2:  # At least metadata and one other section
                        print("SUCCESS: Menu data structure validation passed")
                        return True
                    else:
                        print(f"ERROR: Missing expected data sections: {set(expected_keys) - set(found_keys)}")
                        return False
                else:
                    print("ERROR: Invalid response format")
                    return False
            else:
                print(f"ERROR: Request failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"ERROR: Data validation test failed: {e}")
            return False
            
    except Exception as e:
        print(f"ERROR: Menu data validation test failed: {e}")
        return False
    finally:
        runner.stop_agent()

async def main():
    """Run all menu agent HTTP endpoint tests"""
    print("Testing Menu Agent HTTP REST Endpoints")
    print("=" * 70)
    
    tests = [
        ("Menu Analytics Endpoint", test_menu_analytics_endpoint),
        ("Multiple Menu Endpoints", test_multiple_menu_endpoints),
        ("Error Handling", test_menu_error_handling),
        ("Data Validation", test_menu_data_validation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"ERROR: {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY: SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "SUCCESS: PASS" if result else "ERROR: FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: All menu agent HTTP endpoint tests passed!")
        print("SUCCESS: The menu REST endpoints are working correctly with real HTTP requests")
    else:
        print("WARNING:  Some menu agent HTTP endpoint tests failed")
        print("ERROR: The menu REST endpoints may not be working properly")
    
    return passed == total

if __name__ == '__main__':
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
