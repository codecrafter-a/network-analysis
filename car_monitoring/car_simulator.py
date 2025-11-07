"""
Car simulator that generates car data and sends to monitoring service.
"""
import time
import random
import uuid
from typing import Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class UpdatePriority(Enum):
    """Priority levels for updates."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class CarData:
    """Represents data from a car."""
    car_id: str
    timestamp: datetime
    speed: float
    engine_temp: float
    fuel_level: float
    battery_voltage: float
    mileage: float
    location: tuple  # (lat, lon)
    error_codes: list = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UpdateNotification:
    """Represents an update notification from monitoring service."""
    car_id: str
    update_id: str
    priority: UpdatePriority
    update_type: str
    description: str
    timestamp: datetime
    requires_immediate_action: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class CarSimulator:
    """Simulates a car sending data to monitoring service."""
    
    def __init__(self, car_id: str = None):
        self.car_id = car_id or f"CAR_{uuid.uuid4().hex[:8].upper()}"
        self.mileage = random.uniform(0, 100000)
        self.location = (random.uniform(-90, 90), random.uniform(-180, 180))
    
    def generate_car_data(self) -> CarData:
        """Generate simulated car data."""
        return CarData(
            car_id=self.car_id,
            timestamp=datetime.now(),
            speed=random.uniform(0, 120),
            engine_temp=random.uniform(80, 110),
            fuel_level=random.uniform(0, 100),
            battery_voltage=random.uniform(11.5, 14.5),
            mileage=self.mileage + random.uniform(0, 1),
            location=self.location,
            error_codes=random.choices(
                ["P0301", "P0420", "P0171", "P0442"],
                k=random.randint(0, 2)
            ) if random.random() < 0.3 else [],
            metadata={
                "tire_pressure": [random.uniform(30, 35) for _ in range(4)],
                "brake_pad_wear": random.uniform(0, 100)
            }
        )
    
    def should_send_data(self, last_send_time: float, interval: float = 5.0) -> bool:
        """Determine if car should send data based on interval."""
        return time.time() - last_send_time >= interval

