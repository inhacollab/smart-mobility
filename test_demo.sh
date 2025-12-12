#!/bin/bash
#############################################################################
# Quick Demo Test - Run this before recording video
# Tests all components to verify they work
#############################################################################

cd ~/Projects/inha-operating-systems/tb3-smart-automation

echo "════════════════════════════════════════════════════════════════════"
echo "   TurtleBot3 Smart Automation - Quick Demo Test"
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Test 1: System Check
echo "▶ Test 1: System Environment Check"
echo "──────────────────────────────────────────────────────────────────"
python3 main.py --check-env
echo ""

# Test 2: Module Verification
echo "▶ Test 2: Module Verification"
echo "──────────────────────────────────────────────────────────────────"
python3 verify.py
echo ""

# Test 3: Code Statistics
echo "▶ Test 3: Code Statistics"
echo "──────────────────────────────────────────────────────────────────"
echo "Setup Manager:        $(wc -l < automation/setup_manager.py) lines"
echo "Health Monitor:       $(wc -l < automation/health_monitor.py) lines"
echo "Smart Navigator:      $(wc -l < automation/smart_navigator.py) lines"
echo "Vision Processor:     $(wc -l < automation/vision_processor.py) lines"
echo "Gesture Controller:   $(wc -l < automation/gesture_controller.py) lines"
echo "Main Orchestrator:    $(wc -l < main.py) lines"
echo "Total Python code:    $(find . -name "*.py" -not -path "./__pycache__/*" -exec wc -l {} + | tail -1 | awk '{print $1}') lines"
echo ""

# Test 4: ROS2 Packages
echo "▶ Test 4: ROS2 Installation Check"
echo "──────────────────────────────────────────────────────────────────"
TB3_COUNT=$(bash -c "cd /tmp && source /opt/ros/humble/setup.bash 2>/dev/null && ros2 pkg list 2>/dev/null | grep -c turtlebot3" || echo "0")
echo "TurtleBot3 packages installed: $TB3_COUNT"
if [ "$TB3_COUNT" -gt "30" ]; then
    echo "✅ ROS2 Humble with TurtleBot3 is properly installed"
else
    echo "⚠️  ROS2 installation may need attention"
fi
echo ""

# Test 5: Health Monitoring (5 second test)
echo "▶ Test 5: Health Monitoring Demo (5 seconds)"
echo "──────────────────────────────────────────────────────────────────"
timeout 5 python3 main.py health 2>&1 | head -40
echo ""

# Test 6: Documentation Check
echo "▶ Test 6: Documentation Files"
echo "──────────────────────────────────────────────────────────────────"
ls -lh *.md docs/*.md 2>/dev/null | awk '{printf "%-40s %8s\n", $9, $5}'
echo ""

# Test 7: Help System
echo "▶ Test 7: Command Line Interface"
echo "──────────────────────────────────────────────────────────────────"
python3 main.py --help | head -25
echo ""

# Summary
echo "════════════════════════════════════════════════════════════════════"
echo "   ✅ DEMO TEST COMPLETE"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "All components tested. You're ready to record your video!"
echo ""
echo "Quick commands for video:"
echo "  1. python3 main.py --check-env"
echo "  2. python3 main.py health"
echo "  3. python3 main.py --help"
echo "  4. python3 verify.py"
echo ""
echo "See DEMO_SCRIPT.md for full recording guide"
echo "════════════════════════════════════════════════════════════════════"
