"""
TurtleBot3 Smart Automation System - Automation Package
========================================================
Contains all automation modules for setup, maintenance, navigation, vision, and gestures

Author: Javokhir Yuldoshev
Course: Smart Mobility - INHA University
Date: December 2025
"""

from .setup_manager import InstallationOrchestrator
from .health_monitor import SystemHealthTracker
from .smart_navigator import AutonomousPathfinder
from .vision_processor import ObjectRecognitionEngine
from .gesture_controller import HandMotionInterpreter

__all__ = [
    'InstallationOrchestrator',
    'SystemHealthTracker',
    'AutonomousPathfinder',
    'ObjectRecognitionEngine',
    'HandMotionInterpreter'
]
