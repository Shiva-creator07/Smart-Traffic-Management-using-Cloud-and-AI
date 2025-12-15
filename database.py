from pymongo import MongoClient
from datetime import datetime
import certifi

class TrafficDatabase:
    def __init__(self, connection_string):
        """Initialize MongoDB connection"""
        self.client = MongoClient(connection_string, tlsCAFile=certifi.where())
        self.db = self.client['traffic_management']
        self.collection = self.db['traffic_data']
        
    def insert_traffic_data(self, data):
        """Insert traffic data into MongoDB"""
        document = {
            'timestamp': datetime.now(),
            'camera_id': data.get('camera_id', 'cam_001'),
            'location': data.get('location', 'Main Street'),
            'vehicle_count': data['vehicle_count'],
            'vehicle_types': data.get('vehicle_types', {}),
            'traffic_density': data['traffic_density'],
            'congestion_level': data['congestion_level'],
            'average_count': data['average_count'],
            'trend': data['trend']
        }
        
        result = self.collection.insert_one(document)
        return result.inserted_id
    
    def get_recent_data(self, limit=100):
        """Get recent traffic data"""
        cursor = self.collection.find().sort('timestamp', -1).limit(limit)
        return list(cursor)
    
    def get_data_by_time_range(self, start_time, end_time):
        """Get data within time range"""
        query = {
            'timestamp': {
                '$gte': start_time,
                '$lte': end_time
            }
        }
        return list(self.collection.find(query))
    
    def get_statistics(self):
        """Get traffic statistics"""
        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'avg_vehicles': {'$avg': '$vehicle_count'},
                    'max_vehicles': {'$max': '$vehicle_count'},
                    'min_vehicles': {'$min': '$vehicle_count'},
                    'total_records': {'$sum': 1}
                }
            }
        ]
        result = list(self.collection.aggregate(pipeline))
        return result[0] if result else {}