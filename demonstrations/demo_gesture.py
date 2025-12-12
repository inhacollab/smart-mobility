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

# Gesture recognition - Simplified for STOP and FORWARD commands
def recognize_gesture(hand_landmarks, handedness):
    """Recognize STOP and FORWARD hand gestures for both left and right hands"""
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

    # Thumb detection - different logic for left vs right hand
    if handedness == "Left":
        # For left hand, thumb extends to the right
        if thumb_tip.x > landmarks[3].x:
            fingers_up += 1
    else:  # Right hand
        # For right hand, thumb extends to the left
        if thumb_tip.x < landmarks[3].x:
            fingers_up += 1

    # Other fingers (check if tip is above base) - same for both hands
    finger_tips = [index_tip, middle_tip, ring_tip, pinky_tip]
    finger_bases = [landmarks[6], landmarks[10], landmarks[14], landmarks[18]]

    for tip, base in zip(finger_tips, finger_bases):
        if tip.y < base.y:
            fingers_up += 1

    # Recognize only STOP and FORWARD commands
    if fingers_up == 0:
        return "STOP", (0, 0, 255), "square"  # Red for STOP
    elif fingers_up == 5:
        return "FORWARD", (0, 255, 0), "arrow"  # Green for FORWARD
    else:
        return "UNKNOWN", (128, 128, 128), "question"  # Gray for unrecognized

print("="*60)
print("  🤖 TurtleBot3 Gesture Control Demo")
print("="*60)
print("\nGesture Commands (Works with both LEFT & RIGHT hands):")
print("  ✋ CLOSED FIST (0 fingers)  → STOP")
print("  🖐️  OPEN HAND (5 fingers)   → FORWARD")
print("\nBoth hands are supported - gestures work the same way!")
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
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            # Get handedness (Left or Right)
            hand_label = results.multi_handedness[idx].classification[0].label

            # Draw hand skeleton
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
                mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2)
            )

            # Recognize gesture with handedness
            gesture, color, icon = recognize_gesture(hand_landmarks, hand_label)

            # Display command with visual feedback
            if gesture == "STOP":
                command_text = f"🚫 STOP - {hand_label} hand detected"
                bg_color = (0, 0, 100)  # Dark red background
            elif gesture == "FORWARD":
                command_text = f"▶️ FORWARD - {hand_label} hand detected"
                bg_color = (0, 100, 0)  # Dark green background
            else:
                command_text = f"❓ Unknown gesture - {hand_label} hand"
                bg_color = (50, 50, 50)  # Gray background

            # Draw command background
            cv2.rectangle(frame, (40, 70), (w-40, 130), bg_color, -1)
            cv2.rectangle(frame, (40, 70), (w-40, 130), color, 3)

            # Display command
            cv2.putText(frame, command_text,
                       (60, 105), cv2.FONT_HERSHEY_DUPLEX,
                       1.2, (255, 255, 255), 3)
    else:
        # No hand detected - show waiting message
        cv2.rectangle(frame, (40, 70), (w-40, 130), (50, 50, 70), -1)
        cv2.rectangle(frame, (40, 70), (w-40, 130), (100, 100, 150), 3)
        cv2.putText(frame, "👋 Show your LEFT or RIGHT hand - Make a fist to STOP or open hand to go FORWARD",
                   (60, 105), cv2.FONT_HERSHEY_DUPLEX,
                   1.0, (255, 255, 255), 2)
    
    # Calculate FPS
    fps_counter += 1
    if time.time() - fps_time >= 1.0:
        fps = fps_counter
        fps_counter = 0
        fps_time = time.time()
    
    # Draw info overlay
    cv2.rectangle(frame, (0, 0), (w, 60), (0, 0, 0), -1)
    cv2.putText(frame, "TurtleBot3 Gesture Control - STOP & FORWARD Commands",
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
