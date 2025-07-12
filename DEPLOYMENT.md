# BGM Inserter - Deployment Guide

This guide covers deploying the BGM Inserter API to production environments with S3-based BGM storage.

## 🚀 Quick Start with Docker

### Prerequisites

- Docker and Docker Compose installed
- OpenAI API key
- AWS S3 credentials (for file uploads and BGM storage)

### 1. Environment Setup

Create a `.env` file in the project root:

```bash
# Copy the example file
cp env_example.txt .env

# Edit with your actual values
nano .env
```

Required environment variables:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# AWS S3 Configuration (for file uploads)
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_S3_BUCKET_NAME=your_s3_bucket_name
AWS_REGION=ap-south-1

# AWS S3 Configuration (for BGM files)
BGM_S3_BUCKET_NAME=your_bgm_s3_bucket_name
BGM_S3_PREFIX=bgm/

# API Configuration
ENVIRONMENT=production
CORS_ORIGINS=https://yourdomain.com
```

### 2. S3 BGM Setup

#### Option A: Upload Local BGM Files to S3

1. **Upload your existing BGM files to S3**:

   ```bash
   # Upload BGM files from local folder to S3
   python upload_bgm_to_s3.py --upload

   # List existing BGM files in S3
   python upload_bgm_to_s3.py --list
   ```

2. **S3 Bucket Structure** (automatically created):
   ```
   your-bgm-bucket/
   └── bgm/
       ├── Start HOOK/
       │   ├── ColorFilmMusic - Here We Go Rock.mp3
       │   └── The Upbeat Funky full version.mp3
       ├── WHAT/
       │   └── Art Media - Ambient Background Music (MP3).mp3
       ├── WHY /
       │   └── the ambient music.mp3
       ├── HOW/
       │   └── Ambient Sky (Full).mp3
       └── End HOOK/
           ├── Curious_Thoughts.mp3
           └── Full Version.mp3
   ```

#### Option B: Upload BGM Files Manually

1. **Create S3 bucket** (if not exists):

   ```bash
   aws s3 mb s3://your-bgm-bucket-name
   ```

2. **Upload files with correct structure**:

   ```bash
   # Upload theme folders
   aws s3 cp BGM/Start\ HOOK/ s3://your-bgm-bucket-name/bgm/Start\ HOOK/ --recursive
   aws s3 cp BGM/WHAT/ s3://your-bgm-bucket-name/bgm/WHAT/ --recursive
   aws s3 cp BGM/WHY\ / s3://your-bgm-bucket-name/bgm/WHY\ / --recursive
   aws s3 cp BGM/HOW/ s3://your-bgm-bucket-name/bgm/HOW/ --recursive
   aws s3 cp BGM/End\ HOOK/ s3://your-bgm-bucket-name/bgm/End\ HOOK/ --recursive

   # Make files publicly accessible
   aws s3 sync s3://your-bgm-bucket-name s3://your-bgm-bucket-name --acl public-read
   ```

### 3. Deploy with Docker Compose

```bash
# Build and start the service
docker-compose up -d

# Check logs
docker-compose logs -f

# Check health
curl http://localhost:8000/health
```

### 4. Test the API

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test BGM files endpoint
curl http://localhost:8000/bgm-files

# Test audio processing (replace with actual S3 URL)
curl -X POST http://localhost:8000/process-audio \
  -H "Content-Type: application/json" \
  -d '{
    "s3_url": "https://example.com/audio.mp3",
    "bgm_volume_reduction": 35.0
  }'
```

## 🌐 Production Deployment Options

### Option 1: Docker on VPS/Cloud Server

1. **Deploy to VPS**:

   ```bash
   # SSH to your server
   ssh user@your-server.com

   # Clone repository
   git clone <your-repo-url>
   cd Bgm_inserter

   # Setup environment
   cp env_example.txt .env
   nano .env  # Edit with your values

   # Upload BGM files to S3 (if not done locally)
   python upload_bgm_to_s3.py --upload

   # Deploy
   docker-compose up -d
   ```

2. **Setup Reverse Proxy (Nginx)**:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

### Option 2: AWS ECS/Fargate

1. **Create ECR Repository**:

   ```bash
   aws ecr create-repository --repository-name bgm-inserter
   ```

