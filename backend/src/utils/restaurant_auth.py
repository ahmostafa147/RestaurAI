"""
Restaurant authentication utilities for mapping names to secure keys.
"""
import json
import os
from typing import Optional, Dict

class RestaurantAuth:
    """Manages restaurant authentication and secure key mapping."""

    def __init__(self, restaurants_path: str = None):
        if restaurants_path is None:
            # Default path to restaurants.json
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            restaurants_path = os.path.join(base_path, "agents", "restaurants.json")

        self.restaurants_path = restaurants_path
        self.restaurants_data = self._load_restaurants()
        self.name_to_key_map = self._build_name_to_key_map()

    def _load_restaurants(self) -> Dict:
        """Load restaurants configuration from JSON file."""
        try:
            with open(self.restaurants_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: restaurants.json not found at {self.restaurants_path}")
            return {"restaurants": []}

    def _build_name_to_key_map(self) -> Dict[str, str]:
        """Build mapping from restaurant name to secure key."""
        mapping = {}
        for restaurant in self.restaurants_data.get("restaurants", []):
            name = restaurant.get("name")
            key = restaurant.get("secure_key")
            if name and key:
                mapping[name] = key
        return mapping

    def get_key_by_name(self, restaurant_name: str) -> Optional[str]:
        """
        Get secure key for a restaurant by name.

        Args:
            restaurant_name: Name of the restaurant

        Returns:
            Secure key if found, None otherwise
        """
        return self.name_to_key_map.get(restaurant_name)

    def get_all_restaurants(self) -> list:
        """Get list of all available restaurants."""
        return [
            {
                "name": r.get("name"),
                "id": r.get("id")
            }
            for r in self.restaurants_data.get("restaurants", [])
        ]

    def validate_credentials(self, restaurant_name: str, password: str = None) -> Optional[str]:
        """
        Validate restaurant credentials and return secure key.

        Args:
            restaurant_name: Name of the restaurant
            password: Password (currently unused, for future implementation)

        Returns:
            Secure key if valid, None otherwise
        """
        # For now, we just check if the restaurant exists
        # In production, you'd validate password here
        return self.get_key_by_name(restaurant_name)


# Global instance
_auth_instance = None

def get_auth_instance() -> RestaurantAuth:
    """Get singleton instance of RestaurantAuth."""
    global _auth_instance
    if _auth_instance is None:
        _auth_instance = RestaurantAuth()
    return _auth_instance
