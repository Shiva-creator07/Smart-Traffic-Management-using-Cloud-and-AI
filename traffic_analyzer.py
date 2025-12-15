import numpy as np
from collections import deque
from datetime import datetime

class TrafficAnalyzer:
    def __init__(self, window_size=30):
        self.vehicle_history = deque(maxlen=window_size)
        self.density_threshold = {'low': 5, 'medium': 15, 'high': 25}
        
    def analyze_traffic(self, detections):
        """Analyze traffic conditions"""
        vehicle_count = len(detections)
        self.vehicle_history.append(vehicle_count)
        
        # Calculate metrics
        avg_count = np.mean(self.vehicle_history)
        traffic_density = self.calculate_density(vehicle_count)
        congestion_level = self.get_congestion_level(vehicle_count)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'vehicle_count': vehicle_count,
            'average_count': float(avg_count),
            'traffic_density': traffic_density,
            'congestion_level': congestion_level,
            'trend': self.calculate_trend()
        }
    
    def calculate_density(self, count):
        """Calculate traffic density"""
        if count < self.density_threshold['low']:
            return 'low'
        elif count < self.density_threshold['medium']:
            return 'medium'
        elif count < self.density_threshold['high']:
            return 'high'
        return 'critical'
    
    def get_congestion_level(self, count):
        """Get congestion percentage"""
        max_capacity = 50  # Adjust based on road capacity
        return min((count / max_capacity) * 100, 100)
    
    def calculate_trend(self):
        """Calculate traffic trend"""
        if len(self.vehicle_history) < 2:
            return 'stable'
        
        recent = list(self.vehicle_history)[-10:]
        if len(recent) < 2:
            return 'stable'
            
        trend = np.polyfit(range(len(recent)), recent, 1)[0]
        
        if trend > 0.5:
            return 'increasing'
        elif trend < -0.5:
            return 'decreasing'
        return 'stable'