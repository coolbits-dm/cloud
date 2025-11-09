#!/bin/bash
# CoolBits.ai Development Environment Setup
# One-command developer setup for onboarding < 20 minutes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "🚀 Setting up CoolBits.ai development environment..."

# Check prerequisites
check_prerequisites() {
    log_info "📋 Checking prerequisites..."
    
    local missing_tools=()
    
    if ! command -v git &> /dev/null; then
        missing_tools+=("git")
    fi
    
    if ! command -v docker &> /dev/null; then
        missing_tools+=("docker")
    fi
    
    if ! command -v python3 &> /dev/null; then
        missing_tools+=("python3")
    fi
    
    if ! command -v gcloud &> /dev/null; then
        missing_tools+=("gcloud")
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_info "Please install the missing tools and run this script again."
        exit 1
    fi
    
    log_success "All prerequisites found"
}

# Setup Python environment
setup_python() {
    log_info "🐍 Setting up Python environment..."
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install development dependencies
    if [ -f "requirements-dev.txt" ]; then
        pip install -r requirements-dev.txt
    else
        pip install streamlit requests pytest black flake8 mypy pre-commit
    fi
    
    log_success "Python environment ready"
}

# Setup pre-commit hooks
setup_pre_commit() {
    log_info "🔧 Setting up pre-commit hooks..."
    
    if [ -f ".pre-commit-config.yaml" ]; then
        pip install pre-commit
        pre-commit install
        log_success "Pre-commit hooks installed"
    else
        log_warning "Pre-commit configuration not found, skipping..."
    fi
}

# Setup VS Code workspace
setup_vscode() {
    log_info "💻 Setting up VS Code workspace..."
    
    mkdir -p .vscode
    
    # Create VS Code settings
    cat > .vscode/settings.json << EOF
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.linting.flake8Enabled": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/venv": true,
        "**/.pytest_cache": true
    },
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests"
    ]
}
EOF

    # Create VS Code launch configuration
    cat > .vscode/launch.json << EOF
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "CoolBits Debug",
            "type": "python",
            "request": "launch",
            "program": "\${workspaceFolder}/coolbits_web_app.py",
            "console": "integratedTerminal",
            "env": {
                "OPIPE_ENV": "development",
                "GOOGLE_CLOUD_PROJECT": "coolbits-ai"
            }
        }
    ]
}
EOF

    log_success "VS Code workspace configured"
}

# Setup Docker environment
setup_docker() {
    log_info "🐳 Setting up Docker environment..."
    
    # Create development Docker Compose file
    cat > docker-compose.dev.yml << EOF
version: '3.8'
services:
  coolbits-dev:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPIPE_ENV=development
      - GOOGLE_CLOUD_PROJECT=coolbits-ai
    volumes:
      - .:/app
      - /app/venv
    command: streamlit run coolbits_web_app.py --server.port=8501 --server.address=0.0.0.0
    depends_on:
      - redis-dev
      - postgres-dev
    
  redis-dev:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    
  postgres-dev:
    image: postgres:15
    environment:
      - POSTGRES_DB=coolbits_dev
      - POSTGRES_USER=coolbits
      - POSTGRES_PASSWORD=dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./sql/init.sql:/docker-entrypoint-initdb.d/init.sql

volumes:
  postgres_data:
  redis_data:
EOF

    log_success "Docker environment configured"
}

# Setup development scripts
setup_scripts() {
    log_info "📜 Setting up development scripts..."
    
    # Create logs directory
    mkdir -p logs
    
    # Create test directory
    mkdir -p tests
    
    # Create basic test file
    cat > tests/test_basic.py << EOF
import pytest
import requests

def test_health_check():
    """Test basic health check"""
    response = requests.get("http://localhost:8501/_stcore/health")
    assert response.status_code == 200

def test_api_endpoints():
    """Test API endpoints"""
    endpoints = ["/api/v1/health", "/api/v1/status"]
    
    for endpoint in endpoints:
        response = requests.get(f"http://localhost:8501{endpoint}")
        assert response.status_code == 200
EOF

    log_success "Development scripts configured"
}

# Setup environment variables
setup_env() {
    log_info "🔐 Setting up environment variables..."
    
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# CoolBits.ai Development Environment
OPIPE_ENV=development
GOOGLE_CLOUD_PROJECT=coolbits-ai
DEBUG=true

# Database
DATABASE_URL=postgresql://coolbits:dev_password@localhost:5432/coolbits_dev

# Redis
REDIS_URL=redis://localhost:6379

# API Keys (use Secret Manager in production)
OPENAI_API_KEY=your_openai_key_here
XAI_API_KEY=your_xai_key_here
EOF
        log_warning "Created .env file - please update with your API keys"
    else
        log_info ".env file already exists"
    fi
}

# Main setup function
main() {
    log_info "Starting CoolBits.ai development setup..."
    
    check_prerequisites
    setup_python
    setup_pre_commit
    setup_vscode
    setup_docker
    setup_scripts
    setup_env
    
    echo ""
    log_success "🎉 Development environment setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Activate Python environment: source venv/bin/activate"
    echo "2. Update .env file with your API keys"
    echo "3. Start development: docker-compose -f docker-compose.dev.yml up -d"
    echo "4. Open VS Code: code ."
    echo "5. Visit: http://localhost:8501"
    echo ""
    echo "Happy coding! 🚀"
}

# Run main function
main "$@"
