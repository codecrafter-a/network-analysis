"""
Update scheduler that decides when to schedule updates based on priority.
"""
import time
import threading
from queue import Queue
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from car_monitoring.car_simulator import UpdateNotification, UpdatePriority


class UpdateScheduler:
    """
    Schedules updates based on their priority and nature.
    Critical updates are scheduled immediately, others can be deferred.
    """
    
    def __init__(self, car_id: str):
        self.car_id = car_id
        self.pending_updates: Dict[str, UpdateNotification] = {}
        self.scheduled_updates: List[tuple] = []  # (timestamp, update_id)
        self.update_queue = Queue()
        self.running = False
        self.worker_thread = None
        self.callbacks: List[callable] = []
    
    def register_callback(self, callback: callable):
        """Register callback for when updates are ready to be applied."""
        self.callbacks.append(callback)
    
    def receive_update(self, update: UpdateNotification):
        """Receive an update notification from monitoring service."""
        self.pending_updates[update.update_id] = update
        self._schedule_update(update)
    
    def _schedule_update(self, update: UpdateNotification):
        """Schedule an update based on its priority."""
        now = datetime.now()
        
        if update.priority == UpdatePriority.CRITICAL or update.requires_immediate_action:
            # Schedule immediately
            schedule_time = now
            print(f"[{self.car_id}] CRITICAL update scheduled immediately: {update.update_type}")
        elif update.priority == UpdatePriority.HIGH:
            # Schedule within 1 minute
            schedule_time = now + timedelta(seconds=60)
            print(f"[{self.car_id}] HIGH priority update scheduled in 1 minute: {update.update_type}")
        elif update.priority == UpdatePriority.MEDIUM:
            # Schedule within 5 minutes
            schedule_time = now + timedelta(minutes=5)
            print(f"[{self.car_id}] MEDIUM priority update scheduled in 5 minutes: {update.update_type}")
        else:  # LOW
            # Schedule within 30 minutes or next maintenance window
            schedule_time = now + timedelta(minutes=30)
            print(f"[{self.car_id}] LOW priority update scheduled in 30 minutes: {update.update_type}")
        
        self.scheduled_updates.append((schedule_time, update.update_id))
        self.scheduled_updates.sort(key=lambda x: x[0])  # Sort by time
    
    def start(self):
        """Start the scheduler worker thread."""
        if self.running:
            return
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
    
    def stop(self):
        """Stop the scheduler worker thread."""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=2.0)
    
    def _worker_loop(self):
        """Worker loop that processes scheduled updates."""
        while self.running:
            try:
                now = datetime.now()
                
                # Check for updates that are ready
                ready_updates = []
                remaining_updates = []
                
                for schedule_time, update_id in self.scheduled_updates:
                    if schedule_time <= now:
                        ready_updates.append(update_id)
                    else:
                        remaining_updates.append((schedule_time, update_id))
                
                self.scheduled_updates = remaining_updates
                
                # Process ready updates
                for update_id in ready_updates:
                    if update_id in self.pending_updates:
                        update = self.pending_updates.pop(update_id)
                        self._apply_update(update)
                
                # Sleep until next scheduled update or 1 second
                if self.scheduled_updates:
                    next_time = self.scheduled_updates[0][0]
                    sleep_time = max(0, (next_time - datetime.now()).total_seconds())
                    sleep_time = min(sleep_time, 1.0)  # Check at least every second
                else:
                    sleep_time = 1.0
                
                time.sleep(sleep_time)
                
            except Exception as e:
                print(f"Error in scheduler worker loop: {e}")
                time.sleep(1.0)
    
    def _apply_update(self, update: UpdateNotification):
        """Apply an update and notify callbacks."""
        print(f"[{self.car_id}] Applying update: {update.update_type} - {update.description}")
        
        for callback in self.callbacks:
            try:
                callback(update)
            except Exception as e:
                print(f"Error in update callback: {e}")
    
    def get_pending_count(self) -> int:
        """Get count of pending updates."""
        return len(self.pending_updates)
    
    def get_scheduled_count(self) -> int:
        """Get count of scheduled updates."""
        return len(self.scheduled_updates)

