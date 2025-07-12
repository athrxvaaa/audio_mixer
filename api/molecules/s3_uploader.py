import boto3
import os
from pathlib import Path
from typing import Optional
import uuid
from datetime import datetime

class S3Uploader:
    """Molecule component for uploading files to AWS S3."""
    
    def __init__(self):
        # Use environment variables for AWS credentials
        self.access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.bucket_name = os.getenv('AWS_S3_BUCKET_NAME', 'lisa-research')
        self.region = os.getenv('AWS_REGION', 'ap-south-1')
        
        # Validate required environment variables
        if not self.access_key or not self.secret_key:
            raise ValueError("AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables must be set")
        
        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        )
    
    def upload_file(self, file_path: str, custom_filename: Optional[str] = None) -> str:
        """
        Upload a file to S3 and return the public URL.
        
        Args:
            file_path: Path to the file to upload
            custom_filename: Optional custom filename for S3
            
        Returns:
            Public S3 URL of the uploaded file
        """
        try:
            # Generate unique filename if not provided
            if not custom_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_id = str(uuid.uuid4())[:8]
                original_name = Path(file_path).name
                custom_filename = f"processed_audio/{timestamp}_{unique_id}_{original_name}"
            
            # Upload file to S3
            print(f"Uploading {file_path} to S3 as {custom_filename}")
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                custom_filename,
                ExtraArgs={
                    'ContentType': 'audio/wav'
                }
            )
            
            # Generate public URL
            s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{custom_filename}"
            print(f"File uploaded successfully: {s3_url}")
            
            return s3_url
            
        except Exception as e:
            print(f"Error uploading to S3: {str(e)}")
            raise Exception(f"Failed to upload file to S3: {str(e)}")
    
    def upload_processed_audio(self, file_path: str, original_filename: str) -> str:
        """
        Upload processed audio file with organized naming.
        
        Args:
            file_path: Path to the processed audio file
            original_filename: Original filename for reference
            
        Returns:
            Public S3 URL of the uploaded file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        original_stem = Path(original_filename).stem
        
        s3_filename = f"processed_audio/{timestamp}_{unique_id}_{original_stem}_with_bgm.wav"
        
        return self.upload_file(file_path, s3_filename) 