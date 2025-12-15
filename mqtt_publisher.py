# mqtt_publisher.py
import paho.mqtt.client as mqtt
import json

class MQTTPublisher:
    def __init__(self, broker, port, topic):
        self.client = mqtt.Client()
        self.broker = broker
        self.port = port
        self.topic = topic
        
    def connect(self):
        self.client.connect(self.broker, self.port)
        self.client.loop_start()
        
    def publish_data(self, data):
        message = json.dumps(data)
        self.client.publish(self.topic, message)
        
    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()