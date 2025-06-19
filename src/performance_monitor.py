"""Performance monitoring utilities for the Image Auto-Tagger application.

This module provides tools for tracking processing times, API usage,
and system performance metrics.
"""

import time
import psutil
import threading
from collections import defaultdict, deque
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path

@dataclass
class APICallMetrics:
    """Metrics for API calls."""
    api_name: str
    operation: str
    duration_ms: float
    success: bool
    timestamp: datetime
    error_type: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None

@dataclass
class ProcessingMetrics:
    """Metrics for file processing."""
    file_path: str
    file_size: int
    processing_duration_ms: float
    api_calls: List[APICallMetrics] = field(default_factory=list)
    success: bool = True
    error_type: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class SystemMetrics:
    """System resource metrics."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_usage_percent: float
    active_threads: int

class PerformanceMonitor:
    """Monitor and track application performance metrics."""
    
    def __init__(self, max_history: int = 1000):
        """Initialize the performance monitor.
        
        Args:
            max_history: Maximum number of metrics to keep in memory
        """
        self._max_history = max_history
        self._api_metrics: deque = deque(maxlen=max_history)
        self._processing_metrics: deque = deque(maxlen=max_history)
        self._system_metrics: deque = deque(maxlen=max_history)
        
        # Aggregated statistics
        self._api_stats = defaultdict(lambda: {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'total_duration_ms': 0.0,
            'min_duration_ms': float('inf'),
            'max_duration_ms': 0.0,
            'recent_errors': deque(maxlen=10)
        })
        
        self._processing_stats = {
            'total_files': 0,
            'successful_files': 0,
            'failed_files': 0,
            'total_size_mb': 0.0,
            'total_duration_ms': 0.0,
            'files_per_minute': 0.0,
            'mb_per_minute': 0.0
        }
        
        # Thread safety
        self._lock = threading.Lock()
        
        # System monitoring
        self._system_monitor_active = False
        self._system_monitor_thread = None
        self._system_monitor_interval = 30  # seconds
    
    @contextmanager
    def time_api_call(self, api_name: str, operation: str, file_path: Optional[str] = None):
        """Context manager to time API calls.
        
        Args:
            api_name: Name of the API
            operation: Operation being performed
            file_path: Optional file path being processed
            
        Yields:
            Dictionary to store additional metrics
        """
        start_time = time.perf_counter()
        metrics_data = {}
        success = True
        error_type = None
        
        try:
            yield metrics_data
        except Exception as e:
            success = False
            error_type = type(e).__name__
            raise
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            file_size = None
            if file_path and Path(file_path).exists():
                file_size = Path(file_path).stat().st_size
            
            metric = APICallMetrics(
                api_name=api_name,
                operation=operation,
                duration_ms=duration_ms,
                success=success,
                timestamp=datetime.now(),
                error_type=error_type,
                file_path=file_path,
                file_size=file_size
            )
            
            self.record_api_call(metric)
    
    @contextmanager
    def time_file_processing(self, file_path: str):
        """Context manager to time file processing.
        
        Args:
            file_path: Path to the file being processed
            
        Yields:
            ProcessingMetrics object to collect API calls
        """
        start_time = time.perf_counter()
        file_size = Path(file_path).stat().st_size if Path(file_path).exists() else 0
        
        processing_metric = ProcessingMetrics(
            file_path=file_path,
            file_size=file_size,
            processing_duration_ms=0.0
        )
        
        success = True
        error_type = None
        
        try:
            yield processing_metric
        except Exception as e:
            success = False
            error_type = type(e).__name__
            raise
        finally:
            processing_metric.processing_duration_ms = (time.perf_counter() - start_time) * 1000
            processing_metric.success = success
            processing_metric.error_type = error_type
            
            self.record_file_processing(processing_metric)
    
    def record_api_call(self, metric: APICallMetrics) -> None:
        """Record an API call metric.
        
        Args:
            metric: API call metrics to record
        """
        with self._lock:
            self._api_metrics.append(metric)
            
            # Update aggregated statistics
            key = f"{metric.api_name}.{metric.operation}"
            stats = self._api_stats[key]
            
            stats['total_calls'] += 1
            if metric.success:
                stats['successful_calls'] += 1
            else:
                stats['failed_calls'] += 1
                if metric.error_type:
                    stats['recent_errors'].append({
                        'timestamp': metric.timestamp,
                        'error_type': metric.error_type,
                        'file_path': metric.file_path
                    })
            
            stats['total_duration_ms'] += metric.duration_ms
            stats['min_duration_ms'] = min(stats['min_duration_ms'], metric.duration_ms)
            stats['max_duration_ms'] = max(stats['max_duration_ms'], metric.duration_ms)
    
    def record_file_processing(self, metric: ProcessingMetrics) -> None:
        """Record a file processing metric.
        
        Args:
            metric: File processing metrics to record
        """
        with self._lock:
            self._processing_metrics.append(metric)
            
            # Update aggregated statistics
            self._processing_stats['total_files'] += 1
            if metric.success:
                self._processing_stats['successful_files'] += 1
            else:
                self._processing_stats['failed_files'] += 1
            
            self._processing_stats['total_size_mb'] += metric.file_size / (1024 * 1024)
            self._processing_stats['total_duration_ms'] += metric.processing_duration_ms
            
            # Calculate rates (files and MB per minute)
            if len(self._processing_metrics) > 1:
                recent_metrics = list(self._processing_metrics)[-min(10, len(self._processing_metrics)):]
                if len(recent_metrics) > 1:
                    time_span = (recent_metrics[-1].timestamp - recent_metrics[0].timestamp).total_seconds()
                    if time_span > 0:
                        files_per_second = len(recent_metrics) / time_span
                        self._processing_stats['files_per_minute'] = files_per_second * 60
                        
                        total_mb = sum(m.file_size for m in recent_metrics) / (1024 * 1024)
                        mb_per_second = total_mb / time_span
                        self._processing_stats['mb_per_minute'] = mb_per_second * 60
    
    def start_system_monitoring(self, interval: int = 30) -> None:
        """Start system resource monitoring.
        
        Args:
            interval: Monitoring interval in seconds
        """
        if self._system_monitor_active:
            return
        
        self._system_monitor_interval = interval
        self._system_monitor_active = True
        self._system_monitor_thread = threading.Thread(
            target=self._system_monitor_loop,
            daemon=True
        )
        self._system_monitor_thread.start()
    
    def stop_system_monitoring(self) -> None:
        """Stop system resource monitoring."""
        self._system_monitor_active = False
        if self._system_monitor_thread:
            self._system_monitor_thread.join(timeout=5)
    
    def _system_monitor_loop(self) -> None:
        """System monitoring loop (runs in separate thread)."""
        while self._system_monitor_active:
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                metric = SystemMetrics(
                    timestamp=datetime.now(),
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    memory_used_mb=memory.used / (1024 * 1024),
                    disk_usage_percent=disk.percent,
                    active_threads=threading.active_count()
                )
                
                with self._lock:
                    self._system_metrics.append(metric)
                
                # Wait for next interval
                time.sleep(self._system_monitor_interval)
                
            except Exception:
                # Silently continue if system monitoring fails
                time.sleep(self._system_monitor_interval)
    
    def get_api_statistics(self, api_name: Optional[str] = None) -> Dict[str, Any]:
        """Get API call statistics.
        
        Args:
            api_name: Optional API name to filter by
            
        Returns:
            Dictionary of API statistics
        """
        with self._lock:
            if api_name:
                # Filter by API name
                filtered_stats = {}
                for key, stats in self._api_stats.items():
                    if key.startswith(f"{api_name}."):
                        filtered_stats[key] = stats.copy()
                        # Calculate average duration
                        if stats['total_calls'] > 0:
                            filtered_stats[key]['avg_duration_ms'] = (
                                stats['total_duration_ms'] / stats['total_calls']
                            )
                return filtered_stats
            else:
                # Return all statistics
                result = {}
                for key, stats in self._api_stats.items():
                    result[key] = stats.copy()
                    # Calculate average duration
                    if stats['total_calls'] > 0:
                        result[key]['avg_duration_ms'] = (
                            stats['total_duration_ms'] / stats['total_calls']
                        )
                return result
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get file processing statistics.
        
        Returns:
            Dictionary of processing statistics
        """
        with self._lock:
            stats = self._processing_stats.copy()
            
            # Calculate averages
            if stats['total_files'] > 0:
                stats['avg_duration_ms'] = stats['total_duration_ms'] / stats['total_files']
                stats['avg_file_size_mb'] = stats['total_size_mb'] / stats['total_files']
                stats['success_rate'] = stats['successful_files'] / stats['total_files']
            else:
                stats['avg_duration_ms'] = 0.0
                stats['avg_file_size_mb'] = 0.0
                stats['success_rate'] = 0.0
            
            return stats
    
    def get_system_statistics(self, last_n_minutes: int = 10) -> Dict[str, Any]:
        """Get system resource statistics.
        
        Args:
            last_n_minutes: Number of minutes to include in statistics
            
        Returns:
            Dictionary of system statistics
        """
        with self._lock:
            if not self._system_metrics:
                return {}
            
            # Filter recent metrics
            cutoff_time = datetime.now() - timedelta(minutes=last_n_minutes)
            recent_metrics = [
                m for m in self._system_metrics 
                if m.timestamp >= cutoff_time
            ]
            
            if not recent_metrics:
                return {}
            
            # Calculate statistics
            cpu_values = [m.cpu_percent for m in recent_metrics]
            memory_values = [m.memory_percent for m in recent_metrics]
            memory_used_values = [m.memory_used_mb for m in recent_metrics]
            
            return {
                'sample_count': len(recent_metrics),
                'time_span_minutes': last_n_minutes,
                'cpu': {
                    'avg': sum(cpu_values) / len(cpu_values),
                    'min': min(cpu_values),
                    'max': max(cpu_values)
                },
                'memory': {
                    'avg_percent': sum(memory_values) / len(memory_values),
                    'min_percent': min(memory_values),
                    'max_percent': max(memory_values),
                    'avg_used_mb': sum(memory_used_values) / len(memory_used_values),
                    'min_used_mb': min(memory_used_values),
                    'max_used_mb': max(memory_used_values)
                },
                'threads': {
                    'current': threading.active_count(),
                    'avg': sum(m.active_threads for m in recent_metrics) / len(recent_metrics)
                }
            }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a comprehensive performance summary.
        
        Returns:
            Dictionary containing all performance metrics
        """
        return {
            'api_statistics': self.get_api_statistics(),
            'processing_statistics': self.get_processing_statistics(),
            'system_statistics': self.get_system_statistics(),
            'monitoring_info': {
                'api_metrics_count': len(self._api_metrics),
                'processing_metrics_count': len(self._processing_metrics),
                'system_metrics_count': len(self._system_metrics),
                'system_monitoring_active': self._system_monitor_active
            }
        }
    
    def reset_statistics(self) -> None:
        """Reset all collected statistics."""
        with self._lock:
            self._api_metrics.clear()
            self._processing_metrics.clear()
            self._system_metrics.clear()
            self._api_stats.clear()
            self._processing_stats = {
                'total_files': 0,
                'successful_files': 0,
                'failed_files': 0,
                'total_size_mb': 0.0,
                'total_duration_ms': 0.0,
                'files_per_minute': 0.0,
                'mb_per_minute': 0.0
            }

# Global performance monitor instance
_performance_monitor = PerformanceMonitor()

def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance.
    
    Returns:
        PerformanceMonitor instance
    """
    return _performance_monitor

def time_api_call(api_name: str, operation: str, file_path: Optional[str] = None):
    """Context manager to time API calls using the global monitor.
    
    Args:
        api_name: Name of the API
        operation: Operation being performed
        file_path: Optional file path being processed
    """
    return _performance_monitor.time_api_call(api_name, operation, file_path)

def time_file_processing(file_path: str):
    """Context manager to time file processing using the global monitor.
    
    Args:
        file_path: Path to the file being processed
    """
    return _performance_monitor.time_file_processing(file_path)