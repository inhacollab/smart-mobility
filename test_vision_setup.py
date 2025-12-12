#!/usr/bin/env python3
"""
Simple Vision Test - Tests if opencv and ultralytics work
Without needing ROS2 or full system
"""

import sys

print("=" * 70)
print("🎥 Vision Module Test")
print("=" * 70)
print()

# Test 1: Check if opencv is available
print("Test 1: Checking OpenCV...")
try:
    import cv2
    print(f"  ✅ OpenCV installed: {cv2.__version__}")
    
    # Try to open webcam
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        print("  ✅ Webcam accessible")
        ret, frame = cap.read()
        if ret:
            print(f"  ✅ Frame captured: {frame.shape}")
        cap.release()
    else:
        print("  ⚠️  Webcam not accessible")
except ImportError:
    print("  ❌ OpenCV not installed")
    print("     Install: pip3 install --user opencv-python")

print()

# Test 2: Check if ultralytics is available
print("Test 2: Checking Ultralytics (YOLOv8)...")
try:
    from ultralytics import YOLO
    print("  ✅ Ultralytics installed")
    
    # Try to load a tiny model
    print("  Testing model loading (this may download ~6MB)...")
    model = YOLO('yolov8n.pt')
    print("  ✅ YOLOv8 model loaded successfully")
    
except ImportError:
    print("  ❌ Ultralytics not installed")
    print("     Install: pip3 install --user ultralytics")
except Exception as e:
    print(f"  ⚠️  Error loading model: {e}")

print()

# Test 3: Check mediapipe for gesture control
print("Test 3: Checking MediaPipe (for gestures)...")
try:
    import mediapipe as mp
    print(f"  ✅ MediaPipe installed")
except ImportError:
    print("  ❌ MediaPipe not installed")
    print("     Install: pip3 install --user mediapipe")

print()
print("=" * 70)
print("Summary:")
print("  - If all ✅, you can run: python3 main.py vision --webcam")
print("  - If all ✅, you can run: python3 main.py gesture")
print("  - If ❌, install missing packages with pip3")
print("=" * 70)
