"""
Main entry point for weather alert system.
"""
import sys
import os
import time
import random
from datetime import datetime, timedelta

# Add parent directory to path to allow imports when running from this directory
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from weather_alert.weather_service import WeatherService, WeatherType, WeatherSeverity
from weather_alert.fleet_manager import FleetManager, Truck, Operator, TruckStatus, MaintenanceRecord
from weather_alert.alert_system import WeatherAlertSystem, AlertDeliveryStatus


def create_sample_fleet() -> FleetManager:
    """Create a sample fleet for demonstration."""
    fleet = FleetManager()
    
    # Create operators
    operators = [
        Operator("OP001", "John Smith", "DL12345", "+1-555-0101", "john@example.com", 5, "+1-555-0102"),
        Operator("OP002", "Jane Doe", "DL12346", "+1-555-0201", "jane@example.com", 8, "+1-555-0202"),
        Operator("OP003", "Bob Johnson", "DL12347", "+1-555-0301", "bob@example.com", 3, "+1-555-0302"),
    ]
    
    for operator in operators:
        fleet.add_operator(operator)
    
    # Create trucks
    locations = [
        (40.7128, -74.0060),  # New York
        (34.0522, -118.2437),  # Los Angeles
        (41.8781, -87.6298),   # Chicago
        (29.7604, -95.3698),   # Houston
        (33.4484, -112.0740),  # Phoenix
    ]
    
    for i in range(5):
        truck = Truck(
            truck_id=f"TRUCK_{i+1:03d}",
            license_plate=f"ABC-{i+1:04d}",
            make="Freightliner",
            model="Cascadia",
            year=2020 + (i % 3),
            current_location=locations[i],
            status=TruckStatus.IN_TRANSIT,
            operator_id=operators[i % len(operators)].operator_id
        )
        fleet.add_truck(truck)
        fleet.assign_operator(truck.truck_id, truck.operator_id)
        
        # Add maintenance record
        maintenance = MaintenanceRecord(
            record_id=f"MAINT_{i+1}",
            truck_id=truck.truck_id,
            maintenance_type="Regular Service",
            date=datetime.now() - timedelta(days=30),
            mileage=50000 + i * 10000,
            description="Oil change and inspection",
            next_maintenance_due=datetime.now() + timedelta(days=60 - i * 10),
            cost=500.0
        )
        fleet.add_maintenance_record(maintenance)
    
    return fleet


def simulate_truck_movement(fleet: FleetManager, duration: int = 60):
    """Simulate trucks moving (updating locations)."""
    import threading
    
    def move_truck(truck_id: str):
        truck = fleet.get_truck(truck_id)
        if not truck:
            return
        
        base_location = truck.current_location
        start_time = time.time()
        
        while time.time() - start_time < duration:
            # Simulate movement (small random changes)
            new_lat = base_location[0] + random.uniform(-0.1, 0.1)
            new_lon = base_location[1] + random.uniform(-0.1, 0.1)
            fleet.update_truck_location(truck_id, (new_lat, new_lon))
            time.sleep(10)  # Update every 10 seconds
    
    threads = []
    for truck_id in fleet.trucks.keys():
        thread = threading.Thread(target=move_truck, args=(truck_id,), daemon=True)
        thread.start()
        threads.append(thread)
    
    return threads


def main():
    """Main function demonstrating weather alert system."""
    print("=" * 60)
    print("Weather Alert System for Truck Fleet")
    print("=" * 60)
    print("\nThis system monitors weather conditions and ensures")
    print("critical alerts reach drivers immediately.")
    print("\nFeatures:")
    print("  - Real-time weather monitoring")
    print("  - Critical alert immediate delivery")
    print("  - Multiple delivery channels (SMS, push, in-cab)")
    print("  - Retry logic for failed deliveries")
    print("  - Fleet management integration")
    
    # Create services
    weather_service = WeatherService()
    fleet = create_sample_fleet()
    alert_system = WeatherAlertSystem(weather_service, fleet)
    
    # Register callback
    def on_alert_delivered(delivery):
        """Callback when alert is delivered."""
        if delivery.status == AlertDeliveryStatus.DELIVERED:
            operator = fleet.get_operator(delivery.operator_id)
            if operator:
                print(f"    Driver {operator.name} notified via: {', '.join(delivery.delivery_methods)}")
    
    alert_system.register_callback(on_alert_delivered)
    
    # Start system
    alert_system.start()
    
    # Simulate truck movement
    print("\nStarting truck movement simulation...")
    movement_threads = simulate_truck_movement(fleet, duration=120)
    
    print("\nFleet Status:")
    for truck in fleet.trucks.values():
        operator = fleet.get_operator(truck.operator_id) if truck.operator_id else None
        print(f"  {truck.truck_id} ({truck.license_plate}) - "
              f"Location: {truck.current_location}, "
              f"Operator: {operator.name if operator else 'None'}")
    
    # Generate weather alerts
    print("\n" + "=" * 60)
    print("Generating Weather Alerts")
    print("=" * 60)
    
    time.sleep(2)
    
    # Critical alert
    print("\n1. Generating CRITICAL weather alert (Tornado)...")
    tornado_location = (40.7128, -74.0060)  # Near New York
    tornado_alert = weather_service.generate_alert(
        WeatherType.TORNADO,
        tornado_location,
        WeatherSeverity.CRITICAL
    )
    print(f"   Alert: {tornado_alert.description}")
    print(f"   Location: {tornado_alert.location}")
    print(f"   Radius: {tornado_alert.radius_km}km")
    print(f"   Action: {tornado_alert.recommended_action}")
    
    time.sleep(5)
    
    # High priority alert
    print("\n2. Generating HIGH priority alert (Blizzard)...")
    blizzard_location = (41.8781, -87.6298)  # Near Chicago
    blizzard_alert = weather_service.generate_alert(
        WeatherType.BLIZZARD,
        blizzard_location,
        WeatherSeverity.HIGH
    )
    print(f"   Alert: {blizzard_alert.description}")
    print(f"   Location: {blizzard_alert.location}")
    
    time.sleep(5)
    
    # Medium priority alert
    print("\n3. Generating MEDIUM priority alert (Heavy Rain)...")
    rain_location = (34.0522, -118.2437)  # Near Los Angeles
    rain_alert = weather_service.generate_alert(
        WeatherType.HEAVY_RAIN,
        rain_location,
        WeatherSeverity.MEDIUM
    )
    print(f"   Alert: {rain_alert.description}")
    print(f"   Location: {rain_alert.location}")
    
    # Monitor for a while
    print("\n" + "=" * 60)
    print("Monitoring alerts and deliveries...")
    print("=" * 60)
    
    try:
        for i in range(12):  # Monitor for 60 seconds
            time.sleep(5)
            stats = alert_system.get_alert_statistics()
            if stats["total_deliveries"] > 0:
                print(f"\n[{i*5}s] Alert Statistics:")
                print(f"  Total: {stats['total_deliveries']}, "
                      f"Delivered: {stats['delivered']}, "
                      f"Failed: {stats['failed']}, "
                      f"Success Rate: {stats['success_rate']:.1%}")
    except KeyboardInterrupt:
        print("\nShutting down...")
    
    # Final statistics
    print("\n" + "=" * 60)
    print("Final Statistics")
    print("=" * 60)
    final_stats = alert_system.get_alert_statistics()
    for key, value in final_stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2%}")
        else:
            print(f"  {key}: {value}")
    
    # Stop system
    alert_system.stop()
    print("\nSystem stopped.")


if __name__ == "__main__":
    main()

