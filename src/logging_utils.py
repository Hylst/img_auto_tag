"""Logging utilities for the Image Auto-Tagger application.

This module provides centralized logging configuration and utilities
for structured logging throughout the application.
"""

import logging
import logging.handlers
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from enum import Enum

class LogLevel(Enum):
    """Enumeration of log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON.
        
        Args:
            record: The log record to format
            
        Returns:
            JSON-formatted log string
        """
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data
        
        # Add processing context if present
        for attr in ['file_path', 'api_name', 'operation', 'duration_ms']:
            if hasattr(record, attr):
                log_data[attr] = getattr(record, attr)
        
        return json.dumps(log_data, ensure_ascii=False)

class ImageTaggerLogger:
    """Centralized logger for the Image Auto-Tagger application."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the logger (only once due to singleton pattern)."""
        if not self._initialized:
            self._loggers = {}
            self._log_dir = None
            self._console_level = LogLevel.INFO
            self._file_level = LogLevel.DEBUG
            self._structured_logging = False
            self._initialized = True
    
    def configure(
        self,
        log_dir: Optional[str] = None,
        console_level: LogLevel = LogLevel.INFO,
        file_level: LogLevel = LogLevel.DEBUG,
        structured_logging: bool = False,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ) -> None:
        """Configure logging settings.
        
        Args:
            log_dir: Directory for log files (None to disable file logging)
            console_level: Minimum level for console output
            file_level: Minimum level for file output
            structured_logging: Whether to use JSON structured logging
            max_file_size: Maximum size of log files before rotation
            backup_count: Number of backup files to keep
        """
        self._log_dir = Path(log_dir) if log_dir else None
        self._console_level = console_level
        self._file_level = file_level
        self._structured_logging = structured_logging
        self._max_file_size = max_file_size
        self._backup_count = backup_count
        
        # Create log directory if specified
        if self._log_dir:
            self._log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        self._configure_root_logger()
    
    def _configure_root_logger(self) -> None:
        """Configure the root logger with handlers."""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)  # Set to lowest level, handlers will filter
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Add console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, self._console_level.value))
        
        if self._structured_logging:
            console_handler.setFormatter(StructuredFormatter())
        else:
            console_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            console_handler.setFormatter(logging.Formatter(console_format))
        
        root_logger.addHandler(console_handler)
        
        # Add file handler if log directory is specified
        if self._log_dir:
            log_file = self._log_dir / 'image_tagger.log'
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=self._max_file_size,
                backupCount=self._backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(getattr(logging, self._file_level.value))
            
            if self._structured_logging:
                file_handler.setFormatter(StructuredFormatter())
            else:
                file_format = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
                file_handler.setFormatter(logging.Formatter(file_format))
            
            root_logger.addHandler(file_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger instance for the specified name.
        
        Args:
            name: Logger name (typically module name)
            
        Returns:
            Logger instance
        """
        if name not in self._loggers:
            self._loggers[name] = logging.getLogger(name)
        return self._loggers[name]
    
    def log_api_call(
        self,
        logger: logging.Logger,
        api_name: str,
        operation: str,
        duration_ms: Optional[float] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log an API call with structured information.
        
        Args:
            logger: Logger instance to use
            api_name: Name of the API (e.g., 'vision', 'gemini')
            operation: Operation performed (e.g., 'annotate_image', 'generate_content')
            duration_ms: Duration of the call in milliseconds
            success: Whether the call was successful
            error_message: Error message if call failed
            extra_data: Additional data to include in log
        """
        level = logging.INFO if success else logging.ERROR
        status = "SUCCESS" if success else "FAILED"
        
        message = f"API call {status}: {api_name}.{operation}"
        if duration_ms is not None:
            message += f" ({duration_ms:.2f}ms)"
        if error_message:
            message += f" - {error_message}"
        
        # Create log record with extra attributes
        extra = {
            'api_name': api_name,
            'operation': operation,
            'success': success
        }
        
        if duration_ms is not None:
            extra['duration_ms'] = duration_ms
        if error_message:
            extra['error_message'] = error_message
        if extra_data:
            extra['extra_data'] = extra_data
        
        logger.log(level, message, extra=extra)
    
    def log_file_processing(
        self,
        logger: logging.Logger,
        file_path: str,
        operation: str,
        success: bool = True,
        duration_ms: Optional[float] = None,
        file_size: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> None:
        """Log file processing with structured information.
        
        Args:
            logger: Logger instance to use
            file_path: Path to the file being processed
            operation: Operation performed (e.g., 'analyze', 'rename', 'validate')
            success: Whether the operation was successful
            duration_ms: Duration of the operation in milliseconds
            file_size: Size of the file in bytes
            error_message: Error message if operation failed
        """
        level = logging.INFO if success else logging.ERROR
        status = "SUCCESS" if success else "FAILED"
        
        message = f"File processing {status}: {operation} - {Path(file_path).name}"
        if duration_ms is not None:
            message += f" ({duration_ms:.2f}ms)"
        if error_message:
            message += f" - {error_message}"
        
        # Create log record with extra attributes
        extra = {
            'file_path': file_path,
            'operation': operation,
            'success': success
        }
        
        if duration_ms is not None:
            extra['duration_ms'] = duration_ms
        if file_size is not None:
            extra['file_size'] = file_size
        if error_message:
            extra['error_message'] = error_message
        
        logger.log(level, message, extra=extra)
    
    def log_performance_metrics(
        self,
        logger: logging.Logger,
        metrics: Dict[str, Any]
    ) -> None:
        """Log performance metrics.
        
        Args:
            logger: Logger instance to use
            metrics: Dictionary of performance metrics
        """
        message = "Performance metrics"
        logger.info(message, extra={'performance_metrics': metrics})

# Global logger instance
_logger_instance = ImageTaggerLogger()

def configure_logging(
    log_dir: Optional[str] = None,
    console_level: LogLevel = LogLevel.INFO,
    file_level: LogLevel = LogLevel.DEBUG,
    structured_logging: bool = False,
    **kwargs
) -> None:
    """Configure application logging.
    
    Args:
        log_dir: Directory for log files
        console_level: Minimum level for console output
        file_level: Minimum level for file output
        structured_logging: Whether to use JSON structured logging
        **kwargs: Additional configuration options
    """
    _logger_instance.configure(
        log_dir=log_dir,
        console_level=console_level,
        file_level=file_level,
        structured_logging=structured_logging,
        **kwargs
    )

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return _logger_instance.get_logger(name)

def log_api_call(
    logger: logging.Logger,
    api_name: str,
    operation: str,
    **kwargs
) -> None:
    """Log an API call. See ImageTaggerLogger.log_api_call for details."""
    _logger_instance.log_api_call(logger, api_name, operation, **kwargs)

def log_file_processing(
    logger: logging.Logger,
    file_path: str,
    operation: str,
    **kwargs
) -> None:
    """Log file processing. See ImageTaggerLogger.log_file_processing for details."""
    _logger_instance.log_file_processing(logger, file_path, operation, **kwargs)

def log_performance_metrics(
    logger: logging.Logger,
    metrics: Dict[str, Any]
) -> None:
    """Log performance metrics. See ImageTaggerLogger.log_performance_metrics for details."""
    _logger_instance.log_performance_metrics(logger, metrics)