#!/bin/bash

# CoolBits.ai Deployment Scripts
# ===============================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="coolbits-ai"
REGION="europe-west1"
SERVICE_NAME="coolbits"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Build and push Docker image
build_and_push() {
    local tag=$1
    log_info "Building Docker image with tag: ${tag}"
    
    docker build -t "${IMAGE_NAME}:${tag}" .
    docker push "${IMAGE_NAME}:${tag}"
    
    log_success "Image built and pushed: ${IMAGE_NAME}:${tag}"
}

# Deploy to staging
deploy_staging() {
    log_info "Deploying to staging environment..."
    
    # Build staging image
    build_and_push "staging"
    
    # Deploy to Cloud Run
    gcloud run deploy "${SERVICE_NAME}-staging" \
        --image="${IMAGE_NAME}:staging" \
        --platform=managed \
        --region="${REGION}" \
        --allow-unauthenticated \
        --port=8501 \
        --memory=2Gi \
        --cpu=1 \
        --min-instances=1 \
        --max-instances=10 \
        --set-env-vars="OPIPE_ENV=staging" \
        --project="${PROJECT_ID}"
    
    log_success "Staging deployment completed"
}

# Deploy canary
deploy_canary() {
    local canary_percentage=${1:-10}
    log_info "Deploying canary with ${canary_percentage}% traffic..."
    
    # Build canary image
    build_and_push "canary"
    
    # Deploy canary service
    gcloud run deploy "${SERVICE_NAME}-canary" \
        --image="${IMAGE_NAME}:canary" \
        --platform=managed \
        --region="${REGION}" \
        --allow-unauthenticated \
        --port=8501 \
        --memory=2Gi \
        --cpu=1 \
        --min-instances=1 \
        --max-instances=5 \
        --set-env-vars="OPIPE_ENV=canary" \
        --project="${PROJECT_ID}"
    
    # Update traffic split
    gcloud run services update-traffic "${SERVICE_NAME}-production" \
        --to-latest \
        --platform=managed \
        --region="${REGION}" \
        --project="${PROJECT_ID}"
    
    log_success "Canary deployment completed with ${canary_percentage}% traffic"
}

# Promote canary to production
promote_canary() {
    log_info "Promoting canary to production..."
    
    # Build production image from canary
    build_and_push "production"
    
    # Deploy to production
    gcloud run deploy "${SERVICE_NAME}-production" \
        --image="${IMAGE_NAME}:production" \
        --platform=managed \
        --region="${REGION}" \
        --allow-unauthenticated \
        --port=8501 \
        --memory=4Gi \
        --cpu=2 \
        --min-instances=2 \
        --max-instances=50 \
        --set-env-vars="OPIPE_ENV=production" \
        --project="${PROJECT_ID}"
    
    # Update traffic to 100% production
    gcloud run services update-traffic "${SERVICE_NAME}-production" \
        --to-latest \
        --platform=managed \
        --region="${REGION}" \
        --project="${PROJECT_ID}"
    
    log_success "Canary promoted to production"
}

# Rollback to previous version
rollback() {
    local target_version=$1
    log_info "Rolling back to version: ${target_version}"
    
    # Deploy previous version
    gcloud run deploy "${SERVICE_NAME}-production" \
        --image="${IMAGE_NAME}:${target_version}" \
        --platform=managed \
        --region="${REGION}" \
        --allow-unauthenticated \
        --port=8501 \
        --memory=4Gi \
        --cpu=2 \
        --min-instances=2 \
        --max-instances=50 \
        --set-env-vars="OPIPE_ENV=production" \
        --project="${PROJECT_ID}"
    
    log_success "Rollback to ${target_version} completed"
}

# Health check
health_check() {
    local service_url=$1
    log_info "Performing health check on: ${service_url}"
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "${service_url}/_stcore/health" > /dev/null; then
            log_success "Health check passed"
            return 0
        fi
        
        log_warning "Health check attempt ${attempt}/${max_attempts} failed"
        sleep 10
        ((attempt++))
    done
    
    log_error "Health check failed after ${max_attempts} attempts"
    return 1
}

# Get service URL
get_service_url() {
    local service_name=$1
    gcloud run services describe "${service_name}" \
        --platform=managed \
        --region="${REGION}" \
        --project="${PROJECT_ID}" \
        --format="value(status.url)"
}

# Main script
case "$1" in
    "staging")
        deploy_staging
        STAGING_URL=$(get_service_url "${SERVICE_NAME}-staging")
        health_check "${STAGING_URL}"
        ;;
    "canary")
        deploy_canary "$2"
        CANARY_URL=$(get_service_url "${SERVICE_NAME}-canary")
        health_check "${CANARY_URL}"
        ;;
    "promote")
        promote_canary
        PROD_URL=$(get_service_url "${SERVICE_NAME}-production")
        health_check "${PROD_URL}"
        ;;
    "rollback")
        rollback "$2"
        PROD_URL=$(get_service_url "${SERVICE_NAME}-production")
        health_check "${PROD_URL}"
        ;;
    "health")
        SERVICE_URL=$(get_service_url "${SERVICE_NAME}-production")
        health_check "${SERVICE_URL}"
        ;;
    *)
        echo "Usage: $0 {staging|canary|promote|rollback|health}"
        echo "  staging   - Deploy to staging environment"
        echo "  canary    - Deploy canary with optional percentage (default: 10%)"
        echo "  promote   - Promote canary to production"
        echo "  rollback  - Rollback to specific version"
        echo "  health    - Check production health"
        exit 1
        ;;
esac
