from pydantic import BaseModel
from typing import List, Optional

class HealthResponse(BaseModel):
    """Atom component for health check response."""
    status: str
    service: str

class BGMFileInfo(BaseModel):
    """Atom component for BGM file information."""
    filename: str
    file_path: str

class BGMFilesResponse(BaseModel):
    """Atom component for BGM files list response."""
    bgm_files: List[str]

class ErrorResponse(BaseModel):
    """Atom component for error response."""
    detail: str
    error_code: Optional[str] = None

class ProcessingStatus(BaseModel):
    """Atom component for processing status."""
    status: str
    message: str
    progress: Optional[float] = None 