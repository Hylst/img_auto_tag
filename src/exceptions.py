"""Custom exception classes for the Image Auto-Tagger application.

This module defines specific exception types to improve error handling
and debugging throughout the application.
"""

class ImageTaggerError(Exception):
    """Base exception class for all Image Tagger errors."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        """Initialize the exception.
        
        Args:
            message: Human-readable error message
            error_code: Optional error code for programmatic handling
            details: Optional dictionary with additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
    
    def to_dict(self) -> dict:
        """Convert exception to dictionary for JSON serialization."""
        return {
            'error_type': self.__class__.__name__,
            'error_code': self.error_code,
            'message': self.message,
            'details': self.details
        }

class ConfigurationError(ImageTaggerError):
    """Raised when there's an issue with application configuration."""
    pass

class CredentialsError(ImageTaggerError):
    """Raised when there's an issue with API credentials."""
    pass

class APIError(ImageTaggerError):
    """Base class for API-related errors."""
    
    def __init__(self, message: str, api_name: str, status_code: int = None, **kwargs):
        """Initialize API error.
        
        Args:
            message: Error message
            api_name: Name of the API that failed (e.g., 'vision', 'gemini')
            status_code: HTTP status code if applicable
            **kwargs: Additional arguments passed to base class
        """
        super().__init__(message, **kwargs)
        self.api_name = api_name
        self.status_code = status_code
        if not self.details:
            self.details = {}
        self.details.update({
            'api_name': api_name,
            'status_code': status_code
        })

class VisionAPIError(APIError):
    """Raised when Google Vision API encounters an error."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, api_name='vision', **kwargs)

class GeminiAPIError(APIError):
    """Raised when Gemini API encounters an error."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, api_name='gemini', **kwargs)

class RateLimitError(APIError):
    """Raised when API rate limits are exceeded."""
    
    def __init__(self, message: str, api_name: str, retry_after: int = None, **kwargs):
        """Initialize rate limit error.
        
        Args:
            message: Error message
            api_name: Name of the API
            retry_after: Seconds to wait before retrying
            **kwargs: Additional arguments
        """
        super().__init__(message, api_name, **kwargs)
        self.retry_after = retry_after
        self.details['retry_after'] = retry_after

class QuotaExceededError(APIError):
    """Raised when API quota is exceeded."""
    pass

class AuthenticationError(APIError):
    """Raised when API authentication fails."""
    pass

class ValidationError(ImageTaggerError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field_name: str = None, field_value = None, **kwargs):
        """Initialize validation error.
        
        Args:
            message: Error message
            field_name: Name of the field that failed validation
            field_value: Value that failed validation
            **kwargs: Additional arguments
        """
        super().__init__(message, **kwargs)
        self.field_name = field_name
        self.field_value = field_value
        if not self.details:
            self.details = {}
        self.details.update({
            'field_name': field_name,
            'field_value': str(field_value) if field_value is not None else None
        })

class FileProcessingError(ImageTaggerError):
    """Raised when there's an error processing a file."""
    
    def __init__(self, message: str, file_path: str = None, **kwargs):
        """Initialize file processing error.
        
        Args:
            message: Error message
            file_path: Path to the file that caused the error
            **kwargs: Additional arguments
        """
        super().__init__(message, **kwargs)
        self.file_path = file_path
        if not self.details:
            self.details = {}
        self.details['file_path'] = file_path

class UnsupportedFormatError(FileProcessingError):
    """Raised when an unsupported file format is encountered."""
    pass

class FileSizeError(FileProcessingError):
    """Raised when a file is too large to process."""
    
    def __init__(self, message: str, file_path: str = None, file_size: int = None, max_size: int = None, **kwargs):
        """Initialize file size error.
        
        Args:
            message: Error message
            file_path: Path to the file
            file_size: Actual file size in bytes
            max_size: Maximum allowed size in bytes
            **kwargs: Additional arguments
        """
        super().__init__(message, file_path, **kwargs)
        self.file_size = file_size
        self.max_size = max_size
        self.details.update({
            'file_size': file_size,
            'max_size': max_size
        })

class JSONParsingError(ImageTaggerError):
    """Raised when JSON parsing fails."""
    
    def __init__(self, message: str, raw_content: str = None, **kwargs):
        """Initialize JSON parsing error.
        
        Args:
            message: Error message
            raw_content: The raw content that failed to parse
            **kwargs: Additional arguments
        """
        super().__init__(message, **kwargs)
        self.raw_content = raw_content
        if not self.details:
            self.details = {}
        # Only include first 500 chars of raw content to avoid huge error messages
        self.details['raw_content_preview'] = raw_content[:500] if raw_content else None

class ProcessingTimeoutError(ImageTaggerError):
    """Raised when processing times out."""
    
    def __init__(self, message: str, timeout_seconds: int = None, **kwargs):
        """Initialize timeout error.
        
        Args:
            message: Error message
            timeout_seconds: The timeout value that was exceeded
            **kwargs: Additional arguments
        """
        super().__init__(message, **kwargs)
        self.timeout_seconds = timeout_seconds
        if not self.details:
            self.details = {}
        self.details['timeout_seconds'] = timeout_seconds

class CircuitBreakerError(ImageTaggerError):
    """Raised when circuit breaker is open due to repeated failures."""
    
    def __init__(self, message: str, failure_count: int = None, **kwargs):
        """Initialize circuit breaker error.
        
        Args:
            message: Error message
            failure_count: Number of consecutive failures
            **kwargs: Additional arguments
        """
        super().__init__(message, **kwargs)
        self.failure_count = failure_count
        if not self.details:
            self.details = {}
        self.details['failure_count'] = failure_count