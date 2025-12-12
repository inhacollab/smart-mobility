#!/bin/bash
###############################################################################
# Test Vision - Run YOLOv8 detection on webcam
###############################################################################

echo "👁️  Testing Vision Processing"
echo "=========================================="
echo ""

cd "$(dirname "$0")/.."

echo "Checking dependencies..."
python3 -c "import ultralytics" 2>/dev/null || {
    echo "⚠️  Installing ultralytics..."
    pip3 install ultralytics
}

python3 -c "import cv2" 2>/dev/null || {
    echo "⚠️  Installing opencv-python..."
    pip3 install opencv-python
}

echo ""
echo "Starting webcam detection..."
echo "Press 'q' in the video window to stop"
echo ""

python3 main.py vision --webcam --duration 60
