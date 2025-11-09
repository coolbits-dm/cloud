# Integration Script for cblm-index with existing RAG infrastructure
# Integrates the new cblm-index with Vector Search and Discovery Engine

param(
    [string]$ProjectId = "coolbits-ai",
    [string]$CblmIndexLocation = "europe-west3",
    [string]$ExistingIndexLocation = "europe-west4"
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

# Function to check Vector Search indexes status
function Check-VectorSearchIndexes {
    param([string]$Location, [string]$AccessToken)
    
    Write-Processing "Checking Vector Search indexes in $Location..."
    
    $url = "https://${Location}-aiplatform.googleapis.com/v1/projects/${ProjectId}/locations/${Location}/indexes"
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Get -Headers @{
            "Authorization" = "Bearer $AccessToken"
            "Content-Type" = "application/json"
        } -ErrorAction Stop
        
        if ($response.indexes) {
            Write-Success "Found $($response.indexes.Count) Vector Search indexes in ${Location}:"
            foreach ($index in $response.indexes) {
                Write-Host "  - Name: $($index.displayName)" -ForegroundColor $Green
                Write-Host "    ID: $($index.name)" -ForegroundColor $Cyan
                Write-Host "    State: $($index.state)" -ForegroundColor $Yellow
                Write-Host "    Create Time: $($index.createTime)" -ForegroundColor $Blue
                Write-Host ""
            }
        } else {
            Write-Warning "No Vector Search indexes found in $Location."
        }
        
        return $response.indexes
    } catch {
        Write-Error "Error checking Vector Search indexes in $Location`: $($_.Exception.Message)"
        return $null
    }
}

# Function to check Index Endpoints status
function Check-IndexEndpoints {
    param([string]$Location, [string]$AccessToken)
    
    Write-Processing "Checking Index Endpoints in $Location..."
    
    $url = "https://${Location}-aiplatform.googleapis.com/v1/projects/${ProjectId}/locations/${Location}/indexEndpoints"
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Get -Headers @{
            "Authorization" = "Bearer $AccessToken"
            "Content-Type" = "application/json"
        } -ErrorAction Stop
        
        if ($response.indexEndpoints) {
            Write-Success "Found $($response.indexEndpoints.Count) Index Endpoints in ${Location}:"
            foreach ($endpoint in $response.indexEndpoints) {
                Write-Host "  - Name: $($endpoint.displayName)" -ForegroundColor $Green
                Write-Host "    ID: $($endpoint.name)" -ForegroundColor $Cyan
                Write-Host "    State: $($endpoint.state)" -ForegroundColor $Yellow
                Write-Host "    Deployed Indexes: $($endpoint.deployedIndexes.Count)" -ForegroundColor $Blue
                Write-Host ""
            }
        } else {
            Write-Warning "No Index Endpoints found in $Location."
        }
        
        return $response.indexEndpoints
    } catch {
        Write-Error "Error checking Index Endpoints in $Location`: $($_.Exception.Message)"
        return $null
    }
}

# Function to create Index Endpoint for cblm-index
function Create-CblmIndexEndpoint {
    param([string]$AccessToken)
    
    Write-Processing "Creating Index Endpoint for cblm-index..."
    
    $url = "https://${CblmIndexLocation}-aiplatform.googleapis.com/v1/projects/${ProjectId}/locations/${CblmIndexLocation}/indexEndpoints"
    
    $body = @{
        displayName = "cblm-index Endpoint"
        description = "Index endpoint for cblm-index Vector Search system"
        network = "projects/271190369805/global/networks/default"
    } | ConvertTo-Json -Compress
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Post -Headers @{
            "Authorization" = "Bearer $AccessToken"
            "Content-Type" = "application/json"
        } -Body $body -ErrorAction Stop
        
        Write-Success "Index Endpoint for cblm-index created successfully."
        Write-Success "Endpoint name: $($response.name)"
        return $response.name
    } catch {
        Write-Error "Error creating Index Endpoint for cblm-index`: $($_.Exception.Message)"
        return $null
    }
}

