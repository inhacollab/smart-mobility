#!/usr/bin/env python3
"""
Real-time Health Monitoring Dashboard
Visual display of system health with live graphs
"""
import cv2
import numpy as np
import time
import psutil
from collections import deque

print("="*60)
print("  🤖 TurtleBot3 Health Monitor Dashboard")
print("="*60)
print("\nStarting real-time monitoring...")
print("Press 'q' to quit")
print("="*60)

# Create window
width, height = 1280, 720
frame = np.zeros((height, width, 3), dtype=np.uint8)

# Data buffers for graphs (last 100 points)
cpu_history = deque(maxlen=100)
mem_history = deque(maxlen=100)
disk_history = deque(maxlen=100)

# Battery simulation
battery_level = 100
battery_draining = True

def draw_text(img, text, pos, size=0.8, color=(255, 255, 255), thickness=2):
    cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, size, color, thickness)

def draw_bar(img, x, y, w, h, value, max_val, color):
    """Draw a progress bar"""
    # Background
    cv2.rectangle(img, (x, y), (x+w, y+h), (50, 50, 50), -1)
    # Fill
    fill_w = int((value / max_val) * w)
    cv2.rectangle(img, (x, y), (x+fill_w, y+h), color, -1)
    # Border
    cv2.rectangle(img, (x, y), (x+w, y+h), (200, 200, 200), 2)
    # Text
    percentage = int((value / max_val) * 100)
    draw_text(img, f"{percentage}%", (x+w+10, y+h-5), 0.6, color)

def draw_graph(img, x, y, w, h, data, color, max_val=100):
    """Draw a line graph"""
    # Background
    cv2.rectangle(img, (x, y), (x+w, y+h), (30, 30, 30), -1)
    cv2.rectangle(img, (x, y), (x+w, y+h), (100, 100, 100), 2)
    
    if len(data) < 2:
        return
    
    # Draw grid lines
    for i in range(0, 101, 25):
        grid_y = y + h - int((i/100) * h)
        cv2.line(img, (x, grid_y), (x+w, grid_y), (50, 50, 50), 1)
    
    # Draw data line
    points = []
    for i, value in enumerate(data):
        px = x + int((i / len(data)) * w)
        py = y + h - int((value / max_val) * h)
        points.append((px, py))
    
    for i in range(len(points)-1):
        cv2.line(img, points[i], points[i+1], color, 2)

start_time = time.time()

while True:
    # Clear frame
    frame[:] = (20, 20, 20)
    
    # Header
    cv2.rectangle(frame, (0, 0), (width, 80), (0, 50, 100), -1)
    draw_text(frame, "TurtleBot3 Health Monitor Dashboard", (20, 50), 1.2, (0, 255, 255), 3)
    
    elapsed = int(time.time() - start_time)
    draw_text(frame, f"Runtime: {elapsed}s", (width-200, 50), 0.8, (255, 255, 255))
    
    # Get system stats
    cpu_percent = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Update history
    cpu_history.append(cpu_percent)
    mem_history.append(mem.percent)
    disk_history.append(disk.percent)
    
    # Simulate battery
    if battery_draining:
        battery_level -= 0.1
        if battery_level <= 20:
            battery_draining = False
    else:
        battery_level += 0.2
        if battery_level >= 100:
            battery_draining = True
    battery_level = max(0, min(100, battery_level))
    
    # Left column - Current Status
    y_offset = 120
    
    # Battery
    draw_text(frame, "Battery Status", (40, y_offset), 1.0, (255, 255, 0), 2)
    y_offset += 40
    battery_color = (0, 255, 0) if battery_level > 50 else (0, 165, 255) if battery_level > 20 else (0, 0, 255)
    draw_bar(frame, 40, y_offset, 400, 40, battery_level, 100, battery_color)
    y_offset += 80
    
    # CPU
    draw_text(frame, "CPU Usage", (40, y_offset), 1.0, (100, 200, 255), 2)
    y_offset += 40
    cpu_color = (0, 255, 0) if cpu_percent < 50 else (0, 165, 255) if cpu_percent < 80 else (0, 0, 255)
    draw_bar(frame, 40, y_offset, 400, 40, cpu_percent, 100, cpu_color)
    y_offset += 80
    
    # Memory
    draw_text(frame, "Memory Usage", (40, y_offset), 1.0, (150, 100, 255), 2)
    y_offset += 40
    mem_color = (0, 255, 0) if mem.percent < 50 else (0, 165, 255) if mem.percent < 80 else (0, 0, 255)
    draw_bar(frame, 40, y_offset, 400, 40, mem.percent, 100, mem_color)
    draw_text(frame, f"{mem.used/(1024**3):.1f}GB / {mem.total/(1024**3):.1f}GB", 
             (40, y_offset + 70), 0.6, (180, 180, 180))
    y_offset += 100
    
    # Disk
    draw_text(frame, "Disk Usage", (40, y_offset), 1.0, (255, 150, 50), 2)
    y_offset += 40
    disk_color = (0, 255, 0) if disk.percent < 50 else (0, 165, 255) if disk.percent < 80 else (0, 0, 255)
    draw_bar(frame, 40, y_offset, 400, 40, disk.percent, 100, disk_color)
    draw_text(frame, f"{disk.used/(1024**3):.1f}GB / {disk.total/(1024**3):.1f}GB", 
             (40, y_offset + 70), 0.6, (180, 180, 180))
    
    # Right column - Graphs
    graph_x = 600
    graph_w = 640
    graph_h = 150
    
    # CPU Graph
    draw_text(frame, "CPU History", (graph_x, 120), 1.0, (100, 200, 255), 2)
    draw_graph(frame, graph_x, 140, graph_w, graph_h, cpu_history, (100, 200, 255))
    
    # Memory Graph
    draw_text(frame, "Memory History", (graph_x, 330), 1.0, (150, 100, 255), 2)
    draw_graph(frame, graph_x, 350, graph_w, graph_h, mem_history, (150, 100, 255))
    
    # Disk Graph
    draw_text(frame, "Disk History", (graph_x, 540), 1.0, (255, 150, 50), 2)
    draw_graph(frame, graph_x, 560, graph_w, graph_h, disk_history, (255, 150, 50))
    
    # Status indicators
    status_y = 100
    statuses = [
        ("Motors", "READY", (0, 255, 0)),
        ("Sensors", "ACTIVE", (0, 255, 0)),
        ("Network", "CONNECTED", (0, 255, 0)),
        ("ROS2", "RUNNING", (0, 255, 0))
    ]
    
    for i, (name, status, color) in enumerate(statuses):
        x = 40 + (i * 150)
        cv2.circle(frame, (x, status_y), 8, color, -1)
        draw_text(frame, f"{name}: {status}", (x + 15, status_y + 5), 0.5, color)
    
    # Footer
    draw_text(frame, "Press 'q' to quit", (20, height - 20), 0.7, (200, 200, 200))
    
    # Display
    cv2.imshow('TurtleBot3 Health Monitor', frame)
    
    if cv2.waitKey(100) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
print("\n✅ Demo completed!")
