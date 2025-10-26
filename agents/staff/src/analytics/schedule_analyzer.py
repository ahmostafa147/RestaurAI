"""
Schedule analyzer for staff management - analyzes coverage and utilization patterns
"""

import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from backend.src.core.staff_manager import StaffManager
from backend.src.models.staff import StaffMember, Shift


@dataclass
class CoverageMetrics:
    """Metrics for shift coverage analysis"""
    day_of_week: str
    time_slot: str
    total_staff: int
    roles_covered: List[str]
    coverage_score: float  # 0-1 scale
    is_understaffed: bool
    is_overstaffed: bool


@dataclass
class UtilizationMetrics:
    """Metrics for individual staff utilization"""
    staff_id: int
    staff_name: str
    role: str
    total_hours_per_week: float
    consecutive_days: int
    is_overworked: bool
    is_underutilized: bool
    work_pattern_score: float  # 0-1 scale


class ScheduleAnalyzer:
    """Analyzes staff schedules for coverage gaps and utilization patterns"""
    
    def __init__(self):
        """Initialize the schedule analyzer"""
        self.time_slots = [
            ("06:00", "10:00"),  # Early morning
            ("10:00", "14:00"),  # Lunch
            ("14:00", "18:00"),  # Afternoon
            ("18:00", "22:00"),  # Dinner
            ("22:00", "02:00")   # Late night
        ]
        
        # Role demand expectations (staff needed per time slot)
        self.role_demands = {
            "chef": {"06:00-10:00": 1, "10:00-14:00": 2, "14:00-18:00": 1, "18:00-22:00": 2, "22:00-02:00": 1},
            "cook": {"06:00-10:00": 1, "10:00-14:00": 2, "14:00-18:00": 1, "18:00-22:00": 2, "22:00-02:00": 1},
            "waiter": {"06:00-10:00": 1, "10:00-14:00": 3, "14:00-18:00": 1, "18:00-22:00": 4, "22:00-02:00": 2},
            "server": {"06:00-10:00": 1, "10:00-14:00": 3, "14:00-18:00": 1, "18:00-22:00": 4, "22:00-02:00": 2},
            "host": {"06:00-10:00": 0, "10:00-14:00": 1, "14:00-18:00": 0, "18:00-22:00": 1, "22:00-02:00": 0},
            "bartender": {"06:00-10:00": 0, "10:00-14:00": 1, "14:00-18:00": 0, "18:00-22:00": 2, "22:00-02:00": 1},
            "manager": {"06:00-10:00": 0, "10:00-14:00": 1, "14:00-18:00": 0, "18:00-22:00": 1, "22:00-02:00": 0}
        }
    
    def analyze_coverage(self, restaurant_key: str) -> List[CoverageMetrics]:
        """
        Analyze coverage for all time slots across the week
        
        Args:
            restaurant_key: Restaurant identifier
            
        Returns:
            List of coverage metrics for each day/time combination
        """
        staff_manager = StaffManager(restaurant_key)
        coverage_metrics = []
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for day in days:
            for start_time, end_time in self.time_slots:
                time_slot = f"{start_time}-{end_time}"
                
                # Get staff working during this time slot
                available_staff = staff_manager.get_available_staff(day, start_time)
                
                # Count staff by role
                role_counts = {}
                roles_covered = []
                
                for member in available_staff:
                    # Extract role type from descriptive role
                    role_type = self._extract_role_type(member.role)
                    role_counts[role_type] = role_counts.get(role_type, 0) + 1
                    roles_covered.append(role_type)
                
                # Calculate coverage score
                coverage_score = self._calculate_coverage_score(role_counts, time_slot)
                
                # Determine if understaffed/overstaffed
                total_demand = sum(self.role_demands.get(role, {}).get(time_slot, 0) for role in role_counts.keys())
                total_staff = len(available_staff)
                
                is_understaffed = total_staff < total_demand * 0.8  # 20% buffer
                is_overstaffed = total_staff > total_demand * 1.3  # 30% buffer
                
                coverage_metrics.append(CoverageMetrics(
                    day_of_week=day,
                    time_slot=time_slot,
                    total_staff=total_staff,
                    roles_covered=list(set(roles_covered)),
                    coverage_score=coverage_score,
                    is_understaffed=is_understaffed,
                    is_overstaffed=is_overstaffed
                ))
        
        return coverage_metrics
    
    def analyze_utilization(self, restaurant_key: str) -> List[UtilizationMetrics]:
        """
        Analyze individual staff utilization patterns
        
        Args:
            restaurant_key: Restaurant identifier
            
        Returns:
            List of utilization metrics for each staff member
        """
        staff_manager = StaffManager(restaurant_key)
        utilization_metrics = []
        
        for member in staff_manager.staff.values():
            if member.status != "active":
                continue
            
            # Calculate total hours per week
            total_hours = self._calculate_weekly_hours(member)
            
            # Calculate consecutive days
            consecutive_days = self._calculate_consecutive_days(member)
            
            # Determine work pattern issues
            is_overworked = total_hours > 50 or consecutive_days > 5
            is_underutilized = total_hours < 20
            
            # Calculate work pattern score
            work_pattern_score = self._calculate_work_pattern_score(total_hours, consecutive_days)
            
            utilization_metrics.append(UtilizationMetrics(
                staff_id=member.id,
                staff_name=member.name,
                role=member.role,
                total_hours_per_week=total_hours,
                consecutive_days=consecutive_days,
                is_overworked=is_overworked,
                is_underutilized=is_underutilized,
                work_pattern_score=work_pattern_score
            ))
        
        return utilization_metrics
    
    def identify_weaknesses(self, restaurant_key: str) -> Dict[str, Any]:
        """
        Identify schedule weaknesses and coverage gaps
        
        Args:
            restaurant_key: Restaurant identifier
            
        Returns:
            Dictionary containing weakness analysis
        """
        coverage_metrics = self.analyze_coverage(restaurant_key)
        utilization_metrics = self.analyze_utilization(restaurant_key)
        
        # Find understaffed time slots
        understaffed_slots = [
            metric for metric in coverage_metrics 
            if metric.is_understaffed
        ]
        
        # Find overstaffed time slots
        overstaffed_slots = [
            metric for metric in coverage_metrics 
            if metric.is_overstaffed
        ]
        
        # Find overworked staff
        overworked_staff = [
            metric for metric in utilization_metrics 
            if metric.is_overworked
        ]
        
        # Find underutilized staff
        underutilized_staff = [
            metric for metric in utilization_metrics 
            if metric.is_underutilized
        ]
        
        # Calculate overall coverage score
        overall_coverage = sum(metric.coverage_score for metric in coverage_metrics) / len(coverage_metrics)
        
        return {
            "overall_coverage_score": overall_coverage,
            "understaffed_slots": [
                {
                    "day": slot.day_of_week,
                    "time": slot.time_slot,
                    "staff_count": slot.total_staff,
                    "roles": slot.roles_covered,
                    "coverage_score": slot.coverage_score
                }
                for slot in understaffed_slots
            ],
            "overstaffed_slots": [
                {
                    "day": slot.day_of_week,
                    "time": slot.time_slot,
                    "staff_count": slot.total_staff,
                    "roles": slot.roles_covered,
                    "coverage_score": slot.coverage_score
                }
                for slot in overstaffed_slots
            ],
            "overworked_staff": [
                {
                    "staff_id": staff.staff_id,
                    "name": staff.staff_name,
                    "role": staff.role,
                    "weekly_hours": staff.total_hours_per_week,
                    "consecutive_days": staff.consecutive_days,
                    "pattern_score": staff.work_pattern_score
                }
                for staff in overworked_staff
            ],
            "underutilized_staff": [
                {
                    "staff_id": staff.staff_id,
                    "name": staff.staff_name,
                    "role": staff.role,
                    "weekly_hours": staff.total_hours_per_week,
                    "pattern_score": staff.work_pattern_score
                }
                for staff in underutilized_staff
            ],
            "total_weaknesses": len(understaffed_slots) + len(overworked_staff) + len(underutilized_staff)
        }
    
    def suggest_absence_replacements(self, restaurant_key: str, absent_staff_id: int, 
                                   absence_date: str) -> List[Dict[str, Any]]:
        """
        Suggest replacements when someone calls in absent
        
        Args:
            restaurant_key: Restaurant identifier
            absent_staff_id: ID of absent staff member
            absence_date: Date of absence (YYYY-MM-DD)
            
        Returns:
            List of suggested replacements with priority scores
        """
        staff_manager = StaffManager(restaurant_key)
        
        # Get absent staff member
        absent_member = staff_manager.get_staff_member(absent_staff_id)
        if not absent_member:
            return []
        
        # Determine day of week for absence
        absence_day = datetime.strptime(absence_date, "%Y-%m-%d").strftime("%A")
        
        # Get all staff who could potentially cover
        all_staff = staff_manager.get_staff()
        suggestions = []
        
        for member_data in all_staff:
            member = StaffManager(restaurant_key).get_staff_member(member_data["id"])
            if not member or member.id == absent_staff_id or member.status != "active":
                continue
            
            # Check if they're already scheduled on this day
            works_on_day = any(shift.day_of_week.lower() == absence_day.lower() for shift in member.shifts)
            
            # Calculate compatibility score
            compatibility_score = self._calculate_compatibility_score(absent_member, member)
            
            # Check availability
            is_available = not works_on_day
            
            suggestions.append({
                "staff_id": member.id,
                "name": member.name,
                "role": member.role,
                "compatibility_score": compatibility_score,
                "is_available": is_available,
                "priority": self._calculate_priority_score(absent_member, member, is_available)
            })
        
        # Sort by priority score (highest first)
        suggestions.sort(key=lambda x: x["priority"], reverse=True)
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def _extract_role_type(self, descriptive_role: str) -> str:
        """Extract role type from descriptive role string"""
        role_lower = descriptive_role.lower()
        
        if "chef" in role_lower or "head chef" in role_lower:
            return "chef"
        elif "cook" in role_lower or "line cook" in role_lower:
            return "cook"
        elif "waiter" in role_lower or "server" in role_lower:
            return "waiter"
        elif "host" in role_lower or "hostess" in role_lower:
            return "host"
        elif "bartender" in role_lower or "bar" in role_lower:
            return "bartender"
        elif "manager" in role_lower or "supervisor" in role_lower:
            return "manager"
        else:
            return "other"
    
    def _calculate_coverage_score(self, role_counts: Dict[str, int], time_slot: str) -> float:
        """Calculate coverage score for a time slot"""
        total_score = 0.0
        total_roles = 0
        
        for role, count in role_counts.items():
            if role in self.role_demands:
                demand = self.role_demands[role].get(time_slot, 0)
                if demand > 0:
                    # Score based on how close we are to demand
                    ratio = min(count / demand, 1.0) if demand > 0 else 0.0
                    total_score += ratio
                    total_roles += 1
        
        return total_score / total_roles if total_roles > 0 else 0.0
    
    def _calculate_weekly_hours(self, member: StaffMember) -> float:
        """Calculate total hours per week for a staff member"""
        total_hours = 0.0
        
        for shift in member.shifts:
            start_time = datetime.strptime(shift.start_time, "%H:%M")
            end_time = datetime.strptime(shift.end_time, "%H:%M")
            
            # Handle overnight shifts
            if end_time < start_time:
                end_time += timedelta(days=1)
            
            hours = (end_time - start_time).total_seconds() / 3600
            total_hours += hours
        
        return total_hours
    
    def _calculate_consecutive_days(self, member: StaffMember) -> int:
        """Calculate maximum consecutive days worked"""
        days = [shift.day_of_week.lower() for shift in member.shifts]
        day_order = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        
        max_consecutive = 0
        current_consecutive = 0
        
        for day in day_order:
            if day in days:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return max_consecutive
    
    def _calculate_work_pattern_score(self, weekly_hours: float, consecutive_days: int) -> float:
        """Calculate work pattern score (0-1, higher is better)"""
        # Ideal: 35-45 hours per week, max 5 consecutive days
        hours_score = 1.0 - abs(weekly_hours - 40) / 40  # Penalty for deviation from 40 hours
        days_score = 1.0 - max(0, consecutive_days - 5) / 7  # Penalty for >5 consecutive days
        
        return max(0, (hours_score + days_score) / 2)
    
    def _calculate_compatibility_score(self, absent_member: StaffMember, candidate: StaffMember) -> float:
        """Calculate compatibility score between absent member and candidate"""
        absent_role_type = self._extract_role_type(absent_member.role)
        candidate_role_type = self._extract_role_type(candidate.role)
        
        # Same role type gets highest score
        if absent_role_type == candidate_role_type:
            return 1.0
        
        # Cross-role compatibility matrix
        compatibility_matrix = {
            "chef": {"cook": 0.8, "manager": 0.3},
            "cook": {"chef": 0.8, "manager": 0.3},
            "waiter": {"server": 1.0, "host": 0.6, "bartender": 0.4},
            "server": {"waiter": 1.0, "host": 0.6, "bartender": 0.4},
            "host": {"waiter": 0.6, "server": 0.6, "manager": 0.5},
            "bartender": {"waiter": 0.4, "server": 0.4},
            "manager": {"chef": 0.3, "cook": 0.3, "host": 0.5}
        }
        
        return compatibility_matrix.get(absent_role_type, {}).get(candidate_role_type, 0.1)
    
    def _calculate_priority_score(self, absent_member: StaffMember, candidate: StaffMember, is_available: bool) -> float:
        """Calculate priority score for replacement suggestions"""
        compatibility = self._calculate_compatibility_score(absent_member, candidate)
        availability_bonus = 1.0 if is_available else 0.3
        
        return compatibility * availability_bonus