# Main execution
function Main {
    Write-Status "Starting cblm-index integration with existing RAG infrastructure..."
    Write-Status "Project: $ProjectId"
    Write-Status "cblm-index Location: $CblmIndexLocation"
    Write-Status "Existing indexes Location: $ExistingIndexLocation"
    Write-Status ""

    $accessToken = Get-AccessToken
    if (-not $accessToken) {
        Write-Error "Cannot proceed without an access token."
        return
    }

    # Check existing infrastructure
    Write-Status "Checking existing Vector Search infrastructure..."
    Write-Status ""
    
    $cblmIndexes = Check-VectorSearchIndexes -Location $CblmIndexLocation -AccessToken $accessToken
    $existingIndexes = Check-VectorSearchIndexes -Location $ExistingIndexLocation -AccessToken $accessToken
    
    $cblmEndpoints = Check-IndexEndpoints -Location $CblmIndexLocation -AccessToken $accessToken
    $existingEndpoints = Check-IndexEndpoints -Location $ExistingIndexLocation -AccessToken $accessToken

    Write-Status ""
    Write-Status "==========================================================="
    Write-Status "=== INFRASTRUCTURE SUMMARY ==="
    Write-Status "==========================================================="
    
    $cblmIndexCount = if ($cblmIndexes) { $cblmIndexes.Count } else { 0 }
    $existingIndexCount = if ($existingIndexes) { $existingIndexes.Count } else { 0 }
    $cblmEndpointCount = if ($cblmEndpoints) { $cblmEndpoints.Count } else { 0 }
    $existingEndpointCount = if ($existingEndpoints) { $existingEndpoints.Count } else { 0 }
    
    Write-Host "cblm-index region ($CblmIndexLocation):" -ForegroundColor $Cyan
    Write-Host "  - Vector Search Indexes: $cblmIndexCount" -ForegroundColor $Blue
    Write-Host "  - Index Endpoints: $cblmEndpointCount" -ForegroundColor $Blue
    
    Write-Host "Existing RAG region ($ExistingIndexLocation):" -ForegroundColor $Cyan
    Write-Host "  - Vector Search Indexes: $existingIndexCount" -ForegroundColor $Blue
    Write-Host "  - Index Endpoints: $existingEndpointCount" -ForegroundColor $Blue

    # Create Index Endpoint for cblm-index if needed
    if ($cblmEndpointCount -eq 0 -and $cblmIndexCount -gt 0) {
        Write-Status ""
        Write-Status "Creating Index Endpoint for cblm-index..."
        $endpointName = Create-CblmIndexEndpoint -AccessToken $accessToken
        if ($endpointName) {
            Write-Success "Successfully created Index Endpoint for cblm-index"
        }
    }

    Write-Status ""
    Write-Status "INTEGRATION POINTS:"
    Write-Status "==================="
    Write-Host "• cblm-index can be integrated with existing cblm-search app" -ForegroundColor $Green
    Write-Host "• Both regions provide Vector Search capabilities" -ForegroundColor $Green
    Write-Host "• Agent Garden can orchestrate indexes from both regions" -ForegroundColor $Green
    Write-Host "• Agent Engine can query indexes from both regions" -ForegroundColor $Green
    Write-Host "• Unified RAG system across multiple regions" -ForegroundColor $Green

    Write-Status ""
    Write-Status "NEXT STEPS:"
    Write-Status "==========="
    Write-Host "1. Wait for cblm-index to finish loading (Creating → Ready)" -ForegroundColor $Yellow
    Write-Host "2. Deploy cblm-index to its endpoint" -ForegroundColor $Green
    Write-Host "3. Upload documents to cblm-search bucket" -ForegroundColor $Green
    Write-Host "4. Test vector search queries" -ForegroundColor $Green
    Write-Host "5. Integrate with Agent Garden and Agent Engine" -ForegroundColor $Green
    Write-Host "6. Configure unified RAG system" -ForegroundColor $Green
}

# Run the main function
Main
