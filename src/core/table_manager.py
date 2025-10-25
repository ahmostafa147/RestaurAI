from typing import List, Dict, Optional
from ..database import db
from ..models.table import Table

class TableManager:
    """Manages restaurant tables and reservations"""
    
    def __init__(self, restaurant_key: str, tables: List[Table] = None):
        """Initialize table manager with restaurant key and tables"""
        self.restaurant_key = restaurant_key
        self.tables = tables if tables is not None else []
    
    def make_reservation(self, name: str, party_size: int, time: str) -> Dict:
        """Make a new reservation"""
        reservation = {
            "id": len(self.get_reservations()) + 1, 
            "name": name, 
            "party_size": party_size, 
            "time": time, 
            "status": "confirmed"
        }
        db.log_event(self.restaurant_key, "reservation", reservation)
        return reservation
    
    def get_reservations(self) -> List[Dict]:
        """Get all reservations"""
        return [e["data"] for e in db.get_events(self.restaurant_key, "reservation")]
    
    def get_tables(self) -> List[Dict]:
        """Return all tables as dictionaries"""
        return [table.to_dict() for table in self.tables]
    
    def get_table(self, table_id: int) -> Optional[Table]:
        """Get a specific table by ID"""
        for table in self.tables:
            if table.id == table_id:
                return table
        return None
    
    def get_available_tables(self, party_size: int) -> List[Table]:
        """Get tables that can accommodate the party size and are available"""
        return [table for table in self.tables 
                if table.status == "available" and table.num_ppl >= party_size]
    
    def update_table_status(self, table_id: int, status: str) -> bool:
        """Update the status of a table"""
        table = self.get_table(table_id)
        if table:
            table.status = status
            return True
        return False
    
    def seat_party(self, table_number: int):
        """Seat a party at a table"""
        if self.update_table_status(table_number, "occupied"):
            db.log_event(self.restaurant_key, "seat", {"table": table_number, "status": "occupied"})
        #Raise exception if table is invalid
        raise ValueError(f"Table {table_number} is not available")

    def clear_table(self, table_number: int):
        """Clear a table after service"""
        if self.update_table_status(table_number, "available"):
            db.log_event(self.restaurant_key, "clear", {"table": table_number, "status": "available"})
