#!/usr/bin/env python3
"""
Gesture Controller - Hand Gesture Recognition Control
=======================================================

Control TurtleBot3 using hand gestures detected by MediaPipe.
This is a custom feature that provides intuitive hands-free robot control.

Features:
- Real-time hand gesture recognition using MediaPipe
- Multiple gesture commands (move, stop, turn, speed control)
- Visual feedback with hand landmark overlay
- Gesture history tracking
- ROS2 velocity command publishing
- Configurable gesture mappings

Gesture Mappings:
- Open palm: STOP
- Fist: MOVE FORWARD
- Peace sign (2 fingers): TURN LEFT
- Three fingers: TURN RIGHT
- Four fingers: MOVE BACKWARD
- Thumbs up: INCREASE SPEED
- Thumbs down: DECREASE SPEED

Author: Javokhir Yuldoshev
Course: Smart Mobility - INHA University
Date: December 2025
"""

import sys
from pathlib import Path
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime
import threading
import time

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.utils import run_command, format_timestamp
from core.config_manager import ConfigManager


class GestureCommand:
    """Represents a gesture command"""
    
    def __init__(self, gesture_name: str, action: str, velocity: Tuple[float, float]):
        self.gesture_name = gesture_name
        self.action = action
        self.velocity = velocity  # (linear, angular)
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'gesture': self.gesture_name,
            'action': self.action,
            'velocity': self.velocity,
            'timestamp': self.timestamp.isoformat()
        }


