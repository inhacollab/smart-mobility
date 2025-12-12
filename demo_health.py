#!/usr/bin/env python3
"""
Real-time Health Monitoring Dashboard
Modern visual display of system health with enhanced graphics
"""
import cv2
import numpy as np
import time
import psutil
import math
from collections import deque

print("="*60)
print("  🤖 TurtleBot3 Health Monitor Dashboard")
print("="*60)
print("\nStarting real-time monitoring...")
print("Press 'q' to quit")
print("="*60)

# Create window with higher resolution
width, height = 1400, 900
frame = np.zeros((height, width, 3), dtype=np.uint8)

# Data buffers for graphs (last 120 points for smoother graphs)
cpu_history = deque(maxlen=120)
mem_history = deque(maxlen=120)
disk_history = deque(maxlen=120)
net_history = deque(maxlen=120)

# Battery simulation with more realistic behavior
battery_level = 85
battery_trend = -0.05  # Gradual discharge

# Modern color palette
COLORS = {
    'bg_dark': (15, 15, 25),
    'bg_card': (25, 25, 40),
    'bg_header': (0, 40, 80),
    'accent_primary': (0, 180, 255),
    'accent_secondary': (255, 100, 150),
    'success': (0, 255, 120),
    'warning': (255, 180, 0),
    'error': (255, 50, 50),
    'text_primary': (255, 255, 255),
    'text_secondary': (180, 180, 200),
    'cpu': (100, 200, 255),
    'memory': (150, 100, 255),
    'disk': (255, 150, 50),
    'network': (0, 255, 150),
    'battery': (255, 200, 0)
}

def draw_text(img, text, pos, size=0.8, color=(255, 255, 255), thickness=2, font=cv2.FONT_HERSHEY_SIMPLEX):
    cv2.putText(img, text, pos, font, size, color, thickness)

def draw_rounded_rect(img, top_left, bottom_right, color, radius=10, thickness=-1):
    """Draw a rounded rectangle"""
    x1, y1 = top_left
    x2, y2 = bottom_right

    # Draw main rectangle
    cv2.rectangle(img, (x1 + radius, y1), (x2 - radius, y2), color, thickness)
    cv2.rectangle(img, (x1, y1 + radius), (x2, y2 - radius), color, thickness)

    # Draw corners
    cv2.circle(img, (x1 + radius, y1 + radius), radius, color, thickness)
    cv2.circle(img, (x2 - radius, y1 + radius), radius, color, thickness)
    cv2.circle(img, (x1 + radius, y2 - radius), radius, color, thickness)
    cv2.circle(img, (x2 - radius, y2 - radius), radius, color, thickness)

def draw_gradient_bar(img, x, y, w, h, value, max_val, color_start, color_end, radius=8):
    """Draw a gradient progress bar"""
    # Background
    draw_rounded_rect(img, (x, y), (x+w, y+h), (40, 40, 50), radius)

    # Gradient fill
    fill_w = int((value / max_val) * (w - 4))
    if fill_w > 0:
        for i in range(fill_w):
            ratio = i / (w - 4)
            r = int(color_start[0] + (color_end[0] - color_start[0]) * ratio)
            g = int(color_start[1] + (color_end[1] - color_start[1]) * ratio)
            b = int(color_start[2] + (color_end[2] - color_start[2]) * ratio)
            cv2.line(img, (x + 2 + i, y + 2), (x + 2 + i, y + h - 2), (b, g, r), 1)

    # Border
    draw_rounded_rect(img, (x, y), (x+w, y+h), (100, 100, 120), radius, 2)

    # Percentage text
    percentage = int((value / max_val) * 100)
    text_color = COLORS['text_primary'] if percentage < 80 else COLORS['warning'] if percentage < 90 else COLORS['error']
    draw_text(img, f"{percentage}%", (x+w+15, y+h-8), 0.7, text_color)

