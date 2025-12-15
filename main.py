import cv2
import time
from vehicle_detector import VehicleDetector
from traffic_analyzer import TrafficAnalyzer
from database import TrafficDatabase
from mqtt_publisher import MQTTPublisher

class TrafficManagementSystem:
    def __init__(self, video_source, mongo_uri, mqtt_broker):
        self.detector = VehicleDetector('yolov8n.pt')
        self.analyzer = TrafficAnalyzer()
        self.db = TrafficDatabase(mongo_uri)
        self.mqtt = MQTTPublisher(mqtt_broker, 1883, 'traffic/data')
        self.video_source = video_source
        
    def run(self):
        """Main processing loop"""
        # For IP Webcam - add /video endpoint
        if isinstance(self.video_source, str) and 'http' in self.video_source:
            if not self.video_source.endswith('/video'):
                self.video_source += '/video'
        
        cap = cv2.VideoCapture(self.video_source)
        
        # Set buffer size to reduce latency
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if not cap.isOpened():
            print("Error: Could not open video source")
            print(f"Tried to connect to: {self.video_source}")
            return
        
        print(f"Successfully connected to: {self.video_source}")
        self.mqtt.connect()
        
        frame_count = 0
        process_every_n_frames = 5
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Failed to grab frame, retrying...")
                    time.sleep(1)
                    continue
                
                frame_count += 1
                
                # Process frame
                if frame_count % process_every_n_frames == 0:
                    # Resize frame for better performance
                    frame = cv2.resize(frame, (640, 480))
                    
                    # Detect vehicles
                    detections, annotated_frame = self.detector.detect_vehicles(frame)
                    
                    # Count by type
                    vehicle_types = self.detector.count_vehicles_by_type(detections)
                    
                    # Analyze traffic
                    analysis = self.analyzer.analyze_traffic(detections)
                    analysis['vehicle_types'] = vehicle_types
                    analysis['camera_id'] = 'mobile_cam_001'
                    analysis['location'] = 'Mobile Camera - Street View'
                    
                    # Save to database
                    self.db.insert_traffic_data(analysis)
                    
                    # Publish to IoT
                    self.mqtt.publish_data(analysis)
                    
                    # Display with info
                    cv2.putText(annotated_frame, 
                               f"Vehicles: {analysis['vehicle_count']}", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                               1, (0, 255, 0), 2)
                    cv2.putText(annotated_frame, 
                               f"Density: {analysis['traffic_density']}", 
                               (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 
                               1, (0, 255, 0), 2)
                    cv2.putText(annotated_frame, 
                               f"Congestion: {analysis['congestion_level']:.1f}%", 
                               (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 
                               1, (0, 255, 0), 2)
                    
                    # Add FPS counter
                    cv2.putText(annotated_frame, 
                               f"Source: Mobile Camera", 
                               (10, annotated_frame.shape[0] - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 
                               0.5, (255, 255, 0), 1)
                    
                    cv2.imshow('Traffic Management - Mobile Camera', annotated_frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            print("\nStopping system...")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.mqtt.disconnect()
            print("System stopped successfully")

if __name__ == "__main__":
    MONGO_URI = "mongodb+srv://aryan:aryan3323@cluster0.lpxyvko.mongodb.net/"
    MQTT_BROKER = "broker.hivemq.com"
    

    MOBILE_IP = "192.168.29.159"  
    MOBILE_PORT = "8080"
    VIDEO_SOURCE = f"http://192.168.29.159:8080/video"
    

    system = TrafficManagementSystem(VIDEO_SOURCE, MONGO_URI, MQTT_BROKER)
    system.run()