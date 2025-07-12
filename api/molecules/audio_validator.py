from pathlib import Path
from typing import Set, Tuple
from pydub import AudioSegment
import os

class AudioValidator:
    """Molecule component for validating audio files and formats."""
    
    SUPPORTED_EXTENSIONS: Set[str] = {'.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg', '.wma'}
    MAX_FILE_SIZE_MB: int = 100  # 100MB limit
    
    @classmethod
    def validate_file_extension(cls, filename: str) -> Tuple[bool, str]:
        """
        Validate if the file extension is supported.
        
        Args:
            filename: Name of the file to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not filename:
            return False, "No filename provided"
        
        file_extension = Path(filename).suffix.lower()
        
        if file_extension not in cls.SUPPORTED_EXTENSIONS:
            return False, f"Unsupported file type: {file_extension}. Supported types: {', '.join(cls.SUPPORTED_EXTENSIONS)}"
        
        return True, ""
    
    @classmethod
    def validate_file_size(cls, file_path: str) -> Tuple[bool, str]:
        """
        Validate if the file size is within acceptable limits.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"
        
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        
        if file_size_mb > cls.MAX_FILE_SIZE_MB:
            return False, f"File too large: {file_size_mb:.2f}MB. Maximum allowed: {cls.MAX_FILE_SIZE_MB}MB"
        
        return True, ""
    
    @classmethod
    def validate_audio_file(cls, file_path: str) -> Tuple[bool, str]:
        """
        Validate if the file is a valid audio file that can be processed.
        
        Args:
            file_path: Path to the audio file to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file extension
        is_valid_ext, ext_error = cls.validate_file_extension(file_path)
        if not is_valid_ext:
            return False, ext_error
        
        # Check file size
        is_valid_size, size_error = cls.validate_file_size(file_path)
        if not is_valid_size:
            return False, size_error
        
        # Check if file is empty
        if os.path.getsize(file_path) == 0:
            return False, "Audio file is empty"
        
        # Try to load the audio file
        try:
            AudioSegment.from_file(file_path)
            return True, ""
        except Exception as e:
            return False, f"Invalid audio file: {str(e)}"
    
    @classmethod
    def get_supported_formats(cls) -> Set[str]:
        """Get the set of supported audio file formats."""
        return cls.SUPPORTED_EXTENSIONS.copy() 