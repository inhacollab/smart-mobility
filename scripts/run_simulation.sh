#!/bin/bash
#############################################################################
# TurtleBot3 Gazebo Simulation Launcher
# Ensures clean environment and proper model loading
#############################################################################

echo "🤖 TurtleBot3 Simulation Launcher"
echo "=================================="
echo ""

# Kill any existing Gazebo processes
echo "Cleaning up old Gazebo processes..."
pkill -9 gzserver 2>/dev/null
pkill -9 gzclient 2>/dev/null
sleep 2

# Check if conda is active and warn
if [ ! -z "$CONDA_DEFAULT_ENV" ]; then
    echo "⚠️  WARNING: Conda environment detected: $CONDA_DEFAULT_ENV"
    echo "   ROS2 Humble requires system Python 3.10"
    echo "   Run: conda deactivate"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Source ROS2 environment
echo "Setting up ROS2 environment..."
source /opt/ros/humble/setup.bash

# Set TurtleBot3 model
export TURTLEBOT3_MODEL=burger
echo "Robot model: $TURTLEBOT3_MODEL"
echo ""

# Check if ros2 command is available
if ! command -v ros2 &> /dev/null; then
    echo "❌ Error: ros2 command not found"
    echo "   Please install ROS2 Humble or source the setup file"
    exit 1
fi

# Launch Gazebo simulation
echo "🚀 Launching Gazebo simulation..."
echo "   World: TurtleBot3 World (with obstacles)"
echo ""
echo "Controls:"
echo "  - Mouse: Rotate view"
echo "  - Scroll: Zoom in/out"
echo "  - W/A/S/D: Move view"
echo ""
echo "In another terminal, run:"
echo "  ros2 run turtlebot3_teleop teleop_keyboard"
echo ""

ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
