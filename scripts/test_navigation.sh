#!/bin/bash
###############################################################################
# Test Navigation - Launch simulation and test navigation
###############################################################################

echo "🧭 Testing TurtleBot3 Navigation"
echo "=========================================="

# Source environment
if [ -f "$HOME/tb3_ws/install/setup.bash" ]; then
    source $HOME/tb3_ws/install/setup.bash
else
    echo "❌ Workspace not found. Run install.sh first."
    exit 1
fi

export TURTLEBOT3_MODEL=burger

echo "1. Launching Gazebo simulation..."
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py &
GAZEBO_PID=$!
sleep 5

echo "2. Waiting for simulation to start..."
sleep 10

echo "3. Launching navigation..."
ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True &
NAV_PID=$!
sleep 5

echo ""
echo "=========================================="
echo "✅ Navigation test environment launched!"
echo "=========================================="
echo ""
echo "📝 Instructions:"
echo "  1. RViz should open automatically"
echo "  2. Set initial pose using '2D Pose Estimate' button"
echo "  3. Set goal using '2D Goal Pose' button"
echo "  4. Watch the robot navigate!"
echo ""
echo "Press Ctrl+C to stop all processes"
echo ""

# Wait for user interrupt
wait $NAV_PID

# Cleanup
echo "Shutting down..."
kill $GAZEBO_PID $NAV_PID 2>/dev/null
