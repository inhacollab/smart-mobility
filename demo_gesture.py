#!/usr/bin/env python3
"""
Real-time Hand Gesture Control Demo
Shows webcam with hand tracking and recognized gestures
"""
import cv2
import mediapipe as mp
import time

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Gesture recognition
def recognize_gesture(hand_landmarks):
    """Recognize basic hand gestures"""
    landmarks = hand_landmarks.landmark
    
    # Get finger tip and base positions
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]
    
    wrist = landmarks[0]
    
    # Count extended fingers
    fingers_up = 0
    
    # Thumb (check if tip is to the right of base)
    if thumb_tip.x > landmarks[3].x:
        fingers_up += 1
    
    # Other fingers (check if tip is above base)
    finger_tips = [index_tip, middle_tip, ring_tip, pinky_tip]
    finger_bases = [landmarks[6], landmarks[10], landmarks[14], landmarks[18]]
    
    for tip, base in zip(finger_tips, finger_bases):
        if tip.y < base.y:
            fingers_up += 1
    
    # Recognize gestures
    if fingers_up == 0:
        return "STOP ✋", (0, 0, 255)  # Red
    elif fingers_up == 5:
        return "FORWARD 👋", (0, 255, 0)  # Green
    elif fingers_up == 1:
        return "SLOW ☝️", (255, 255, 0)  # Yellow
    elif fingers_up == 2:
        return "TURN ✌️", (255, 165, 0)  # Orange
    else:
        return f"{fingers_up} fingers", (255, 255, 255)  # White

print("="*60)
print("  🤖 TurtleBot3 Gesture Control Demo")
print("="*60)
print("\nGesture Commands:")
print("  ✋ Fist (0 fingers)    → STOP")
print("  👋 Open hand (5)       → FORWARD")
print("  ☝️  One finger (1)      → SLOW")
print("  ✌️  Two fingers (2)     → TURN")
print("\nPress 'q' to quit")
print("="*60)

# Open webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

fps_time = time.time()
fps_counter = 0
fps = 0

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break
    
    # Flip frame horizontally for mirror effect
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    
    # Convert to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    
    # Draw hand landmarks and recognize gestures
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw hand skeleton
            mp_drawing.draw_landmarks(
                frame, 
                hand_landmarks, 
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
                mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2)
            )
            
            # Recognize gesture
            gesture, color = recognize_gesture(hand_landmarks)
            
            # Display gesture text
            cv2.putText(frame, f"Gesture: {gesture}", 
                       (50, 100), cv2.FONT_HERSHEY_DUPLEX, 
                       1.5, color, 3)
    else:
        cv2.putText(frame, "No hand detected", 
                   (50, 100), cv2.FONT_HERSHEY_DUPLEX, 
                   1.5, (128, 128, 128), 3)
    
    # Calculate FPS
    fps_counter += 1
    if time.time() - fps_time >= 1.0:
        fps = fps_counter
        fps_counter = 0
        fps_time = time.time()
    
    # Draw info overlay
    cv2.rectangle(frame, (0, 0), (w, 60), (0, 0, 0), -1)
    cv2.putText(frame, "TurtleBot3 Gesture Control", 
               (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 
               1, (0, 255, 255), 2)
    cv2.putText(frame, f"FPS: {fps}", 
               (w - 150, 35), cv2.FONT_HERSHEY_SIMPLEX, 
               0.8, (0, 255, 0), 2)
    
    # Show instructions
    cv2.putText(frame, "Press 'q' to quit", 
               (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 
               0.7, (255, 255, 255), 2)
    
    # Display
    cv2.imshow('TurtleBot3 Gesture Control', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
hands.close()
print("\n✅ Demo completed!")
