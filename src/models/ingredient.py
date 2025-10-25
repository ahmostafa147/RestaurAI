from dataclasses import dataclass, asdict
from typing import Dict, Optional
import json

@dataclass
class Ingredient:
    """Represents an ingredient with id, name, and quantity"""
    id: int
    name: str
    quantity: float
    unit: str
    available: bool = True
    
    def to_dict(self) -> Dict:
        """Convert Ingredient to dictionary for JSON serialization"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert Ingredient to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Ingredient':
        """Create Ingredient from dictionary"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Ingredient':
        """Create Ingredient from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)


class IngredientJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles Ingredient objects automatically"""
    def default(self, obj):
        if isinstance(obj, Ingredient):
            return obj.to_dict()
        return super().default(obj)


def ingredient_json_dumps(obj, **kwargs):
    """JSON dumps with automatic Ingredient serialization"""
    return json.dumps(obj, cls=IngredientJSONEncoder, **kwargs)


def ingredient_json_loads(json_str, **kwargs):
    """JSON loads with automatic Ingredient deserialization"""
    return json.loads(json_str, **kwargs) 