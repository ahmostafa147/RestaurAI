"""
Mock data generation for staff testing
"""

import sys
import os
import json
from typing import Dict, List, Any
from datetime import datetime, timedelta

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.src.models.staff import StaffMember, Shift
from backend.src.core.restaurant import Restaurant


def generate_mock_staff_data():
    """Generate realistic mock staff data for both restaurants"""
    
    # Load restaurant configurations
    restaurants_file = os.path.join(os.path.dirname(__file__), '..', 'restaurants.json')
    with open(restaurants_file, 'r') as f:
        config = json.load(f)
        restaurants = config.get('restaurants', [])
    
    for restaurant in restaurants:
        restaurant_id = restaurant['id']
        secure_key = restaurant['secure_key']
        restaurant_name = restaurant['name']
        
        print(f"Generating mock staff data for {restaurant_name} ({restaurant_id})")
        
        # Create restaurant instance
        restaurant_instance = Restaurant(key=secure_key)
        
        # Generate staff based on restaurant type
        if "causwells" in restaurant_id.lower():
            staff_members = generate_causwells_staff()
        elif "cote" in restaurant_id.lower():
            staff_members = generate_cote_ouest_staff()
        else:
            staff_members = generate_generic_staff()
        
        # Add staff to restaurant
        for staff_data in staff_members:
            success = restaurant_instance.add_staff_member(staff_data)
            if success:
                print(f"  Added {staff_data['name']} ({staff_data['role']})")
            else:
                print(f"  Failed to add {staff_data['name']}")
        
        print(f"Completed generating staff for {restaurant_name}\n")


def generate_causwells_staff() -> List[Dict[str, Any]]:
    """Generate staff for Causwells (American restaurant)"""
    return [
        {
            "id": 1,
            "name": "Marcus Johnson",
            "role": "Head Chef - 12 years experience, specializes in American cuisine and grill techniques",
            "shifts": [
                {"day_of_week": "Monday", "start_time": "10:00", "end_time": "22:00"},
                {"day_of_week": "Tuesday", "start_time": "10:00", "end_time": "22:00"},
                {"day_of_week": "Wednesday", "start_time": "10:00", "end_time": "22:00"},
                {"day_of_week": "Thursday", "start_time": "10:00", "end_time": "22:00"},
                {"day_of_week": "Friday", "start_time": "10:00", "end_time": "23:00"},
                {"day_of_week": "Saturday", "start_time": "10:00", "end_time": "23:00"}
            ],
            "status": "active",
            "contact_info": "marcus.johnson@causwells.com"
        },
        {
            "id": 2,
            "name": "Sarah Chen",
            "role": "Line Cook - 5 years experience, specializes in sautéing and prep work",
            "shifts": [
                {"day_of_week": "Monday", "start_time": "14:00", "end_time": "22:00"},
                {"day_of_week": "Tuesday", "start_time": "14:00", "end_time": "22:00"},
                {"day_of_week": "Wednesday", "start_time": "14:00", "end_time": "22:00"},
                {"day_of_week": "Thursday", "start_time": "14:00", "end_time": "22:00"},
                {"day_of_week": "Friday", "start_time": "14:00", "end_time": "23:00"},
                {"day_of_week": "Saturday", "start_time": "14:00", "end_time": "23:00"}
            ],
            "status": "active",
            "contact_info": "sarah.chen@causwells.com"
        },
        {
            "id": 3,
            "name": "David Rodriguez",
            "role": "Server - 3 years experience, excellent customer service skills",
            "shifts": [
                {"day_of_week": "Monday", "start_time": "16:00", "end_time": "22:00"},
                {"day_of_week": "Tuesday", "start_time": "16:00", "end_time": "22:00"},
                {"day_of_week": "Wednesday", "start_time": "16:00", "end_time": "22:00"},
                {"day_of_week": "Thursday", "start_time": "16:00", "end_time": "22:00"},
                {"day_of_week": "Friday", "start_time": "16:00", "end_time": "23:00"},
                {"day_of_week": "Saturday", "start_time": "16:00", "end_time": "23:00"}
            ],
            "status": "active",
            "contact_info": "david.rodriguez@causwells.com"
        },
        {
            "id": 4,
            "name": "Emily Watson",
            "role": "Server - Weekend specialist, 2 years experience",
            "shifts": [
                {"day_of_week": "Friday", "start_time": "17:00", "end_time": "23:00"},
                {"day_of_week": "Saturday", "start_time": "17:00", "end_time": "23:00"},
                {"day_of_week": "Sunday", "start_time": "17:00", "end_time": "22:00"}
            ],
            "status": "active",
            "contact_info": "emily.watson@causwells.com"
        },
        {
            "id": 5,
            "name": "Michael Thompson",
            "role": "Bartender - 4 years experience, craft cocktails specialist",
            "shifts": [
                {"day_of_week": "Tuesday", "start_time": "18:00", "end_time": "02:00"},
                {"day_of_week": "Wednesday", "start_time": "18:00", "end_time": "02:00"},
                {"day_of_week": "Thursday", "start_time": "18:00", "end_time": "02:00"},
                {"day_of_week": "Friday", "start_time": "18:00", "end_time": "02:00"},
                {"day_of_week": "Saturday", "start_time": "18:00", "end_time": "02:00"}
            ],
            "status": "active",
            "contact_info": "michael.thompson@causwells.com"
        },
        {
            "id": 6,
            "name": "Lisa Park",
            "role": "Host - 1 year experience, bilingual English/Korean",
            "shifts": [
                {"day_of_week": "Monday", "start_time": "17:00", "end_time": "22:00"},
                {"day_of_week": "Tuesday", "start_time": "17:00", "end_time": "22:00"},
                {"day_of_week": "Wednesday", "start_time": "17:00", "end_time": "22:00"},
                {"day_of_week": "Thursday", "start_time": "17:00", "end_time": "22:00"},
                {"day_of_week": "Friday", "start_time": "17:00", "end_time": "23:00"},
                {"day_of_week": "Saturday", "start_time": "17:00", "end_time": "23:00"}
            ],
            "status": "active",
            "contact_info": "lisa.park@causwells.com"
        },
        {
            "id": 7,
            "name": "Robert Kim",
            "role": "Manager - 8 years experience, operations and staff management",
            "shifts": [
                {"day_of_week": "Monday", "start_time": "15:00", "end_time": "23:00"},
                {"day_of_week": "Tuesday", "start_time": "15:00", "end_time": "23:00"},
                {"day_of_week": "Wednesday", "start_time": "15:00", "end_time": "23:00"},
                {"day_of_week": "Thursday", "start_time": "15:00", "end_time": "23:00"},
                {"day_of_week": "Friday", "start_time": "15:00", "end_time": "23:00"},
                {"day_of_week": "Saturday", "start_time": "15:00", "end_time": "23:00"}
            ],
            "status": "active",
            "contact_info": "robert.kim@causwells.com"
        }
    ]


