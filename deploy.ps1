# CoolBits.ai Deployment Scripts for Windows PowerShell
# =====================================================

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("staging", "canary", "promote", "rollback", "health")]
    [string]$Action,
    
    [Parameter(Mandatory=$false)]
    [string]$Version = "10"
)

# Configuration
$PROJECT_ID = "coolbits-ai"
$REGION = "europe-west1"
$SERVICE_NAME = "coolbits"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"

# Functions
function Log-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor $Blue
}

function Log-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $Green
}

function Log-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor $Yellow
}

function Log-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $Red
}

# Build and push Docker image
function Build-AndPush {
    param([string]$Tag)
    
    Log-Info "Building Docker image with tag: $Tag"
    
    try {
        docker build -t "$IMAGE_NAME`:$Tag" .
        docker push "$IMAGE_NAME`:$Tag"
        Log-Success "Image built and pushed: $IMAGE_NAME`:$Tag"
    } catch {
        Log-Error "Failed to build/push image: $_"
        throw
    }
}

# Deploy to staging
function Deploy-Staging {
    Log-Info "Deploying to staging environment..."
    
    try {
        # Build staging image
        Build-AndPush "staging"
        
        # Deploy to Cloud Run
        gcloud run deploy "$SERVICE_NAME-staging" `
            --image="$IMAGE_NAME`:staging" `
            --platform=managed `
            --region=$REGION `
            --allow-unauthenticated `
            --port=8501 `
            --memory=2Gi `
            --cpu=1 `
            --min-instances=1 `
            --max-instances=10 `
            --set-env-vars="OPIPE_ENV=staging" `
            --project=$PROJECT_ID
        
        Log-Success "Staging deployment completed"
    } catch {
        Log-Error "Staging deployment failed: $_"
        throw
    }
}

# Deploy canary
function Deploy-Canary {
    param([string]$CanaryPercentage = "10")
    
    Log-Info "Deploying canary with $CanaryPercentage% traffic..."
    
    try {
        # Build canary image
        Build-AndPush "canary"
        
        # Deploy canary service
        gcloud run deploy "$SERVICE_NAME-canary" `
            --image="$IMAGE_NAME`:canary" `
            --platform=managed `
            --region=$REGION `
            --allow-unauthenticated `
            --port=8501 `
            --memory=2Gi `
            --cpu=1 `
            --min-instances=1 `
            --max-instances=5 `
            --set-env-vars="OPIPE_ENV=canary" `
            --project=$PROJECT_ID
        
        # Update traffic split
        gcloud run services update-traffic "$SERVICE_NAME-production" `
            --to-latest `
            --platform=managed `
            --region=$REGION `
            --project=$PROJECT_ID
        
        Log-Success "Canary deployment completed with $CanaryPercentage% traffic"
    } catch {
        Log-Error "Canary deployment failed: $_"
        throw
    }
}

# Promote canary to production
function Promote-Canary {
    Log-Info "Promoting canary to production..."
    
    try {
        # Build production image from canary
        Build-AndPush "production"
        
        # Deploy to production
        gcloud run deploy "$SERVICE_NAME-production" `
            --image="$IMAGE_NAME`:production" `
            --platform=managed `
            --region=$REGION `
            --allow-unauthenticated `
            --port=8501 `
            --memory=4Gi `
            --cpu=2 `
            --min-instances=2 `
            --max-instances=50 `
            --set-env-vars="OPIPE_ENV=production" `
            --project=$PROJECT_ID
        
        # Update traffic to 100% production
        gcloud run services update-traffic "$SERVICE_NAME-production" `
            --to-latest `
            --platform=managed `
            --region=$REGION `
            --project=$PROJECT_ID
        
        Log-Success "Canary promoted to production"
    } catch {
        Log-Error "Canary promotion failed: $_"
        throw
    }
}

# Rollback to previous version
function Rollback-ToVersion {
    param([string]$TargetVersion)
    
    Log-Info "Rolling back to version: $TargetVersion"
    
    try {
        # Deploy previous version
        gcloud run deploy "$SERVICE_NAME-production" `
            --image="$IMAGE_NAME`:$TargetVersion" `
            --platform=managed `
            --region=$REGION `
            --allow-unauthenticated `
            --port=8501 `
            --memory=4Gi `
            --cpu=2 `
            --min-instances=2 `
            --max-instances=50 `
            --set-env-vars="OPIPE_ENV=production" `
            --project=$PROJECT_ID
        
        Log-Success "Rollback to $TargetVersion completed"
    } catch {
        Log-Error "Rollback failed: $_"
        throw
    }
}

# Health check
function Test-Health {
    param([string]$ServiceUrl)
    
    Log-Info "Performing health check on: $ServiceUrl"
    
    $maxAttempts = 30
    $attempt = 1
    
    while ($attempt -le $maxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri "$ServiceUrl/_stcore/health" -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Log-Success "Health check passed"
                return $true
            }
        } catch {
            Log-Warning "Health check attempt $attempt/$maxAttempts failed"
            Start-Sleep -Seconds 10
            $attempt++
        }
    }
    
    Log-Error "Health check failed after $maxAttempts attempts"
    return $false
}

# Get service URL
function Get-ServiceUrl {
    param([string]$ServiceName)
    
    try {
        $url = gcloud run services describe $ServiceName `
            --platform=managed `
            --region=$REGION `
            --project=$PROJECT_ID `
            --format="value(status.url)"
        return $url
    } catch {
        Log-Error "Failed to get service URL for $ServiceName"
        throw
    }
}

# Main script execution
Write-Host "🚀 CoolBits.ai Deployment Script" -ForegroundColor $Green
Write-Host "=================================" -ForegroundColor $Green

try {
    switch ($Action) {
        "staging" {
            Deploy-Staging
            $stagingUrl = Get-ServiceUrl "$SERVICE_NAME-staging"
            Test-Health $stagingUrl
        }
        "canary" {
            Deploy-Canary $Version
            $canaryUrl = Get-ServiceUrl "$SERVICE_NAME-canary"
            Test-Health $canaryUrl
        }
        "promote" {
            Promote-Canary
            $prodUrl = Get-ServiceUrl "$SERVICE_NAME-production"
            Test-Health $prodUrl
        }
        "rollback" {
            if (-not $Version -or $Version -eq "10") {
                Log-Error "Please specify target version for rollback"
                exit 1
            }
            Rollback-ToVersion $Version
            $prodUrl = Get-ServiceUrl "$SERVICE_NAME-production"
            Test-Health $prodUrl
        }
        "health" {
            $serviceUrl = Get-ServiceUrl "$SERVICE_NAME-production"
            Test-Health $serviceUrl
        }
    }
    
    Log-Success "Deployment operation completed successfully!"
    
} catch {
    Log-Error "Deployment operation failed: $_"
    exit 1
}
