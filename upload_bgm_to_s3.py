#!/usr/bin/env python3
"""
Script to upload BGM files from local folder to S3 bucket.
This script maintains the same folder structure in S3 as the local BGM folder.
"""

import os
import boto3
from pathlib import Path
from dotenv import load_dotenv
import argparse

def upload_bgm_to_s3():
    """Upload BGM files from local folder to S3 bucket."""
    
    # Load environment variables
    load_dotenv()
    
    # Get S3 configuration
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    bgm_bucket_name = os.getenv('BGM_S3_BUCKET_NAME')
    bgm_s3_prefix = os.getenv('BGM_S3_PREFIX', 'bgm/')
    aws_region = os.getenv('AWS_REGION', 'ap-south-1')
    
    # Validate required environment variables
    if not aws_access_key or not aws_secret_key:
        print("❌ Error: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY must be set")
        return False
    
    if not bgm_bucket_name:
        print("❌ Error: BGM_S3_BUCKET_NAME must be set")
        return False
    
    # Check if local BGM folder exists
    local_bgm_folder = Path("BGM")
    if not local_bgm_folder.exists():
        print("❌ Error: Local BGM folder not found")
        return False
    
    # Initialize S3 client
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
        
        # Test bucket access
        s3_client.head_bucket(Bucket=bgm_bucket_name)
        print(f"✅ Successfully connected to S3 bucket: {bgm_bucket_name}")
        
    except Exception as e:
        print(f"❌ Error connecting to S3: {e}")
        return False
    
    # Supported audio file extensions
    audio_extensions = {'.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg', '.wma'}
    
    # Upload files
    uploaded_count = 0
    skipped_count = 0
    
    print(f"📁 Uploading BGM files from {local_bgm_folder} to S3...")
    
    for theme_folder in local_bgm_folder.iterdir():
        if theme_folder.is_dir():
            theme_name = theme_folder.name
            print(f"\n🎵 Processing theme: {theme_name}")
            
            for audio_file in theme_folder.iterdir():
                if audio_file.is_file() and audio_file.suffix.lower() in audio_extensions:
                    # Create S3 key
                    s3_key = f"{bgm_s3_prefix}{theme_name}/{audio_file.name}"
                    
                    try:
                        # Check if file already exists in S3
                        try:
                            s3_client.head_object(Bucket=bgm_bucket_name, Key=s3_key)
                            print(f"  ⏭️  Skipping {audio_file.name} (already exists)")
                            skipped_count += 1
                            continue
                        except:
                            pass  # File doesn't exist, proceed with upload
                        
                        # Upload file
                        print(f"  📤 Uploading {audio_file.name}...")
                        s3_client.upload_file(
                            str(audio_file),
                            bgm_bucket_name,
                            s3_key,
                            ExtraArgs={
                                'ContentType': 'audio/mpeg' if audio_file.suffix.lower() == '.mp3' else 'audio/wav'
                            }
                        )
                        
                        # Make file publicly accessible
                        s3_client.put_object_acl(
                            Bucket=bgm_bucket_name,
                            Key=s3_key,
                            ACL='public-read'
                        )
                        
                        print(f"  ✅ Uploaded {audio_file.name}")
                        uploaded_count += 1
                        
                    except Exception as e:
                        print(f"  ❌ Error uploading {audio_file.name}: {e}")
    
    print(f"\n📊 Upload Summary:")
    print(f"  ✅ Uploaded: {uploaded_count} files")
    print(f"  ⏭️  Skipped: {skipped_count} files (already exist)")
    print(f"  📁 S3 Bucket: {bgm_bucket_name}")
    print(f"  📂 S3 Prefix: {bgm_s3_prefix}")
    
    if uploaded_count > 0:
        print(f"\n🎉 BGM files successfully uploaded to S3!")
        print(f"💡 You can now remove the local BGM folder and use S3 for BGM storage.")
    
    return True

def list_s3_bgm_files():
    """List BGM files currently in S3 bucket."""
    
    # Load environment variables
    load_dotenv()
    
    # Get S3 configuration
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    bgm_bucket_name = os.getenv('BGM_S3_BUCKET_NAME')
    bgm_s3_prefix = os.getenv('BGM_S3_PREFIX', 'bgm/')
    aws_region = os.getenv('AWS_REGION', 'ap-south-1')
    
    # Validate required environment variables
    if not aws_access_key or not aws_secret_key:
        print("❌ Error: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY must be set")
        return False
    
    if not bgm_bucket_name:
        print("❌ Error: BGM_S3_BUCKET_NAME must be set")
        return False
    
    # Initialize S3 client
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
        
    except Exception as e:
        print(f"❌ Error connecting to S3: {e}")
        return False
    
    # List files
    try:
        response = s3_client.list_objects_v2(
            Bucket=bgm_bucket_name,
            Prefix=bgm_s3_prefix
        )
        
        if 'Contents' not in response:
            print(f"📁 No BGM files found in S3 bucket: {bgm_bucket_name}")
            return True
        
        print(f"📁 BGM files in S3 bucket: {bgm_bucket_name}")
        print(f"📂 Prefix: {bgm_s3_prefix}")
        print()
        
        current_theme = None
        for obj in response['Contents']:
            key = obj['Key']
            if key.endswith('/'):  # Skip folder objects
                continue
            
            # Extract theme from key
            theme = key.replace(bgm_s3_prefix, '').split('/')[0]
            filename = Path(key).name
            
            if theme != current_theme:
                current_theme = theme
                print(f"🎵 Theme: {theme}")
            
            print(f"  📄 {filename}")
        
        print(f"\n📊 Total files: {len([obj for obj in response['Contents'] if not obj['Key'].endswith('/')])}")
        
    except Exception as e:
        print(f"❌ Error listing S3 files: {e}")
        return False
    
    return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Upload BGM files to S3 or list existing files')
    parser.add_argument('--list', action='store_true', help='List existing BGM files in S3')
    parser.add_argument('--upload', action='store_true', help='Upload BGM files to S3')
    
    args = parser.parse_args()
    
    if args.list:
        list_s3_bgm_files()
    elif args.upload:
        upload_bgm_to_s3()
    else:
        # Default to upload
        upload_bgm_to_s3()

if __name__ == "__main__":
    main() 