def generate_cote_ouest_staff() -> List[Dict[str, Any]]:
    """Generate staff for Cote Ouest Bistro (French restaurant)"""
    return [
        {
            "id": 1,
            "name": "Pierre Dubois",
            "role": "Head Chef - 15 years experience, trained in France, specializes in French cuisine",
            "shifts": [
                {"day_of_week": "Monday", "start_time": "09:00", "end_time": "21:00"},
                {"day_of_week": "Tuesday", "start_time": "09:00", "end_time": "21:00"},
                {"day_of_week": "Wednesday", "start_time": "09:00", "end_time": "21:00"},
                {"day_of_week": "Thursday", "start_time": "09:00", "end_time": "21:00"},
                {"day_of_week": "Friday", "start_time": "09:00", "end_time": "22:00"},
                {"day_of_week": "Saturday", "start_time": "09:00", "end_time": "22:00"}
            ],
            "status": "active",
            "contact_info": "pierre.dubois@coteouest.com"
        },
        {
            "id": 2,
            "name": "Marie Leclerc",
            "role": "Sous Chef - 8 years experience, pastry specialist",
            "shifts": [
                {"day_of_week": "Monday", "start_time": "10:00", "end_time": "20:00"},
                {"day_of_week": "Tuesday", "start_time": "10:00", "end_time": "20:00"},
                {"day_of_week": "Wednesday", "start_time": "10:00", "end_time": "20:00"},
                {"day_of_week": "Thursday", "start_time": "10:00", "end_time": "20:00"},
                {"day_of_week": "Friday", "start_time": "10:00", "end_time": "21:00"},
                {"day_of_week": "Saturday", "start_time": "10:00", "end_time": "21:00"}
            ],
            "status": "active",
            "contact_info": "marie.leclerc@coteouest.com"
        },
        {
            "id": 3,
            "name": "Antoine Moreau",
            "role": "Waiter - 6 years experience, fluent in French and English",
            "shifts": [
                {"day_of_week": "Monday", "start_time": "11:00", "end_time": "21:00"},
                {"day_of_week": "Tuesday", "start_time": "11:00", "end_time": "21:00"},
                {"day_of_week": "Wednesday", "start_time": "11:00", "end_time": "21:00"},
                {"day_of_week": "Thursday", "start_time": "11:00", "end_time": "21:00"},
                {"day_of_week": "Friday", "start_time": "11:00", "end_time": "22:00"},
                {"day_of_week": "Saturday", "start_time": "11:00", "end_time": "22:00"}
            ],
            "status": "active",
            "contact_info": "antoine.moreau@coteouest.com"
        },
        {
            "id": 4,
            "name": "Sophie Martin",
            "role": "Waiter - 4 years experience, wine knowledge specialist",
            "shifts": [
                {"day_of_week": "Tuesday", "start_time": "17:00", "end_time": "22:00"},
                {"day_of_week": "Wednesday", "start_time": "17:00", "end_time": "22:00"},
                {"day_of_week": "Thursday", "start_time": "17:00", "end_time": "22:00"},
                {"day_of_week": "Friday", "start_time": "17:00", "end_time": "22:00"},
                {"day_of_week": "Saturday", "start_time": "17:00", "end_time": "22:00"},
                {"day_of_week": "Sunday", "start_time": "17:00", "end_time": "21:00"}
            ],
            "status": "active",
            "contact_info": "sophie.martin@coteouest.com"
        },
        {
            "id": 5,
            "name": "Jean-Paul Rousseau",
            "role": "Sommelier - 10 years experience, certified wine expert",
            "shifts": [
                {"day_of_week": "Wednesday", "start_time": "18:00", "end_time": "22:00"},
                {"day_of_week": "Thursday", "start_time": "18:00", "end_time": "22:00"},
                {"day_of_week": "Friday", "start_time": "18:00", "end_time": "22:00"},
                {"day_of_week": "Saturday", "start_time": "18:00", "end_time": "22:00"},
                {"day_of_week": "Sunday", "start_time": "18:00", "end_time": "21:00"}
            ],
            "status": "active",
            "contact_info": "jeanpaul.rousseau@coteouest.com"
        },
        {
            "id": 6,
            "name": "Claire Bernard",
            "role": "Host - 2 years experience, bilingual French/English",
            "shifts": [
                {"day_of_week": "Monday", "start_time": "17:00", "end_time": "21:00"},
                {"day_of_week": "Tuesday", "start_time": "17:00", "end_time": "21:00"},
                {"day_of_week": "Wednesday", "start_time": "17:00", "end_time": "21:00"},
                {"day_of_week": "Thursday", "start_time": "17:00", "end_time": "21:00"},
                {"day_of_week": "Friday", "start_time": "17:00", "end_time": "22:00"},
                {"day_of_week": "Saturday", "start_time": "17:00", "end_time": "22:00"}
            ],
            "status": "active",
            "contact_info": "claire.bernard@coteouest.com"
        },
        {
            "id": 7,
            "name": "François Leroy",
            "role": "Manager - 12 years experience, fine dining operations specialist",
            "shifts": [
                {"day_of_week": "Monday", "start_time": "14:00", "end_time": "22:00"},
                {"day_of_week": "Tuesday", "start_time": "14:00", "end_time": "22:00"},
                {"day_of_week": "Wednesday", "start_time": "14:00", "end_time": "22:00"},
                {"day_of_week": "Thursday", "start_time": "14:00", "end_time": "22:00"},
                {"day_of_week": "Friday", "start_time": "14:00", "end_time": "22:00"},
                {"day_of_week": "Saturday", "start_time": "14:00", "end_time": "22:00"}
            ],
            "status": "active",
            "contact_info": "francois.leroy@coteouest.com"
        }
    ]


