#!/bin/bash
# CoolBits.ai Production Deployment Script

set -e

echo "🚀 CoolBits.ai Production Deployment"
echo "=================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if GitHub token is provided
if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ GITHUB_TOKEN environment variable is required"
    echo "   Set it with: export GITHUB_TOKEN=your_token"
    exit 1
fi

# Login to GitHub Container Registry
echo "🔐 Logging in to GitHub Container Registry..."
echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$(whoami)" --password-stdin

# Create application directory
echo "📁 Setting up application directory..."
mkdir -p /opt/coolbits
cd /opt/coolbits

# Download production docker-compose
echo "📥 Downloading production configuration..."
curl -O https://raw.githubusercontent.com/coolbits-dm/coolbits.ai/main/docker-compose.prod.yml
mv docker-compose.prod.yml docker-compose.yml

# Create production environment file
echo "⚙️ Creating production environment..."
cat > .env << EOF
OPIPE_ENV=prod
DB_URL=sqlite:///./data/coolbits.db
AGENTS_ENABLED=mock
EOF

# Create data and logs directories
echo "📂 Creating data directories..."
mkdir -p data logs qdrant_storage

# Pull latest images
echo "📦 Pulling latest images..."
docker compose pull

# Start services
echo "🚀 Starting CoolBits.ai services..."
docker compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 30

# Check service status
echo "📊 Service Status:"
docker compose ps

# Show logs
echo "📋 Recent logs:"
docker compose logs --tail=50 web

echo ""
echo "✅ Deployment complete!"
echo "🌐 CoolBits.ai is available at: http://localhost:8501"
echo "📊 Qdrant is available at: http://localhost:6333"
echo ""
echo "📋 Useful commands:"
echo "  View logs: docker compose logs -f"
echo "  Restart: docker compose restart"
echo "  Stop: docker compose down"
echo "  Update: docker compose pull && docker compose up -d"
