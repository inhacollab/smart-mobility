#!/bin/bash
#############################################################################
# Visual Demos - Show actual working features with GUI
#############################################################################

echo "════════════════════════════════════════════════════════════════════"
echo "   🤖 TurtleBot3 Visual Demonstrations"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "Choose a demo to run:"
echo ""
echo "  1) 📊 Health Monitor Dashboard  - Live system monitoring with graphs"
echo "  2) 👋 Gesture Control Demo      - Hand gesture recognition"
echo "  3) 👁️  Vision System Demo        - Object detection with YOLOv8"
echo "  4) 🚀 Run ALL demos in sequence"
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo ""

read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "▶ Starting Health Monitor Dashboard..."
        echo "  (Press 'q' to quit)"
        python3 demonstrations/demo_health.py
        ;;
    2)
        echo ""
        echo "▶ Starting Gesture Control Demo..."
        echo "  (Show different hand gestures to control robot)"
        echo "  (Press 'q' to quit)"
        python3 demonstrations/demo_gesture.py
        ;;
    3)
        echo ""
        echo "▶ Starting Vision System Demo..."
        echo "  (Point camera at objects to detect them)"
        echo "  (Press 'q' to quit)"
        python3 demonstrations/demo_vision.py
        ;;
    4)
        echo ""
        echo "▶ Running ALL demos in sequence..."
        echo ""
        echo "Demo 1/3: Health Monitor (20 seconds)"
        timeout 20 python3 demonstrations/demo_health.py 2>/dev/null || true
        echo ""
        echo "Demo 2/3: Gesture Control (20 seconds)"
        timeout 20 python3 demonstrations/demo_gesture.py 2>/dev/null || true
        echo ""
        echo "Demo 3/3: Vision System (20 seconds)"
        timeout 20 python3 demonstrations/demo_vision.py 2>/dev/null || true
        echo ""
        echo "✅ All demos completed!"
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "   ✅ Demo completed successfully!"
echo "════════════════════════════════════════════════════════════════════"
