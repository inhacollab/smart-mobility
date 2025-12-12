"""
TurtleBot3 Smart Automation System - Automation Package
========================================================
Contains all automation modules for setup, maintenance, navigation, vision, and gestures

Course: Smart Mobility
"""

from .setup_manager import SetupManager
from .health_monitor import HealthMonitor
from .smart_navigator import SmartNavigator
from .vision_processor import VisionProcessor
from .gesture_controller import GestureController

__all__ = [
    'SetupManager',
    'HealthMonitor',
    'SmartNavigator',
    'VisionProcessor',
    'GestureController'
]
