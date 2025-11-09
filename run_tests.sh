# CoolBits.ai Test Scripts
# ========================

#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 CoolBits.ai Test Suite${NC}"
echo "================================"

# Function to run Python tests
run_python_tests() {
    echo -e "${YELLOW}📝 Running Python tests...${NC}"
    
    # Install test dependencies
    pip install pytest pytest-cov pytest-mock black isort flake8 mypy
    
    # Run linting
    echo -e "${YELLOW}🔍 Running Python linting...${NC}"
    black --check --diff . || echo -e "${RED}❌ Black formatting issues found${NC}"
    isort --check-only --diff . || echo -e "${RED}❌ Import sorting issues found${NC}"
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || echo -e "${RED}❌ Flake8 issues found${NC}"
    
    # Run type checking
    echo -e "${YELLOW}🔍 Running type checking...${NC}"
    mypy . --ignore-missing-imports || echo -e "${RED}❌ Type checking issues found${NC}"
    
    # Run unit tests
    echo -e "${YELLOW}🧪 Running Python unit tests...${NC}"
    pytest tests/unit/ --cov=. --cov-report=xml --cov-report=html || echo -e "${RED}❌ Python tests failed${NC}"
    
    echo -e "${GREEN}✅ Python tests completed${NC}"
}

# Function to run Node.js tests
run_node_tests() {
    echo -e "${YELLOW}📝 Running Node.js tests...${NC}"
    
    # Install dependencies
    npm install
    
    # Install dev dependencies
    npm install --save-dev eslint prettier jest @types/jest
    
    # Run linting
    echo -e "${YELLOW}🔍 Running Node.js linting...${NC}"
    npx eslint . --ext .js,.ts,.jsx,.tsx || echo -e "${RED}❌ ESLint issues found${NC}"
    npx prettier --check . || echo -e "${RED}❌ Prettier formatting issues found${NC}"
    
    # Run tests
    echo -e "${YELLOW}🧪 Running Node.js tests...${NC}"
    npm test || echo -e "${RED}❌ Node.js tests failed${NC}"
    
    echo -e "${GREEN}✅ Node.js tests completed${NC}"
}

# Function to run E2E tests
run_e2e_tests() {
    echo -e "${YELLOW}📝 Running E2E tests...${NC}"
    
    # Install Playwright
    pip install playwright
    npx playwright install --with-deps
    
    # Start application
    echo -e "${YELLOW}🚀 Starting application for E2E tests...${NC}"
    python -m streamlit run coolbits_web_app.py --server.port=8501 &
    APP_PID=$!
    
    # Wait for app to start
    sleep 10
    
    # Run E2E tests
    echo -e "${YELLOW}🧪 Running E2E tests...${NC}"
    pytest tests/e2e/ --browser chromium --browser webkit || echo -e "${RED}❌ E2E tests failed${NC}"
    
    # Stop application
    kill $APP_PID
    
    echo -e "${GREEN}✅ E2E tests completed${NC}"
}

# Function to run Docker tests
run_docker_tests() {
    echo -e "${YELLOW}📝 Running Docker tests...${NC}"
    
    # Build Docker image
    echo -e "${YELLOW}🔨 Building Docker image...${NC}"
    docker build -t coolbits-test:latest . || echo -e "${RED}❌ Docker build failed${NC}"
    
    # Test Docker image
    echo -e "${YELLOW}🧪 Testing Docker image...${NC}"
    docker run --rm -d --name coolbits-test -p 8501:8501 coolbits-test:latest || echo -e "${RED}❌ Docker run failed${NC}"
    
    # Wait for container to start
    sleep 30
    
    # Test health endpoint
    curl -f http://localhost:8501/_stcore/health || echo -e "${RED}❌ Health check failed${NC}"
    
    # Stop container
    docker stop coolbits-test
    
    echo -e "${GREEN}✅ Docker tests completed${NC}"
}

# Main execution
case "$1" in
    "python")
        run_python_tests
        ;;
    "node")
        run_node_tests
        ;;
    "e2e")
        run_e2e_tests
        ;;
    "docker")
        run_docker_tests
        ;;
    "all")
        run_python_tests
        run_node_tests
        run_e2e_tests
        run_docker_tests
        ;;
    *)
        echo "Usage: $0 {python|node|e2e|docker|all}"
        echo "  python  - Run Python tests and linting"
        echo "  node    - Run Node.js tests and linting"
        echo "  e2e     - Run end-to-end tests"
        echo "  docker  - Run Docker tests"
        echo "  all     - Run all tests"
        exit 1
        ;;
esac

echo -e "${GREEN}🎉 Test suite completed!${NC}"
