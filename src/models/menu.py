from dataclasses import dataclass, field
from typing import Dict, Optional, List
from .ingredient import Ingredient

@dataclass
class MenuItem:
    """Represents a menu item with id, name, price, and category"""
    id: int
    name: str
    price: float
    category: str
    description: Optional[str] = None
    available: bool = True
    ingredients: List[Ingredient] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert MenuItem to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "category": self.category,
            "description": self.description,
            "available": self.available,
            "ingredients": [ingredient.to_dict() for ingredient in self.ingredients]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MenuItem':
        """Create MenuItem from dictionary"""
        return cls(
            id=data["id"],
            name=data["name"],
            price=data["price"],
            category=data["category"],
            description=data.get("description"),
            available=data.get("available", True),
            ingredients=[Ingredient.from_dict(ingredient) for ingredient in data.get("ingredients", [])]
        )