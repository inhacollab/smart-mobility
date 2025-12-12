"""
Enhanced Logging System
=======================
Provides colored console output and structured file logging

Features:
- Color-coded log levels
- Rotating file handlers
- JSON structured logging
- Performance metrics tracking
"""

import logging
import logging.handlers
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
import sys


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output for console"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
        }
        
        if hasattr(record, 'metrics'):
            log_data['metrics'] = record.metrics
            
        return json.dumps(log_data)


def setup_logger(name: str, log_dir: Optional[Path] = None, level=logging.INFO):
    """
    Setup logger with both console and file handlers
    
    Args:
        name: Logger name
        log_dir: Directory for log files
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = ColoredFormatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Regular log file
        log_file = log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-20s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # JSON log file for structured data
        json_log_file = log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.json"
        json_handler = logging.handlers.RotatingFileHandler(
            json_log_file,
            maxBytes=10*1024*1024,
            backupCount=5
        )
        json_handler.setLevel(logging.INFO)
        json_handler.setFormatter(JSONFormatter())
        logger.addHandler(json_handler)
    
    return logger


class MetricsLogger:
    """Logger for performance metrics"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.metrics = {}
    
    def record_metric(self, name: str, value: float, unit: str = ""):
        """Record a performance metric"""
        self.metrics[name] = {'value': value, 'unit': unit, 'timestamp': datetime.utcnow().isoformat()}
        self.logger.info(f"Metric: {name} = {value} {unit}", extra={'metrics': self.metrics})
    
    def get_metrics(self):
        """Get all recorded metrics"""
        return self.metrics
    
    def clear_metrics(self):
        """Clear all metrics"""
        self.metrics.clear()
