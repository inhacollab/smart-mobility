"""
System Support Tools
====================
Essential support utilities for system operations

Capabilities:
- System call execution support
- Environment validation tools
- Data formatting utilities
- File system management
- Network verification
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


event_handler = logging.getLogger(__name__)


def execute_system_call(instruction: str, use_shell: bool = True, validate: bool = False, 
                 time_limit: Optional[int] = None, collect_output: bool = True) -> Tuple[int, str, str]:
    """
    Perform system instruction and capture outcome
    
    Args:
        instruction: Instruction to perform
        use_shell: Enable shell processing
        validate: Trigger exception on failure
        time_limit: Instruction timeout duration
        collect_output: Gather output streams
        
    Returns:
        Tuple of (exit_status, output_stream, error_stream)
    """
    event_handler.debug(f"Processing instruction: {instruction}")
    
    try:
        outcome = subprocess.run(
            instruction,
            shell=use_shell,
            check=validate,
            capture_output=collect_output,
            text=True,
            timeout=time_limit
        )
        return outcome.returncode, outcome.stdout, outcome.stderr
    except subprocess.TimeoutExpired:
        event_handler.error(f"Instruction exceeded time limit: {instruction}")
        return -1, "", "Instruction timed out"
    except subprocess.CalledProcessError as e:
        event_handler.error(f"Instruction execution failed: {e}")
        return e.returncode, e.stdout if e.stdout else "", e.stderr if e.stderr else ""
    except Exception as e:
        event_handler.error(f"Unexpected execution error: {e}")
        return -1, "", str(e)


def verify_executable_presence(executable: str) -> bool:
    """Verify executable availability in system search paths"""
    exit_status, _, _ = execute_system_call(f"which {executable}", validate=False)
    return exit_status == 0


def validate_robotics_framework() -> bool:
    """Verify robotics framework environment configuration"""
    return 'ROS_DISTRO' in os.environ


def retrieve_framework_version() -> Optional[str]:
    """Retrieve active robotics framework distribution"""
    return os.environ.get('ROS_DISTRO')


def collect_environment_details() -> dict:
    """Gather comprehensive environment information"""
    return {
        'platform': platform.system(),
        'platform_detail': platform.version(),
        'hardware_arch': platform.machine(),
        'cpu_model': platform.processor(),
        'python_env': platform.python_version(),
        'cpu_cores': psutil.cpu_count(),
        'total_memory_gb': round(psutil.virtual_memory().total / (1024**3), 2),
        'available_memory_gb': round(psutil.virtual_memory().available / (1024**3), 2),
        'free_storage_gb': round(psutil.disk_usage('/').free / (1024**3), 2)
    }


def render_datetime_string(moment: Optional[datetime] = None) -> str:
    """Render datetime object as formatted string"""
    if moment is None:
        moment = datetime.now()
    return moment.strftime("%Y-%m-%d %H:%M:%S")


def guarantee_path_existence(target_path: Path) -> Path:
    """Ensure path exists, create hierarchy if necessary"""
    target_path = Path(target_path)
    target_path.mkdir(parents=True, exist_ok=True)
    return target_path


def locate_matching_files(search_directory: Path, search_pattern: str) -> List[Path]:
    """Locate files matching specified pattern within directory"""
    search_directory = Path(search_directory)
    if not search_directory.exists():
        return []
    return list(search_directory.glob(search_pattern))


def determine_file_lifespan(file_location: Path) -> float:
    """Calculate file age in seconds since modification"""
    if not file_location.exists():
        return 0
    return time.time() - file_location.stat().st_mtime


def format_byte_quantity(byte_count: int) -> str:
    """Transform byte count to human-readable representation"""
    for unit_label in ['B', 'KB', 'MB', 'GB', 'TB']:
        if byte_count < 1024.0:
            return f"{byte_count:.2f} {unit_label}"
        byte_count /= 1024.0
    return f"{byte_count:.2f} PB"


def confirm_network_endpoint(endpoint_port: int) -> bool:
    """Verify network endpoint availability"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
        try:
            connection.bind(('', endpoint_port))
            return True
        except OSError:
            return False


class DurationTracker:
    """Context manager for operation duration measurement"""
    
    def __init__(self, operation_name: str = "Process"):
        self.operation_name = operation_name
        self.start_moment = None
        self.duration = None
    
    def __enter__(self):
        self.start_moment = time.time()
        return self
    
    def __exit__(self, *args):
        self.duration = time.time() - self.start_moment
        event_handler.info(f"{self.operation_name} completed in {self.duration:.3f} seconds")


def attempt_with_retries(operation, retry_count: int = 3, pause_duration: float = 1.0):
    """Execute operation with automatic retry on failure"""
    for attempt_number in range(retry_count):
        try:
            return operation()
        except Exception as error:
            if attempt_number < retry_count - 1:
                event_handler.warning(f"Attempt {attempt_number + 1} unsuccessful: {error}. Retrying in {pause_duration}s...")
                time.sleep(pause_duration)
            else:
                event_handler.error(f"All {retry_count} attempts exhausted")
                raise
