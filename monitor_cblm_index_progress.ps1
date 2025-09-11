# Monitor cblm-index Creation Progress
# Monitors the creation progress of cblm-index and other Vector Search components

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

# Function to check operations status
function Check-OperationsStatus {
    param([string]$Location, [string]$AccessToken)
    
    Write-Processing "Checking operations status in ${Location}..."
    
    $url = "https://${Location}-aiplatform.googleapis.com/v1/projects/${ProjectId}/locations/${Location}/operations"
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Get -Headers @{
            "Authorization" = "Bearer $AccessToken"
            "Content-Type" = "application/json"
        } -ErrorAction Stop
        
        if ($response.operations) {
            $indexOperations = $response.operations | Where-Object { 
                $_.metadata.operationType -eq "CREATE_INDEX" -or 
                $_.metadata.operationType -eq "CREATE_INDEX_ENDPOINT" 
            }
            
            if ($indexOperations) {
                Write-Success "Found $($indexOperations.Count) Vector Search operations in ${Location}:"
                foreach ($op in $indexOperations) {
                    $status = if ($op.done) { "COMPLETED" } else { "IN_PROGRESS" }
                    $color = if ($op.done) { $Green } else { $Yellow }
                    Write-Host "  - Operation: $($op.metadata.operationType)" -ForegroundColor $Cyan
                    Write-Host "    Status: $status" -ForegroundColor $color
                    Write-Host "    Name: $($op.name)" -ForegroundColor $Blue
                    if ($op.metadata) {
                        Write-Host "    Resource: $($op.metadata.genericMetadata.resourceName)" -ForegroundColor $Blue
                    }
                    Write-Host ""
                }
            } else {
                Write-Warning "No Vector Search operations found in ${Location}."
            }
        } else {
            Write-Warning "No operations found in ${Location}."
        }
        
        return $indexOperations
    } catch {
        Write-Error "Error checking operations in ${Location}: $($_.Exception.Message)"
        return $null
    }
}

# Function to check specific index status
function Check-SpecificIndexStatus {
    param([string]$IndexId, [string]$Location, [string]$AccessToken)
    
    Write-Processing "Checking specific index status: $IndexId"
    
    $url = "https://${Location}-aiplatform.googleapis.com/v1/projects/${ProjectId}/locations/${Location}/indexes/${IndexId}"
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Get -Headers @{
            "Authorization" = "Bearer $AccessToken"
            "Content-Type" = "application/json"
        } -ErrorAction Stop
        
        Write-Success "Index Status Details:"
        Write-Host "  - Name: $($response.displayName)" -ForegroundColor $Green
        Write-Host "  - State: $($response.state)" -ForegroundColor $Yellow
        Write-Host "  - Create Time: $($response.createTime)" -ForegroundColor $Blue
        Write-Host "  - Update Time: $($response.updateTime)" -ForegroundColor $Blue
        if ($response.metadata) {
            Write-Host "  - Dimensions: $($response.metadata.config.dimensions)" -ForegroundColor $Cyan
            Write-Host "  - Distance Measure: $($response.metadata.config.distanceMeasureType)" -ForegroundColor $Cyan
        }
        
        return $response
    } catch {
        Write-Error "Error checking index $IndexId`: $($_.Exception.Message)"
        return $null
    }
}

# Main execution
function Main {
    Write-Status "Starting cblm-index progress monitoring..."
    Write-Status "Project: $ProjectId"
    Write-Status "cblm-index Location: $CblmIndexLocation"
    Write-Status "Existing indexes Location: $ExistingIndexLocation"
    Write-Status ""

    $accessToken = Get-AccessToken
    if (-not $accessToken) {
        Write-Error "Cannot proceed without an access token."
        return
    }

    # Check operations in both regions
    Write-Status "Checking Vector Search operations status..."
    Write-Status ""
    
    $cblmOperations = Check-OperationsStatus -Location $CblmIndexLocation -AccessToken $accessToken
    $existingOperations = Check-OperationsStatus -Location $ExistingIndexLocation -AccessToken $accessToken

    # Check specific cblm-index status if we have the ID
    if ($cblmOperations) {
        Write-Status ""
        Write-Status "Checking specific cblm-index status..."
        $cblmIndexId = "4844448231981056000"  # From your screenshot
        $indexStatus = Check-SpecificIndexStatus -IndexId $cblmIndexId -Location $CblmIndexLocation -AccessToken $accessToken
    }

    Write-Status ""
    Write-Status "==========================================================="
    Write-Status "=== PROGRESS SUMMARY ==="
    Write-Status "==========================================================="
    
    $cblmOpCount = if ($cblmOperations) { $cblmOperations.Count } else { 0 }
    $existingOpCount = if ($existingOperations) { $existingOperations.Count } else { 0 }
    
    Write-Host "cblm-index region ($CblmIndexLocation):" -ForegroundColor $Cyan
    Write-Host "  - Active Operations: $cblmOpCount" -ForegroundColor $Blue
    
    Write-Host "Existing RAG region ($ExistingIndexLocation):" -ForegroundColor $Cyan
    Write-Host "  - Active Operations: $existingOpCount" -ForegroundColor $Blue

    Write-Status ""
    Write-Status "NEXT STEPS:"
    Write-Status "==========="
    Write-Host "1. Wait for cblm-index to finish loading (Creating → Ready)" -ForegroundColor $Yellow
    Write-Host "2. Wait for existing indexes to finish creating" -ForegroundColor $Yellow
    Write-Host "3. Create Index Endpoints for cblm-index" -ForegroundColor $Green
    Write-Host "4. Deploy indexes to endpoints" -ForegroundColor $Green
    Write-Host "5. Upload documents to buckets" -ForegroundColor $Green
    Write-Host "6. Test vector search queries" -ForegroundColor $Green
    Write-Host "7. Integrate with Agent Garden and Agent Engine" -ForegroundColor $Green

    Write-Status ""
    Write-Status "MONITORING COMMANDS:"
    Write-Status "==================="
    Write-Host "To monitor progress manually:" -ForegroundColor $Cyan
    Write-Host "gcloud ai indexes list --project=coolbits-ai --region=europe-west3" -ForegroundColor $Yellow
    Write-Host "gcloud ai indexes list --project=coolbits-ai --region=europe-west4" -ForegroundColor $Yellow
    Write-Host "gcloud ai index-endpoints list --project=coolbits-ai --region=europe-west3" -ForegroundColor $Yellow
    Write-Host "gcloud ai index-endpoints list --project=coolbits-ai --region=europe-west4" -ForegroundColor $Yellow
}

# Run the main function
Main
