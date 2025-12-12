# TurtleBot3 Smart Automation System

**Course:** Smart Mobility  
**Target Platform:** Ubuntu 22.04 + ROS2 Humble

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Operating System Concepts](#operating-system-concepts)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

This project presents a comprehensive automation system for TurtleBot3 mobile robots using ROS2 Humble on Ubuntu 22.04. It integrates modern AI tools (YOLOv8, MediaPipe) with robotic automation to demonstrate practical applications of operating system concepts including process management, resource monitoring, file I/O, and inter-process communication.

The system provides five core modules:
1. **Setup Automation** - Automated installation and configuration
2. **Health Monitoring** - Real-time system diagnostics and maintenance
3. **Smart Navigation** - Behavior tree-based autonomous navigation
4. **Vision Processing** - YOLOv8 object detection with tracking
5. **Gesture Control** - MediaPipe hand gesture recognition (Custom Feature)

## ✨ Features

### 1. Setup Automation (`automation/setup_manager.py`)

- ✅ Automated ROS2 Humble installation with GPG key verification
- ✅ TurtleBot3 package installation (simulation, navigation, SLAM)
- ✅ Workspace creation and automated building
- ✅ Environment configuration with .bashrc integration
- ✅ Systemd service generation for auto-start
- ✅ Comprehensive verification and health checks
- ✅ Rollback support on installation failure

**Unique Approach:** Unlike template projects, this implementation uses:
- Systemd service creation for production deployment
- Multi-stage verification with detailed reporting
- Configuration validation before installation
- Automated testing post-installation

### 2. Health Monitoring (`automation/health_monitor.py`)

- 🏥 Real-time battery monitoring with multi-level alerts (Good/Low/Critical)
- 🔍 Comprehensive sensor diagnostics (LiDAR, IMU, Camera, Odometry)
- ⚙️ Motor health tracking (temperature, current, RPM)
- 💻 System resource monitoring (CPU, Memory, Disk, Network)
- 📊 Historical data logging with trend analysis
- 🚨 Automated fault detection and recovery
- 📄 Health report generation (text + JSON)

**Unique Features:**
- Alert cooldown system to prevent spam
- Automated response to critical conditions
- Performance metrics tracking
- Health score calculation (0-100)

### 3. Smart Navigation (`automation/smart_navigator.py`)

- 🗺️ SLAM mapping using Cartographer
- 🧭 Autonomous navigation with Nav2 stack
- 🌳 Behavior tree-based decision making
- 📍 Multi-waypoint navigation
- 🔄 Patrol route execution
- 🏠 Return-to-base capability
- 🚧 Dynamic obstacle avoidance
- 📊 Navigation history logging

**Unique Approach:**
- Behavior tree architecture for intelligent decision-making
- Pre-flight checks (battery, obstacles) before navigation
- Waypoint sequencing with progress tracking
- Comprehensive navigation state machine

### 4. Vision Processing (`automation/vision_processor.py`)

- 👁️ Real-time YOLOv8 object detection
- 🎯 Multi-object tracking support
- 🤝 Object interaction behaviors:
  - Follow object (maintain distance)
  - Avoid objects (collision avoidance)
  - Approach object (go to target)
- 📸 Webcam and image file processing
- 📊 Detection statistics and analytics
- 🔄 ROS2 topic publishing

**Unique Features:**
- Object interaction mode system
- Detection history with class distribution
- Confidence-based filtering
- Real-time performance metrics

### 5. Gesture Control (`automation/gesture_controller.py`) **[Custom Feature]**

- 🖐️ Real-time hand gesture recognition using MediaPipe
- 🎮 Intuitive robot control:
  - Open Palm → STOP
  - Fist → MOVE FORWARD
  - Peace Sign (2 fingers) → TURN LEFT
  - Three Fingers → TURN RIGHT
  - Four Fingers → MOVE BACKWARD
  - Thumbs Up → INCREASE SPEED
  - Thumbs Down → DECREASE SPEED
- 📹 Visual feedback with hand landmark overlay
- ⚡ Dynamic speed control
- 📊 Gesture usage statistics

**Why This Feature:**
- Provides hands-free robot control
- Demonstrates computer vision integration
- Intuitive and accessible interface
- Real-world application potential

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Main Orchestrator                       │
│                      (main.py)                              │
└───────────┬─────────────────────────────────────────────────┘
            │
            ├───► Setup Manager ───────► System Installation
            │                           ├─ ROS2 Humble
            │                           ├─ TurtleBot3 Packages
            │                           └─ Workspace Build
            │
            ├───► Health Monitor ───────► Real-time Diagnostics
            │                           ├─ Battery Monitoring
            │                           ├─ Sensor Health
            │                           ├─ Motor Status
            │                           └─ Resource Tracking
            │
            ├───► Smart Navigator ──────► Autonomous Navigation
            │                           ├─ SLAM Mapping
            │                           ├─ Path Planning
            │                           ├─ Behavior Trees
            │                           └─ Waypoint Navigation
            │
            ├───► Vision Processor ─────► Object Detection
            │                           ├─ YOLOv8 Detection
            │                           ├─ Object Tracking
            │                           └─ Interaction Modes
            │
            └───► Gesture Controller ───► Hand Gesture Control
                                        ├─ MediaPipe Detection
                                        ├─ Gesture Recognition
                                        └─ Velocity Commands
```

## 📦 Prerequisites

### Hardware
- **Computer:** x86_64 system with Ubuntu 22.04 LTS
- **RAM:** Minimum 8GB (16GB recommended)
- **Disk:** 15GB free space
- **Camera:** (Optional) For gesture control and vision features
- **TurtleBot3:** (Optional) Physical robot or use Gazebo simulation

### Software
- **OS:** Ubuntu 22.04 LTS (Jammy Jellyfish)
- **ROS2:** Humble Hawksbill
- **Python:** 3.10+
- **Git:** For repository cloning

## 🚀 Installation

### Option 1: Automated Installation (Recommended)

```bash
# Clone the repository
cd ~/Projects/inha-operating-systems/tb3-smart-automation

# Run installation script
sudo ./scripts/install.sh
```

The installation script will:
1. Check system requirements
2. Install ROS2 Humble
3. Install TurtleBot3 packages
4. Create and build workspace
5. Configure environment
6. Install Python dependencies
7. Verify installation

### Option 2: Manual Installation

See [docs/INSTALLATION_GUIDE.md](docs/INSTALLATION_GUIDE.md) for detailed manual installation steps.

### Option 3: Using Python Setup Module

```bash
# Use the setup automation module
python3 main.py setup
```

## 💻 Usage

### Interactive Menu

```bash
python3 main.py --interactive
```

### Command Line Interface

```bash
# Check environment
python3 main.py --check-env

# Setup (first time)
python3 main.py setup

# Health monitoring
python3 main.py health                    # Single check
python3 main.py health --monitor          # Continuous monitoring
python3 main.py health --save-report      # Save report to file

# Navigation
python3 main.py navigate --slam                    # Start SLAM mapping
python3 main.py navigate --save-map my_map         # Save map
python3 main.py navigate --load-map maps/my_map    # Load map
python3 main.py navigate --goto 1.0 1.0 0.0       # Navigate to pose
python3 main.py navigate --patrol                  # Patrol mode
python3 main.py navigate --return-home             # Return to base

# Vision processing
python3 main.py vision --webcam                    # Webcam detection
python3 main.py vision --image path/to/image.jpg   # Detect in image
python3 main.py vision --follow person             # Follow person
python3 main.py vision --duration 60               # Run for 60 seconds

# Gesture control
python3 main.py gesture                            # Start gesture control
python3 main.py gesture --calibrate                # Calibrate gestures
python3 main.py gesture --report                   # Show usage report
```

### Quick Test Scripts

```bash
# Test health monitoring
./scripts/health_check.sh

# Test navigation in simulation
./scripts/test_navigation.sh

# Test vision processing
./scripts/test_vision.sh

# Test gesture control
./scripts/test_gesture.sh
```

## 📁 Project Structure

```
tb3-smart-automation/
├── main.py                          # Main orchestration script
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
│
├── core/                            # Core utilities
│   ├── __init__.py
│   ├── logger.py                    # Enhanced logging system
│   ├── config_manager.py            # Configuration management
│   └── utils.py                     # Utility functions
│
├── automation/                      # Automation modules
│   ├── __init__.py
│   ├── setup_manager.py             # Setup automation
│   ├── health_monitor.py            # Health monitoring
│   ├── smart_navigator.py           # Navigation automation
│   ├── vision_processor.py          # Vision processing
│   └── gesture_controller.py        # Gesture control
│
├── config/                          # Configuration files
│   └── system_config.yaml           # Main configuration
│
├── scripts/                         # Shell scripts
│   ├── install.sh                   # Installation script
│   ├── health_check.sh              # Health check script
│   ├── test_navigation.sh           # Navigation test
│   ├── test_vision.sh               # Vision test
│   └── test_gesture.sh              # Gesture test
│
├── logs/                            # Log files (auto-generated)
│   ├── *.log                        # Text logs
│   └── *.json                       # JSON logs
│
└── docs/                            # Documentation
    ├── INSTALLATION_GUIDE.md        # Detailed installation
    ├── TESTING_GUIDE.md             # Testing procedures
    ├── API_REFERENCE.md             # API documentation
    └── TROUBLESHOOTING.md           # Common issues
```

## 🧪 Testing

### Testing on Ubuntu 22.04

1. **Prerequisites Check:**
```bash
python3 main.py --check-env
```

2. **Setup Testing:**
```bash
# Check requirements only (no installation)
python3 main.py setup --check-only

# Full setup
python3 main.py setup
```

3. **Module Testing:**
```bash
# Test each module individually
./scripts/health_check.sh
./scripts/test_vision.sh
./scripts/test_gesture.sh
```

4. **Simulation Testing:**
```bash
# Launch Gazebo simulation
ros2 launch turtlebot3_gazebo empty_world.launch.py

# In another terminal, test navigation
python3 main.py navigate --slam
```

### Without Robot Hardware

All features can be tested in simulation:
- Navigation: Gazebo simulation
- Vision: Webcam or image files
- Gesture: Webcam
- Health: Simulated sensors

See [docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md) for detailed testing procedures.

## 🖥️ Operating System Concepts

This project demonstrates key OS concepts:

### 1. Process Management
- **Multi-threading:** Health monitoring and gesture control run in separate threads
- **Process synchronization:** Thread-safe operations with locks
- **Signal handling:** Graceful shutdown on SIGINT/SIGTERM

### 2. Inter-Process Communication
- **ROS2 Topics:** Publisher-subscriber pattern for sensor data
- **ROS2 Services:** Request-response for commands
- **ROS2 Actions:** Long-running tasks with feedback

### 3. Resource Management
- **CPU Monitoring:** Real-time CPU usage tracking
- **Memory Management:** Memory usage and leak detection
- **Disk I/O:** Log file rotation and management

### 4. File Systems
- **Configuration files:** YAML parsing and management
- **Log files:** Structured logging with rotation
- **File I/O:** Reading sensors, writing reports

### 5. System Calls
- **Process execution:** subprocess for shell commands
- **System information:** psutil for hardware metrics
- **Network I/O:** ROS2 network communication

## 🔧 Troubleshooting

### Common Issues

1. **ROS2 not found:**
```bash
source ~/.bashrc
# or
source /opt/ros/humble/setup.bash
```

2. **Permission denied on scripts:**
```bash
chmod +x scripts/*.sh
chmod +x main.py
```

3. **Python module not found:**
```bash
pip3 install -r requirements.txt
```

4. **Gazebo won't start:**
```bash
export TURTLEBOT3_MODEL=burger
killall gzserver gzclient
ros2 launch turtlebot3_gazebo empty_world.launch.py
```

5. **Camera not detected:**
```bash
# Check available cameras
ls /dev/video*

# Try different camera ID in config
gesture.camera_id: 0  # Change to 1, 2, etc.
```

For more issues, see [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## 📝 Configuration

Edit `config/system_config.yaml` to customize:

```yaml
robot:
  model: "burger"      # burger, waffle, waffle_pi
  use_sim: false       # true for simulation

health_monitor:
  check_interval: 5.0  # seconds between checks
  battery_low_threshold: 20.0  # percent

navigation:
  max_linear_speed: 0.22  # m/s
  max_angular_speed: 2.84  # rad/s

vision:
  confidence_threshold: 0.5  # YOLO confidence
  enable_tracking: true

gesture:
  camera_id: 0
  min_detection_confidence: 0.7
```

## 🤝 Contributing

This is an academic project, but suggestions are welcome:

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is created for educational purposes as part of a Smart Mobility course.

## 🙏 Acknowledgments

- ROBOTIS for TurtleBot3 platform and documentation
- ROS2 community for excellent documentation and support
- Ultralytics for YOLOv8
- Google MediaPipe team
- All open-source contributors

## 📚 References

1. ROS2 Humble Documentation: https://docs.ros.org/en/humble/
2. TurtleBot3 Manual: https://emanual.robotis.com/docs/en/platform/turtlebot3/
3. YOLOv8 Documentation: https://docs.ultralytics.com/
4. MediaPipe Documentation: https://developers.google.com/mediapipe
5. Robotics and Autonomous Systems References

---

**Course:** Smart Mobility
