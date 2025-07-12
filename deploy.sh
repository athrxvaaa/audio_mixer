#!/bin/bash

# BGM Inserter Deployment Script
set -e

echo "🚀 Starting BGM Inserter deployment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file based on env_example.txt"
    exit 1
fi

# Check if BGM folder exists
if [ ! -d "BGM" ]; then
    echo "❌ Error: BGM folder not found!"
    echo "Please ensure the BGM folder exists with the correct structure"
    exit 1
fi

# Load environment variables
source .env

# Validate required environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY is not set in .env file"
    exit 1
fi

echo "✅ Environment validation passed"

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down || true

# Build and start containers
echo "🔨 Building and starting containers..."
docker-compose up -d --build

# Wait for service to be ready
echo "⏳ Waiting for service to be ready..."
sleep 10

# Check health
echo "🏥 Checking service health..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Service is healthy!"
        break
    fi
    echo "⏳ Waiting for service to be ready... (attempt $i/30)"
    sleep 2
done

if [ $i -eq 30 ]; then
    echo "❌ Service failed to start properly"
    echo "📋 Checking logs..."
    docker-compose logs
    exit 1
fi

# Test API endpoints
echo "🧪 Testing API endpoints..."
curl -s http://localhost:8000/ | jq . || echo "Root endpoint test failed"
curl -s http://localhost:8000/health | jq . || echo "Health endpoint test failed"
curl -s http://localhost:8000/bgm-files | jq . || echo "BGM files endpoint test failed"

echo "🎉 Deployment completed successfully!"
echo "📚 API documentation: http://localhost:8000/docs"
echo "🔗 Health check: http://localhost:8000/health"
echo "📋 View logs: docker-compose logs -f" 