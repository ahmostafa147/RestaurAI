from typing import Dict, List, Optional
from ..models.ingredient import Ingredient
from ..database import db

class IngredientManager:
    """Manages restaurant inventory and ingredient operations"""
    
    def __init__(self, restaurant_key: str):
        """Initialize ingredient manager with inventory"""
        self.restaurant_key = restaurant_key
        # Load from database
        self.inventory = self._load_inventory()
        self._name_to_id = {ingredient.name: ingredient.id for ingredient in self.inventory.values()} if self.inventory else {}
    
    def _load_inventory(self) -> Dict[int, Ingredient]:
        """Load inventory from database"""
        inventory_data = db.get_data(self.restaurant_key, "inventory")
        if not inventory_data:
            return {}
        
        # Convert dict data back to Ingredient objects
        inventory = {}  
        for ingredient_id_str, ingredient_dict in inventory_data.items():
            ingredient_id = int(ingredient_id_str)
            ingredient = Ingredient(
                id=ingredient_dict["id"],
                name=ingredient_dict["name"],
                quantity=ingredient_dict["quantity"],
                unit=ingredient_dict["unit"],
                available=ingredient_dict.get("available", True)
            )
            inventory[ingredient_id] = ingredient
        
        return inventory
    
    def _save_inventory(self):
        """Save current inventory to database"""
        # Convert inventory to serializable format
        inventory_data = {}
        for ingredient_id, ingredient in self.inventory.items():
            inventory_data[str(ingredient_id)] = ingredient.to_dict()
        
        # Save to database
        db.set_data(self.restaurant_key, "inventory", inventory_data)
        
        # Log as backup event
        db.log_event(self.restaurant_key, "inventory_update", inventory_data)
    
    def override_inventory(self, inventory: Dict[int, Ingredient]):
        """Override inventory completely (for restaurant init/overhaul)"""
        self.inventory = inventory
        self._name_to_id = {ingredient.name: ingredient.id for ingredient in self.inventory.values()}
        self._save_inventory()
    
    def get_inventory(self) -> List[Dict]:
        """Return all inventory items as dictionaries"""
        return [ingredient.to_dict() for ingredient in self.inventory.values()]
    
    def get_ingredient(self, ingredient_id: int) -> Optional[Ingredient]:
        """Get a specific ingredient from inventory by ID"""
        return self.inventory.get(ingredient_id)
    
    def has_enough_ingredient(self, required_ingredient: Ingredient) -> bool:
        """Check if the restaurant has enough of a specific ingredient"""
        ingredient = self.inventory.get(required_ingredient.id)
        if ingredient:
            return (ingredient.name == required_ingredient.name and 
                    ingredient.unit == required_ingredient.unit and
                    ingredient.quantity >= required_ingredient.quantity and
                    ingredient.available)
        return False
    
    def add_ingredient(self, ingredient: Ingredient) -> bool:
        """Add or update an ingredient in inventory"""
        if ingredient.id in self.inventory:
            # Update quantity
            self.inventory[ingredient.id].quantity += ingredient.quantity
        else:
            # Add new ingredient
            self.inventory[ingredient.id] = ingredient
            # Update reverse lookup
            self._name_to_id[ingredient.name] = ingredient.id
        
        # Save to database
        self._save_inventory()
        return True
    
    def remove_ingredient(self, ingredient_id: int, quantity: float) -> bool:
        """Remove a specific quantity of an ingredient from inventory"""
        if ingredient_id in self.inventory:
            ingredient = self.inventory[ingredient_id]
            if ingredient.quantity >= quantity:
                ingredient.quantity -= quantity
                if ingredient.quantity <= 0:
                    # Remove from both dictionaries
                    del self.inventory[ingredient_id]
                    del self._name_to_id[ingredient.name]
                
                # Save to database
                self._save_inventory()
                return True
        return False
        
    def get_ingredient_by_name(self, ingredient_name: str) -> Optional[Ingredient]:
        """Get a specific ingredient from inventory by name"""
        ingredient_id = self._name_to_id.get(ingredient_name)
        return self.inventory.get(ingredient_id) if ingredient_id else None
    
    def get_ingredient_by_id_or_name(self, identifier) -> Optional[Ingredient]:
        """Get ingredient by either ID (int) or name (str)"""
        if isinstance(identifier, int):
            return self.get_ingredient(identifier)
        elif isinstance(identifier, str):
            return self.get_ingredient_by_name(identifier)
        return None
    
    def remove_ingredient_by_name(self, ingredient_name: str, quantity: float) -> bool:
        """Remove a specific quantity of an ingredient by name"""
        ingredient_id = self._name_to_id.get(ingredient_name)
        if ingredient_id:
            return self.remove_ingredient(ingredient_id, quantity)
        return False
