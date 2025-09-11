# CoolBits.ai Makefile
# ===================

.PHONY: help build test lint format clean install dev start stop health release docker-build docker-run sbom verify

# Default target
help:
	@echo "CoolBits.ai Development Commands"
	@echo "================================"
	@echo "build     - Build the application"
	@echo "test      - Run tests"
	@echo "lint      - Run linting"
	@echo "format    - Format code"
	@echo "clean     - Clean build artifacts"
	@echo "install   - Install dependencies"
	@echo "dev       - Start development server"
	@echo "start     - Start production services"
	@echo "stop      - Stop all services"
	@echo "health    - Check system health"
	@echo "release   - Create release"
	@echo "docker-build - Build Docker image"
	@echo "docker-run   - Run Docker container"
	@echo "sbom      - Generate SBOM"
	@echo "verify    - Verify release readiness"

# Build
build: clean
	@echo "🔨 Building CoolBits.ai..."
	python -m pip install -r requirements.txt
	@echo "✅ Build complete"

# Test
test:
	@echo "🧪 Running tests..."
	python -m pytest tests/ -v
	@echo "✅ Tests complete"

# Lint
lint:
	@echo "🔍 Running linting..."
	python -m flake8 . --exclude=.venv,node_modules
	@echo "✅ Linting complete"

# Format
format:
	@echo "🎨 Formatting code..."
	python -m black . --exclude=.venv,node_modules
	@echo "✅ Formatting complete"

# Clean
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "✅ Clean complete"

# Install
install: build
	@echo "📦 Installing CoolBits.ai..."
	pip install -e .
	@echo "✅ Installation complete"

# Development
dev:
	@echo "🚀 Starting development server..."
	python coolbits_main_dashboard.py

# Start production services
start:
	@echo "🚀 Starting CoolBits.ai services..."
	pwsh scripts/autostart.ps1 -Action start

# Stop all services
stop:
	@echo "🛑 Stopping CoolBits.ai services..."
	pwsh scripts/autostart.ps1 -Action stop

# Health check
health:
	@echo "🏥 Checking system health..."
	pwsh scripts/doctor.ps1

# Release
release:
	@echo "🚀 Creating release..."
	python scripts/release.py $(VERSION)
	@echo "✅ Release $(VERSION) created"

# Docker build
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t coolbits-ai:latest .
	@echo "✅ Docker image built"

# Docker run
docker-run:
	@echo "🐳 Running Docker container..."
	docker run -p 8080:8080 -p 8100:8100 coolbits-ai:latest

# Generate SBOM
sbom:
	@echo "📋 Generating SBOM..."
	python scripts/generate_sbom.py
	@echo "✅ SBOM generated"

# Verify release readiness
verify:
	@echo "🔍 Verifying release readiness..."
	python scripts/release.py --verify-only
	@echo "✅ Release verification complete"

# Development workflow
dev-setup: install
	@echo "🛠️  Setting up development environment..."
	mkdir -p logs
	touch logs/boot-health.log
	@echo "✅ Development setup complete"

# Production deployment
deploy: build test lint verify
	@echo "🚀 Deploying to production..."
	pwsh scripts/autostart.ps1 -Action start
	@echo "✅ Deployment complete"

# Full CI pipeline
ci: clean build test lint format verify
	@echo "🔄 CI pipeline complete"

# Quick start for new developers
quickstart: dev-setup
	@echo "⚡ Quick start complete!"
	@echo "Run 'make dev' to start development server"
	@echo "Run 'make health' to check system status"