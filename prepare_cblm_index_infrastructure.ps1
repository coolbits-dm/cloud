# Prepare cblm-index Infrastructure
# Creates Index Endpoint and prepares for cblm-index integration

param(
    [string]$ProjectId = "coolbits-ai",
    [string]$ProjectNumber = "271190369805",
    [string]$Location = "europe-west3"
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

# Function to create Index Endpoint for cblm-index
function Create-CblmIndexEndpoint {
    param([string]$AccessToken)
    
    Write-Processing "Creating Index Endpoint for cblm-index..."
    
    $url = "https://${Location}-aiplatform.googleapis.com/v1/projects/${ProjectId}/locations/${Location}/indexEndpoints"
    
    $body = @{
        displayName = "cblm-index Endpoint"
        description = "Index endpoint for cblm-index Vector Search system"
        network = "projects/${ProjectNumber}/global/networks/default"
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

# Function to check existing buckets
function Check-ExistingBuckets {
    param([string]$AccessToken)
    
    Write-Processing "Checking existing buckets for cblm-index integration..."
    
    $url = "https://storage.googleapis.com/storage/v1/b"
    $params = "?project=${ProjectId}"
    
    try {
        $response = Invoke-RestMethod -Uri "${url}${params}" -Method Get -Headers @{
            "Authorization" = "Bearer $AccessToken"
            "Content-Type" = "application/json"
        } -ErrorAction Stop
        
        if ($response.items) {
            $cblmBuckets = $response.items | Where-Object { $_.name -like "*cblm*" }
            if ($cblmBuckets) {
                Write-Success "Found $($cblmBuckets.Count) cblm-related buckets:"
                foreach ($bucket in $cblmBuckets) {
                    Write-Host "  - Name: $($bucket.name)" -ForegroundColor $Green
                    Write-Host "    Location: $($bucket.location)" -ForegroundColor $Cyan
                    Write-Host "    Created: $($bucket.timeCreated)" -ForegroundColor $Blue
                    Write-Host ""
                }
            } else {
                Write-Warning "No cblm-related buckets found."
            }
        } else {
            Write-Warning "No buckets found."
        }
        
        return $cblmBuckets
    } catch {
        Write-Error "Error checking buckets: $($_.Exception.Message)"
        return $null
    }
}

# Main execution
function Main {
    Write-Status "Starting cblm-index infrastructure preparation..."
    Write-Status "Project: $ProjectId (Number: $ProjectNumber)"
    Write-Status "Location: $Location"
    Write-Status ""

    $accessToken = Get-AccessToken
    if (-not $accessToken) {
        Write-Error "Cannot proceed without an access token."
        return
    }

    # Check existing buckets
    $cblmBuckets = Check-ExistingBuckets -AccessToken $accessToken

    # Create Index Endpoint for cblm-index
    Write-Status ""
    Write-Status "Creating Index Endpoint for cblm-index..."
    $endpointName = Create-CblmIndexEndpoint -AccessToken $accessToken
    
    if ($endpointName) {
        Write-Success "Successfully created Index Endpoint for cblm-index"
    } else {
        Write-Warning "Failed to create Index Endpoint for cblm-index"
    }

    Write-Status ""
    Write-Status "==========================================================="
    Write-Status "=== INFRASTRUCTURE PREPARATION SUMMARY ==="
    Write-Status "==========================================================="
    
    $bucketCount = if ($cblmBuckets) { $cblmBuckets.Count } else { 0 }
    $endpointCreated = if ($endpointName) { "Yes" } else { "No" }
    
    Write-Host "cblm-index region ($Location):" -ForegroundColor $Cyan
    Write-Host "  - Related Buckets: $bucketCount" -ForegroundColor $Blue
    Write-Host "  - Index Endpoint Created: $endpointCreated" -ForegroundColor $Blue

    Write-Status ""
    Write-Status "INTEGRATION WITH EXISTING INFRASTRUCTURE:"
    Write-Status "=========================================="
    Write-Host "• cblm-index will work alongside existing RAG indexes" -ForegroundColor $Green
    Write-Host "• cblm-search app can query both cblm-index and industry-specific indexes" -ForegroundColor $Green
    Write-Host "• Agent Garden can orchestrate queries across all regions" -ForegroundColor $Green
    Write-Host "• Agent Engine can provide unified search capabilities" -ForegroundColor $Green
    Write-Host "• Multi-region RAG system for redundancy and performance" -ForegroundColor $Green

    Write-Status ""
    Write-Status "NEXT STEPS:"
    Write-Status "==========="
    Write-Host "1. Wait for cblm-index to finish loading (Creating → Ready)" -ForegroundColor $Yellow
    Write-Host "2. Deploy cblm-index to its endpoint" -ForegroundColor $Green
    Write-Host "3. Upload documents to cblm-search bucket" -ForegroundColor $Green
    Write-Host "4. Test vector search queries" -ForegroundColor $Green
    Write-Host "5. Integrate with Agent Garden and Agent Engine" -ForegroundColor $Green
    Write-Host "6. Configure unified RAG system across regions" -ForegroundColor $Green

    Write-Status ""
    Write-Status "DEPLOYMENT COMMANDS:"
    Write-Status "==================="
    Write-Host "After cblm-index is ready, deploy it to endpoint:" -ForegroundColor $Cyan
    Write-Host "gcloud ai index-endpoints deploy-index INDEX_ENDPOINT_ID --index=4844448231981056000 --deployed-index-id=cblm-index-deployed --project=coolbits-ai --region=europe-west3" -ForegroundColor $Yellow
}

# Run the main function
Main
