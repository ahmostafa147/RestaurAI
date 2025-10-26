"""
Unit tests for StaffManager
"""

import sys
import os
import unittest
from datetime import datetime, date

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.src.core.staff_manager import StaffManager
from backend.src.models.staff import StaffMember, Shift


class TestStaffManager(unittest.TestCase):
    """Test cases for StaffManager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_restaurant_key = "test-restaurant-key"
        self.staff_manager = StaffManager(self.test_restaurant_key)
        
        # Clear any existing staff data
        self.staff_manager.staff = {}
        self.staff_manager._name_to_id = {}
        self.staff_manager.absences = {}
    
    def tearDown(self):
        """Clean up after tests"""
        # Clear test data
        self.staff_manager.staff = {}
        self.staff_manager._name_to_id = {}
        self.staff_manager.absences = {}
    
    def test_add_staff_member(self):
        """Test adding a staff member"""
        staff_data = {
            "id": 1,
            "name": "John Doe",
            "role": "Chef - 5 years experience",
            "shifts": [
                {"day_of_week": "Monday", "start_time": "09:00", "end_time": "17:00"},
                {"day_of_week": "Tuesday", "start_time": "09:00", "end_time": "17:00"}
            ],
            "status": "active",
            "contact_info": "john@restaurant.com"
        }
        
        staff_member = StaffMember.from_dict(staff_data)
        result = self.staff_manager.add_staff_member(staff_member)
        
        self.assertTrue(result)
        self.assertEqual(len(self.staff_manager.staff), 1)
        self.assertIn(1, self.staff_manager.staff)
        self.assertEqual(self.staff_manager.staff[1].name, "John Doe")
    
    def test_get_staff_member(self):
        """Test retrieving a staff member by ID"""
        # Add a staff member first
        staff_data = {
            "id": 1,
            "name": "Jane Smith",
            "role": "Server - 3 years experience",
            "shifts": [{"day_of_week": "Monday", "start_time": "10:00", "end_time": "18:00"}],
            "status": "active"
        }
        staff_member = StaffMember.from_dict(staff_data)
        self.staff_manager.add_staff_member(staff_member)
        
        # Test retrieval
        retrieved = self.staff_manager.get_staff_member(1)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Jane Smith")
        
        # Test non-existent staff
        non_existent = self.staff_manager.get_staff_member(999)
        self.assertIsNone(non_existent)
    
    def test_get_staff_by_name(self):
        """Test retrieving a staff member by name"""
        # Add a staff member first
        staff_data = {
            "id": 1,
            "name": "Alice Johnson",
            "role": "Manager - 8 years experience",
            "shifts": [{"day_of_week": "Monday", "start_time": "08:00", "end_time": "20:00"}],
            "status": "active"
        }
        staff_member = StaffMember.from_dict(staff_data)
        self.staff_manager.add_staff_member(staff_member)
        
        # Test retrieval
        retrieved = self.staff_manager.get_staff_by_name("Alice Johnson")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, 1)
        
        # Test non-existent staff
        non_existent = self.staff_manager.get_staff_by_name("Bob Wilson")
        self.assertIsNone(non_existent)
    
    def test_get_staff_by_role(self):
        """Test retrieving staff members by role"""
        # Add multiple staff members with different roles
        chef_data = {
            "id": 1,
            "name": "Chef Mike",
            "role": "Head Chef - 10 years experience",
            "shifts": [{"day_of_week": "Monday", "start_time": "09:00", "end_time": "17:00"}],
            "status": "active"
        }
        server_data = {
            "id": 2,
            "name": "Server Sarah",
            "role": "Server - 2 years experience",
            "shifts": [{"day_of_week": "Monday", "start_time": "10:00", "end_time": "18:00"}],
            "status": "active"
        }
        
        self.staff_manager.add_staff_member(StaffMember.from_dict(chef_data))
        self.staff_manager.add_staff_member(StaffMember.from_dict(server_data))
        
        # Test role-based retrieval
        chefs = self.staff_manager.get_staff_by_role("chef")
        self.assertEqual(len(chefs), 1)
        self.assertEqual(chefs[0].name, "Chef Mike")
        
        servers = self.staff_manager.get_staff_by_role("server")
        self.assertEqual(len(servers), 1)
        self.assertEqual(servers[0].name, "Server Sarah")
    
    def test_remove_staff_member(self):
        """Test removing a staff member"""
        # Add a staff member first
        staff_data = {
            "id": 1,
            "name": "Bob Wilson",
            "role": "Bartender - 4 years experience",
            "shifts": [{"day_of_week": "Friday", "start_time": "18:00", "end_time": "02:00"}],
            "status": "active"
        }
        staff_member = StaffMember.from_dict(staff_data)
        self.staff_manager.add_staff_member(staff_member)
        
        # Verify staff was added
        self.assertEqual(len(self.staff_manager.staff), 1)
        
        # Remove staff member
        result = self.staff_manager.remove_staff_member(1)
        self.assertTrue(result)
        self.assertEqual(len(self.staff_manager.staff), 0)
        
        # Try to remove non-existent staff
        result = self.staff_manager.remove_staff_member(999)
        self.assertFalse(result)
    
    def test_get_available_staff(self):
        """Test getting available staff for a specific day and time"""
        # Add staff members with different schedules
        monday_staff = {
            "id": 1,
            "name": "Monday Worker",
            "role": "Server - works Mondays",
            "shifts": [{"day_of_week": "Monday", "start_time": "10:00", "end_time": "18:00"}],
            "status": "active"
        }
        tuesday_staff = {
            "id": 2,
            "name": "Tuesday Worker",
            "role": "Chef - works Tuesdays",
            "shifts": [{"day_of_week": "Tuesday", "start_time": "09:00", "end_time": "17:00"}],
            "status": "active"
        }
        
        self.staff_manager.add_staff_member(StaffMember.from_dict(monday_staff))
        self.staff_manager.add_staff_member(StaffMember.from_dict(tuesday_staff))
        
        # Test Monday availability
        monday_available = self.staff_manager.get_available_staff("Monday")
        self.assertEqual(len(monday_available), 1)
        self.assertEqual(monday_available[0].name, "Monday Worker")
        
        # Test Tuesday availability
        tuesday_available = self.staff_manager.get_available_staff("Tuesday")
        self.assertEqual(len(tuesday_available), 1)
        self.assertEqual(tuesday_available[0].name, "Tuesday Worker")
        
        # Test Wednesday (no staff)
        wednesday_available = self.staff_manager.get_available_staff("Wednesday")
        self.assertEqual(len(wednesday_available), 0)
    
    def test_mark_absent(self):
        """Test marking staff as absent"""
        # Add a staff member first
        staff_data = {
            "id": 1,
            "name": "Test Staff",
            "role": "Server - test role",
            "shifts": [{"day_of_week": "Monday", "start_time": "10:00", "end_time": "18:00"}],
            "status": "active"
        }
        staff_member = StaffMember.from_dict(staff_data)
        self.staff_manager.add_staff_member(staff_member)
        
        # Mark as absent
        today = date.today().isoformat()
        result = self.staff_manager.mark_absent(1, today)
        self.assertTrue(result)
        
        # Verify absence was recorded
        self.assertIn(today, self.staff_manager.absences)
        self.assertIn(1, self.staff_manager.absences[today])
        
        # Test marking non-existent staff as absent
        result = self.staff_manager.mark_absent(999, today)
        self.assertFalse(result)
    
    def test_clear_absence(self):
        """Test clearing staff absence"""
        # Add a staff member and mark as absent
        staff_data = {
            "id": 1,
            "name": "Test Staff",
            "role": "Server - test role",
            "shifts": [{"day_of_week": "Monday", "start_time": "10:00", "end_time": "18:00"}],
            "status": "active"
        }
        staff_member = StaffMember.from_dict(staff_data)
        self.staff_manager.add_staff_member(staff_member)
        
        today = date.today().isoformat()
        self.staff_manager.mark_absent(1, today)
        
        # Clear absence
        result = self.staff_manager.clear_absence(1, today)
        self.assertTrue(result)
        
        # Verify absence was cleared
        if today in self.staff_manager.absences:
            self.assertNotIn(1, self.staff_manager.absences[today])
        else:
            # Date key was removed because it became empty - this is correct behavior
            pass
    
    def test_get_schedule_for_day(self):
        """Test getting schedule for a specific day"""
        # Add staff members with Monday shifts
        staff1_data = {
            "id": 1,
            "name": "Morning Staff",
            "role": "Chef - morning shift",
            "shifts": [{"day_of_week": "Monday", "start_time": "06:00", "end_time": "14:00"}],
            "status": "active"
        }
        staff2_data = {
            "id": 2,
            "name": "Evening Staff",
            "role": "Server - evening shift",
            "shifts": [{"day_of_week": "Monday", "start_time": "14:00", "end_time": "22:00"}],
            "status": "active"
        }
        
        self.staff_manager.add_staff_member(StaffMember.from_dict(staff1_data))
        self.staff_manager.add_staff_member(StaffMember.from_dict(staff2_data))
        
        # Get Monday schedule
        monday_schedule = self.staff_manager.get_schedule_for_day("Monday")
        self.assertEqual(len(monday_schedule), 2)
        
        # Verify schedule details
        names = [shift["staff_name"] for shift in monday_schedule]
        self.assertIn("Morning Staff", names)
        self.assertIn("Evening Staff", names)
    
    def test_get_staff_utilization(self):
        """Test getting staff utilization metrics"""
        # Add multiple staff members
        staff1_data = {
            "id": 1,
            "name": "Full Time Staff",
            "role": "Chef - full time",
            "shifts": [
                {"day_of_week": "Monday", "start_time": "09:00", "end_time": "17:00"},
                {"day_of_week": "Tuesday", "start_time": "09:00", "end_time": "17:00"},
                {"day_of_week": "Wednesday", "start_time": "09:00", "end_time": "17:00"},
                {"day_of_week": "Thursday", "start_time": "09:00", "end_time": "17:00"},
                {"day_of_week": "Friday", "start_time": "09:00", "end_time": "17:00"}
            ],
            "status": "active"
        }
        staff2_data = {
            "id": 2,
            "name": "Part Time Staff",
            "role": "Server - part time",
            "shifts": [
                {"day_of_week": "Saturday", "start_time": "10:00", "end_time": "18:00"},
                {"day_of_week": "Sunday", "start_time": "10:00", "end_time": "18:00"}
            ],
            "status": "active"
        }
        
        self.staff_manager.add_staff_member(StaffMember.from_dict(staff1_data))
        self.staff_manager.add_staff_member(StaffMember.from_dict(staff2_data))
        
        # Get utilization metrics
        utilization = self.staff_manager.get_staff_utilization()
        
        self.assertEqual(utilization["total_staff"], 2)
        self.assertEqual(utilization["active_staff"], 2)
        self.assertEqual(utilization["total_shifts"], 7)  # 5 + 2 shifts
        self.assertAlmostEqual(utilization["avg_shifts_per_staff"], 3.5, places=1)


if __name__ == '__main__':
    unittest.main()
