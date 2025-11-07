"""
Robust weather alert system for truck fleet.
Handles critical weather events and ensures immediate notification to drivers.
"""
import time
import threading
from typing import Dict, List, Set
from queue import Queue, PriorityQueue
from dataclasses import dataclass
from datetime import datetime
from weather_alert.weather_service import WeatherService, WeatherAlert, WeatherSeverity
from weather_alert.fleet_manager import FleetManager, Truck, Operator


class AlertDeliveryStatus:
    """Status of alert delivery."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    ACKNOWLEDGED = "acknowledged"


@dataclass
class AlertDelivery:
    """Represents an alert delivery to a truck/operator."""
    alert_id: str
    truck_id: str
    operator_id: str
    alert: WeatherAlert
    priority: int  # Lower = higher priority
    timestamp: datetime
    status: str = AlertDeliveryStatus.PENDING
    retry_count: int = 0
    delivery_methods: List[str] = None  # ["sms", "push", "email", "in_cab"]


class WeatherAlertSystem:
    """
    Robust weather alert system that ensures critical alerts reach drivers immediately.
    """
    
    def __init__(self, weather_service: WeatherService, fleet_manager: FleetManager):
        self.weather_service = weather_service
        self.fleet_manager = fleet_manager
        self.alert_queue = PriorityQueue()
        self.delivery_history: Dict[str, List[AlertDelivery]] = {}
        self.running = False
        self.worker_thread = None
        self.monitor_thread = None
        self.alert_callbacks: List[callable] = []
        
        # Delivery channels (simulated)
        self.delivery_channels = {
            "sms": self._send_sms,
            "push": self._send_push_notification,
            "email": self._send_email,
            "in_cab": self._send_in_cab_alert
        }
    
    def register_callback(self, callback: callable):
        """Register callback for alert deliveries."""
        self.alert_callbacks.append(callback)
    
    def start(self):
        """Start the alert system."""
        if self.running:
            return
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.worker_thread.start()
        self.monitor_thread.start()
    
    def stop(self):
        """Stop the alert system."""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=2.0)
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
    
    def _monitor_loop(self):
        """Monitor weather alerts and check for trucks in affected areas."""
        while self.running:
            try:
                # Cleanup expired alerts
                self.weather_service.cleanup_expired_alerts()
                
                # Check each active alert
                for alert in self.weather_service.active_alerts.values():
                    # Find trucks in affected area
                    trucks_in_area = self.fleet_manager.get_trucks_in_area(
                        alert.location,
                        radius_km=alert.radius_km
                    )
                    
                    # Create alert deliveries for each truck
                    for truck in trucks_in_area:
                        if truck.status.value not in ["out_of_service", "maintenance"]:
                            self._create_alert_delivery(truck, alert)
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                print(f"Error in monitor loop: {e}")
                time.sleep(5)
    
    def _create_alert_delivery(self, truck: Truck, alert: WeatherAlert):
        """Create an alert delivery for a truck."""
        # Check if already delivered
        delivery_key = f"{alert.alert_id}_{truck.truck_id}"
        if delivery_key in self.delivery_history:
            # Check if already successfully delivered
            if any(d.status == AlertDeliveryStatus.DELIVERED 
                   for d in self.delivery_history[delivery_key]):
                return
        
        # Determine priority
        if alert.severity == WeatherSeverity.CRITICAL:
            priority = 1
        elif alert.severity == WeatherSeverity.HIGH:
            priority = 2
        elif alert.severity == WeatherSeverity.MEDIUM:
            priority = 5
        else:
            priority = 10
        
        # Determine delivery methods based on severity
        if alert.severity == WeatherSeverity.CRITICAL:
            delivery_methods = ["in_cab", "sms", "push"]  # Multiple channels
        elif alert.severity == WeatherSeverity.HIGH:
            delivery_methods = ["in_cab", "push"]
        else:
            delivery_methods = ["push"]
        
        operator = None
        if truck.operator_id:
            operator = self.fleet_manager.get_operator(truck.operator_id)
        
        delivery = AlertDelivery(
            alert_id=alert.alert_id,
            truck_id=truck.truck_id,
            operator_id=truck.operator_id or "UNKNOWN",
            alert=alert,
            priority=priority,
            timestamp=datetime.now(),
            delivery_methods=delivery_methods
        )
        
        # Queue for delivery
        self.alert_queue.put((priority, time.time(), delivery))
        
        # Track in history
        if delivery_key not in self.delivery_history:
            self.delivery_history[delivery_key] = []
        self.delivery_history[delivery_key].append(delivery)
    
    def _worker_loop(self):
        """Worker loop that processes alert deliveries."""
        while self.running:
            try:
                # Get next delivery (non-blocking)
                try:
                    priority, _, delivery = self.alert_queue.get(timeout=0.1)
                except:
                    continue
                
                # Deliver alert through all specified channels
                success = False
                for method in delivery.delivery_methods:
                    if method in self.delivery_channels:
                        try:
                            result = self.delivery_channels[method](delivery)
                            if result:
                                success = True
                                delivery.status = AlertDeliveryStatus.SENT
                        except Exception as e:
                            print(f"Error delivering via {method}: {e}")
                
                if success:
                    delivery.status = AlertDeliveryStatus.DELIVERED
                    print(f"\n✓ Alert delivered to {delivery.truck_id}: {delivery.alert.description}")
                else:
                    # Retry logic for critical alerts
                    if delivery.alert.severity == WeatherSeverity.CRITICAL and delivery.retry_count < 3:
                        delivery.retry_count += 1
                        delivery.priority = 1  # Keep high priority
                        self.alert_queue.put((delivery.priority, time.time(), delivery))
                        print(f"⚠ Retrying critical alert delivery to {delivery.truck_id} (attempt {delivery.retry_count})")
                    else:
                        delivery.status = AlertDeliveryStatus.FAILED
                        print(f"✗ Failed to deliver alert to {delivery.truck_id}")
                
                # Notify callbacks
                for callback in self.alert_callbacks:
                    try:
                        callback(delivery)
                    except Exception as e:
                        print(f"Error in alert callback: {e}")
                
            except Exception as e:
                print(f"Error in worker loop: {e}")
                time.sleep(0.1)
    
    def _send_sms(self, delivery: AlertDelivery) -> bool:
        """Send SMS alert (simulated)."""
        operator = self.fleet_manager.get_operator(delivery.operator_id)
        if operator:
            print(f"  → SMS to {operator.phone}: {delivery.alert.description}")
            time.sleep(0.1)  # Simulate network delay
            return True
        return False
    
    def _send_push_notification(self, delivery: AlertDelivery) -> bool:
        """Send push notification (simulated)."""
        print(f"  → Push notification to truck {delivery.truck_id}")
        time.sleep(0.05)
        return True
    
    def _send_email(self, delivery: AlertDelivery) -> bool:
        """Send email alert (simulated)."""
        operator = self.fleet_manager.get_operator(delivery.operator_id)
        if operator:
            print(f"  → Email to {operator.email}: {delivery.alert.description}")
            time.sleep(0.2)
            return True
        return False
    
    def _send_in_cab_alert(self, delivery: AlertDelivery) -> bool:
        """Send in-cab alert (highest priority, immediate)."""
        print(f"  → IN-CAB ALERT to truck {delivery.truck_id}: "
              f"{delivery.alert.recommended_action}")
        time.sleep(0.01)  # Fastest delivery
        return True
    
    def get_alert_statistics(self) -> Dict:
        """Get statistics about alert deliveries."""
        total = 0
        delivered = 0
        failed = 0
        pending = 0
        
        for deliveries in self.delivery_history.values():
            for delivery in deliveries:
                total += 1
                if delivery.status == AlertDeliveryStatus.DELIVERED:
                    delivered += 1
                elif delivery.status == AlertDeliveryStatus.FAILED:
                    failed += 1
                elif delivery.status == AlertDeliveryStatus.PENDING:
                    pending += 1
        
        return {
            "total_deliveries": total,
            "delivered": delivered,
            "failed": failed,
            "pending": pending,
            "success_rate": delivered / total if total > 0 else 0.0
        }

