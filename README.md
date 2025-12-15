Traditional traffic signals operate on fixed timers, which do not adapt to real-time road conditions, causing unnecessary delays, pollution, and fuel consumption.

This project uses AI (Computer Vision + ML) and Cloud Computing to build a smart, automated traffic control system capable of:

Detecting the number of vehicles using video feeds.

Predicting congestion.

Dynamically changing signal timings.

Monitoring city-wide traffic using a cloud dashboard.

Alerting authorities about accidents or unusual events.

Core Idea

Use AI models (like YOLOv8) to analyze live traffic camera feeds and send real-time vehicle counts to the cloud. A cloud-based backend calculates the optimal signal duration and sends it back to the traffic lights.

It’s a real-time, AI-powered, cloud-integrated traffic management system.

Key Objectives

Detect and count vehicles from live CCTV/video streams.

Identify congestion levels (low, medium, high).

Adjust traffic light timings automatically.

Provide a live traffic dashboard for monitoring.

Store data in cloud for analytics and predictions.

Reduce congestion, waiting time, and fuel consumption.

CCTV Camera/Live Feed ↓ AI Engine (YOLOv8 / OpenCV) ↓
Vehicle Count + Congestion Level ↓ Cloud Backend (AWS / IBM Cloud / Azure) ↓ Decision Engine (Signal Timing Algorithm) ↓ Traffic Signal Controller (Simulated or Real) ↓ Dashboard for Monitoring (React/Streamlit)

