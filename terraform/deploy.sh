# CoolBits.ai Terraform Deployment Scripts
# ========================================

#!/bin/bash
# deploy.sh - Deploy CoolBits infrastructure with Terraform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
PROJECT_ID="coolbits-ai"
REGION="europe-west3"
ENVIRONMENT="production"
TERRAFORM_DIR="terraform"

# Check if required tools are installed
check_dependencies() {
    log_info "Checking dependencies..."
    
    if ! command -v terraform &> /dev/null; then
        log_error "Terraform is not installed. Please install Terraform first."
        exit 1
    fi
    
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI is not installed. Please install gcloud CLI first."
        exit 1
    fi
    
    log_success "All dependencies are installed"
}

# Authenticate with Google Cloud
authenticate_gcloud() {
    log_info "Authenticating with Google Cloud..."
    
    gcloud auth login
    gcloud config set project $PROJECT_ID
    gcloud auth application-default login
    
    log_success "Authenticated with Google Cloud"
}

# Initialize Terraform
init_terraform() {
    log_info "Initializing Terraform..."
    
    cd $TERRAFORM_DIR
    
    # Check if terraform.tfvars exists
    if [ ! -f "terraform.tfvars" ]; then
        log_warning "terraform.tfvars not found. Please copy terraform.tfvars.example and fill in your values."
        exit 1
    fi
    
    terraform init
    terraform validate
    
    log_success "Terraform initialized and validated"
}

# Plan Terraform deployment
plan_terraform() {
    log_info "Planning Terraform deployment..."
    
    terraform plan -out=tfplan
    
    log_success "Terraform plan completed"
}

# Apply Terraform deployment
apply_terraform() {
    log_info "Applying Terraform deployment..."
    
    terraform apply tfplan
    
    log_success "Terraform deployment completed"
}

# Deploy Cloud Run services
deploy_cloud_run() {
    log_info "Deploying Cloud Run services..."
    
    # Build and push Docker image
    docker build -t gcr.io/$PROJECT_ID/coolbits:latest .
    docker push gcr.io/$PROJECT_ID/coolbits:latest
    
    # Deploy to Cloud Run
    gcloud run deploy coolbits-production \
        --image=gcr.io/$PROJECT_ID/coolbits:latest \
        --platform=managed \
        --region=$REGION \
        --allow-unauthenticated \
        --port=8501 \
        --memory=4Gi \
        --cpu=2 \
        --min-instances=2 \
        --max-instances=50 \
        --set-env-vars="OPIPE_ENV=production" \
        --project=$PROJECT_ID
    
    log_success "Cloud Run services deployed"
}

# Configure DNS
configure_dns() {
    log_info "Configuring DNS..."
    
    # Get load balancer IP
    LB_IP=$(terraform output -raw load_balancer_ip)
    
    log_info "Load balancer IP: $LB_IP"
    log_warning "Please configure your DNS records to point to this IP address"
    
    log_success "DNS configuration completed"
}

# Run health checks
health_checks() {
    log_info "Running health checks..."
    
    # Get load balancer URL
    LB_URL=$(terraform output -raw load_balancer_url)
    
    # Wait for services to be ready
    sleep 30
    
    # Check main application
    if curl -f -s "$LB_URL/_stcore/health" > /dev/null; then
        log_success "Main application health check passed"
    else
        log_error "Main application health check failed"
        exit 1
    fi
    
    # Check API
    if curl -f -s "$LB_URL/api/v1/health" > /dev/null; then
        log_success "API health check passed"
    else
        log_error "API health check failed"
        exit 1
    fi
    
    log_success "All health checks passed"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up temporary files..."
    
    if [ -f "tfplan" ]; then
        rm tfplan
    fi
    
    log_success "Cleanup completed"
}

# Main deployment function
main() {
    log_info "Starting CoolBits infrastructure deployment..."
    
    check_dependencies
    authenticate_gcloud
    init_terraform
    plan_terraform
    
    # Ask for confirmation
    read -p "Do you want to proceed with the deployment? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Deployment cancelled"
        exit 0
    fi
    
    apply_terraform
    deploy_cloud_run
    configure_dns
    health_checks
    cleanup
    
    log_success "CoolBits infrastructure deployment completed successfully!"
    
    # Display important information
    echo
    log_info "Important Information:"
    echo "  - Load Balancer IP: $(terraform output -raw load_balancer_ip)"
    echo "  - Load Balancer URL: $(terraform output -raw load_balancer_url)"
    echo "  - Database Connection: $(terraform output -raw db_primary_connection_name)"
    echo "  - Redis Host: $(terraform output -raw redis_host)"
    echo "  - Monitoring Dashboard: $(terraform output -raw dashboard_url)"
    echo
    log_warning "Remember to configure your DNS records and update your application configuration!"
}

# Run main function
main "$@"
