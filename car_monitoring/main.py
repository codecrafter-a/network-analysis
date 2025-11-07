"""
Main entry point for car monitoring system.
"""
import sys
import os
import time
import threading

# Add parent directory to path to allow imports when running from this directory
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from car_monitoring.car_simulator import CarSimulator, UpdatePriority
from car_monitoring.monitoring_client import MonitoringClient
from car_monitoring.update_scheduler import UpdateScheduler


def simulate_car_system(car_id: str, duration: int = 30):
    """Simulate a complete car system with monitoring."""
    print(f"\n{'='*60}")
    print(f"Starting Car System: {car_id}")
    print(f"{'='*60}")
    
    # Create components
    car = CarSimulator(car_id)
    client = MonitoringClient("http://monitoring-service.com", max_requests_per_second=10)
    scheduler = UpdateScheduler(car_id)
    
    # Register callbacks
    def on_update_received(update):
        """Callback when update is received from monitoring service."""
        scheduler.receive_update(update)
    
    def on_update_ready(update):
        """Callback when update is ready to be applied."""
        print(f"\n[{car_id}] UPDATE READY TO APPLY:")
        print(f"  Type: {update.update_type}")
        print(f"  Priority: {update.priority.value}")
        print(f"  Description: {update.description}")
        print(f"  Immediate Action: {update.requires_immediate_action}")
        # In real system, this would trigger actual update process
    
    client.register_callback(car_id, on_update_received)
    scheduler.register_callback(on_update_ready)
    
    # Start services
    client.start()
    scheduler.start()
    
    # Simulate car sending data
    last_send_time = 0
    start_time = time.time()
    
    print(f"\n[{car_id}] Car system running...")
    print(f"[{car_id}] Sending data to monitoring service every 5 seconds")
    print(f"[{car_id}] Monitoring service rate limit: 10 requests/second\n")
    
    try:
        while time.time() - start_time < duration:
            if car.should_send_data(last_send_time, interval=5.0):
                car_data = car.generate_car_data()
                
                # Determine priority for request
                priority = 5  # Normal
                if car_data.engine_temp > 100 or car_data.battery_voltage < 12.5:
                    priority = 1  # Critical
                elif car_data.fuel_level < 20:
                    priority = 3  # High
                
                print(f"[{car_id}] Sending data: speed={car_data.speed:.1f}km/h, "
                      f"temp={car_data.engine_temp:.1f}°C, fuel={car_data.fuel_level:.1f}%")
                
                client.send_car_data(car_data, priority=priority)
                last_send_time = time.time()
            
            time.sleep(1)
            
            # Print status
            if int(time.time()) % 10 == 0:
                print(f"\n[{car_id}] Status: "
                      f"Pending updates: {scheduler.get_pending_count()}, "
                      f"Scheduled: {scheduler.get_scheduled_count()}")
    
    except KeyboardInterrupt:
        print(f"\n[{car_id}] Shutting down...")
    finally:
        client.stop()
        scheduler.stop()
        print(f"[{car_id}] Car system stopped")


def main():
    """Main function demonstrating multiple cars."""
    print("=" * 60)
    print("Car Monitoring System")
    print("=" * 60)
    print("\nThis system simulates cars sending data to a rate-limited")
    print("monitoring service and handling update notifications.")
    print("\nFeatures:")
    print("  - Rate-limited client (10 req/sec)")
    print("  - Priority-based request queuing")
    print("  - Update scheduling based on priority")
    print("  - Critical updates scheduled immediately")
    print("  - Non-critical updates can be deferred")
    
    # Simulate single car
    simulate_car_system("CAR_001", duration=60)
    
    # Uncomment to simulate multiple cars
    # print("\n\nSimulating multiple cars...")
    # threads = []
    # for i in range(3):
    #     car_id = f"CAR_{i+1:03d}"
    #     thread = threading.Thread(
    #         target=simulate_car_system,
    #         args=(car_id, 30),
    #         daemon=True
    #     )
    #     thread.start()
    #     threads.append(thread)
    #     time.sleep(2)  # Stagger starts
    # 
    # for thread in threads:
    #     thread.join()


if __name__ == "__main__":
    main()

