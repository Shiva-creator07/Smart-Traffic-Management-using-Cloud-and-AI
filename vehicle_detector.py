from ultralytics import YOLO
import cv2
import numpy as np
from datetime import datetime

class VehicleDetector:
    def __init__(self, model_path='yolov8n.pt'):
        """Initialize YOLOv8 model"""
        self.model = YOLO(model_path)
        self.vehicle_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
        
    def detect_vehicles(self, frame):
        """Detect vehicles in frame"""
        results = self.model(frame, classes=self.vehicle_classes)
        
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = box.conf[0].cpu().numpy()
                class_id = int(box.cls[0].cpu().numpy())
                
                detections.append({
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'confidence': float(confidence),
                    'class_id': class_id,
                    'class_name': result.names[class_id]
                })
        
        return detections, results[0].plot()
    
    def count_vehicles_by_type(self, detections):
        """Count vehicles by type"""
        counts = {}
        for det in detections:
            class_name = det['class_name']
            counts[class_name] = counts.get(class_name, 0) + 1
        return counts