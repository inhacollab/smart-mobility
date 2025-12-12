"""
Utility Functions
=================
Common utility functions used across the system

Features:
- Command execution helpers
- File system operations
- Time and date utilities
- System information
"""

import subprocess
import os
import platform
import psutil
import time
from pathlib import Path
from typing import Optional, Tuple, List
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


def run_command(command: str, shell: bool = True, check: bool = False, 
                timeout: Optional[int] = None, capture_output: bool = True) -> Tuple[int, str, str]:
    """
    Execute shell command and return result
    
    Args:
        command: Command to execute
        shell: Use shell execution
        check: Raise exception on error
        timeout: Command timeout in seconds
        capture_output: Capture stdout/stderr
        
    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    logger.debug(f"Executing command: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=shell,
            check=check,
            capture_output=capture_output,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out: {command}")
        return -1, "", "Command timed out"
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e}")
        return e.returncode, e.stdout if e.stdout else "", e.stderr if e.stderr else ""
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return -1, "", str(e)


def check_command_exists(command: str) -> bool:
    """Check if a command exists in system PATH"""
    returncode, _, _ = run_command(f"which {command}", check=False)
    return returncode == 0


def check_ros_environment() -> bool:
    """Check if ROS2 environment is sourced"""
    return 'ROS_DISTRO' in os.environ


def get_ros_distro() -> Optional[str]:
    """Get current ROS distribution"""
    return os.environ.get('ROS_DISTRO')


def get_system_info() -> dict:
    """Get system information"""
    return {
        'os': platform.system(),
        'os_version': platform.version(),
        'architecture': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
        'cpu_count': psutil.cpu_count(),
        'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
        'memory_available_gb': round(psutil.virtual_memory().available / (1024**3), 2),
        'disk_free_gb': round(psutil.disk_usage('/').free / (1024**3), 2)
    }


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Format datetime as string"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def ensure_directory(path: Path) -> Path:
    """Ensure directory exists, create if not"""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def find_files(directory: Path, pattern: str) -> List[Path]:
    """Find files matching pattern in directory"""
    directory = Path(directory)
    if not directory.exists():
        return []
    return list(directory.glob(pattern))


def get_file_age(file_path: Path) -> float:
    """Get file age in seconds"""
    if not file_path.exists():
        return 0
    return time.time() - file_path.stat().st_mtime


def human_readable_size(size_bytes: int) -> str:
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def check_port_available(port: int) -> bool:
    """Check if network port is available"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('', port))
            return True
        except OSError:
            return False


class Timer:
    """Simple context manager for timing operations"""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.elapsed = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        self.elapsed = time.time() - self.start_time
        logger.info(f"{self.name} took {self.elapsed:.3f} seconds")


def retry(func, max_attempts: int = 3, delay: float = 1.0):
    """Retry function execution on failure"""
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt < max_attempts - 1:
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                time.sleep(delay)
            else:
                logger.error(f"All {max_attempts} attempts failed")
                raise
