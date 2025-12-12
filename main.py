#!/usr/bin/env python3
"""
TurtleBot3 Smart Automation - Main Orchestration Script
========================================================

Comprehensive automation system for TurtleBot3 with ROS2 Humble.
Integrates all modules: Setup, Health Monitoring, Navigation, Vision, and Gesture Control.

Author: Javokhir Yuldoshev
Student ID: 12214760
Course: Smart Mobility
Institution: INHA University
Professor: Prof. MP
Submission Date: December 12, 2025

This project demonstrates OS concepts including:
- Process management (multi-threading for concurrent operations)
- Inter-process communication (ROS2 topics/services)
- Resource monitoring (CPU, memory, battery)
- File I/O operations (logging, configuration)
- System automation (installation, maintenance)

Usage:
    python main.py --help
    python main.py setup
    python main.py health --monitor
    python main.py navigate --slam
    python main.py vision --webcam
    python main.py gesture
"""

import sys
import os
from pathlib import Path
import argparse
import logging
from datetime import datetime
import signal

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.logger import setup_logger
from core.config_manager import ConfigManager
from core.utils import get_system_info, check_ros_environment, get_ros_distro

from automation.setup_manager import SetupManager
from automation.health_monitor import HealthMonitor
from automation.smart_navigator import SmartNavigator
from automation.vision_processor import VisionProcessor
from automation.gesture_controller import GestureController


