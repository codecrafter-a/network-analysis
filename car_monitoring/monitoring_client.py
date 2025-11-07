"""
Client for interacting with the monitoring service.
Handles rate limiting and request queuing.
"""
import time
import threading
import random
from queue import Queue, PriorityQueue
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from car_monitoring.car_simulator import CarData, UpdateNotification, UpdatePriority


@dataclass
class Request:
    """Represents a request to the monitoring service."""
    car_id: str
    data: CarData
    priority: int  # Lower number = higher priority
    timestamp: float
    retry_count: int = 0


class MonitoringClient:
    """
    Client for monitoring service with rate limiting and priority queuing.
    """
    
    def __init__(self, service_url: str, max_requests_per_second: int = 10):
        self.service_url = service_url
        self.max_requests_per_second = max_requests_per_second
        self.request_queue = PriorityQueue()
        self.response_queue = Queue()
        self.rate_limiter = RateLimiter(max_requests_per_second)
        self.running = False
        self.worker_thread = None
        self.callbacks: Dict[str, List[Callable]] = {}  # car_id -> callbacks
    
    def register_callback(self, car_id: str, callback: Callable[[UpdateNotification], None]):
        """Register a callback for update notifications."""
        if car_id not in self.callbacks:
            self.callbacks[car_id] = []
        self.callbacks[car_id].append(callback)
    
    def send_car_data(self, car_data: CarData, priority: int = 5) -> bool:
        """
        Queue car data to be sent to monitoring service.
        Priority: 1=critical, 5=normal, 10=low
        """
        request = Request(
            car_id=car_data.car_id,
            data=car_data,
            priority=priority,
            timestamp=time.time()
        )
        self.request_queue.put((priority, time.time(), request))
        return True
    
    def start(self):
        """Start the client worker thread."""
        if self.running:
            return
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
    
    def stop(self):
        """Stop the client worker thread."""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=2.0)
    
    def _worker_loop(self):
        """Worker loop that processes requests with rate limiting."""
        while self.running:
            try:
                # Get next request (non-blocking)
                try:
                    priority, _, request = self.request_queue.get(timeout=0.1)
                except:
                    continue
                
                # Wait for rate limiter
                self.rate_limiter.acquire()
                
                # Send request to monitoring service
                response = self._send_to_service(request)
                
                if response:
                    # Process response
                    self._handle_response(response)
                else:
                    # Retry logic
                    if request.retry_count < 3:
                        request.retry_count += 1
                        request.priority += 1  # Lower priority for retries
                        self.request_queue.put((request.priority, time.time(), request))
                
            except Exception as e:
                print(f"Error in worker loop: {e}")
                time.sleep(0.1)
    
    def _send_to_service(self, request: Request) -> Optional[UpdateNotification]:
        """
        Send request to monitoring service (simulated).
        In real implementation, this would be an HTTP request.
        """
        # Simulate network delay
        time.sleep(0.05)
        
        # Simulate monitoring service response
        # The service analyzes the car data and returns updates
        car_data = request.data
        
        updates = []
        
        # Critical updates
        if car_data.engine_temp > 105:
            updates.append(UpdateNotification(
                car_id=car_data.car_id,
                update_id=f"UPDATE_{int(time.time())}",
                priority=UpdatePriority.CRITICAL,
                update_type="engine_overheat",
                description="Engine temperature critical - immediate attention required",
                timestamp=datetime.now(),
                requires_immediate_action=True
            ))
        
        if car_data.battery_voltage < 12.0:
            updates.append(UpdateNotification(
                car_id=car_data.car_id,
                update_id=f"UPDATE_{int(time.time())}",
                priority=UpdatePriority.CRITICAL,
                update_type="battery_low",
                description="Battery voltage low - risk of breakdown",
                timestamp=datetime.now(),
                requires_immediate_action=True
            ))
        
        # High priority updates
        if car_data.fuel_level < 15:
            updates.append(UpdateNotification(
                car_id=car_data.car_id,
                update_id=f"UPDATE_{int(time.time())}",
                priority=UpdatePriority.HIGH,
                update_type="low_fuel",
                description="Fuel level low",
                timestamp=datetime.now(),
                requires_immediate_action=False
            ))
        
        # Medium priority updates
        if car_data.error_codes:
            updates.append(UpdateNotification(
                car_id=car_data.car_id,
                update_id=f"UPDATE_{int(time.time())}",
                priority=UpdatePriority.MEDIUM,
                update_type="error_codes",
                description=f"Diagnostic codes detected: {', '.join(car_data.error_codes)}",
                timestamp=datetime.now(),
                requires_immediate_action=False
            ))
        
        # Low priority updates (maintenance reminders, etc.)
        if random.random() < 0.1:  # 10% chance
            updates.append(UpdateNotification(
                car_id=car_data.car_id,
                update_id=f"UPDATE_{int(time.time())}",
                priority=UpdatePriority.LOW,
                update_type="maintenance_reminder",
                description="Scheduled maintenance due soon",
                timestamp=datetime.now(),
                requires_immediate_action=False
            ))
        
        # Return first update (in real scenario, might return multiple)
        return updates[0] if updates else None
    
    def _handle_response(self, update: UpdateNotification):
        """Handle response from monitoring service."""
        if update and update.car_id in self.callbacks:
            for callback in self.callbacks[update.car_id]:
                try:
                    callback(update)
                except Exception as e:
                    print(f"Error in callback: {e}")


class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self, max_requests_per_second: int):
        self.max_requests = max_requests_per_second
        self.tokens = max_requests_per_second
        self.last_update = time.time()
        self.lock = threading.Lock()
    
    def acquire(self):
        """Acquire a token, blocking if necessary."""
        with self.lock:
            now = time.time()
            # Add tokens based on elapsed time
            elapsed = now - self.last_update
            self.tokens = min(
                self.max_requests,
                self.tokens + elapsed * self.max_requests
            )
            self.last_update = now
            
            # Wait if no tokens available
            if self.tokens < 1:
                wait_time = (1 - self.tokens) / self.max_requests
                time.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1

