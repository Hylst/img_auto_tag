"""Configuration management module for the Image Auto-Tagger application.

This module provides centralized configuration management with support for
environment variables, validation, and default values.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class APIConfig:
    """Configuration for API settings."""
    default_api: str = "vision"
    retry_count: int = 3
    retry_delay: float = 2.0
    timeout: int = 60
    gemini_model: str = "gemini-1.5-pro-latest"
    gemini_temperature: float = 0.7
    vision_max_results: int = 50

@dataclass
class ProcessingConfig:
    """Configuration for image processing settings."""
    max_workers: int = 4
    supported_formats: list = field(default_factory=lambda: ['.jpg', '.jpeg', '.png', '.webp', '.bmp'])
    max_file_size_mb: int = 20
    backup_enabled: bool = False
    rename_files: bool = True

@dataclass
class OutputConfig:
    """Configuration for output settings."""
    default_language: str = "fr"
    output_format: str = "json"
    include_raw_data: bool = False
    pretty_print: bool = True
    timestamp_format: str = "%Y%m%d_%H%M%S"

@dataclass
class LoggingConfig:
    """Configuration for logging settings."""
    level: str = "INFO"
    format: str = "%(message)s"
    enable_rich_tracebacks: bool = True
    log_file: Optional[str] = None

@dataclass
class AppConfig:
    """Main application configuration."""
    api: APIConfig = field(default_factory=APIConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

class ConfigManager:
    """Manages application configuration with environment variable support."""
    
    def __init__(self, config_file: Optional[Path] = None):
        """Initialize the configuration manager.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.config_file = config_file
        self._config = AppConfig()
        self._load_config()
        self._apply_env_overrides()
        self._validate_config()
    
    def _load_config(self) -> None:
        """Load configuration from file if it exists."""
        if self.config_file and self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                self._update_config_from_dict(config_data)
                logger.info(f"Configuration loaded from {self.config_file}")
            except Exception as e:
                logger.warning(f"Failed to load config file {self.config_file}: {e}")
    
    def _update_config_from_dict(self, config_data: Dict[str, Any]) -> None:
        """Update configuration from dictionary data."""
        if 'api' in config_data:
            api_data = config_data['api']
            for key, value in api_data.items():
                if hasattr(self._config.api, key):
                    setattr(self._config.api, key, value)
        
        if 'processing' in config_data:
            proc_data = config_data['processing']
            for key, value in proc_data.items():
                if hasattr(self._config.processing, key):
                    setattr(self._config.processing, key, value)
        
        if 'output' in config_data:
            output_data = config_data['output']
            for key, value in output_data.items():
                if hasattr(self._config.output, key):
                    setattr(self._config.output, key, value)
        
        if 'logging' in config_data:
            log_data = config_data['logging']
            for key, value in log_data.items():
                if hasattr(self._config.logging, key):
                    setattr(self._config.logging, key, value)
    
    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides."""
        # API configuration
        if os.getenv('GEMINI_API_KEY'):
            logger.info("Gemini API key found in environment")
        
        if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            logger.info("Google credentials found in environment")
        
        # Override specific settings from environment
        env_mappings = {
            'IMG_TAGGER_API': ('api', 'default_api'),
            'IMG_TAGGER_WORKERS': ('processing', 'max_workers', int),
            'IMG_TAGGER_LANGUAGE': ('output', 'default_language'),
            'IMG_TAGGER_LOG_LEVEL': ('logging', 'level'),
            'IMG_TAGGER_RETRY_COUNT': ('api', 'retry_count', int),
            'IMG_TAGGER_TIMEOUT': ('api', 'timeout', int),
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                section = getattr(self._config, config_path[0])
                attr_name = config_path[1]
                converter = config_path[2] if len(config_path) > 2 else str
                try:
                    setattr(section, attr_name, converter(value))
                    logger.debug(f"Applied environment override: {env_var}={value}")
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid environment value for {env_var}: {value} ({e})")
    
    def _validate_config(self) -> None:
        """Validate configuration values."""
        # Validate API settings
        if self._config.api.default_api not in ['vision', 'gemini']:
            raise ValueError(f"Invalid default API: {self._config.api.default_api}")
        
        if self._config.api.retry_count < 1:
            raise ValueError("Retry count must be at least 1")
        
        if self._config.api.timeout < 1:
            raise ValueError("Timeout must be at least 1 second")
        
        # Validate processing settings
        if self._config.processing.max_workers < 1:
            raise ValueError("Max workers must be at least 1")
        
        if self._config.processing.max_file_size_mb < 1:
            raise ValueError("Max file size must be at least 1 MB")
        
        # Validate output settings
        if self._config.output.default_language not in ['fr', 'en']:
            raise ValueError(f"Unsupported language: {self._config.output.default_language}")
        
        logger.debug("Configuration validation passed")
    
    def get_config(self) -> AppConfig:
        """Get the current configuration."""
        return self._config
    
    def save_config(self, output_file: Path) -> None:
        """Save current configuration to file."""
        config_dict = {
            'api': {
                'default_api': self._config.api.default_api,
                'retry_count': self._config.api.retry_count,
                'retry_delay': self._config.api.retry_delay,
                'timeout': self._config.api.timeout,
                'gemini_model': self._config.api.gemini_model,
                'gemini_temperature': self._config.api.gemini_temperature,
                'vision_max_results': self._config.api.vision_max_results,
            },
            'processing': {
                'max_workers': self._config.processing.max_workers,
                'supported_formats': self._config.processing.supported_formats,
                'max_file_size_mb': self._config.processing.max_file_size_mb,
                'backup_enabled': self._config.processing.backup_enabled,
                'rename_files': self._config.processing.rename_files,
            },
            'output': {
                'default_language': self._config.output.default_language,
                'output_format': self._config.output.output_format,
                'include_raw_data': self._config.output.include_raw_data,
                'pretty_print': self._config.output.pretty_print,
                'timestamp_format': self._config.output.timestamp_format,
            },
            'logging': {
                'level': self._config.logging.level,
                'format': self._config.logging.format,
                'enable_rich_tracebacks': self._config.logging.enable_rich_tracebacks,
                'log_file': self._config.logging.log_file,
            }
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            logger.info(f"Configuration saved to {output_file}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise

def get_default_config_manager() -> ConfigManager:
    """Get a default configuration manager instance."""
    config_file = Path("config/app_config.json")
    return ConfigManager(config_file if config_file.exists() else None)