class TurtleBot3SmartAutomation:
    """
    Main orchestration class for TurtleBot3 Smart Automation System
    
    Coordinates all automation modules and provides unified interface.
    """
    
    def __init__(self, config_path: Path = None):
        """Initialize the automation system"""
        self.setup_signal_handlers()
        
        # Setup logging
        log_dir = Path('logs')
        self.logger = setup_logger('tb3_automation', log_dir)
        
        self.logger.info("=" * 80)
        self.logger.info("🤖 TURTLEBOT3 SMART AUTOMATION SYSTEM")
        self.logger.info("=" * 80)
        self.logger.info(f"Author: Javokhir Yuldoshev")
        self.logger.info(f"Course: Smart Mobility - INHA University")
        self.logger.info(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 80)
        
        # Load configuration
        self.config = ConfigManager(config_path)
        
        # Initialize modules
        self.setup_manager = None
        self.health_monitor = None
        self.navigator = None
        self.vision_processor = None
        self.gesture_controller = None
        
        # System state
        self.running = False
        
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n\n🛑 Received shutdown signal...")
        self.shutdown()
        sys.exit(0)
    
    def print_header(self, title: str):
        """Print formatted section header"""
        print("\n" + "=" * 80)
        print(f" {title}")
        print("=" * 80 + "\n")
    
    def check_environment(self) -> bool:
        """Check system environment and prerequisites"""
        self.print_header("🔍 ENVIRONMENT CHECK")
        
        # System info
        sys_info = get_system_info()
        print(f"OS: {sys_info['os']} {sys_info['os_version']}")
        print(f"Architecture: {sys_info['architecture']}")
        print(f"Python: {sys_info['python_version']}")
        print(f"CPU Cores: {sys_info['cpu_count']}")
        print(f"Memory: {sys_info['memory_available_gb']:.1f} GB / {sys_info['memory_total_gb']:.1f} GB")
        print(f"Disk Space: {sys_info['disk_free_gb']:.1f} GB free")
        
        # ROS2 environment
        if check_ros_environment():
            ros_distro = get_ros_distro()
            print(f"\n✅ ROS2 environment detected: {ros_distro}")
            if ros_distro != 'humble':
                print(f"⚠️  Warning: Expected 'humble', found '{ros_distro}'")
            return True
        else:
            print("\n❌ ROS2 environment not detected")
            print("💡 Run setup first: python main.py setup")
            return False
    
    def run_setup(self, args):
        """Execute setup automation"""
        self.print_header("🔧 SETUP AUTOMATION")
        
        self.setup_manager = SetupManager(self.config)
        
        if args.check_only:
            passed, details = self.setup_manager.check_system_requirements()
            if passed:
                print("\n✅ All system requirements met")
            else:
                print("\n❌ Some requirements not met:")
                for check, result in details.items():
                    status = "✅" if result else "❌"
                    print(f"  {status} {check}")
            return
        
        success = self.setup_manager.run_full_setup()
        
        if success:
            print("\n" + "=" * 80)
            print("✅ SETUP COMPLETED SUCCESSFULLY!")
            print("=" * 80)
            print("\n📝 Next Steps:")
            print("  1. Source your environment: source ~/.bashrc")
            print("  2. Check environment: python main.py --check-env")
            print("  3. Run health check: python main.py health")
            print("  4. Start navigation: python main.py navigate --slam")
            print("=" * 80)
        else:
            print("\n❌ Setup encountered errors. Check logs for details.")
    
    def run_health_monitoring(self, args):
        """Execute health monitoring"""
        self.print_header("🏥 HEALTH MONITORING")
        
        self.health_monitor = HealthMonitor(self.config)
        
        if args.monitor:
            print("Starting continuous monitoring...")
            print("Press Ctrl+C to stop\n")
            
            self.health_monitor.start_monitoring()
            
            try:
                while True:
                    import time
                    time.sleep(10)
                    
                    # Print periodic status
                    metrics = self.health_monitor.current_metrics
                    print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
                          f"Battery: {metrics.battery_level:.1f}% | "
                          f"CPU: {metrics.system['cpu_usage']:.1f}% | "
                          f"Alerts: {len(metrics.alerts)}", end='')
            except KeyboardInterrupt:
                print("\n\nStopping monitoring...")
                self.health_monitor.stop_monitoring()
        else:
            # Single diagnostic run
            results = self.health_monitor.run_diagnostics()
            
            if args.save_report:
                self.health_monitor.save_report()
                print(f"\n💾 Report saved to logs/")
    
    def run_navigation(self, args):
        """Execute navigation automation"""
        self.print_header("🧭 NAVIGATION AUTOMATION")
        
        self.navigator = SmartNavigator(self.config)
        
        if args.slam:
            print("Starting SLAM mapping...")
            map_name = args.map_name or "my_map"
            self.navigator.start_slam_mapping(map_name)
            print("\n💡 Move the robot around to build the map")
            print(f"💡 When done, save map: python main.py navigate --save-map {map_name}")
            
        elif args.save_map:
            print(f"Saving map: {args.save_map}")
            if self.navigator.save_map(args.save_map):
                print("✅ Map saved successfully")
            else:
                print("❌ Failed to save map")
        
        elif args.load_map:
            print(f"Loading map: {args.load_map}")
            if self.navigator.load_map(Path(args.load_map)):
                self.navigator.start_navigation(Path(args.load_map))
                print("\n✅ Navigation started")
                print("💡 Set initial pose in RViz")
                print("💡 Then use: python main.py navigate --goto X Y THETA")
            else:
                print("❌ Failed to load map")
        
        elif args.goto:
            if len(args.goto) != 3:
                print("❌ Error: --goto requires 3 arguments (x y theta)")
                return
            
            x, y, theta = map(float, args.goto)
            self.navigator.navigate_to_pose(x, y, theta)
            print(f"✅ Goal sent: ({x}, {y}, {theta})")
        
        elif args.patrol:
            print("Starting patrol mode...")
            # Default patrol route
            route = [
                (1.0, 0.0, 0.0),
                (1.0, 1.0, 1.57),
                (0.0, 1.0, 3.14),
                (0.0, 0.0, 0.0)
            ]
            self.navigator.patrol_route(route)
        
        elif args.return_home:
            print("Returning to base...")
            self.navigator.return_to_base()
        
        else:
            print("Navigation options:")
            print("  --slam              Start SLAM mapping")
            print("  --save-map NAME     Save current map")
            print("  --load-map PATH     Load existing map")
            print("  --goto X Y THETA    Navigate to pose")
            print("  --patrol            Start patrol route")
            print("  --return-home       Return to base")
    
    def run_vision_processing(self, args):
        """Execute vision processing"""
        self.print_header("👁️  VISION PROCESSING")
        
        self.vision_processor = VisionProcessor(self.config)
        
        if not self.vision_processor.load_model():
            print("❌ Failed to load YOLOv8 model")
            print("💡 Install dependencies: pip install ultralytics opencv-python")
            return
        
        if args.webcam:
            duration = args.duration or 30
            print(f"Running webcam detection for {duration} seconds...")
            print("💡 Press 'q' to stop early")
            self.vision_processor.detect_webcam(duration)
        
        elif args.image:
            image_path = Path(args.image)
            if not image_path.exists():
                print(f"❌ Image not found: {image_path}")
                return
            
            detections = self.vision_processor.detect_image(image_path)
            print(f"\n✅ Detected {len(detections)} objects:")
            for obj in detections:
                print(f"  - {obj.class_name}: {obj.confidence:.2%}")
        
        elif args.follow:
            target = args.follow
            print(f"Following {target}...")
            self.vision_processor.start_detection()
            self.vision_processor.follow_object(target)
            print("💡 Press Ctrl+C to stop")
            
            try:
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopping...")
                self.vision_processor.stop_detection()
        
        elif args.report:
            print(self.vision_processor.generate_detection_report())
        
        else:
            print("Vision options:")
            print("  --webcam            Run detection on webcam")
            print("  --image PATH        Detect objects in image")
            print("  --follow CLASS      Follow detected object")
            print("  --duration SEC      Webcam duration (default: 30s)")
            print("  --report            Show detection report")
    
    def run_gesture_control(self, args):
        """Execute gesture control"""
        self.print_header("🖐️  GESTURE CONTROL")
        
        self.gesture_controller = GestureController(self.config)
        
        if args.calibrate:
            self.gesture_controller.calibrate_gestures()
            return
        
        print("Gesture Mappings:")
        print("  Open Palm → STOP")
        print("  Fist → MOVE FORWARD")
        print("  Peace Sign (2 fingers) → TURN LEFT")
        print("  Three Fingers → TURN RIGHT")
        print("  Four Fingers → MOVE BACKWARD")
        print("  Thumbs Up → INCREASE SPEED")
        print("  Thumbs Down → DECREASE SPEED")
        print("\nStarting gesture control...")
        print("💡 Press 'q' in the video window to stop\n")
        
        self.gesture_controller.start_gesture_control()
        
        try:
            import time
            while self.gesture_controller.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            self.gesture_controller.stop_gesture_control()
            
            if args.report:
                print("\n" + self.gesture_controller.generate_gesture_report())
    
    def interactive_menu(self):
        """Run interactive menu"""
        self.print_header("🎮 INTERACTIVE MENU")
        
        while True:
            print("\nTurtleBot3 Smart Automation")
            print("-" * 40)
            print("1. Setup & Installation")
            print("2. Health Monitoring")
            print("3. Navigation")
            print("4. Vision Processing")
            print("5. Gesture Control")
            print("6. System Status")
            print("0. Exit")
            print("-" * 40)
            
            try:
                choice = input("\nSelect option: ").strip()
                
                if choice == '0':
                    print("\nGoodbye! 👋")
                    break
                elif choice == '1':
                    print("\n1. Check requirements")
                    print("2. Full installation")
                    sub = input("Select: ").strip()
                    if sub == '1':
                        self.run_setup(argparse.Namespace(check_only=True))
                    elif sub == '2':
                        confirm = input("This will install ROS2 and TurtleBot3. Continue? (yes/no): ")
                        if confirm.lower() == 'yes':
                            self.run_setup(argparse.Namespace(check_only=False))
                
                elif choice == '2':
                    print("\n1. Single health check")
                    print("2. Continuous monitoring")
                    sub = input("Select: ").strip()
                    if sub == '1':
                        self.run_health_monitoring(argparse.Namespace(monitor=False, save_report=True))
                    elif sub == '2':
                        self.run_health_monitoring(argparse.Namespace(monitor=True, save_report=False))
                
                elif choice == '3':
                    print("\n1. Start SLAM")
                    print("2. Navigate to pose")
                    print("3. Patrol mode")
                    print("4. Return home")
                    sub = input("Select: ").strip()
                    # Implement sub-menus...
                    
                elif choice == '4':
                    print("\n1. Webcam detection")
                    print("2. Detect from image")
                    print("3. Follow object")
                    sub = input("Select: ").strip()
                    # Implement sub-menus...
                
                elif choice == '5':
                    self.run_gesture_control(argparse.Namespace(calibrate=False, report=True))
                
                elif choice == '6':
                    self.check_environment()
                
                else:
                    print("❌ Invalid option")
                    
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                self.logger.error(f"Menu error: {e}", exc_info=True)
    
    def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("Shutting down...")
        
        # Stop all running modules
        if self.health_monitor:
            self.health_monitor.stop_monitoring()
        if self.vision_processor:
            self.vision_processor.stop_detection()
        if self.gesture_controller:
            self.gesture_controller.stop_gesture_control()
        
        self.logger.info("Shutdown complete")


