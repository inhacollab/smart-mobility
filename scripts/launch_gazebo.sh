#!/bin/bash
# Simple TurtleBot3 Gazebo Launcher
# Works from any directory

# Kill old processes
pkill -9 gzserver gzclient 2>/dev/null
sleep 1

# Change to home to avoid path issues
cd ~

# Source ROS2 (using bash version for compatibility)
source /opt/ros/humble/setup.bash

# Set Gazebo plugin path
export GAZEBO_PLUGIN_PATH=/opt/ros/humble/lib:$GAZEBO_PLUGIN_PATH
export LD_LIBRARY_PATH=/opt/ros/humble/lib:$LD_LIBRARY_PATH

# Set model
export TURTLEBOT3_MODEL=burger

echo "=========================================="
echo "Launching TurtleBot3 Simulation"
echo "Model: burger"
echo "=========================================="
echo ""
echo "Wait for Gazebo to fully load (~30 seconds)"
echo "You should see a small red/black robot"
echo ""

# Launch
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
