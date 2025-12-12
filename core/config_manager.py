"""
Configuration Handler
====================
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


class ConfigurationHandler:
    """Manages system configuration with validation"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.system_logger = logging.getLogger(__name__)
        self.configuration_file = config_path or Path("config/system_config.yaml")
        self.configuration_data: Dict[str, Any] = {}
        self.load_configuration()
    
    def load_configuration(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            if not self.configuration_file.exists():
                self.system_logger.warning(f"Configuration file not found: {self.configuration_file}")
                self.configuration_data = self._get_fallback_configuration()
                return self.configuration_data
            
            with open(self.configuration_file, 'r') as f:
                raw_config = yaml.safe_load(f)
            
            # Substitute environment variables
            self.configuration_data = self._replace_environment_variables(raw_config)
            self.system_logger.info(f"Configuration loaded from {self.configuration_file}")
            return self.configuration_data
            
        except Exception as e:
            self.system_logger.error(f"Failed to load configuration: {e}")
            self.configuration_data = self._get_fallback_configuration()
            return self.configuration_data
    
    def _replace_environment_variables(self, config: Any) -> Any:
        """Recursively substitute environment variables in configuration"""
        if isinstance(config, dict):
            return {k: self._replace_environment_variables(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._replace_environment_variables(item) for item in config]
        elif isinstance(config, str):
            # Replace ${VAR_NAME} with environment variable
            if config.startswith('${') and config.endswith('}'):
                var_name = config[2:-1]
                return os.environ.get(var_name, config)
            return config
        else:
            return config
    
    def _get_fallback_configuration(self) -> Dict[str, Any]:
        """Return fallback configuration"""
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
    
    def retrieve(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.configuration_data
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def update(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.configuration_data
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def persist_configuration(self, path: Optional[Path] = None):
        """Save configuration to YAML file"""
        save_path = path or self.configuration_file
        try:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'w') as f:
                yaml.dump(self.configuration_data, f, default_flow_style=False, sort_keys=False)
            self.system_logger.info(f"Configuration saved to {save_path}")
        except Exception as e:
            self.system_logger.error(f"Failed to save configuration: {e}")
    
    def verify_configuration(self) -> bool:
        """Validate configuration against schema"""
        required_sections = ['system', 'robot', 'setup', 'health_monitor', 'navigation', 'vision']
        
        for section in required_sections:
            if section not in self.configuration_data:
                self.system_logger.error(f"Missing required configuration section: {section}")
                return False
        
        self.system_logger.info("Configuration validation passed")
        return True
