"""
Event Recording Framework
=========================
Advanced event recording with visual indicators and structured data storage

Capabilities:
- Visual-coded event levels
- Cyclic file management
- Structured data recording
- Performance indicator monitoring
"""

import logging
import logging.handlers
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
import sys


class ColorfulOutputFormatter(logging.Formatter):
    """Custom formatter with visual indicators for terminal display"""
    
    VISUAL_CODES = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    CODE_RESET = '\033[0m'
    
    def format(self, record):
        event_level = record.levelname
        if event_level in self.VISUAL_CODES:
            record.levelname = f"{self.VISUAL_CODES[event_level]}{event_level}{self.CODE_RESET}"
        return super().format(record)


class StructuredDataFormatter(logging.Formatter):
    """Structured data formatter for organized recording"""
    
    def format(self, record):
        event_data = {
            'recorded_at': datetime.utcnow().isoformat(),
            'severity': record.levelname,
            'component': record.module,
            'operation': record.funcName,
            'location': record.lineno,
            'details': record.getMessage(),
        }
        
        if hasattr(record, 'indicators'):
            event_data['indicators'] = record.indicators
            
        return json.dumps(event_data)


def initialize_event_recorder(name: str, storage_path: Optional[Path] = None, severity_level=logging.INFO):
    """
    Initialize event recorder with multiple output channels
    
    Args:
        name: Recorder identifier
        storage_path: Directory for event files
        severity_level: Event filtering level
        
    Returns:
        Configured recorder instance
    """
    recorder = logging.getLogger(name)
    recorder.setLevel(severity_level)
    recorder.propagate = False
    
    # Clear previous output channels
    recorder.handlers.clear()
    
    # Terminal channel with visual indicators
    terminal_channel = logging.StreamHandler(sys.stdout)
    terminal_channel.setLevel(severity_level)
    visual_formatter = ColorfulOutputFormatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    terminal_channel.setFormatter(visual_formatter)
    recorder.addHandler(terminal_channel)
    
    # File channel with rotation
    if storage_path:
        storage_path = Path(storage_path)
        storage_path.mkdir(parents=True, exist_ok=True)
        
        # Standard event file
        event_file = storage_path / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_channel = logging.handlers.RotatingFileHandler(
            event_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_channel.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-20s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_channel.setFormatter(file_formatter)
        recorder.addHandler(file_channel)
        
        # Structured data file for organized records
        structured_file = storage_path / f"{name}_{datetime.now().strftime('%Y%m%d')}.json"
        structured_channel = logging.handlers.RotatingFileHandler(
            structured_file,
            maxBytes=10*1024*1024,
            backupCount=5
        )
        structured_channel.setLevel(logging.INFO)
        structured_channel.setFormatter(StructuredDataFormatter())
        recorder.addHandler(structured_channel)
    
    return recorder


class PerformanceTracker:
    """Tracker for system performance indicators"""
    
    def __init__(self, recorder: logging.Logger):
        self.recorder = recorder
        self.indicators = {}
    
    def capture_indicator(self, indicator_name: str, measurement: float, measurement_unit: str = ""):
        """Capture a performance indicator"""
        self.indicators[indicator_name] = {'measurement': measurement, 'unit': measurement_unit, 'captured_at': datetime.utcnow().isoformat()}
        self.recorder.info(f"Indicator: {indicator_name} = {measurement} {measurement_unit}", extra={'indicators': self.indicators})
    
    def retrieve_indicators(self):
        """Retrieve all captured indicators"""
        return self.indicators
    
    def reset_indicators(self):
        """Reset all indicators"""
        self.indicators.clear()
