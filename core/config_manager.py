"""
Configuration Manager
=====================
Handles YAML configuration loading, validation, and environment variables

Features:
- YAML configuration loading
- Environment variable substitution
- Schema validation
- Configuration hot-reload
"""

import yaml
import os
from pathlib import Path
from typing import Any, Dict, Optional
import logging


class ConfigManager:
    """Manages system configuration with validation"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or Path("config/system_config.yaml")
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            if not self.config_path.exists():
                self.logger.warning(f"Config file not found: {self.config_path}")
                self.config = self._get_default_config()
                return self.config
            
            with open(self.config_path, 'r') as f:
                raw_config = yaml.safe_load(f)
            
            # Substitute environment variables
            self.config = self._substitute_env_vars(raw_config)
            self.logger.info(f"Configuration loaded from {self.config_path}")
            return self.config
            
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            self.config = self._get_default_config()
            return self.config
    
    def _substitute_env_vars(self, config: Any) -> Any:
        """Recursively substitute environment variables in config"""
        if isinstance(config, dict):
            return {k: self._substitute_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._substitute_env_vars(item) for item in config]
        elif isinstance(config, str):
            # Replace ${VAR_NAME} with environment variable
            if config.startswith('${') and config.endswith('}'):
                var_name = config[2:-1]
                return os.environ.get(var_name, config)
            return config
        else:
            return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            'system': {
                'name': 'TurtleBot3 Smart Automation',
                'version': '1.0.0',
                'ros_distro': 'humble',
                'log_level': 'INFO'
            },
            'robot': {
                'model': 'burger',
                'namespace': 'tb3',
                'use_sim': False
            },
            'setup': {
                'workspace_path': '~/tb3_ws',
                'auto_install': True,
                'verify_installation': True
            },
            'health_monitor': {
                'check_interval': 5.0,
                'battery_low_threshold': 20.0,
                'battery_critical_threshold': 10.0,
                'enable_alerts': True,
                'save_history': True
            },
            'navigation': {
                'planner': 'NavFn',
                'controller': 'DWB',
                'max_speed': 0.22,
                'min_speed': 0.0,
                'use_behavior_tree': True
            },
            'vision': {
                'model': 'yolov8n.pt',
                'confidence_threshold': 0.5,
                'enable_tracking': True,
                'publish_rate': 10.0
            },
            'gesture': {
                'camera_id': 0,
                'min_detection_confidence': 0.7,
                'enable_feedback': True
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_config(self, path: Optional[Path] = None):
        """Save configuration to YAML file"""
        save_path = path or self.config_path
        try:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            self.logger.info(f"Configuration saved to {save_path}")
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
    
    def validate_config(self) -> bool:
        """Validate configuration against schema"""
        required_sections = ['system', 'robot', 'setup', 'health_monitor', 'navigation', 'vision']
        
        for section in required_sections:
            if section not in self.config:
                self.logger.error(f"Missing required config section: {section}")
                return False
        
        self.logger.info("Configuration validation passed")
        return True
