import psutil
import time
from collections import deque
import threading

class NetworkUsageMonitor:
    def __init__(self):
        self.upload_speeds = deque(maxlen=100)
        self.download_speeds = deque(maxlen=100)
        self.is_monitoring = False
        self.monitor_thread = None
        self.last_upload = 0
        self.last_download = 0
        self.last_time = time.time()
        
    def start_monitoring(self):
        """Start network usage monitoring"""
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_network)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop network usage monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
    
    def _monitor_network(self):
        """Monitor network usage in a loop"""
        while self.is_monitoring:
            try:
                # Get network I/O statistics
                net_io = psutil.net_io_counters()
                current_time = time.time()
                time_delta = current_time - self.last_time
                
                if time_delta > 0:
                    # Calculate speeds in KB/s
                    upload_speed = (net_io.bytes_sent - self.last_upload) / time_delta / 1024
                    download_speed = (net_io.bytes_recv - self.last_download) / time_delta / 1024
                    
                    self.upload_speeds.append(upload_speed)
                    self.download_speeds.append(download_speed)
                    
                    self.last_upload = net_io.bytes_sent
                    self.last_download = net_io.bytes_recv
                    self.last_time = current_time
                
                time.sleep(1)  # Update every second
                
            except Exception as e:
                print(f"Error monitoring network: {e}")
                time.sleep(5)
    
    def get_network_stats(self):
        """Get current network statistics"""
        if not self.upload_speeds or not self.download_speeds:
            return {
                'upload_speed': 0,
                'download_speed': 0,
                'upload_history': [0] * 50,
                'download_history': [0] * 50
            }
        
        return {
            'upload_speed': self.upload_speeds[-1] if self.upload_speeds else 0,
            'download_speed': self.download_speeds[-1] if self.download_speeds else 0,
            'upload_history': list(self.upload_speeds),
            'download_history': list(self.download_speeds)
        }