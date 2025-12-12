#!/bin/bash
###############################################################################
# Health Check Script - Quick health diagnostics
###############################################################################

echo "🏥 TurtleBot3 Health Check"
echo "=========================================="
echo ""

# Source ROS2 environment
if [ -f "$HOME/tb3_ws/install/setup.bash" ]; then
    source $HOME/tb3_ws/install/setup.bash
fi

# Check if ROS2 is running
echo "Checking ROS2 daemon..."
if ros2 daemon status &> /dev/null; then
    echo "✅ ROS2 daemon is running"
else
    echo "⚠️  ROS2 daemon not running, starting..."
    ros2 daemon start
fi

echo ""
echo "📊 System Resources:"
echo "----------------------------------------"
echo -n "CPU Usage: "
top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1
echo -n "Memory Usage: "
free | grep Mem | awk '{printf "%.1f%%\n", $3/$2 * 100.0}'
echo -n "Disk Usage: "
df -h / | tail -1 | awk '{print $5}'

echo ""
echo "🔋 Battery Status:"
echo "----------------------------------------"
# Try to read battery from ROS topic
timeout 2 ros2 topic echo /battery_state --once 2>/dev/null || echo "❌ Battery topic not available"

echo ""
echo "📡 Active ROS2 Topics:"
echo "----------------------------------------"
ros2 topic list | head -10

echo ""
echo "🔍 Node Status:"
echo "----------------------------------------"
ros2 node list | head -10

echo ""
echo "=========================================="
echo "Health check complete!"
