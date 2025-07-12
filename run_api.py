#!/usr/bin/env python3
"""
Startup script for the BGM Inserter API.
"""

import uvicorn
import os
from pathlib import Path
from dotenv import load_dotenv

def validate_environment():
    """Validate required environment variables."""
    load_dotenv()
    
    required_vars = ['OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment.")
        return False
    
    # Check for AWS credentials if S3 upload is enabled
    if os.getenv('ENABLE_S3_UPLOAD', 'true').lower() == 'true':
        aws_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
        missing_aws = [var for var in aws_vars if not os.getenv(var)]
        if missing_aws:
            print(f"⚠️  Warning: Missing AWS credentials: {', '.join(missing_aws)}")
            print("S3 upload functionality will be disabled.")
            os.environ['ENABLE_S3_UPLOAD'] = 'false'
    
    return True

def main():
    """Run the BGM Inserter API server."""
    
    # Validate environment
    if not validate_environment():
        return 1
    
    # Check if BGM folder exists
    if not os.path.exists('BGM'):
        print("❌ Error: 'BGM' folder not found. Please create it and add themed BGM audio files.")
        print("Required folder structure:")
        print("  BGM/")
        print("    Start HOOK/")
        print("    WHAT/")
        print("    WHY /")
        print("    HOW/")
        print("    End HOOK/")
        return 1
    
    # Create output directory if it doesn't exist
    Path("output_audio").mkdir(exist_ok=True)
    
    # Get configuration from environment
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '8000'))
    environment = os.getenv('ENVIRONMENT', 'development')
    
    # Configure for production vs development
    reload_enabled = environment == 'development'
    log_level = os.getenv('LOG_LEVEL', 'info')
    
    # Run the API server
    print(f"🚀 Starting BGM Inserter API server...")
    print(f"🌍 Environment: {environment}")
    print(f"🔗 API will be available at: http://{host}:{port}")
    print(f"📚 API documentation will be available at: http://{host}:{port}/docs")
    print(f"🔄 Auto-reload: {'enabled' if reload_enabled else 'disabled'}")
    
    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=reload_enabled,
        log_level=log_level,
        access_log=True
    )

if __name__ == "__main__":
    exit(main()) 