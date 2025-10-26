from typing import Dict, List, Optional
from datetime import datetime, date
from ..models.staff import StaffMember, Shift
from ..database import db

class StaffManager:
    """Manages restaurant staff and scheduling operations"""
    
    def __init__(self, restaurant_key: str):
        """Initialize staff manager with staff data"""
        self.restaurant_key = restaurant_key
        # Load from database
        self.staff = self._load_staff()
        self._name_to_id = {member.name: member.id for member in self.staff.values()} if self.staff else {}
        self.absences = self._load_absences()
    
    def _load_staff(self) -> Dict[int, StaffMember]:
        """Load staff from database"""
        staff_data = db.get_data(self.restaurant_key, "staff")
        if not staff_data:
            return {}
        
        # Convert dict data back to StaffMember objects
        staff = {}  
        for staff_id_str, staff_dict in staff_data.items():
            staff_id = int(staff_id_str)
            staff_member = StaffMember.from_dict(staff_dict)
            staff[staff_id] = staff_member
        
        return staff
    
    def _load_absences(self) -> Dict[str, List[int]]:
        """Load absence data from database"""
        absence_data = db.get_data(self.restaurant_key, "absences")
        if not absence_data:
            return {}
        
        # Convert string keys back to proper format
        absences = {}
        for date_str, staff_ids in absence_data.items():
            absences[date_str] = staff_ids
        
        return absences
    
    def _save_staff(self):
        """Save current staff to database"""
        # Convert staff to serializable format
        staff_data = {}
        for staff_id, staff_member in self.staff.items():
            staff_data[str(staff_id)] = staff_member.to_dict()
        
        # Save to database
        db.set_data(self.restaurant_key, "staff", staff_data)
        
        # Log as backup event
        db.log_event(self.restaurant_key, "staff_update", staff_data)
    
    def _save_absences(self):
        """Save absence data to database"""
        db.set_data(self.restaurant_key, "absences", self.absences)
    
    def get_staff(self) -> List[Dict]:
        """Return all staff members as dictionaries"""
        return [member.to_dict() for member in self.staff.values()]
    
    def get_staff_member(self, staff_id: int) -> Optional[StaffMember]:
        """Get a specific staff member by ID"""
        return self.staff.get(staff_id)
    
    def get_staff_by_name(self, name: str) -> Optional[StaffMember]:
        """Get a specific staff member by name"""
        staff_id = self._name_to_id.get(name)
        return self.staff.get(staff_id) if staff_id else None
    
    def get_staff_by_role(self, role: str) -> List[StaffMember]:
        """Get all staff members with a specific role"""
        return [member for member in self.staff.values() if role.lower() in member.role.lower()]
    
    def add_staff_member(self, staff_member: StaffMember) -> bool:
        """Add a new staff member"""
        if staff_member.id in self.staff:
            return False  # Staff member with this ID already exists
        
        self.staff[staff_member.id] = staff_member
        self._name_to_id[staff_member.name] = staff_member.id
        
        # Save to database
        self._save_staff()
        return True
    
    def remove_staff_member(self, staff_id: int) -> bool:
        """Remove a staff member"""
        if staff_id in self.staff:
            member = self.staff[staff_id]
            del self.staff[staff_id]
            del self._name_to_id[member.name]
            
            # Save to database
            self._save_staff()
            return True
        return False
    
    def update_staff_member(self, staff_id: int, **kwargs) -> bool:
        """Update a staff member's properties"""
        if staff_id not in self.staff:
            return False
        
        member = self.staff[staff_id]
        
        # Update allowed fields
        if 'name' in kwargs:
            old_name = member.name
            member.name = kwargs['name']
            del self._name_to_id[old_name]
            self._name_to_id[member.name] = staff_id
        
        if 'role' in kwargs:
            member.role = kwargs['role']
        
        if 'shifts' in kwargs:
            member.shifts = kwargs['shifts']
        
        if 'status' in kwargs:
            member.status = kwargs['status']
        
        if 'contact_info' in kwargs:
            member.contact_info = kwargs['contact_info']
        
        # Save to database
        self._save_staff()
        return True
    
    def get_available_staff(self, day_of_week: str, time: str = None) -> List[StaffMember]:
        """Get staff members available on a specific day and optionally time"""
        available = []
        
        for member in self.staff.values():
            if member.status != "active":
                continue
            
            # Check if staff member works on this day
            works_today = any(shift.day_of_week.lower() == day_of_week.lower() for shift in member.shifts)
            if not works_today:
                continue
            
            # If time is specified, check if they're scheduled at that time
            if time:
                works_at_time = any(
                    shift.day_of_week.lower() == day_of_week.lower() and
                    shift.start_time <= time <= shift.end_time
                    for shift in member.shifts
                )
                if not works_at_time:
                    continue
            
            # Check if they're absent on this date
            today_str = date.today().isoformat()
            if today_str in self.absences and member.id in self.absences[today_str]:
                continue
            
            available.append(member)
        
        return available
    
    def mark_absent(self, staff_id: int, absence_date: str = None) -> bool:
        """Mark a staff member as absent on a specific date"""
        if staff_id not in self.staff:
            return False
        
        if absence_date is None:
            absence_date = date.today().isoformat()
        
        if absence_date not in self.absences:
            self.absences[absence_date] = []
        
        if staff_id not in self.absences[absence_date]:
            self.absences[absence_date].append(staff_id)
            self._save_absences()
            
            # Log absence event
            db.log_event(self.restaurant_key, "staff_absence", {
                "staff_id": staff_id,
                "staff_name": self.staff[staff_id].name,
                "date": absence_date
            })
        
        return True
    
    def clear_absence(self, staff_id: int, absence_date: str = None) -> bool:
        """Clear an absence for a staff member on a specific date"""
        if absence_date is None:
            absence_date = date.today().isoformat()
        
        if absence_date in self.absences and staff_id in self.absences[absence_date]:
            self.absences[absence_date].remove(staff_id)
            if not self.absences[absence_date]:  # Remove empty date
                del self.absences[absence_date]
            self._save_absences()
            return True
        
        return False
    
    def get_schedule_for_day(self, day_of_week: str) -> List[Dict]:
        """Get schedule for a specific day of the week"""
        schedule = []
        
        for member in self.staff.values():
            if member.status != "active":
                continue
            
            for shift in member.shifts:
                if shift.day_of_week.lower() == day_of_week.lower():
                    schedule.append({
                        "staff_id": member.id,
                        "staff_name": member.name,
                        "role": member.role,
                        "start_time": shift.start_time,
                        "end_time": shift.end_time,
                        "contact_info": member.contact_info
                    })
        
        return schedule
    
    def get_schedule_for_week(self) -> Dict[str, List[Dict]]:
        """Get schedule for the entire week"""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekly_schedule = {}
        
        for day in days:
            weekly_schedule[day] = self.get_schedule_for_day(day)
        
        return weekly_schedule
    
    def get_absences_for_date(self, target_date: str = None) -> List[Dict]:
        """Get all absences for a specific date"""
        if target_date is None:
            target_date = date.today().isoformat()
        
        absences = []
        if target_date in self.absences:
            for staff_id in self.absences[target_date]:
                member = self.staff.get(staff_id)
                if member:
                    absences.append({
                        "staff_id": staff_id,
                        "staff_name": member.name,
                        "role": member.role,
                        "date": target_date
                    })
        
        return absences
    
    def get_staff_utilization(self) -> Dict[str, any]:
        """Get staff utilization metrics"""
        total_staff = len(self.staff)
        active_staff = len([m for m in self.staff.values() if m.status == "active"])
        
        # Calculate average shifts per staff member
        total_shifts = sum(len(member.shifts) for member in self.staff.values())
        avg_shifts_per_staff = total_shifts / total_staff if total_staff > 0 else 0
        
        # Role distribution
        role_counts = {}
        for member in self.staff.values():
            role_counts[member.role] = role_counts.get(member.role, 0) + 1
        
        return {
            "total_staff": total_staff,
            "active_staff": active_staff,
            "total_shifts": total_shifts,
            "avg_shifts_per_staff": avg_shifts_per_staff,
            "role_distribution": role_counts
        }
