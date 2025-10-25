from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from ..database import db
from ..models.menu import MenuItem
from ..models.table import Table
from ..models.ingredient import Ingredient
from .ingredient_manager import IngredientManager
from .table_manager import TableManager
from .order_manager import OrderManager

class Restaurant:
    def __init__(self, name: str = None, key: str = None, menu: Dict[str, List[MenuItem]] = None, tables: List[Table] = None, inventory: Dict[int, Ingredient] = None):
        if key:
            self.key = key
            restaurant_data = db.get_restaurant(key)
            self.name = restaurant_data["name"]
        else:
            self.name = name
            self.key = db.create_restaurant(name)
        
        # Initialize managers
        self.ingredient_manager = IngredientManager(self.key, inventory)
        self.table_manager = TableManager(self.key, tables)
        self.order_manager = OrderManager(self.key, menu, self.ingredient_manager)
    

    # Core restaurant operations
    def reserve_table(self, name: str, party_size: int, time: str) -> Dict:
        """Make a reservation"""
        return self.table_manager.make_reservation(name, party_size, time)
    
    def create_ticket(self, table_number: int) -> Dict:
        """Create a new ticket for a table"""
        return self.order_manager.create_ticket(table_number)
    
    def place_order(self, table_number: int, item_id: int, ticket_id: int = None) -> Dict:
        """Place a new order for a single item"""
        return self.order_manager.place_order(table_number, item_id, ticket_id)
    
    def get_tickets(self) -> List[Dict]:
        """Get all tickets"""
        return self.order_manager.get_tickets()
    
    def get_ticket(self, ticket_id: int) -> Optional[Dict]:
        """Get a specific ticket by ID"""
        return self.order_manager.get_ticket(ticket_id)
    
    def get_ticket_orders(self, ticket_id: int) -> List[Dict]:
        """Get all orders for a specific ticket"""
        return self.order_manager.get_ticket_orders(ticket_id)
    
    def get_table_orders(self, table_number: int) -> List[Dict]:
        """Get all orders for a specific table"""
        return self.order_manager.get_table_orders(table_number)
    
    def close_ticket(self, ticket_id: int) -> bool:
        """Close a ticket and calculate total"""
        return self.order_manager.close_ticket(ticket_id)
    
    def seat_party(self, table_number: int):
        """Seat a party at a table"""
        return self.table_manager.seat_party(table_number)

    def clear_table(self, table_number: int):
        """Clear a table after service"""
        return self.table_manager.clear_table(table_number)
    