def generate_generic_staff() -> List[Dict[str, Any]]:
    """Generate generic staff for any restaurant"""
    return [
        {
            "id": 1,
            "name": "John Smith",
            "role": "Head Chef - 10 years experience",
            "shifts": [
                {"day_of_week": "Monday", "start_time": "10:00", "end_time": "22:00"},
                {"day_of_week": "Tuesday", "start_time": "10:00", "end_time": "22:00"},
                {"day_of_week": "Wednesday", "start_time": "10:00", "end_time": "22:00"},
                {"day_of_week": "Thursday", "start_time": "10:00", "end_time": "22:00"},
                {"day_of_week": "Friday", "start_time": "10:00", "end_time": "23:00"},
                {"day_of_week": "Saturday", "start_time": "10:00", "end_time": "23:00"}
            ],
            "status": "active",
            "contact_info": "john.smith@restaurant.com"
        },
        {
            "id": 2,
            "name": "Jane Doe",
            "role": "Server - 3 years experience",
            "shifts": [
                {"day_of_week": "Monday", "start_time": "16:00", "end_time": "22:00"},
                {"day_of_week": "Tuesday", "start_time": "16:00", "end_time": "22:00"},
                {"day_of_week": "Wednesday", "start_time": "16:00", "end_time": "22:00"},
                {"day_of_week": "Thursday", "start_time": "16:00", "end_time": "22:00"},
                {"day_of_week": "Friday", "start_time": "16:00", "end_time": "23:00"},
                {"day_of_week": "Saturday", "start_time": "16:00", "end_time": "23:00"}
            ],
            "status": "active",
            "contact_info": "jane.doe@restaurant.com"
        }
    ]


if __name__ == "__main__":
    print("Generating mock staff data for all restaurants...")
    generate_mock_staff_data()
    print("Mock staff data generation completed!")
