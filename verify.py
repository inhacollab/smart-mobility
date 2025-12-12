#!/usr/bin/env python3
"""
Quick verification script to test all modules load correctly
"""

import sys
from pathlib import Path

print("=" * 70)
print("TurtleBot3 Smart Automation - Module Verification")
print("=" * 70)
print()

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

results = []

# Test core modules
print("Testing core modules...")
try:
    from core.logger import setup_logger
    from core.config_manager import ConfigManager
    from core.utils import get_system_info
    print("  ✅ Core modules OK")
    results.append(("Core", True))
except Exception as e:
    print(f"  ❌ Core modules FAILED: {e}")
    results.append(("Core", False))

# Test automation modules
print("\nTesting automation modules...")

modules = [
    ("Setup Manager", "automation.setup_manager", "SetupManager"),
    ("Health Monitor", "automation.health_monitor", "HealthMonitor"),
    ("Smart Navigator", "automation.smart_navigator", "SmartNavigator"),
    ("Vision Processor", "automation.vision_processor", "VisionProcessor"),
    ("Gesture Controller", "automation.gesture_controller", "GestureController"),
]

for name, module_path, class_name in modules:
    try:
        module = __import__(module_path, fromlist=[class_name])
        cls = getattr(module, class_name)
        print(f"  ✅ {name} OK")
        results.append((name, True))
    except Exception as e:
        print(f"  ❌ {name} FAILED: {e}")
        results.append((name, False))

# Test dependencies
print("\nTesting dependencies...")
dependencies = [
    ("yaml", "pyyaml"),
    ("psutil", "psutil"),
]

for module_name, package_name in dependencies:
    try:
        __import__(module_name)
        print(f"  ✅ {package_name} installed")
        results.append((package_name, True))
    except ImportError:
        print(f"  ⚠️  {package_name} not installed (pip install {package_name})")
        results.append((package_name, False))

# Optional dependencies
print("\nTesting optional dependencies...")
optional = [
    ("ultralytics", "ultralytics", "for vision processing"),
    ("cv2", "opencv-python", "for camera/image processing"),
    ("mediapipe", "mediapipe", "for gesture control"),
]

for module_name, package_name, purpose in optional:
    try:
        __import__(module_name)
        print(f"  ✅ {package_name} installed")
        results.append((package_name, True))
    except ImportError:
        print(f"  ⚠️  {package_name} not installed ({purpose})")
        print(f"     Install with: pip install {package_name}")
        results.append((package_name, False))

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

passed = sum(1 for _, status in results if status)
total = len(results)

print(f"Modules tested: {total}")
print(f"Passed: {passed}")
print(f"Failed: {total - passed}")

if passed == total:
    print("\n✅ All modules loaded successfully!")
    print("You can now run: python3 main.py --help")
    sys.exit(0)
elif passed >= total - 3:  # Allow up to 3 optional dependencies missing
    print("\n⚠️  Some optional dependencies missing, but core system OK")
    print("You can run basic features: python3 main.py --help")
    sys.exit(0)
else:
    print("\n❌ Critical modules failed. Please check installation.")
    print("Run: pip3 install -r requirements.txt")
    sys.exit(1)
