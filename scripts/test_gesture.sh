#!/bin/bash
###############################################################################
# Test Gesture Control - Run hand gesture recognition
###############################################################################

echo "🖐️  Testing Gesture Control"
echo "=========================================="
echo ""

cd "$(dirname "$0")/.."

echo "Checking dependencies..."
python3 -c "import mediapipe" 2>/dev/null || {
    echo "⚠️  Installing mediapipe..."
    pip3 install mediapipe
}

python3 -c "import cv2" 2>/dev/null || {
    echo "⚠️  Installing opencv-python..."
    pip3 install opencv-python
}

echo ""
echo "Gesture Mappings:"
echo "  Open Palm → STOP"
echo "  Fist → MOVE FORWARD"
echo "  Peace Sign → TURN LEFT"
echo "  Three Fingers → TURN RIGHT"
echo "  Four Fingers → MOVE BACKWARD"
echo "  Thumbs Up → INCREASE SPEED"
echo "  Thumbs Down → DECREASE SPEED"
echo ""
echo "Starting gesture control..."
echo "Press 'q' in the video window to stop"
echo ""

python3 main.py gesture --report
