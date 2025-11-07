"""
Fleet manager that tracks trucks, operators, and maintenance records.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TruckStatus(Enum):
    """Status of a truck."""
    IN_TRANSIT = "in_transit"
    LOADING = "loading"
    UNLOADING = "unloading"
    MAINTENANCE = "maintenance"
    PARKED = "parked"
    OUT_OF_SERVICE = "out_of_service"


@dataclass
class Operator:
    """Represents a truck operator/driver."""
    operator_id: str
    name: str
    license_number: str
    phone: str
    email: str
    experience_years: int
    emergency_contact: str
    metadata: Dict = field(default_factory=dict)


@dataclass
class MaintenanceRecord:
    """Maintenance record for a truck."""
    record_id: str
    truck_id: str
    maintenance_type: str
    date: datetime
    mileage: float
    description: str
    next_maintenance_due: datetime
    cost: float = 0.0


@dataclass
class Truck:
    """Represents a truck in the fleet."""
    truck_id: str
    license_plate: str
    make: str
    model: str
    year: int
    current_location: tuple  # (lat, lon)
    status: TruckStatus
    operator_id: Optional[str] = None
    current_route: Optional[str] = None
    last_update: datetime = field(default_factory=datetime.now)
    maintenance_records: List[MaintenanceRecord] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


class FleetManager:
    """Manages fleet of trucks, operators, and maintenance records."""
    
    def __init__(self):
        self.trucks: Dict[str, Truck] = {}
        self.operators: Dict[str, Operator] = {}
        self.maintenance_records: Dict[str, List[MaintenanceRecord]] = {}
    
    def add_truck(self, truck: Truck):
        """Add a truck to the fleet."""
        self.trucks[truck.truck_id] = truck
        if truck.truck_id not in self.maintenance_records:
            self.maintenance_records[truck.truck_id] = []
    
    def add_operator(self, operator: Operator):
        """Add an operator to the system."""
        self.operators[operator.operator_id] = operator
    
    def assign_operator(self, truck_id: str, operator_id: str):
        """Assign an operator to a truck."""
        if truck_id in self.trucks and operator_id in self.operators:
            self.trucks[truck_id].operator_id = operator_id
    
    def add_maintenance_record(self, record: MaintenanceRecord):
        """Add a maintenance record for a truck."""
        if record.truck_id not in self.maintenance_records:
            self.maintenance_records[record.truck_id] = []
        self.maintenance_records[record.truck_id].append(record)
        if record.truck_id in self.trucks:
            self.trucks[record.truck_id].maintenance_records.append(record)
    
    def update_truck_location(self, truck_id: str, location: tuple):
        """Update truck's current location."""
        if truck_id in self.trucks:
            self.trucks[truck_id].current_location = location
            self.trucks[truck_id].last_update = datetime.now()
    
    def update_truck_status(self, truck_id: str, status: TruckStatus):
        """Update truck's status."""
        if truck_id in self.trucks:
            self.trucks[truck_id].status = status
    
    def get_truck(self, truck_id: str) -> Optional[Truck]:
        """Get truck by ID."""
        return self.trucks.get(truck_id)
    
    def get_operator(self, operator_id: str) -> Optional[Operator]:
        """Get operator by ID."""
        return self.operators.get(operator_id)
    
    def get_trucks_in_area(self, location: tuple, radius_km: float = 50.0) -> List[Truck]:
        """Get all trucks within a radius of a location."""
        trucks_in_area = []
        for truck in self.trucks.values():
            distance = self._calculate_distance(location, truck.current_location)
            if distance <= radius_km:
                trucks_in_area.append(truck)
        return trucks_in_area
    
    def get_trucks_by_status(self, status: TruckStatus) -> List[Truck]:
        """Get all trucks with a specific status."""
        return [truck for truck in self.trucks.values() if truck.status == status]
    
    def get_maintenance_due_soon(self, days: int = 30) -> List[Truck]:
        """Get trucks with maintenance due within specified days."""
        due_soon = []
        cutoff_date = datetime.now() + timedelta(days=days)
        
        for truck in self.trucks.values():
            if truck.maintenance_records:
                latest_record = max(truck.maintenance_records, key=lambda r: r.date)
                if latest_record.next_maintenance_due <= cutoff_date:
                    due_soon.append(truck)
        
        return due_soon
    
    def _calculate_distance(self, loc1: tuple, loc2: tuple) -> float:
        """Calculate distance between two locations in km (simplified)."""
        lat_diff = abs(loc1[0] - loc2[0])
        lon_diff = abs(loc1[1] - loc2[1])
        return ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111.0


# Import timedelta
from datetime import timedelta

