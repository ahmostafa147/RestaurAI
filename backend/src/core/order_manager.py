from datetime import datetime
from typing import List, Dict, Optional
from ..models.menu import MenuItem
from ..models.ingredient import Ingredient
from ..database import db
from .ingredient_manager import IngredientManager


class OrderManager:
    """Manages restaurant orders and menu operations"""
    
    def __init__(self, restaurant_key: str, menu: Dict[str, List[MenuItem]], ingredient_manager: IngredientManager):
        """Initialize order manager with restaurant key, menu, and ingredient manager"""
        self.restaurant_key = restaurant_key
        self.ingredient_manager = ingredient_manager
        self.tickets = self._load_tickets()
        self.ticket_counter = self._load_ticket_counter()
        
        # Load or set menu
        if menu is not None:
            # Save menu to database if provided
            self.menu = menu
            self._save_menu()
        else:
            # Load menu from database
            self.menu = self._load_menu()
    
    def _load_tickets(self) -> List[Dict]:
        """Load active tickets from database"""
        tickets_data = db.get_data(self.restaurant_key, "active_tickets")
        return tickets_data.get("tickets", [])
    
    def _load_ticket_counter(self) -> int:
        """Load ticket counter from database"""
        counter_data = db.get_data(self.restaurant_key, "ticket_counter")
        return counter_data.get("counter", 0)
    
    def _load_menu(self) -> Dict[str, List[MenuItem]]:
        """Load menu from database"""
        menu_data = db.get_data(self.restaurant_key, "menu")
        if not menu_data:
            return {}
        
        # Convert dict data back to MenuItem objects
        menu = {}
        for category, items_data in menu_data.items():
            menu[category] = []
            for item_dict in items_data:
                # Convert ingredients
                ingredients = []
                for ing_dict in item_dict.get('ingredients', []):
                    ingredient = Ingredient(
                        id=ing_dict['id'],
                        name=ing_dict['name'],
                        quantity=ing_dict['quantity'],
                        unit=ing_dict['unit'],
                        available=ing_dict.get('available', True),
                        cost=ing_dict.get('cost', 0.0),
                        supplier=ing_dict.get('supplier', '')
                    )
                    ingredients.append(ingredient)
                
                # Create MenuItem
                menu_item = MenuItem(
                    id=item_dict['id'],
                    name=item_dict['name'],
                    price=item_dict['price'],
                    category=category,
                    description=item_dict.get('description'),
                    available=item_dict.get('available', True),
                    ingredients=ingredients
                )
                menu[category].append(menu_item)
        
        return menu
    
    def _save_menu(self):
        """Save menu to database"""
        # Convert menu to serializable format
        menu_data = {}
        for category, items in self.menu.items():
            menu_data[category] = [item.to_dict() for item in items]
        
        # Save to database
        db.set_data(self.restaurant_key, "menu", menu_data)
    
    def _save_ticket_counter(self):
        """Save ticket counter to database"""
        counter_data = {"counter": self.ticket_counter}
        db.set_data(self.restaurant_key, "ticket_counter", counter_data)
    
    def _get_next_ticket_id(self) -> int:
        """Get next unique ticket ID and increment counter"""
        self.ticket_counter += 1
        self._save_ticket_counter()
        return self.ticket_counter
    
    def _save_tickets(self):
        """Save active tickets to database"""
        tickets_data = {"tickets": self.tickets}
        db.set_data(self.restaurant_key, "active_tickets", tickets_data)
        
        # Log as backup event
        db.log_event(self.restaurant_key, "active_tickets_update", tickets_data)
    
    def _check_ingredient_availability(self, menu_item: MenuItem) -> bool:
        """Check if there are enough ingredients for a menu item"""
        for ingredient in menu_item.ingredients:
            if not self.ingredient_manager.has_enough_ingredient(ingredient):
                return False
        return True
    
    def _update_menu_availability(self):
        """Update menu item availability based on ingredient availability"""
        for category_items in self.menu.values():
            for item in category_items:
                item.available = self._check_ingredient_availability(item)
    
    def create_ticket(self, table_number: int) -> Dict:
        """Create a new ticket for a table"""
        ticket = {
            "id": self._get_next_ticket_id(),
            "table": table_number,
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "orders": [],
            "total": 0.0
        }
        
        # Add to tickets list and save
        self.tickets.append(ticket)
        self._save_tickets()
        
        return ticket
    
    def get_tickets(self) -> List[Dict]:
        """Get all tickets"""
        return self.tickets
    
    def get_ticket(self, ticket_id: int) -> Optional[Dict]:
        """Get a specific ticket by ID"""
        tickets = self.get_tickets()
        for ticket in tickets:
            if ticket["id"] == ticket_id:
                return ticket
        raise ValueError(f"Ticket with ID {ticket_id} not found")
    
    def get_ticket_orders(self, ticket_id: int) -> List[Dict]:
        """Get all orders for a specific ticket"""
        ticket = self.get_ticket(ticket_id)
        return ticket.get("orders", []) if ticket else []
    
    def _update_ticket_with_order(self, ticket_id: int, order: Dict):
        """Update ticket with new order and recalculate total"""
        ticket = self.get_ticket(ticket_id)
        if not ticket:
            return
        
        # Add order to ticket
        ticket["orders"].append(order)
        
        # Recalculate total from orders
        ticket["total"] = sum(order["total"] for order in ticket["orders"])
        
        # Save tickets to database
        self._save_tickets()
    
    def close_ticket(self, ticket_id: int) -> bool:
        """Close a ticket and remove from active tickets"""
        ticket = self.get_ticket(ticket_id)
        if not ticket:
            return False
        
        # Update ticket status
        ticket["status"] = "closed"
        ticket["closed_at"] = datetime.now().isoformat()
        
        # Log the closed ticket as an individual event
        db.log_event(self.restaurant_key, "closed_ticket", ticket)
        
        # Remove from active tickets
        self.tickets = [t for t in self.tickets if t["id"] != ticket_id]
        
        # Save updated active tickets
        self._save_tickets()
        return True

    def place_order(self, table_number: int, item_id: int, ticket_id: int = None) -> Dict:
        """Place a new order for a single item with ingredient validation"""
        # Find the menu item
        menu_item = None
        for category_items in self.menu.values():
            for item in category_items:
                if item.id == item_id:
                    menu_item = item
                    break
            if menu_item:
                break
        
        if not menu_item:
            return {
                "id": len(self.get_orders()) + 1,
                "table": table_number,
                "items": [],
                "total": 0,
                "status": "rejected",
                "reason": f"Item ID {item_id} not found",
                "timestamp": datetime.now().isoformat()
            }
        
        # Check ingredient availability
        if not self._check_ingredient_availability(menu_item):
            return {
                "id": len(self.get_orders()) + 1,
                "table": table_number,
                "items": [],
                "total": 0,
                "status": "rejected",
                "reason": f"Insufficient ingredients for {menu_item.name}",
                "timestamp": datetime.now().isoformat()
            }
        
        # Create order
        order = {
            "id": len(self.get_orders()) + 1, 
            "table": table_number, 
            "ticket_id": ticket_id,
            "items": [menu_item.to_dict()], 
            "total": menu_item.price, 
            "status": "pending", 
            "timestamp": datetime.now().isoformat()
        }
        
        # Consume ingredients after successful order
        for ingredient in menu_item.ingredients:
            self.ingredient_manager.remove_ingredient(ingredient.id, ingredient.quantity)
        
        # Update menu availability after consuming ingredients
        self._update_menu_availability()
        
        # Update ticket if ticket_id is provided
        if ticket_id:
            self._update_ticket_with_order(ticket_id, order)
        else:
            # If no ticket_id, still log the order separately
            db.log_event(self.restaurant_key, "order", order)
        
        return order
    
    def get_orders(self) -> List[Dict]:
        """Get all orders from all tickets"""
        all_orders = []
        for ticket in self.get_tickets():
            all_orders.extend(ticket.get("orders", []))
        return all_orders
    
    def get_order_by_id(self, order_id: int) -> Optional[Dict]:
        """Get a specific order by ID"""
        for ticket in self.get_tickets():
            for order in ticket.get("orders", []):
                if order["id"] == order_id:
                    return order
        return None
    
    def update_order_status(self, order_id: int, status: str) -> bool:
        """Update the status of an order"""
        order = self.get_order_by_id(order_id)
        if order:
            order["status"] = status
            # Log the update
            db.log_event(self.restaurant_key, "order_update", {
                "order_id": order_id,
                "new_status": status
            })
            return True
        return False
    
    def get_menu(self) -> Dict:
        """Return menu as dictionary with MenuItem instances converted to dicts"""
        return {
            category: [item.to_dict() for item in items] 
            for category, items in self.menu.items()
        }
    
    def get_menu_item(self, item_id: int) -> Optional[MenuItem]:
        """Get a specific menu item by ID"""
        for category_items in self.menu.values():
            for item in category_items:
                if item.id == item_id:
                    return item
        return None
    
    def add_menu_item(self, item: MenuItem) -> bool:
        """Add a new menu item to the appropriate category"""
        # Create category if it doesn't exist
        if item.category not in self.menu:
            self.menu[item.category] = []
        
        self.menu[item.category].append(item)
        self._save_menu()  # Save the updated menu to database
        return True
    
    def update_menu_item(self, item_id: int, **kwargs) -> bool:
        """Update a menu item's properties"""
        item = self.get_menu_item(item_id)
        if item:
            for key, value in kwargs.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            return True
        return False
    
    def set_item_availability(self, item_id: int, available: bool) -> bool:
        """Set the availability of a menu item"""
        return self.update_menu_item(item_id, available=available)
    
    def update_menu_availability(self):
        """Public method to update menu availability based on ingredients"""
        self._update_menu_availability()
