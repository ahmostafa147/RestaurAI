from datetime import datetime
from typing import List, Dict
from ..database import db

MENU = {
    "appetizers": [{"id": 1, "name": "Caesar Salad", "price": 8.99}, {"id": 2, "name": "Wings", "price": 12.99}],
    "entrees": [{"id": 3, "name": "Burger", "price": 14.99}, {"id": 4, "name": "Steak", "price": 24.99}, {"id": 5, "name": "Pasta", "price": 16.99}],
    "desserts": [{"id": 6, "name": "Cheesecake", "price": 7.99}, {"id": 7, "name": "Ice Cream", "price": 5.99}]
}

class Restaurant:
    def __init__(self, name: str = None, key: str = None):
        if key:
            self.key = key
            restaurant_data = db.get_restaurant(key)
            self.name = restaurant_data["name"]
        else:
            self.name = name
            self.key = db.create_restaurant(name)

    def reserve_table(self, name: str, party_size: int, time: str) -> Dict:
        reservation = {"id": len(self.get_reservations()) + 1, "name": name, "party_size": party_size, "time": time, "status": "confirmed"}
        db.log_event(self.key, "reservation", reservation)
        return reservation

    def place_order(self, table_number: int, item_ids: List[int]) -> Dict:
        order_items = []
        total = 0
        for item_id in item_ids:
            for category in MENU.values():
                for item in category:
                    if item["id"] == item_id:
                        order_items.append(item)
                        total += item["price"]
        order = {"id": len(self.get_orders()) + 1, "table": table_number, "items": order_items, "total": round(total, 2), "status": "pending", "timestamp": datetime.now().isoformat()}
        db.log_event(self.key, "order", order)
        return order

    def seat_party(self, table_number: int):
        db.log_event(self.key, "seat", {"table": table_number, "status": "occupied"})

    def clear_table(self, table_number: int):
        db.log_event(self.key, "clear", {"table": table_number, "status": "available"})

    def get_reservations(self) -> List[Dict]:
        return [e["data"] for e in db.get_events(self.key, "reservation")]

    def get_orders(self) -> List[Dict]:
        return [e["data"] for e in db.get_events(self.key, "order")]

    def get_menu(self) -> Dict:
        return MENU
