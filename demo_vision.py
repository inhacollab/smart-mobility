#!/usr/bin/env python3
"""
Real-time Object Detection Demo
Shows webcam with YOLOv8 object detection
"""
import cv2
from ultralytics import YOLO
import time

print("="*60)
print("  🤖 TurtleBot3 Vision System Demo")
print("="*60)
print("\nLoading YOLOv8 model...")

# Load YOLO model
model = YOLO('yolov8n.pt')  # nano model for speed

print("✅ Model loaded!")
print("\nDetecting objects in real-time...")
print("Press 'q' to quit")
print("="*60)

# Open webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

fps_time = time.time()
fps_counter = 0
fps = 0

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break
    
    h, w, _ = frame.shape
    
    # Run YOLOv8 detection
    results = model(frame, verbose=False)
    
    # Draw detections
    annotated_frame = results[0].plot()
    
    # Count objects
    num_objects = len(results[0].boxes)
    
    # Calculate FPS
    fps_counter += 1
    if time.time() - fps_time >= 1.0:
        fps = fps_counter
        fps_counter = 0
        fps_time = time.time()
    
    # Draw info overlay
    cv2.rectangle(annotated_frame, (0, 0), (w, 80), (0, 0, 0), -1)
    cv2.putText(annotated_frame, "TurtleBot3 Vision System", 
               (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 
               1, (0, 255, 255), 2)
    cv2.putText(annotated_frame, f"Objects: {num_objects} | FPS: {fps}", 
               (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 
               0.7, (0, 255, 0), 2)
    
    # Show instructions
    cv2.putText(annotated_frame, "Press 'q' to quit", 
               (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 
               0.7, (255, 255, 255), 2)
    
    # Display
    cv2.imshow('TurtleBot3 Vision System', annotated_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("\n✅ Demo completed!")