def create_parser():
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        description="TurtleBot3 Smart Automation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --interactive                    # Interactive menu
  python main.py setup                             # Full installation
  python main.py setup --check-only                # Check requirements only
  python main.py health                            # Run health diagnostics
  python main.py health --monitor                  # Continuous monitoring
  python main.py navigate --slam                   # Start SLAM mapping
  python main.py navigate --goto 1.0 1.0 0.0      # Navigate to pose
  python main.py vision --webcam                   # Webcam detection
  python main.py vision --follow person            # Follow person
  python main.py gesture                           # Gesture control

For more information, see README.md
        """
    )
    
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run interactive menu')
    parser.add_argument('--check-env', action='store_true',
                       help='Check system environment')
    parser.add_argument('--config', type=Path,
                       help='Configuration file path')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Setup and installation')
    setup_parser.add_argument('--check-only', action='store_true',
                             help='Only check requirements')
    
    # Health command
    health_parser = subparsers.add_parser('health', help='Health monitoring')
    health_parser.add_argument('--monitor', action='store_true',
                              help='Continuous monitoring')
    health_parser.add_argument('--save-report', action='store_true',
                              help='Save report to file')
    
    # Navigate command
    nav_parser = subparsers.add_parser('navigate', help='Navigation control')
    nav_parser.add_argument('--slam', action='store_true',
                           help='Start SLAM mapping')
    nav_parser.add_argument('--save-map', type=str,
                           help='Save map with name')
    nav_parser.add_argument('--load-map', type=str,
                           help='Load map from path')
    nav_parser.add_argument('--goto', nargs=3, metavar=('X', 'Y', 'THETA'),
                           help='Navigate to pose')
    nav_parser.add_argument('--patrol', action='store_true',
                           help='Start patrol mode')
    nav_parser.add_argument('--return-home', action='store_true',
                           help='Return to base')
    nav_parser.add_argument('--map-name', type=str, default='my_map',
                           help='Map name for SLAM')
    
    # Vision command
    vision_parser = subparsers.add_parser('vision', help='Vision processing')
    vision_parser.add_argument('--webcam', action='store_true',
                              help='Run detection on webcam')
    vision_parser.add_argument('--image', type=str,
                              help='Detect objects in image')
    vision_parser.add_argument('--follow', type=str,
                              help='Follow detected object class')
    vision_parser.add_argument('--duration', type=int,
                              help='Webcam duration in seconds')
    vision_parser.add_argument('--report', action='store_true',
                              help='Show detection report')
    
    # Gesture command
    gesture_parser = subparsers.add_parser('gesture', help='Gesture control')
    gesture_parser.add_argument('--calibrate', action='store_true',
                               help='Run calibration wizard')
    gesture_parser.add_argument('--report', action='store_true',
                               help='Show gesture report')
    
    return parser


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Create automation system
    system = TurtleBot3SmartAutomation(args.config)
    
    try:
        if args.interactive:
            system.interactive_menu()
        elif args.check_env:
            system.check_environment()
        elif args.command == 'setup':
            system.run_setup(args)
        elif args.command == 'health':
            system.run_health_monitoring(args)
        elif args.command == 'navigate':
            system.run_navigation(args)
        elif args.command == 'vision':
            system.run_vision_processing(args)
        elif args.command == 'gesture':
            system.run_gesture_control(args)
        else:
            parser.print_help()
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
    except Exception as e:
        system.logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    finally:
        system.shutdown()


if __name__ == "__main__":
    main()
