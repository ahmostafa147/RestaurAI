"""
HTTP endpoint tests for staff agent server
"""

import sys
import os
import unittest
import json
import requests
from unittest.mock import patch, MagicMock

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from agents.staff.staff_agent_server import (
    get_restaurant_by_secure_key,
    get_restaurant_by_id,
    get_available_restaurants
)


class TestStaffAgentHTTPEndpoints(unittest.TestCase):
    """Test cases for staff agent HTTP endpoints"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.base_url = "http://localhost:8005"
        self.test_secure_key = "113b9b80-dda7-41e1-b6d1-f1d7428950c3"  # Causwells
        self.test_secure_key2 = "d648f285-a940-4101-a013-97d994cdf18e"  # Cote Ouest
        self.invalid_secure_key = "invalid-key-12345"
    
    def test_get_restaurant_by_secure_key(self):
        """Test restaurant lookup by secure key"""
        # Test valid secure key
        restaurant = get_restaurant_by_secure_key(self.test_secure_key)
        self.assertIsNotNone(restaurant)
        self.assertEqual(restaurant["id"], "causwells-sf")
        self.assertEqual(restaurant["name"], "Causwells")
        
        # Test invalid secure key
        invalid_restaurant = get_restaurant_by_secure_key(self.invalid_secure_key)
        self.assertIsNone(invalid_restaurant)
    
    def test_get_restaurant_by_id(self):
        """Test restaurant lookup by ID"""
        # Test valid restaurant ID
        restaurant = get_restaurant_by_id("causwells-sf")
        self.assertIsNotNone(restaurant)
        self.assertEqual(restaurant["secure_key"], self.test_secure_key)
        
        # Test invalid restaurant ID
        invalid_restaurant = get_restaurant_by_id("invalid-restaurant")
        self.assertIsNone(invalid_restaurant)
    
    def test_get_available_restaurants(self):
        """Test getting list of available restaurants"""
        restaurants = get_available_restaurants()
        
        self.assertIsInstance(restaurants, list)
        self.assertEqual(len(restaurants), 2)
        
        # Check restaurant IDs
        restaurant_ids = [r["id"] for r in restaurants]
        self.assertIn("causwells-sf", restaurant_ids)
        self.assertIn("cote-ouest-bistro-sf", restaurant_ids)
        
        # Check restaurant names
        restaurant_names = [r["name"] for r in restaurants]
        self.assertIn("Causwells", restaurant_names)
        self.assertIn("Cote Ouest Bistro", restaurant_names)
    
    @patch('requests.get')
    def test_schedule_report_endpoint(self, mock_get):
        """Test schedule report endpoint"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": json.dumps({
                "restaurant_id": "causwells-sf",
                "restaurant_name": "Causwells",
                "analytics": {
                    "metadata": {"generated_at": "2024-01-01T00:00:00"},
                    "overall_coverage_score": 0.85,
                    "weaknesses": {"understaffed_slots": []}
                }
            })
        }
        mock_get.return_value = mock_response
        
        # Test endpoint call
        response = requests.get(f"{self.base_url}/schedule_report", 
                               params={"secure_key": self.test_secure_key})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("response", data)
        
        # Parse the nested JSON response
        inner_data = json.loads(data["response"])
        self.assertIn("restaurant_id", inner_data)
        self.assertEqual(inner_data["restaurant_id"], "causwells-sf")
    
    @patch('requests.get')
    def test_weaknesses_endpoint(self, mock_get):
        """Test weaknesses endpoint"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": json.dumps({
                "metadata": {"generated_at": "2024-01-01T00:00:00"},
                "overall_coverage_score": 0.75,
                "understaffed_slots": [
                    {"day": "Friday", "time": "18:00-22:00", "staff_count": 1}
                ]
            })
        }
        mock_get.return_value = mock_response
        
        # Test endpoint call
        response = requests.get(f"{self.base_url}/weaknesses", 
                               params={"secure_key": self.test_secure_key})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("response", data)
        
        # Parse the nested JSON response
        inner_data = json.loads(data["response"])
        self.assertIn("overall_coverage_score", inner_data)
        self.assertIn("understaffed_slots", inner_data)
    
    @patch('requests.get')
    def test_handle_absence_endpoint(self, mock_get):
        """Test handle absence endpoint"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": json.dumps({
                "metadata": {"generated_at": "2024-01-01T00:00:00"},
                "absent_staff": {"staff_id": 1, "name": "John Doe"},
                "suggested_replacements": [
                    {"name": "Jane Smith", "compatibility_score": 0.9}
                ]
            })
        }
        mock_get.return_value = mock_response
        
        # Test endpoint call
        response = requests.get(f"{self.base_url}/handle_absence", 
                               params={
                                   "secure_key": self.test_secure_key,
                                   "staff_id": 1,
                                   "date": "2024-01-01"
                               })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("response", data)
        
        # Parse the nested JSON response
        inner_data = json.loads(data["response"])
        self.assertIn("absent_staff", inner_data)
        self.assertIn("suggested_replacements", inner_data)
    
    @patch('requests.get')
    def test_coverage_metrics_endpoint(self, mock_get):
        """Test coverage metrics endpoint"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": json.dumps({
                "metadata": {"generated_at": "2024-01-01T00:00:00"},
                "coverage_summary": {
                    "total_time_slots": 35,
                    "understaffed_slots": 2,
                    "coverage_percentage": 94.3
                }
            })
        }
        mock_get.return_value = mock_response
        
        # Test endpoint call
        response = requests.get(f"{self.base_url}/coverage_metrics", 
                               params={"secure_key": self.test_secure_key})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("response", data)
        
        # Parse the nested JSON response
        inner_data = json.loads(data["response"])
        self.assertIn("coverage_summary", inner_data)
        self.assertIn("coverage_percentage", inner_data["coverage_summary"])
    
    @patch('requests.get')
    def test_utilization_endpoint(self, mock_get):
        """Test utilization endpoint"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": json.dumps([
                {
                    "staff_id": 1,
                    "staff_name": "John Doe",
                    "role": "Chef",
                    "weekly_hours": 45.0,
                    "is_overworked": True
                }
            ])
        }
        mock_get.return_value = mock_response
        
        # Test endpoint call
        response = requests.get(f"{self.base_url}/utilization", 
                               params={"secure_key": self.test_secure_key})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("response", data)
        
        # Parse the nested JSON response
        inner_data = json.loads(data["response"])
        self.assertIsInstance(inner_data, list)
        if inner_data:
            self.assertIn("staff_id", inner_data[0])
            self.assertIn("weekly_hours", inner_data[0])
    
    @patch('requests.get')
    def test_optimization_endpoint(self, mock_get):
        """Test optimization endpoint"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": json.dumps({
                "recommendations": "Consider redistributing shifts to reduce overwork..."
            })
        }
        mock_get.return_value = mock_response
        
        # Test endpoint call
        response = requests.get(f"{self.base_url}/optimization", 
                               params={"secure_key": self.test_secure_key})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("response", data)
        
        # Parse the nested JSON response
        inner_data = json.loads(data["response"])
        self.assertIn("recommendations", inner_data)
    
    @patch('requests.get')
    def test_error_handling_missing_secure_key(self, mock_get):
        """Test error handling for missing secure_key parameter"""
        # Mock error response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": json.dumps({"error": "secure_key parameter is required"})
        }
        mock_get.return_value = mock_response
        
        # Test endpoint call without secure_key
        response = requests.get(f"{self.base_url}/schedule_report")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        inner_data = json.loads(data["response"])
        self.assertIn("error", inner_data)
        self.assertEqual(inner_data["error"], "secure_key parameter is required")
    
    @patch('requests.get')
    def test_error_handling_invalid_secure_key(self, mock_get):
        """Test error handling for invalid secure_key"""
        # Mock error response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": json.dumps({"error": "Invalid secure_key"})
        }
        mock_get.return_value = mock_response
        
        # Test endpoint call with invalid secure_key
        response = requests.get(f"{self.base_url}/schedule_report", 
                               params={"secure_key": self.invalid_secure_key})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        inner_data = json.loads(data["response"])
        self.assertIn("error", inner_data)
        self.assertEqual(inner_data["error"], "Invalid secure_key")
    
    @patch('requests.get')
    def test_error_handling_missing_staff_id(self, mock_get):
        """Test error handling for missing staff_id parameter in absence endpoint"""
        # Mock error response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": json.dumps({"error": "staff_id parameter is required"})
        }
        mock_get.return_value = mock_response
        
        # Test endpoint call without staff_id
        response = requests.get(f"{self.base_url}/handle_absence", 
                               params={"secure_key": self.test_secure_key})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        inner_data = json.loads(data["response"])
        self.assertIn("error", inner_data)
        self.assertEqual(inner_data["error"], "staff_id parameter is required")


if __name__ == '__main__':
    unittest.main()