def draw_smooth_graph(img, x, y, w, h, data, color, max_val=100, thickness=3):
    """Draw a smooth gradient graph with better styling"""
    if len(data) < 2:
        return

    # Background with subtle gradient
    for i in range(h):
        alpha = i / h
        bg_color = (int(30 + alpha * 20), int(30 + alpha * 20), int(40 + alpha * 20))
        cv2.line(img, (x, y + i), (x + w, y + i), bg_color, 1)

    # Grid lines
    for i in range(0, 101, 20):
        grid_y = y + h - int((i/max_val) * h)
        cv2.line(img, (x, grid_y), (x+w, grid_y), (60, 60, 80), 1)

    # Calculate points
    points = []
    for i, value in enumerate(data):
        px = x + int((i / len(data)) * w)
        py = y + h - int((value / max_val) * h)
        points.append((px, py))

    # Draw smooth curve
    if len(points) > 2:
        for i in range(len(points)-1):
            cv2.line(img, points[i], points[i+1], color, thickness)

    # Add glow effect
    for point in points:
        cv2.circle(img, point, 2, color, -1)

def draw_gauge(img, center, radius, value, max_val, color, label):
    """Draw a circular gauge"""
    x, y = center

    # Background circle
    cv2.circle(img, (x, y), radius, (40, 40, 50), -1)
    cv2.circle(img, (x, y), radius, (80, 80, 100), 2)

    # Progress arc
    angle = int((value / max_val) * 270) - 135  # -135 to +135 degrees
    cv2.ellipse(img, (x, y), (radius-5, radius-5), 0, -135, angle, color, 8)

    # Center dot
    cv2.circle(img, (x, y), 8, color, -1)

    # Value text
    percentage = int((value / max_val) * 100)
    draw_text(img, f"{percentage}%", (x-25, y+8), 0.8, COLORS['text_primary'], 2)

    # Label
    draw_text(img, label, (x-40, y+radius+25), 0.6, COLORS['text_secondary'])

def draw_status_card(img, x, y, w, h, title, status, color, icon="●"):
    """Draw a modern status card"""
    # Card background
    draw_rounded_rect(img, (x, y), (x+w, y+h), COLORS['bg_card'], 15)

    # Header
    draw_rounded_rect(img, (x+5, y+5), (x+w-5, y+40), color, 8)

    # Icon and title
    draw_text(img, icon, (x+15, y+30), 1.2, COLORS['text_primary'])
    draw_text(img, title, (x+45, y+30), 0.8, COLORS['text_primary'], 2)

    # Status
    status_color = COLORS['success'] if status == "ONLINE" else COLORS['warning'] if status == "WARNING" else COLORS['error']
    draw_text(img, status, (x+15, y+h-20), 0.7, status_color, 2)

def create_network_graph():
    """Simulate network activity"""
    return np.random.randint(0, 100)

start_time = time.time()