2. **Build and Push Image**:

   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   docker build -t bgm-inserter .
   docker tag bgm-inserter:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/bgm-inserter:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/bgm-inserter:latest
   ```

3. **Deploy to ECS** (use AWS Console or CLI)

### Option 3: Google Cloud Run

1. **Build and Deploy**:

   ```bash
   # Build image
   docker build -t gcr.io/<project-id>/bgm-inserter .

   # Push to Google Container Registry
   docker push gcr.io/<project-id>/bgm-inserter

   # Deploy to Cloud Run
   gcloud run deploy bgm-inserter \
     --image gcr.io/<project-id>/bgm-inserter \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars ENVIRONMENT=production
   ```

### Option 4: Heroku

1. **Create Heroku App**:

   ```bash
   heroku create your-bgm-inserter-app
   ```

2. **Set Environment Variables**:

   ```bash
   heroku config:set OPENAI_API_KEY=your_key
   heroku config:set ENVIRONMENT=production
   heroku config:set BGM_S3_BUCKET_NAME=your_bgm_bucket
   ```

3. **Deploy**:
   ```bash
   git push heroku main
   ```

## 🔧 Configuration Options

### Environment Variables

| Variable                | Default       | Description                                   |
| ----------------------- | ------------- | --------------------------------------------- |
| `OPENAI_API_KEY`        | Required      | OpenAI API key for transcription and analysis |
| `AWS_ACCESS_KEY_ID`     | -             | AWS access key for S3 operations              |
| `AWS_SECRET_ACCESS_KEY` | -             | AWS secret key for S3 operations              |
| `AWS_S3_BUCKET_NAME`    | lisa-research | S3 bucket for processed audio uploads         |
| `AWS_REGION`            | ap-south-1    | AWS region                                    |
| `BGM_S3_BUCKET_NAME`    | -             | S3 bucket for BGM files                       |
| `BGM_S3_PREFIX`         | bgm/          | S3 prefix for BGM files                       |
| `HOST`                  | 0.0.0.0       | API server host                               |
| `PORT`                  | 8000          | API server port                               |
| `ENVIRONMENT`           | development   | Environment (development/production)          |
| `LOG_LEVEL`             | info          | Logging level                                 |
| `CORS_ORIGINS`          | \*            | Comma-separated allowed origins               |
| `ENABLE_S3_UPLOAD`      | true          | Enable/disable S3 uploads                     |

### S3 BGM Configuration

The application supports two modes for BGM storage:

1. **S3 Mode** (Recommended for production):

   - BGM files stored in S3 bucket
   - Automatic fallback to local files if S3 unavailable
   - Better scalability and deployment flexibility

2. **Local Mode** (Fallback):
   - BGM files stored in local `BGM/` folder
   - Used when S3 credentials not available
   - Good for development and testing

### Security Considerations

1. **Environment Variables**: Never commit `.env` files to version control
2. **CORS Configuration**: Set specific origins in production
3. **API Keys**: Use secure secret management (AWS Secrets Manager, etc.)
4. **HTTPS**: Always use HTTPS in production
5. **Rate Limiting**: Consider adding rate limiting for API endpoints
6. **S3 Permissions**: Ensure proper IAM roles and bucket policies

### Monitoring and Logging

1. **Health Checks**: API includes `/health` endpoint
2. **Logging**: Configure log level via `LOG_LEVEL` environment variable
3. **Metrics**: Consider adding Prometheus metrics
4. **Error Tracking**: Integrate with services like Sentry

## 🚨 Troubleshooting

### Common Issues

1. **FFmpeg not found**:

   - Ensure FFmpeg is installed in Docker image
   - Check Dockerfile includes FFmpeg installation

2. **BGM files not found**:

   - Verify S3 bucket exists and is accessible
   - Check BGM_S3_BUCKET_NAME environment variable
   - Ensure BGM files are uploaded with correct structure
   - Check local BGM folder as fallback

3. **AWS credentials error**:

   - Verify AWS credentials are set correctly
   - Check IAM permissions for S3 access
   - Ensure bucket policies allow public read access for BGM files

4. **OpenAI API errors**:
   - Verify API key is valid and has sufficient credits
   - Check API rate limits

### Debug Commands

```bash
# Check container logs
docker-compose logs -f bgm-inserter-api

# Check container health
docker-compose ps

# Access container shell
docker-compose exec bgm-inserter-api bash

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/bgm-files

# List S3 BGM files
python upload_bgm_to_s3.py --list

# Upload BGM files to S3
python upload_bgm_to_s3.py --upload
```

## 📊 Performance Optimization

1. **Resource Limits**: Set appropriate CPU/memory limits
2. **Caching**: Consider Redis for caching transcriptions
3. **CDN**: Use CloudFront for BGM file delivery
4. **Load Balancing**: Use multiple instances behind a load balancer
5. **Database**: Consider storing processing history in a database

## 🔄 CI/CD Pipeline

Example GitHub Actions workflow:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and push Docker image
        run: |
          docker build -t your-registry/bgm-inserter:${{ github.sha }} .
          docker push your-registry/bgm-inserter:${{ github.sha }}
      - name: Deploy to production
        run: |
          # Your deployment commands here
```

## 📞 Support

For deployment issues:

1. Check the troubleshooting section
2. Review container logs
3. Verify environment configuration
4. Test with a simple audio file first
5. Ensure S3 BGM files are properly uploaded and accessible
