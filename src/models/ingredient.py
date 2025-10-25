from dataclasses import dataclass
from typing import Dict, Optional

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