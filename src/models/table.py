from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class Table:
    """Represents a restaurant table with id, capacity, and special attributes"""
    id: int
    num_ppl: int  # Maximum number of people this table can seat
    description: Optional[str] = None  # Special descriptions like "outside", "near window", "bar seat"
    status: str = "available"  # available, occupied, reserved
    
    def to_dict(self) -> Dict:
        """Convert Table to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "num_ppl": self.num_ppl,
            "description": self.description,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Table':
        """Create Table from dictionary"""
        return cls(
            id=data["id"],
            num_ppl=data["num_ppl"],
            description=data.get("description"),
            status=data.get("status", "available")
        )
