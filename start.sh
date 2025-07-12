#!/bin/bash

# BGM Inserter Startup Script
set -e

echo "🚀 Starting BGM Inserter API..."

# Load environment variables
if [ -f .env ]; then
    echo "📄 Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check required environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY environment variable is not set"
    exit 1
fi

# Check if BGM folder exists
if [ ! -d "BGM" ]; then
    echo "❌ Error: BGM folder not found"
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p output_audio

# Set default values
export HOST=${HOST:-0.0.0.0}
export PORT=${PORT:-8000}
export ENVIRONMENT=${ENVIRONMENT:-production}
export LOG_LEVEL=${LOG_LEVEL:-info}

echo "🌍 Environment: $ENVIRONMENT"
echo "🔗 Host: $HOST"
echo "🚪 Port: $PORT"
echo "📝 Log Level: $LOG_LEVEL"

# Start the API server
exec python run_api.py 