while True:
    # Modern gradient background
    for i in range(height):
        alpha = i / height
        bg_color = (
            int(COLORS['bg_dark'][0] + alpha * 10),
            int(COLORS['bg_dark'][1] + alpha * 10),
            int(COLORS['bg_dark'][2] + alpha * 15)
        )
        cv2.line(frame, (0, i), (width, i), bg_color, 1)

    # Modern header with gradient
    header_height = 100
    for i in range(header_height):
        alpha = i / header_height
        header_color = (
            int(COLORS['bg_header'][0] + alpha * 50),
            int(COLORS['bg_header'][1] + alpha * 100),
            int(COLORS['bg_header'][2] + alpha * 150)
        )
        cv2.line(frame, (0, i), (width, i), header_color, 1)

    # Header content
    draw_text(frame, "🤖 TurtleBot3 Health Monitor", (30, 50), 1.5, COLORS['text_primary'], 3)
    draw_text(frame, "Real-time System Analytics", (30, 80), 0.8, COLORS['text_secondary'], 2)

    elapsed = int(time.time() - start_time)
    draw_text(frame, f"Runtime: {elapsed//3600:02d}:{(elapsed%3600)//60:02d}:{elapsed%60:02d}",
              (width-300, 70), 0.9, COLORS['accent_primary'], 2)

    # Get system stats
    cpu_percent = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    net_activity = create_network_graph()

    # Update history
    cpu_history.append(cpu_percent)
    mem_history.append(mem.percent)
    disk_history.append(disk.percent)
    net_history.append(net_activity)

    # Simulate battery with more realistic behavior
    battery_level += battery_trend
    if battery_level <= 15:
        battery_trend = 0.1  # Start charging
    elif battery_level >= 95:
        battery_trend = -0.05  # Start discharging
    battery_level = max(0, min(100, battery_level))

    # Left column - Gauges and Cards
    col1_x = 50
    col1_y = 130

    # Battery Gauge
    draw_gauge(frame, (col1_x + 80, col1_y + 80), 70, battery_level, 100, COLORS['battery'], "Battery")
    col1_y += 180

    # CPU Gauge
    draw_gauge(frame, (col1_x + 80, col1_y + 80), 70, cpu_percent, 100, COLORS['cpu'], "CPU")
    col1_y += 180

    # Memory Gauge
    draw_gauge(frame, (col1_x + 80, col1_y + 80), 70, mem.percent, 100, COLORS['memory'], "Memory")
    col1_y += 180

    # Disk Gauge
    draw_gauge(frame, (col1_x + 80, col1_y + 80), 70, disk.percent, 100, COLORS['disk'], "Disk")

    # Status Cards
    card_y = 150
    card_width = 200
    card_height = 80

    statuses = [
        ("Motors", "ONLINE", COLORS['success'], "⚙️"),
        ("Sensors", "ACTIVE", COLORS['success'], "📡"),
        ("Network", "CONNECTED", COLORS['success'], "🌐"),
        ("ROS2", "READY", COLORS['warning'], "🤖")
    ]

    for i, (name, status, color, icon) in enumerate(statuses):
        card_x = width - card_width - 50
        draw_status_card(frame, card_x, card_y + i * (card_height + 20), card_width, card_height, name, status, color, icon)

    # Right column - Enhanced Graphs
    graph_x = 350
    graph_y = 130
    graph_w = 600
    graph_h = 120

    # CPU Graph
    draw_rounded_rect(frame, (graph_x-10, graph_y-40), (graph_x+graph_w+10, graph_y+graph_h+10), COLORS['bg_card'], 15)
    draw_text(frame, "CPU Usage History", (graph_x, graph_y-10), 1.0, COLORS['cpu'], 2)
    draw_smooth_graph(frame, graph_x, graph_y, graph_w, graph_h, cpu_history, COLORS['cpu'])
    graph_y += 180

    # Memory Graph
    draw_rounded_rect(frame, (graph_x-10, graph_y-40), (graph_x+graph_w+10, graph_y+graph_h+10), COLORS['bg_card'], 15)
    draw_text(frame, "Memory Usage History", (graph_x, graph_y-10), 1.0, COLORS['memory'], 2)
    draw_smooth_graph(frame, graph_x, graph_y, graph_w, graph_h, mem_history, COLORS['memory'])
    graph_y += 180

    # Disk Graph
    draw_rounded_rect(frame, (graph_x-10, graph_y-40), (graph_x+graph_w+10, graph_y+graph_h+10), COLORS['bg_card'], 15)
    draw_text(frame, "Disk Usage History", (graph_x, graph_y-10), 1.0, COLORS['disk'], 2)
    draw_smooth_graph(frame, graph_x, graph_y, graph_w, graph_h, disk_history, COLORS['disk'])
    graph_y += 180

    # Network Graph
    draw_rounded_rect(frame, (graph_x-10, graph_y-40), (graph_x+graph_w+10, graph_y+graph_h+10), COLORS['bg_card'], 15)
    draw_text(frame, "Network Activity", (graph_x, graph_y-10), 1.0, COLORS['network'], 2)
    draw_smooth_graph(frame, graph_x, graph_y, graph_w, graph_h, net_history, COLORS['network'], 100)

    # Footer with modern styling
    footer_y = height - 60
    draw_rounded_rect(frame, (20, footer_y), (width-20, height-20), (30, 30, 50), 10)
    draw_text(frame, "Press 'q' to quit • Real-time monitoring active", (40, footer_y + 30), 0.8, COLORS['text_secondary'], 2)

    # Performance indicator
    fps = len(cpu_history) / max(1, elapsed) if elapsed > 0 else 30
    draw_text(frame, f"UI FPS: {fps:.1f}", (width-200, footer_y + 30), 0.7, COLORS['accent_primary'], 2)

    # Display
    cv2.imshow('TurtleBot3 Health Monitor', frame)

    if cv2.waitKey(50) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
print("\n✅ Enhanced dashboard demo completed!")