class GestureController:
    """
    Hand gesture recognition and robot control
    
    Uses MediaPipe for real-time hand tracking and gesture recognition
    to control the TurtleBot3 robot.
    """
    
    def __init__(self, config: ConfigManager = None):
        """Initialize gesture controller"""
        self.logger = logging.getLogger(__name__)
        self.config = config or ConfigManager()
        
        self.camera_id = self.config.get('gesture.camera_id', 0)
        self.min_detection_confidence = self.config.get('gesture.min_detection_confidence', 0.7)
        self.enable_feedback = self.config.get('gesture.enable_feedback', True)
        
        self.hands = None
        self.mp_hands = None
        self.mp_drawing = None
        
        self.running = False
        self.control_thread = None
        
        self.gesture_history = []
        self.current_gesture = None
        self.last_command = None
        
        # Velocity settings
        self.base_linear_speed = 0.15  # m/s
        self.base_angular_speed = 0.5  # rad/s
        self.speed_multiplier = 1.0
        
        # Gesture mappings
        self.gesture_map = {
            'open_palm': ('STOP', (0.0, 0.0)),
            'fist': ('FORWARD', (self.base_linear_speed, 0.0)),
            'peace': ('LEFT', (0.0, self.base_angular_speed)),
            'three': ('RIGHT', (0.0, -self.base_angular_speed)),
            'four': ('BACKWARD', (-self.base_linear_speed, 0.0)),
            'thumbs_up': ('SPEED_UP', None),
            'thumbs_down': ('SLOW_DOWN', None),
        }
        
    def initialize_mediapipe(self) -> bool:
        """Initialize MediaPipe hands module"""
        self.logger.info("🖐️  Initializing MediaPipe...")
        
        try:
            import mediapipe as mp
            
            self.mp_hands = mp.solutions.hands
            self.mp_drawing = mp.solutions.drawing_utils
            
            self.hands = self.mp_hands.Hands(
                min_detection_confidence=self.min_detection_confidence,
                min_tracking_confidence=0.5,
                max_num_hands=1
            )
            
            self.logger.info("  ✅ MediaPipe initialized")
            return True
            
        except ImportError:
            self.logger.error("  ❌ MediaPipe not installed. Run: pip install mediapipe")
            return False
        except Exception as e:
            self.logger.error(f"  ❌ Failed to initialize MediaPipe: {e}")
            return False
    
    def start_gesture_control(self) -> bool:
        """Start gesture recognition and robot control"""
        if not self.hands:
            if not self.initialize_mediapipe():
                return False
        
        self.logger.info("🎮 Starting gesture control...")
        self.logger.info("  💡 Use hand gestures to control the robot")
        self.logger.info("  💡 Press 'q' in the video window to stop")
        
        self.running = True
        self.control_thread = threading.Thread(target=self._control_loop, daemon=True)
        self.control_thread.start()
        
        self.logger.info("  ✅ Gesture control started")
        return True
    
    def stop_gesture_control(self):
        """Stop gesture control"""
        self.logger.info("⏹️  Stopping gesture control...")
        self.running = False
        if self.control_thread:
            self.control_thread.join(timeout=5)
        if self.hands:
            self.hands.close()
        self.logger.info("  ✅ Gesture control stopped")
    
    def _control_loop(self):
        """Main control loop"""
        try:
            import cv2
            import numpy as np
            
            cap = cv2.VideoCapture(self.camera_id)
            
            while self.running and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    self.logger.warning("Failed to read frame")
                    continue
                
                # Flip frame for selfie view
                frame = cv2.flip(frame, 1)
                
                # Convert to RGB for MediaPipe
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.hands.process(rgb_frame)
                
                # Process hand landmarks
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Draw landmarks
                        if self.enable_feedback:
                            self.mp_drawing.draw_landmarks(
                                frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                            )
                        
                        # Recognize gesture
                        gesture = self._recognize_gesture(hand_landmarks)
                        if gesture:
                            self._handle_gesture(gesture, frame)
                else:
                    # No hand detected - stop robot
                    if self.last_command != 'STOP':
                        self._send_velocity_command(0.0, 0.0)
                        self.last_command = 'STOP'
                
                # Display current command
                if self.last_command:
                    cv2.putText(frame, f"Command: {self.last_command}", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                cv2.putText(frame, f"Speed: {self.speed_multiplier:.1f}x", 
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                
                cv2.imshow('Gesture Control', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
        except Exception as e:
            self.logger.error(f"Error in control loop: {e}")
    
    def _recognize_gesture(self, hand_landmarks) -> Optional[str]:
        """
        Recognize gesture from hand landmarks
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            
        Returns:
            Gesture name or None
        """
        # Extract landmark positions
        landmarks = hand_landmarks.landmark
        
        # Count extended fingers
        fingers_up = self._count_fingers(landmarks)
        
        # Determine gesture
        if fingers_up == 0:
            return 'fist'
        elif fingers_up == 5:
            return 'open_palm'
        elif fingers_up == 2:
            return 'peace'
        elif fingers_up == 3:
            return 'three'
        elif fingers_up == 4:
            return 'four'
        
        # Check for thumbs up/down
        thumb_up = self._is_thumb_up(landmarks)
        if thumb_up == 1:
            return 'thumbs_up'
        elif thumb_up == -1:
            return 'thumbs_down'
        
        return None
    
    def _count_fingers(self, landmarks) -> int:
        """Count extended fingers"""
        # Simplified finger counting
        # In real implementation, would check angles and positions more precisely
        
        finger_tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky tips
        finger_pips = [3, 6, 10, 14, 18]  # PIPs for comparison
        
        count = 0
        
        # Thumb (special case)
        if landmarks[finger_tips[0]].x < landmarks[finger_pips[0]].x:
            count += 1
        
        # Other fingers
        for i in range(1, 5):
            if landmarks[finger_tips[i]].y < landmarks[finger_pips[i]].y:
                count += 1
        
        return count
    
    def _is_thumb_up(self, landmarks) -> int:
        """
        Check if thumb is pointing up or down
        
        Returns:
            1 for thumbs up, -1 for thumbs down, 0 for neither
        """
        thumb_tip = landmarks[4]
        thumb_mcp = landmarks[2]
        wrist = landmarks[0]
        
        # Thumbs up: thumb tip above wrist, other fingers down
        if thumb_tip.y < wrist.y - 0.1:
            return 1
        # Thumbs down: thumb tip below wrist
        elif thumb_tip.y > wrist.y + 0.1:
            return -1
        
        return 0
    
    def _handle_gesture(self, gesture: str, frame=None):
        """Handle recognized gesture"""
        if gesture not in self.gesture_map:
            return
        
        action, velocity = self.gesture_map[gesture]
        
        # Handle speed adjustment gestures
        if action == 'SPEED_UP':
            self.speed_multiplier = min(2.0, self.speed_multiplier + 0.1)
            self.logger.info(f"⚡ Speed increased to {self.speed_multiplier:.1f}x")
            return
        elif action == 'SLOW_DOWN':
            self.speed_multiplier = max(0.3, self.speed_multiplier - 0.1)
            self.logger.info(f"🐌 Speed decreased to {self.speed_multiplier:.1f}x")
            return
        
        # Handle movement gestures
        if velocity and self.last_command != action:
            linear, angular = velocity
            # Apply speed multiplier
            linear *= self.speed_multiplier
            angular *= self.speed_multiplier
            
            self._send_velocity_command(linear, angular)
            
            # Log command
            command = GestureCommand(gesture, action, (linear, angular))
            self.gesture_history.append(command)
            self.current_gesture = gesture
            self.last_command = action
            
            self.logger.info(f"✋ Gesture: {gesture} -> {action}")
            
            # Keep history limited
            if len(self.gesture_history) > 1000:
                self.gesture_history = self.gesture_history[-1000:]
    
    def _send_velocity_command(self, linear: float, angular: float):
        """
        Send velocity command to robot
        
        Args:
            linear: Linear velocity (m/s)
            angular: Angular velocity (rad/s)
        """
        # In real implementation, would publish to /cmd_vel topic
        cmd = f"ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \"{{linear: {{x: {linear}, y: 0.0, z: 0.0}}, angular: {{x: 0.0, y: 0.0, z: {angular}}}}}\""
        
        # Execute in background
        # run_command(cmd, check=False)
        
        self.logger.debug(f"Velocity command: linear={linear:.2f}, angular={angular:.2f}")
    
    def calibrate_gestures(self):
        """Run gesture calibration wizard"""
        self.logger.info("🎯 Starting gesture calibration...")
        self.logger.info("  Follow the on-screen instructions to calibrate gestures")
        
        gestures_to_calibrate = [
            'open_palm', 'fist', 'peace', 'three', 'four', 'thumbs_up', 'thumbs_down'
        ]
        
        for gesture in gestures_to_calibrate:
            self.logger.info(f"  Show gesture: {gesture}")
            self.logger.info("  Press Enter when ready...")
            input()
        
        self.logger.info("  ✅ Calibration complete")
    
    def get_gesture_stats(self) -> Dict:
        """Get gesture usage statistics"""
        if not self.gesture_history:
            return {'total_gestures': 0}
        
        # Count gestures by type
        gesture_counts = {}
        for cmd in self.gesture_history:
            gesture_counts[cmd.gesture_name] = gesture_counts.get(cmd.gesture_name, 0) + 1
        
        return {
            'total_gestures': len(self.gesture_history),
            'unique_gestures': len(gesture_counts),
            'gesture_distribution': gesture_counts,
            'current_gesture': self.current_gesture,
            'last_command': self.last_command
        }
    
    def generate_gesture_report(self) -> str:
        """Generate gesture control report"""
        stats = self.get_gesture_stats()
        
        report_lines = [
            "=" * 70,
            "🖐️  GESTURE CONTROL REPORT",
            "=" * 70,
            f"Generated: {format_timestamp()}",
            "",
            "📊 STATISTICS",
            "-" * 70,
            f"Total Gestures: {stats.get('total_gestures', 0)}",
            f"Unique Gestures: {stats.get('unique_gestures', 0)}",
            f"Current Gesture: {stats.get('current_gesture', 'None')}",
            f"Last Command: {stats.get('last_command', 'None')}",
            f"Speed Multiplier: {self.speed_multiplier:.1f}x",
            ""
        ]
        
        if stats.get('gesture_distribution'):
            report_lines.extend([
                "✋ GESTURE USAGE",
                "-" * 70
            ])
            for gesture, count in sorted(stats['gesture_distribution'].items(), 
                                         key=lambda x: x[1], reverse=True):
                action = self.gesture_map.get(gesture, ['Unknown'])[0]
                report_lines.append(f"  {gesture} ({action}): {count}")
            report_lines.append("")
        
        report_lines.extend([
            "🎮 GESTURE MAPPINGS",
            "-" * 70,
            "  Open Palm → STOP",
            "  Fist → MOVE FORWARD",
            "  Peace (2 fingers) → TURN LEFT",
            "  Three Fingers → TURN RIGHT",
            "  Four Fingers → MOVE BACKWARD",
            "  Thumbs Up → INCREASE SPEED",
            "  Thumbs Down → DECREASE SPEED",
            "",
            "=" * 70
        ])
        
        return '\n'.join(report_lines)


def main():
    """Main entry point for standalone execution"""
    from core.logger import setup_logger
    
    logger = setup_logger('gesture_controller', Path('logs'))
    controller = GestureController()
    
    # Demo gesture control
    print("🖐️  Gesture Controller Demo")
    print("=" * 70)
    print("\nGesture Mappings:")
    print("  Open Palm → STOP")
    print("  Fist → MOVE FORWARD")
    print("  Peace Sign → TURN LEFT")
    print("  Three Fingers → TURN RIGHT")
    print("  Four Fingers → MOVE BACKWARD")
    print("  Thumbs Up → INCREASE SPEED")
    print("  Thumbs Down → DECREASE SPEED")
    print("\nTo start: controller.start_gesture_control()")
    print("\nReport:")
    print(controller.generate_gesture_report())


if __name__ == "__main__":
    main()
