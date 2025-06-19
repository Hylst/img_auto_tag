"""Input validation utilities for the Image Auto-Tagger application.

This module provides comprehensive validation functions for user inputs,
file paths, API responses, and configuration data.
"""

import re
import json
import mimetypes
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
from urllib.parse import urlparse

from .exceptions import ValidationError, UnsupportedFormatError, FileSizeError

# Constants
SUPPORTED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp'}
SUPPORTED_MIME_TYPES = {
    'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 
    'image/tiff', 'image/webp'
}
MAX_FILE_SIZE_MB = 20  # Maximum file size in MB
MAX_FILENAME_LENGTH = 255
MAX_PATH_LENGTH = 4096

# Regex patterns
FILENAME_PATTERN = re.compile(r'^[^<>:"/\\|?*\x00-\x1f]+$')
SAFE_FILENAME_PATTERN = re.compile(r'^[a-zA-Z0-9._-]+$')
LANGUAGE_CODE_PATTERN = re.compile(r'^[a-z]{2}(-[A-Z]{2})?$')
API_NAME_PATTERN = re.compile(r'^[a-z][a-z0-9_]*$')

class FileValidator:
    """Validator for file-related operations."""
    
    @staticmethod
    def validate_image_file(file_path: Union[str, Path]) -> Path:
        """Validate that a file is a supported image format.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Validated Path object
            
        Raises:
            ValidationError: If file path is invalid
            UnsupportedFormatError: If file format is not supported
            FileSizeError: If file is too large
        """
        # Convert to Path object
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            raise ValidationError(
                f"File does not exist: {file_path}",
                field_name="file_path",
                field_value=str(file_path)
            )
        
        # Check if it's a file (not directory)
        if not path.is_file():
            raise ValidationError(
                f"Path is not a file: {file_path}",
                field_name="file_path",
                field_value=str(file_path)
            )
        
        # Check file extension
        extension = path.suffix.lower()
        if extension not in SUPPORTED_IMAGE_EXTENSIONS:
            raise UnsupportedFormatError(
                f"Unsupported image format: {extension}. Supported formats: {', '.join(SUPPORTED_IMAGE_EXTENSIONS)}",
                file_path=str(file_path)
            )
        
        # Check MIME type
        mime_type, _ = mimetypes.guess_type(str(path))
        if mime_type and mime_type not in SUPPORTED_MIME_TYPES:
            raise UnsupportedFormatError(
                f"Unsupported MIME type: {mime_type}",
                file_path=str(file_path)
            )
        
        # Check file size
        file_size = path.stat().st_size
        max_size_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
        if file_size > max_size_bytes:
            raise FileSizeError(
                f"File too large: {file_size / (1024*1024):.2f}MB. Maximum allowed: {MAX_FILE_SIZE_MB}MB",
                file_path=str(file_path),
                file_size=file_size,
                max_size=max_size_bytes
            )
        
        return path
    
    @staticmethod
    def validate_directory(dir_path: Union[str, Path]) -> Path:
        """Validate that a directory exists and is accessible.
        
        Args:
            dir_path: Path to the directory
            
        Returns:
            Validated Path object
            
        Raises:
            ValidationError: If directory is invalid
        """
        path = Path(dir_path)
        
        if not path.exists():
            raise ValidationError(
                f"Directory does not exist: {dir_path}",
                field_name="directory_path",
                field_value=str(dir_path)
            )
        
        if not path.is_dir():
            raise ValidationError(
                f"Path is not a directory: {dir_path}",
                field_name="directory_path",
                field_value=str(dir_path)
            )
        
        # Check if directory is readable
        try:
            list(path.iterdir())
        except PermissionError:
            raise ValidationError(
                f"Directory is not readable: {dir_path}",
                field_name="directory_path",
                field_value=str(dir_path)
            )
        
        return path
    
    @staticmethod
    def validate_output_path(output_path: Union[str, Path]) -> Path:
        """Validate an output file path.
        
        Args:
            output_path: Path for output file
            
        Returns:
            Validated Path object
            
        Raises:
            ValidationError: If output path is invalid
        """
        path = Path(output_path)
        
        # Check path length
        if len(str(path)) > MAX_PATH_LENGTH:
            raise ValidationError(
                f"Path too long: {len(str(path))} characters. Maximum: {MAX_PATH_LENGTH}",
                field_name="output_path",
                field_value=str(path)
            )
        
        # Check filename length
        if len(path.name) > MAX_FILENAME_LENGTH:
            raise ValidationError(
                f"Filename too long: {len(path.name)} characters. Maximum: {MAX_FILENAME_LENGTH}",
                field_name="filename",
                field_value=path.name
            )
        
        # Check if parent directory exists or can be created
        parent_dir = path.parent
        if not parent_dir.exists():
            try:
                parent_dir.mkdir(parents=True, exist_ok=True)
            except (PermissionError, OSError) as e:
                raise ValidationError(
                    f"Cannot create output directory: {parent_dir}. Error: {e}",
                    field_name="output_directory",
                    field_value=str(parent_dir)
                )
        
        # Check if we can write to the directory
        if not parent_dir.is_dir():
            raise ValidationError(
                f"Output parent is not a directory: {parent_dir}",
                field_name="output_directory",
                field_value=str(parent_dir)
            )
        
        return path
    
    @staticmethod
    def validate_filename(filename: str) -> str:
        """Validate a filename for safety.
        
        Args:
            filename: Filename to validate
            
        Returns:
            Validated filename
            
        Raises:
            ValidationError: If filename is invalid
        """
        if not filename:
            raise ValidationError(
                "Filename cannot be empty",
                field_name="filename",
                field_value=filename
            )
        
        if len(filename) > MAX_FILENAME_LENGTH:
            raise ValidationError(
                f"Filename too long: {len(filename)} characters. Maximum: {MAX_FILENAME_LENGTH}",
                field_name="filename",
                field_value=filename
            )
        
        # Check for invalid characters
        if not FILENAME_PATTERN.match(filename):
            raise ValidationError(
                f"Filename contains invalid characters: {filename}",
                field_name="filename",
                field_value=filename
            )
        
        # Check for reserved names (Windows)
        reserved_names = {
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        }
        
        name_without_ext = Path(filename).stem.upper()
        if name_without_ext in reserved_names:
            raise ValidationError(
                f"Filename uses reserved name: {filename}",
                field_name="filename",
                field_value=filename
            )
        
        return filename
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize a filename by removing/replacing invalid characters.
        
        Args:
            filename: Filename to sanitize
            
        Returns:
            Sanitized filename
        """
        if not filename:
            return "unnamed_file"
        
        # Remove invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', filename)
        
        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip('. ')
        
        # Ensure it's not empty after sanitization
        if not sanitized:
            sanitized = "unnamed_file"
        
        # Truncate if too long
        if len(sanitized) > MAX_FILENAME_LENGTH:
            name, ext = Path(sanitized).stem, Path(sanitized).suffix
            max_name_length = MAX_FILENAME_LENGTH - len(ext)
            sanitized = name[:max_name_length] + ext
        
        return sanitized

class ConfigValidator:
    """Validator for configuration data."""
    
    @staticmethod
    def validate_language_code(lang_code: str) -> str:
        """Validate a language code.
        
        Args:
            lang_code: Language code to validate (e.g., 'en', 'fr', 'en-US')
            
        Returns:
            Validated language code
            
        Raises:
            ValidationError: If language code is invalid
        """
        if not lang_code:
            raise ValidationError(
                "Language code cannot be empty",
                field_name="language_code",
                field_value=lang_code
            )
        
        if not LANGUAGE_CODE_PATTERN.match(lang_code):
            raise ValidationError(
                f"Invalid language code format: {lang_code}. Expected format: 'en' or 'en-US'",
                field_name="language_code",
                field_value=lang_code
            )
        
        return lang_code.lower()
    
    @staticmethod
    def validate_api_name(api_name: str) -> str:
        """Validate an API name.
        
        Args:
            api_name: API name to validate
            
        Returns:
            Validated API name
            
        Raises:
            ValidationError: If API name is invalid
        """
        if not api_name:
            raise ValidationError(
                "API name cannot be empty",
                field_name="api_name",
                field_value=api_name
            )
        
        if not API_NAME_PATTERN.match(api_name):
            raise ValidationError(
                f"Invalid API name format: {api_name}. Must start with letter and contain only lowercase letters, numbers, and underscores",
                field_name="api_name",
                field_value=api_name
            )
        
        return api_name.lower()
    
    @staticmethod
    def validate_credentials_file(creds_path: Union[str, Path]) -> Path:
        """Validate a credentials file.
        
        Args:
            creds_path: Path to credentials file
            
        Returns:
            Validated Path object
            
        Raises:
            ValidationError: If credentials file is invalid
        """
        path = Path(creds_path)
        
        if not path.exists():
            raise ValidationError(
                f"Credentials file does not exist: {creds_path}",
                field_name="credentials_path",
                field_value=str(creds_path)
            )
        
        if not path.is_file():
            raise ValidationError(
                f"Credentials path is not a file: {creds_path}",
                field_name="credentials_path",
                field_value=str(creds_path)
            )
        
        # Check if it's a JSON file
        if path.suffix.lower() != '.json':
            raise ValidationError(
                f"Credentials file must be JSON format: {creds_path}",
                field_name="credentials_path",
                field_value=str(creds_path)
            )
        
        # Try to parse JSON
        try:
            with open(path, 'r', encoding='utf-8') as f:
                creds_data = json.load(f)
            
            # Basic validation for Google service account
            required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
            missing_fields = [field for field in required_fields if field not in creds_data]
            
            if missing_fields:
                raise ValidationError(
                    f"Credentials file missing required fields: {', '.join(missing_fields)}",
                    field_name="credentials_content",
                    field_value="<credentials_data>"
                )
            
            if creds_data.get('type') != 'service_account':
                raise ValidationError(
                    f"Invalid credentials type: {creds_data.get('type')}. Expected: 'service_account'",
                    field_name="credentials_type",
                    field_value=creds_data.get('type')
                )
        
        except json.JSONDecodeError as e:
            raise ValidationError(
                f"Invalid JSON in credentials file: {e}",
                field_name="credentials_format",
                field_value=str(creds_path)
            )
        except Exception as e:
            raise ValidationError(
                f"Error reading credentials file: {e}",
                field_name="credentials_access",
                field_value=str(creds_path)
            )
        
        return path

class DataValidator:
    """Validator for data structures and API responses."""
    
    @staticmethod
    def validate_json_structure(data: Any, required_fields: List[str], optional_fields: List[str] = None) -> Dict[str, Any]:
        """Validate JSON data structure.
        
        Args:
            data: Data to validate
            required_fields: List of required field names
            optional_fields: List of optional field names
            
        Returns:
            Validated data dictionary
            
        Raises:
            ValidationError: If data structure is invalid
        """
        if not isinstance(data, dict):
            raise ValidationError(
                f"Expected dictionary, got {type(data).__name__}",
                field_name="data_type",
                field_value=str(type(data))
            )
        
        # Check required fields
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}",
                field_name="required_fields",
                field_value=missing_fields
            )
        
        # Check for unexpected fields
        allowed_fields = set(required_fields)
        if optional_fields:
            allowed_fields.update(optional_fields)
        
        unexpected_fields = [field for field in data.keys() if field not in allowed_fields]
        if unexpected_fields:
            # This is a warning, not an error
            pass
        
        return data
    
    @staticmethod
    def validate_metadata_structure(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate image metadata structure.
        
        Args:
            metadata: Metadata dictionary to validate
            
        Returns:
            Validated metadata dictionary
            
        Raises:
            ValidationError: If metadata structure is invalid
        """
        required_fields = ['title', 'description', 'tags', 'colors', 'objects']
        optional_fields = ['text_content', 'faces', 'landmarks', 'logos', 'safe_search', 'image_properties']
        
        validated_data = DataValidator.validate_json_structure(
            metadata, required_fields, optional_fields
        )
        
        # Validate specific field types
        if not isinstance(validated_data.get('title'), str):
            raise ValidationError(
                "Title must be a string",
                field_name="title",
                field_value=validated_data.get('title')
            )
        
        if not isinstance(validated_data.get('description'), str):
            raise ValidationError(
                "Description must be a string",
                field_name="description",
                field_value=validated_data.get('description')
            )
        
        if not isinstance(validated_data.get('tags'), list):
            raise ValidationError(
                "Tags must be a list",
                field_name="tags",
                field_value=validated_data.get('tags')
            )
        
        if not isinstance(validated_data.get('colors'), list):
            raise ValidationError(
                "Colors must be a list",
                field_name="colors",
                field_value=validated_data.get('colors')
            )
        
        if not isinstance(validated_data.get('objects'), list):
            raise ValidationError(
                "Objects must be a list",
                field_name="objects",
                field_value=validated_data.get('objects')
            )
        
        return validated_data
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 1000) -> str:
        """Sanitize text content.
        
        Args:
            text: Text to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Remove control characters except newlines and tabs
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Normalize whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        # Truncate if too long
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length].rstrip() + '...'
        
        return sanitized
    
    @staticmethod
    def validate_url(url: str) -> str:
        """Validate a URL.
        
        Args:
            url: URL to validate
            
        Returns:
            Validated URL
            
        Raises:
            ValidationError: If URL is invalid
        """
        if not url:
            raise ValidationError(
                "URL cannot be empty",
                field_name="url",
                field_value=url
            )
        
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise ValidationError(
                    f"Invalid URL format: {url}",
                    field_name="url",
                    field_value=url
                )
        except Exception as e:
            raise ValidationError(
                f"Error parsing URL: {e}",
                field_name="url",
                field_value=url
            )
        
        return url

# Convenience functions
def validate_image_file(file_path: Union[str, Path]) -> Path:
    """Validate an image file. See FileValidator.validate_image_file for details."""
    return FileValidator.validate_image_file(file_path)

def validate_directory(dir_path: Union[str, Path]) -> Path:
    """Validate a directory. See FileValidator.validate_directory for details."""
    return FileValidator.validate_directory(dir_path)

def validate_output_path(output_path: Union[str, Path]) -> Path:
    """Validate an output path. See FileValidator.validate_output_path for details."""
    return FileValidator.validate_output_path(output_path)

def sanitize_filename(filename: str) -> str:
    """Sanitize a filename. See FileValidator.sanitize_filename for details."""
    return FileValidator.sanitize_filename(filename)

def validate_language_code(lang_code: str) -> str:
    """Validate a language code. See ConfigValidator.validate_language_code for details."""
    return ConfigValidator.validate_language_code(lang_code)

def validate_credentials_file(creds_path: Union[str, Path]) -> Path:
    """Validate credentials file. See ConfigValidator.validate_credentials_file for details."""
    return ConfigValidator.validate_credentials_file(creds_path)

def validate_metadata_structure(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Validate metadata structure. See DataValidator.validate_metadata_structure for details."""
    return DataValidator.validate_metadata_structure(metadata)

def sanitize_text(text: str, max_length: int = 1000) -> str:
    """Sanitize text content. See DataValidator.sanitize_text for details."""
    return DataValidator.sanitize_text(text, max_length)