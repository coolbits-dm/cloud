# Check Ray Cluster Status
# Verifies the status of the cblm-cluster Ray on Vertex AI

param(
    [string]$ProjectId = "coolbits-ai",
    [string]$Location = "europe-west3",
    [string]$ClusterName = "cblm-cluster"
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"
$Cyan = "Cyan"

function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

function Write-Processing {
    param([string]$Message)
    Write-Host "[PROCESSING] $Message" -ForegroundColor $Cyan
}

# Function to get access token
function Get-AccessToken {
    Write-Processing "Getting access token..."
    try {
        $token = (gcloud auth print-access-token | Out-String).Trim()
        if ([string]::IsNullOrEmpty($token)) {
            Write-Error "Failed to get access token. Please ensure gcloud is authenticated."
            return $null
        }
        Write-Success "Access token retrieved."
        return $token
    } catch {
        Write-Error "Error getting access token: $($_.Exception.Message)"
        return $null
    }
}

# Function to check Ray cluster status
function Get-RayClusterStatus {
    param([string]$AccessToken)

    Write-Processing "Checking Ray cluster status..."

    $url = "https://${Location}-aiplatform.googleapis.com/v1/projects/${ProjectId}/locations/${Location}/rayClusters/${ClusterName}"
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Get -Headers @{
            "Authorization" = "Bearer $AccessToken"
            "Content-Type" = "application/json"
        } -ErrorAction Stop

        Write-Success "✅ Ray cluster information retrieved successfully!"
        return $response
    } catch {
        Write-Error "Error getting Ray cluster status: $($_.Exception.Message)"
        if ($_.Exception.Response) {
            $errorResponse = $_.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($errorResponse)
            $responseBody = $reader.ReadToEnd()
            Write-Error "HTTP Status: $($_.Exception.Response.StatusCode)"
            Write-Error "Error details: $responseBody"
        }
        return $null
    }
}

# Function to list all Ray clusters
function Get-AllRayClusters {
    param([string]$AccessToken)

    Write-Processing "Listing all Ray clusters..."

    $url = "https://${Location}-aiplatform.googleapis.com/v1/projects/${ProjectId}/locations/${Location}/rayClusters"
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Get -Headers @{
            "Authorization" = "Bearer $AccessToken"
            "Content-Type" = "application/json"
        } -ErrorAction Stop

        Write-Success "✅ Ray clusters list retrieved successfully!"
        return $response
    } catch {
        Write-Error "Error getting Ray clusters list: $($_.Exception.Message)"
        return $null
    }
}

# Main execution
function Main {
    Write-Status "Checking Ray on Vertex AI cluster status..."
    Write-Status "Project: $ProjectId"
    Write-Status "Location: $Location"
    Write-Status "Cluster: $ClusterName"
    Write-Status ""

    $accessToken = Get-AccessToken
    if (-not $accessToken) {
        Write-Error "Cannot proceed without an access token."
        return
    }

    # Get specific cluster status
    $clusterInfo = Get-RayClusterStatus -AccessToken $accessToken
    
    if ($clusterInfo) {
        Write-Success "✅ Ray cluster found!"
        Write-Status ""
        Write-Status "CLUSTER DETAILS:"
        Write-Status "================"
        Write-Host "Name: $($clusterInfo.name)" -ForegroundColor $Cyan
        Write-Host "Display Name: $($clusterInfo.displayName)" -ForegroundColor $Cyan
        Write-Host "State: $($clusterInfo.state)" -ForegroundColor $Green
        Write-Host "Ray Version: $($clusterInfo.rayVersion)" -ForegroundColor $Cyan
        Write-Host "Python Version: $($clusterInfo.pythonVersion)" -ForegroundColor $Cyan
        Write-Host "Description: $($clusterInfo.description)" -ForegroundColor $Cyan
        Write-Host "Created: $($clusterInfo.createTime)" -ForegroundColor $Cyan
        Write-Host "Updated: $($clusterInfo.updateTime)" -ForegroundColor $Cyan
        
        if ($clusterInfo.labels) {
            Write-Host "Labels:" -ForegroundColor $Cyan
            foreach ($label in $clusterInfo.labels.PSObject.Properties) {
                Write-Host "  $($label.Name): $($label.Value)" -ForegroundColor $Yellow
            }
        }
        
        Write-Status ""
        Write-Status "RAY CLUSTER EXPLANATION:"
        Write-Status "========================"
        Write-Host "🎯 Ray is a distributed computing framework for Python" -ForegroundColor $Green
        Write-Host "🚀 Enables parallel processing of AI/ML workloads" -ForegroundColor $Green
        Write-Host "⚡ Scales Python applications across multiple nodes" -ForegroundColor $Green
        Write-Host "🔧 Integrates with Vertex AI for enterprise readiness" -ForegroundColor $Green
        Write-Host "📊 Provides distributed training and inference" -ForegroundColor $Green
        
        Write-Status ""
        Write-Status "USE CASES FOR YOUR PROJECT:"
        Write-Status "=========================="
        Write-Host "• Parallel RAG processing across multiple documents" -ForegroundColor $Cyan
        Write-Host "• Distributed vector embedding generation" -ForegroundColor $Cyan
        Write-Host "• Scalable document processing and indexing" -ForegroundColor $Cyan
        Write-Host "• Multi-node AI model training and inference" -ForegroundColor $Cyan
        Write-Host "• Parallel API request processing" -ForegroundColor $Cyan
        Write-Host "• Distributed data processing pipelines" -ForegroundColor $Cyan
        
        Write-Status ""
        Write-Status "INTEGRATION WITH EXISTING INFRASTRUCTURE:"
        Write-Status "========================================="
        Write-Host "• Works with Vector Search indexes" -ForegroundColor $Green
        Write-Host "• Integrates with Discovery Engine" -ForegroundColor $Green
        Write-Host "• Connects to Cloud Storage buckets" -ForegroundColor $Green
        Write-Host "• Scales ogpt-bridge-service workloads" -ForegroundColor $Green
        Write-Host "• Enhances cblm-search app performance" -ForegroundColor $Green
        
    } else {
        Write-Warning "Could not retrieve specific cluster info. Trying to list all clusters..."
        
        $allClusters = Get-AllRayClusters -AccessToken $accessToken
        if ($allClusters -and $allClusters.rayClusters) {
            Write-Success "Found $($allClusters.rayClusters.Count) Ray clusters:"
            foreach ($cluster in $allClusters.rayClusters) {
                Write-Host "• $($cluster.displayName) - $($cluster.state)" -ForegroundColor $Cyan
            }
        }
    }

    Write-Status ""
    Write-Status "NEXT STEPS:"
    Write-Status "==========="
    Write-Host "1. Wait for cluster to finish provisioning" -ForegroundColor $Green
    Write-Host "2. Connect to Ray dashboard for monitoring" -ForegroundColor $Green
    Write-Host "3. Deploy distributed workloads to the cluster" -ForegroundColor $Green
    Write-Host "4. Integrate with existing RAG infrastructure" -ForegroundColor $Green
    Write-Host "5. Scale document processing and AI workloads" -ForegroundColor $Green
}

# Run the main function
Main
