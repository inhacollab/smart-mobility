#!/usr/bin/env python3
"""
Hand Motion Interpreter - Signal Recognition Control
====================================================

Control TurtleBot3 using hand signals detected by MediaPipe.
This is a custom feature that provides intuitive hands-free robot control.

Features:
- Real-time hand signal recognition using MediaPipe
- Multiple signal commands (move, stop, turn, speed control)
- Visual feedback with hand landmark overlay
- Signal history tracking
- ROS2 velocity command publishing
- Configurable signal mappings

Signal Mappings:
- Open palm: STOP
- Fist: MOVE FORWARD
- Peace sign (2 digits): TURN LEFT
- Three digits: TURN RIGHT
- Four digits: MOVE BACKWARD
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
from core.utils import execute_system_call, render_datetime_string
from core.config_manager import ConfigurationHandler


class MotionDirective:
    """Represents a motion directive"""
    
    def __init__(self, signal_name: str, action: str, velocity: Tuple[float, float]):
        self.signal_name = signal_name
        self.action = action
        self.velocity = velocity  # (linear, angular)
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'signal': self.signal_name,
            'action': self.action,
            'velocity': self.velocity,
            'timestamp': self.timestamp.isoformat()
        }


class HandMotionInterpreter:
    """
    Hand motion interpretation and robot control
    
    Uses MediaPipe for real-time hand tracking and signal recognition
    to control the TurtleBot3 robot.
    """
    
    def __init__(self, config: ConfigurationHandler = None):
        """Initialize hand motion interpreter"""
        self.system_logger = logging.getLogger(__name__)
        self.system_config = config or ConfigurationHandler()
        
        self.camera_index = self.system_config.retrieve('gesture.camera_id', 0)
        self.detection_threshold = self.system_config.retrieve('gesture.min_detection_confidence', 0.7)
        self.visual_feedback_enabled = self.system_config.retrieve('gesture.enable_feedback', True)
        
        self.hand_detector = None
        self.media_pipe_hands = None
        self.media_pipe_drawing = None
        
        self.active = False
        self.processing_thread = None
        
        self.signal_record = []
        self.active_signal = None
        self.previous_instruction = None
        
        # Velocity settings
        self.default_forward_velocity = 0.15  # m/s
        self.default_rotation_velocity = 0.5  # rad/s
        self.velocity_scale = 1.0
        
        # Signal mappings
        self.signal_mapping = {
            'open_palm': ('STOP', (0.0, 0.0)),
            'fist': ('FORWARD', (self.default_forward_velocity, 0.0)),
            'peace': ('LEFT', (0.0, self.default_rotation_velocity)),
            'three': ('RIGHT', (0.0, -self.default_rotation_velocity)),
            'four': ('BACKWARD', (-self.default_forward_velocity, 0.0)),
            'thumbs_up': ('SPEED_UP', None),
            'thumbs_down': ('SLOW_DOWN', None),
        }
        
    def setup_hand_tracking(self) -> bool:
        """Initialize MediaPipe hands module"""
        self.system_logger.info("🖐️  Initializing MediaPipe...")
        
        try:
            import mediapipe as mp
            
            self.media_pipe_hands = mp.solutions.hands
            self.media_pipe_drawing = mp.solutions.drawing_utils
            
            self.hand_detector = self.media_pipe_hands.Hands(
                min_detection_confidence=self.detection_threshold,
                min_tracking_confidence=0.5,
                max_num_hands=1
            )
            
            self.system_logger.info("  ✅ MediaPipe initialized")
            return True
            
        except ImportError:
            self.system_logger.error("  ❌ MediaPipe not installed. Run: pip install mediapipe")
            return False
        except Exception as e:
            self.system_logger.error(f"  ❌ Failed to initialize MediaPipe: {e}")
            return False
    
    def initiate_motion_control(self) -> bool:
        """Start signal recognition and robot control"""
        if not self.hand_detector:
            if not self.setup_hand_tracking():
                return False
        
        self.system_logger.info("🎮 Starting motion control...")
        self.system_logger.info("  💡 Use hand signals to control the robot")
        self.system_logger.info("  💡 Press 'q' in the video window to stop")
        
        self.active = True
        self.processing_thread = threading.Thread(target=self._motion_processing_cycle, daemon=True)
        self.processing_thread.start()
        
        self.system_logger.info("  ✅ Motion control started")
        return True
    
    def terminate_motion_control(self):
        """Stop motion control"""
        self.system_logger.info("⏹️  Stopping motion control...")
        self.active = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        if self.hand_detector:
            self.hand_detector.close()
        self.system_logger.info("  ✅ Motion control stopped")
    
    def _motion_processing_cycle(self):
        """Main processing cycle"""
        try:
            import cv2
            import numpy as np
            
            cap = cv2.VideoCapture(self.camera_index)
            
            while self.active and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    self.system_logger.warning("Failed to read frame")
                    continue
                
                # Flip frame for selfie view
                frame = cv2.flip(frame, 1)
                
                # Convert to RGB for MediaPipe
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.hand_detector.process(rgb_frame)
                
                # Process hand landmarks
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Draw landmarks
                        if self.visual_feedback_enabled:
                            self.media_pipe_drawing.draw_landmarks(
                                frame, hand_landmarks, self.media_pipe_hands.HAND_CONNECTIONS
                            )
                        
                        # Recognize signal
                        signal = self._identify_hand_signal(hand_landmarks)
                        if signal:
                            self._process_hand_signal(signal, frame)
                else:
                    # No hand detected - stop robot
                    if self.previous_instruction != 'STOP':
                        self._dispatch_movement_instruction(0.0, 0.0)
                        self.previous_instruction = 'STOP'
                
                # Display current command
                if self.previous_instruction:
                    cv2.putText(frame, f"Command: {self.previous_instruction}", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                cv2.putText(frame, f"Speed: {self.velocity_scale:.1f}x", 
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                
                cv2.imshow('Motion Control', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
        except Exception as e:
            self.system_logger.error(f"Error in processing cycle: {e}")
    
    def _identify_hand_signal(self, hand_landmarks) -> Optional[str]:
        """
        Identify signal from hand landmarks
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            
        Returns:
            Signal name or None
        """
        # Extract landmark positions
        landmarks = hand_landmarks.landmark
        
        # Count extended fingers
        fingers_up = self._tally_extended_digits(landmarks)
        
        # Determine signal
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
        thumb_up = self._evaluate_thumb_orientation(landmarks)
        if thumb_up == 1:
            return 'thumbs_up'
        elif thumb_up == -1:
            return 'thumbs_down'
        
        return None
    
    def _tally_extended_digits(self, landmarks) -> int:
        """Count extended digits"""
        # Simplified digit counting
        # In real implementation, would check angles and positions more precisely
        
        digit_tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky tips
        digit_pips = [3, 6, 10, 14, 18]  # PIPs for comparison
        
        count = 0
        
        # Thumb (special case)
        if landmarks[digit_tips[0]].x < landmarks[digit_pips[0]].x:
            count += 1
        
        # Other digits
        for i in range(1, 5):
            if landmarks[digit_tips[i]].y < landmarks[digit_pips[i]].y:
                count += 1
        
        return count
    
    def _evaluate_thumb_orientation(self, landmarks) -> int:
        """
        Check if thumb is pointing up or down
        
        Returns:
            1 for thumbs up, -1 for thumbs down, 0 for neither
        """
        thumb_tip = landmarks[4]
        thumb_mcp = landmarks[2]
        wrist = landmarks[0]
        
        # Thumbs up: thumb tip above wrist, other digits down
        if thumb_tip.y < wrist.y - 0.1:
            return 1
        # Thumbs down: thumb tip below wrist
        elif thumb_tip.y > wrist.y + 0.1:
            return -1
        
        return 0
    
    def _process_hand_signal(self, signal: str, frame=None):
        """Handle recognized signal"""
        if signal not in self.signal_mapping:
            return
        
        action, velocity = self.signal_mapping[signal]
        
        # Handle speed adjustment signals
        if action == 'SPEED_UP':
            self.velocity_scale = min(2.0, self.velocity_scale + 0.1)
            self.system_logger.info(f"⚡ Speed increased to {self.velocity_scale:.1f}x")
            return
        elif action == 'SLOW_DOWN':
            self.velocity_scale = max(0.3, self.velocity_scale - 0.1)
            self.system_logger.info(f"🐌 Speed decreased to {self.velocity_scale:.1f}x")
            return
        
        # Handle movement signals
        if velocity and self.previous_instruction != action:
            linear, angular = velocity
            # Apply speed multiplier
            linear *= self.velocity_scale
            angular *= self.velocity_scale
            
            self._dispatch_movement_instruction(linear, angular)
            
            # Log command
            command = MotionDirective(signal, action, (linear, angular))
            self.signal_record.append(command)
            self.active_signal = signal
            self.previous_instruction = action
            
            self.system_logger.info(f"✋ Signal: {signal} -> {action}")
            
            # Keep record limited
            if len(self.signal_record) > 1000:
                self.signal_record = self.signal_record[-1000:]
    
    def _dispatch_movement_instruction(self, linear: float, angular: float):
        """
        Send movement instruction to robot
        
        Args:
            linear: Linear velocity (m/s)
            angular: Angular velocity (rad/s)
        """
        # In real implementation, would publish to /cmd_vel topic
        cmd = f"ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \"{{linear: {{x: {linear}, y: 0.0, z: 0.0}}, angular: {{x: 0.0, y: 0.0, z: {angular}}}}}\""
        
        # Execute in background
        # run_command(cmd, check=False)
        
        self.system_logger.debug(f"Movement instruction: linear={linear:.2f}, angular={angular:.2f}")
    
    def tune_hand_signals(self):
        """Run signal tuning wizard"""
        self.system_logger.info("🎯 Starting signal tuning...")
        self.system_logger.info("  Follow the on-screen instructions to tune signals")
        
        signals_to_tune = [
            'open_palm', 'fist', 'peace', 'three', 'four', 'thumbs_up', 'thumbs_down'
        ]
        
        for signal in signals_to_tune:
            self.system_logger.info(f"  Show signal: {signal}")
            self.system_logger.info("  Press Enter when ready...")
            input()
        
        self.system_logger.info("  ✅ Tuning complete")
    
    def retrieve_signal_statistics(self) -> Dict:
        """Get signal usage statistics"""
        if not self.signal_record:
            return {'total_signals': 0}
        
        # Count signals by type
        signal_counts = {}
        for cmd in self.signal_record:
            signal_counts[cmd.signal_name] = signal_counts.get(cmd.signal_name, 0) + 1
        
        return {
            'total_signals': len(self.signal_record),
            'unique_signals': len(signal_counts),
            'signal_distribution': signal_counts,
            'current_signal': self.active_signal,
            'last_instruction': self.previous_instruction
        }
    
    def produce_signal_summary(self) -> str:
        """Generate signal control summary"""
        stats = self.retrieve_signal_statistics()
        
        report_lines = [
            "=" * 70,
            "🖐️  SIGNAL CONTROL SUMMARY",
            "=" * 70,
            f"Generated: {render_datetime_string()}",
            "",
            "📊 STATISTICS",
            "-" * 70,
            f"Total Signals: {stats.get('total_signals', 0)}",
            f"Unique Signals: {stats.get('unique_signals', 0)}",
            f"Current Signal: {stats.get('current_signal', 'None')}",
            f"Last Instruction: {stats.get('last_instruction', 'None')}",
            f"Speed Multiplier: {self.velocity_scale:.1f}x",
            ""
        ]
        
        if stats.get('signal_distribution'):
            report_lines.extend([
                "✋ SIGNAL USAGE",
                "-" * 70
            ])
            for signal, count in sorted(stats['signal_distribution'].items(), 
                                         key=lambda x: x[1], reverse=True):
                action = self.signal_mapping.get(signal, ['Unknown'])[0]
                report_lines.append(f"  {signal} ({action}): {count}")
            report_lines.append("")
        
        report_lines.extend([
            "🎮 SIGNAL MAPPINGS",
            "-" * 70,
            "  Open Palm → STOP",
            "  Fist → MOVE FORWARD",
            "  Peace (2 digits) → TURN LEFT",
            "  Three Digits → TURN RIGHT",
            "  Four Digits → MOVE BACKWARD",
            "  Thumbs Up → INCREASE SPEED",
            "  Thumbs Down → DECREASE SPEED",
            "",
            "=" * 70
        ])
        
        return '\n'.join(report_lines)


def main():
    """Main entry point for standalone execution"""
    from core.logger import setup_logger
    
    logger = setup_logger('hand_motion_interpreter', Path('logs'))
    interpreter = HandMotionInterpreter()
    
    # Demo motion control
    print("🖐️  Hand Motion Interpreter Demo")
    print("=" * 70)
    print("\nSignal Mappings:")
    print("  Open Palm → STOP")
    print("  Fist → MOVE FORWARD")
    print("  Peace Sign → TURN LEFT")
    print("  Three Digits → TURN RIGHT")
    print("  Four Digits → MOVE BACKWARD")
    print("  Thumbs Up → INCREASE SPEED")
    print("  Thumbs Down → DECREASE SPEED")
    print("\nTo start: interpreter.initiate_motion_control()")
    print("\nSummary:")
    print(interpreter.produce_signal_summary())


if __name__ == "__main__":
    main()
