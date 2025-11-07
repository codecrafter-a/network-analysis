"""
Weather service that provides weather data and alerts.
"""
import random
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class WeatherSeverity(Enum):
    """Severity levels for weather events."""
    CRITICAL = "critical"  # Immediate danger
    HIGH = "high"  # Significant risk
    MEDIUM = "medium"  # Moderate risk
    LOW = "low"  # Minor risk


class WeatherType(Enum):
    """Types of weather events."""
    HURRICANE = "hurricane"
    TORNADO = "tornado"
    BLIZZARD = "blizzard"
    HEAVY_RAIN = "heavy_rain"
    FOG = "fog"
    HIGH_WINDS = "high_winds"
    ICE = "ice"
    EXTREME_HEAT = "extreme_heat"
    EXTREME_COLD = "extreme_cold"


@dataclass
class WeatherAlert:
    """Represents a weather alert."""
    alert_id: str
    weather_type: WeatherType
    severity: WeatherSeverity
    location: tuple  # (lat, lon)
    radius_km: float  # Affected radius
    start_time: datetime
    end_time: datetime
    description: str
    recommended_action: str
    metadata: Dict = None


@dataclass
class LocationWeather:
    """Current weather at a location."""
    location: tuple  # (lat, lon)
    temperature: float
    conditions: str
    wind_speed: float
    visibility: float
    timestamp: datetime


class WeatherService:
    """
    Simulated weather service that provides weather data and alerts.
    In production, this would connect to a real weather API.
    """
    
    def __init__(self):
        self.active_alerts: Dict[str, WeatherAlert] = {}
        self.weather_cache: Dict[tuple, LocationWeather] = {}
    
    def get_weather_at_location(self, location: tuple) -> LocationWeather:
        """Get current weather at a location."""
        # In real implementation, this would query a weather API
        # For simulation, generate realistic weather data
        if location not in self.weather_cache:
            self.weather_cache[location] = LocationWeather(
                location=location,
                temperature=random.uniform(-10, 35),
                conditions=random.choice(["clear", "cloudy", "rainy", "snowy"]),
                wind_speed=random.uniform(0, 30),
                visibility=random.uniform(5, 20),
                timestamp=datetime.now()
            )
        return self.weather_cache[location]
    
    def check_alerts_for_location(self, location: tuple, radius_km: float = 50.0) -> List[WeatherAlert]:
        """Check for active weather alerts near a location."""
        alerts = []
        for alert in self.active_alerts.values():
            distance = self._calculate_distance(location, alert.location)
            if distance <= alert.radius_km + radius_km:
                alerts.append(alert)
        return alerts
    
    def generate_alert(self, weather_type: WeatherType, location: tuple,
                      severity: WeatherSeverity = None) -> WeatherAlert:
        """Generate a new weather alert (for simulation)."""
        if severity is None:
            # Determine severity based on weather type
            if weather_type in [WeatherType.HURRICANE, WeatherType.TORNADO]:
                severity = WeatherSeverity.CRITICAL
            elif weather_type in [WeatherType.BLIZZARD, WeatherType.ICE]:
                severity = WeatherSeverity.HIGH
            else:
                severity = WeatherSeverity.MEDIUM
        
        alert_id = f"ALERT_{int(datetime.now().timestamp())}"
        
        # Determine duration based on severity
        if severity == WeatherSeverity.CRITICAL:
            duration = timedelta(hours=2)
        elif severity == WeatherSeverity.HIGH:
            duration = timedelta(hours=4)
        else:
            duration = timedelta(hours=6)
        
        alert = WeatherAlert(
            alert_id=alert_id,
            weather_type=weather_type,
            severity=severity,
            location=location,
            radius_km=50.0 if severity == WeatherSeverity.CRITICAL else 30.0,
            start_time=datetime.now(),
            end_time=datetime.now() + duration,
            description=self._get_description(weather_type, severity),
            recommended_action=self._get_recommended_action(weather_type, severity)
        )
        
        self.active_alerts[alert_id] = alert
        return alert
    
    def _get_description(self, weather_type: WeatherType, severity: WeatherSeverity) -> str:
        """Get description for weather alert."""
        descriptions = {
            WeatherType.HURRICANE: "Hurricane conditions detected",
            WeatherType.TORNADO: "Tornado warning in effect",
            WeatherType.BLIZZARD: "Blizzard conditions - heavy snow and strong winds",
            WeatherType.HEAVY_RAIN: "Heavy rainfall expected",
            WeatherType.FOG: "Dense fog reducing visibility",
            WeatherType.HIGH_WINDS: "High wind speeds expected",
            WeatherType.ICE: "Icy road conditions",
            WeatherType.EXTREME_HEAT: "Extreme heat warning",
            WeatherType.EXTREME_COLD: "Extreme cold warning"
        }
        return descriptions.get(weather_type, "Weather alert")
    
    def _get_recommended_action(self, weather_type: WeatherType, severity: WeatherSeverity) -> str:
        """Get recommended action for weather alert."""
        if severity == WeatherSeverity.CRITICAL:
            return "STOP IMMEDIATELY - Seek shelter"
        elif severity == WeatherSeverity.HIGH:
            return "Reduce speed significantly - Consider stopping"
        elif severity == WeatherSeverity.MEDIUM:
            return "Exercise caution - Reduce speed"
        else:
            return "Monitor conditions"
    
    def _calculate_distance(self, loc1: tuple, loc2: tuple) -> float:
        """Calculate distance between two locations in km (simplified)."""
        # Simplified distance calculation (Haversine would be more accurate)
        lat_diff = abs(loc1[0] - loc2[0])
        lon_diff = abs(loc1[1] - loc2[1])
        # Rough approximation: 1 degree ≈ 111 km
        return ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111.0
    
    def cleanup_expired_alerts(self):
        """Remove expired alerts."""
        now = datetime.now()
        expired = [aid for aid, alert in self.active_alerts.items() 
                  if alert.end_time < now]
        for aid in expired:
            del self.active_alerts[aid]

