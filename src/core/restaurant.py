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
        self.ingredient_manager = IngredientManager(self.key)
        if inventory:
            self.ingredient_manager.override_inventory(inventory)
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
    
    def get_tables(self) -> List[Dict]:
        """Get all tables"""
        return self.table_manager.get_tables()
    
    def get_table(self, table_id: int) -> Optional[Dict]:
        """Get a specific table by ID"""
        return self.table_manager.get_table(table_id)
    
    def close_ticket(self, ticket_id: int) -> bool:
        """Close a ticket and calculate total"""
        return self.order_manager.close_ticket(ticket_id)
    
    def seat_party(self, table_number: int):
        """Seat a party at a table"""
        return self.table_manager.seat_party(table_number)

    def clear_table(self, table_number: int):
        """Clear a table after service"""
        return self.table_manager.clear_table(table_number)
    
    # Ingredient management wrappers
    def get_inventory(self) -> List[Dict]:
        """Get all inventory items"""
        return self.ingredient_manager.get_inventory()
    
    def get_ingredient(self, ingredient_id: int) -> Optional[Ingredient]:
        """Get a specific ingredient by ID"""
        return self.ingredient_manager.get_ingredient(ingredient_id)
    
    def get_ingredient_by_name(self, ingredient_name: str) -> Optional[Ingredient]:
        """Get a specific ingredient by name"""
        return self.ingredient_manager.get_ingredient_by_name(ingredient_name)
    
    def get_ingredient_by_id_or_name(self, identifier) -> Optional[Ingredient]:
        """Get ingredient by either ID (int) or name (str)"""
        return self.ingredient_manager.get_ingredient_by_id_or_name(identifier)
    
    def has_enough_ingredient(self, required_ingredient: Ingredient) -> bool:
        """Check if the restaurant has enough of a specific ingredient"""
        return self.ingredient_manager.has_enough_ingredient(required_ingredient)
    
    def add_ingredient(self, ingredient: Ingredient) -> bool:
        """Add or update an ingredient in inventory"""
        return self.ingredient_manager.add_ingredient(ingredient)
    
    def remove_ingredient(self, ingredient_id: int, quantity: float) -> bool:
        """Remove a specific quantity of an ingredient from inventory"""
        return self.ingredient_manager.remove_ingredient(ingredient_id, quantity)
    
    def remove_ingredient_by_name(self, ingredient_name: str, quantity: float) -> bool:
        """Remove a specific quantity of an ingredient by name"""
        return self.ingredient_manager.remove_ingredient_by_name(ingredient_name, quantity)
    
    # Order management wrappers
    def get_orders(self) -> List[Dict]:
        """Get all orders from all tickets"""
        return self.order_manager.get_orders()
    
    def get_order_by_id(self, order_id: int) -> Optional[Dict]:
        """Get a specific order by ID"""
        return self.order_manager.get_order_by_id(order_id)
    
    def update_order_status(self, order_id: int, status: str) -> bool:
        """Update the status of an order"""
        return self.order_manager.update_order_status(order_id, status)
    
    def get_menu(self) -> Dict:
        """Get the restaurant menu"""
        return self.order_manager.get_menu()
    
    def get_menu_item(self, item_id: int) -> Optional[MenuItem]:
        """Get a specific menu item by ID"""
        return self.order_manager.get_menu_item(item_id)
    
    def add_menu_item(self, item: MenuItem) -> bool:
        """Add a new menu item to the appropriate category"""
        return self.order_manager.add_menu_item(item)
    
    def update_menu_item(self, item_id: int, **kwargs) -> bool:
        """Update a menu item's properties"""
        return self.order_manager.update_menu_item(item_id, **kwargs)
    
    def set_item_availability(self, item_id: int, available: bool) -> bool:
        """Set the availability of a menu item"""
        return self.order_manager.set_item_availability(item_id, available)
    
    def update_menu_availability(self):
        """Update menu availability based on ingredients"""
        return self.order_manager.update_menu_availability()
    
    # Table management wrappers
    def get_available_tables(self, party_size: int) -> List[Table]:
        """Get tables that can accommodate the party size and are available"""
        return self.table_manager.get_available_tables(party_size)
    
    def update_table_status(self, table_id: int, status: str) -> bool:
        """Update the status of a table"""
        return self.table_manager.update_table_status(table_id, status)
    
    def get_reservations(self) -> List[Dict]:
        """Get all reservations"""
        return self.table_manager.get_reservations()
    
