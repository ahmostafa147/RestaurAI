from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import json

@dataclass
class Shift:
    """Represents a work shift with day, start time, and end time"""
    day_of_week: str  # Monday, Tuesday, etc.
    start_time: str   # Format: "09:00"
    end_time: str     # Format: "17:00"
    
    def to_dict(self) -> Dict:
        """Convert Shift to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Shift':
        """Create Shift from dictionary"""
        return cls(**data)

@dataclass
class StaffMember:
    """Represents a staff member with id, name, role, shifts, and status"""
    id: int
    name: str
    role: str  # Descriptive role for LLM understanding
    shifts: List[Shift]
    status: str = "active"  # active, absent, on_leave
    contact_info: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert StaffMember to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "shifts": [shift.to_dict() for shift in self.shifts],
            "status": self.status,
            "contact_info": self.contact_info
        }
    
    def to_json(self) -> str:
        """Convert StaffMember to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StaffMember':
        """Create StaffMember from dictionary"""
        shifts = [Shift.from_dict(shift_data) for shift_data in data.get("shifts", [])]
        return cls(
            id=data["id"],
            name=data["name"],
            role=data["role"],
            shifts=shifts,
            status=data.get("status", "active"),
            contact_info=data.get("contact_info")
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'StaffMember':
        """Create StaffMember from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)


class StaffJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles StaffMember objects automatically"""
    def default(self, obj):
        if isinstance(obj, StaffMember):
            return obj.to_dict()
        elif isinstance(obj, Shift):
            return obj.to_dict()
        return super().default(obj)


def staff_json_dumps(obj, **kwargs):
    """JSON dumps with automatic StaffMember serialization"""
    return json.dumps(obj, cls=StaffJSONEncoder, **kwargs)


def staff_json_loads(json_str, **kwargs):
    """JSON loads with automatic StaffMember deserialization"""
    return json.loads(json_str, **kwargs)
