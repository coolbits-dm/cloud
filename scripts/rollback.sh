#!/bin/bash
# CoolBits.ai Rollback Script

set -e

echo "🔄 CoolBits.ai Rollback Script"
echo "============================="

# Check if version is provided
if [ -z "$1" ]; then
    echo "❌ Usage: $0 <version_tag>"
    echo "   Example: $0 v0.1.0-docker"
    exit 1
fi

VERSION=$1
echo "🔄 Rolling back to version: $VERSION"

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

# Navigate to application directory
cd /opt/coolbits

# Stop current services
echo "🛑 Stopping current services..."
docker compose down

# Pull previous version
echo "📥 Pulling version $VERSION..."
docker pull ghcr.io/coolbits-dm/coolbits.ai:$VERSION

# Update docker-compose.yml to use specific version
echo "⚙️ Updating configuration for version $VERSION..."
sed -i "s|ghcr.io/coolbits-dm/coolbits.ai:latest|ghcr.io/coolbits-dm/coolbits.ai:$VERSION|g" docker-compose.yml

# Start services with previous version
echo "🚀 Starting services with version $VERSION..."
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
echo "✅ Rollback complete!"
echo "🔄 CoolBits.ai is now running version: $VERSION"
echo "🌐 Available at: http://localhost:8501"
echo ""
echo "📋 To rollback to latest:"
echo "  sed -i 's|ghcr.io/coolbits-dm/coolbits.ai:$VERSION|ghcr.io/coolbits-dm/coolbits.ai:latest|g' docker-compose.yml"
echo "  docker compose pull && docker compose up -d"
