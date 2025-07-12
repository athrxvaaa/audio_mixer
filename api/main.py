from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import tempfile
from pathlib import Path
import uuid
import requests

from api.organisms.bgm_inserter_service import BGMInserterService
from api.molecules.s3_uploader import S3Uploader

app = FastAPI(
    title="BGM Inserter API",
    description="API for inserting background music into audio files based on content analysis",
    version="1.0.0"
)

# Get CORS origins from environment variable
cors_origins = os.getenv('CORS_ORIGINS', '*').split(',')
if cors_origins == ['*'] and os.getenv('ENVIRONMENT') == 'production':
    # In production, default to empty list if not specified
    cors_origins = []

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Initialize the BGM Inserter service and S3 uploader
bgm_service = BGMInserterService()

# Initialize S3 uploader only if enabled and credentials are available
s3_uploader = None
if os.getenv('ENABLE_S3_UPLOAD', 'true').lower() == 'true':
    try:
        s3_uploader = S3Uploader()
    except ValueError as e:
        print(f"Warning: S3 uploader disabled - {e}")
        s3_uploader = None

class AudioProcessRequest(BaseModel):
    """Request model for audio processing with S3 URL."""
    s3_url: str
    bgm_volume_reduction: float = 35.0  # Default volume reduction in dB

@app.get("/")
async def root():
    return {"message": "BGM Inserter API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "BGM Inserter API"}

@app.post("/process-audio")
async def process_audio(request: AudioProcessRequest):
    """
    Process an audio file from S3 URL by adding background music based on content analysis.
    
    - **s3_url**: The S3 URL of the audio file to process (supports mp3, wav, m4a, aac, flac, ogg, wma)
    - **bgm_volume_reduction**: Volume reduction for BGM in dB (default: 35.0)
    
    Returns the processed audio file with background music.
    """
    # Validate S3 URL
    if not request.s3_url.startswith(('http://', 'https://')):
        raise HTTPException(
            status_code=400, 
            detail="Invalid URL. Please provide a valid HTTP/HTTPS URL."
        )
    
    # Validate file type from URL
    allowed_extensions = {'.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg', '.wma'}
    file_extension = Path(request.s3_url).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Create a unique temporary file
    temp_input_path = tempfile.mktemp(suffix=file_extension)
    
    try:
        # Download file from S3 URL
        print(f"Downloading audio file from: {request.s3_url}")
        response = requests.get(request.s3_url, stream=True)
        response.raise_for_status()
        
        # Save downloaded file to temporary location
        with open(temp_input_path, "wb") as buffer:
            for chunk in response.iter_content(chunk_size=8192):
                buffer.write(chunk)
        
        print(f"Downloaded file saved to: {temp_input_path}")
        
        # Process the audio with custom volume reduction
        output_path = bgm_service.process_audio(temp_input_path, bgm_volume_reduction=request.bgm_volume_reduction)
        
        # Generate output filename
        original_filename = Path(request.s3_url).name
        
        # Upload processed audio to S3
        s3_url = None
        if s3_uploader:
            s3_url = s3_uploader.upload_processed_audio(output_path, original_filename)
        
        # Return the S3 URL or local file info
        response_data = {
            "status": "success",
            "message": "Audio processed successfully",
            "original_filename": original_filename,
            "processed_filename": f"processed_{original_filename.replace(file_extension, '.wav')}"
        }
        
        if s3_url:
            response_data["s3_url"] = s3_url
            response_data["message"] = "Audio processed and uploaded successfully"
        else:
            response_data["local_path"] = output_path
            response_data["message"] = "Audio processed successfully (S3 upload disabled)"
        
        return JSONResponse(content=response_data)
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error downloading file from URL: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")
    
    finally:
        # Clean up temporary files
        temp_files_to_cleanup = [temp_input_path]
        if 'output_path' in locals():
            temp_files_to_cleanup.append(output_path)
        
        for temp_path in temp_files_to_cleanup:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass

@app.get("/bgm-files")
async def get_bgm_files():
    """
    Get a list of available background music files.
    """
    try:
        bgm_files = bgm_service.get_available_bgm_files()
        return {"bgm_files": bgm_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving BGM files: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 