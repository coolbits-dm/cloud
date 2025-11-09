# Index Endpoints Creation Script for CoolBits.ai
# Creates Index Endpoints for serving Vector Search queries

param(
    [string]$ProjectId = "coolbits-ai",
    [string]$Location = "europe-west4"
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

# Function to create Index Endpoint
function Create-IndexEndpoint {
    param(
        [string]$RagId,
        [string]$DisplayName,
        [string]$AccessToken
    )

    Write-Processing "Creating Index Endpoint: $DisplayName"

    $url = "https://${Location}-aiplatform.googleapis.com/v1/projects/${ProjectId}/locations/${Location}/indexEndpoints"
    
    $body = @{
        displayName = "$DisplayName Index Endpoint"
        description = "Index endpoint for $DisplayName RAG system vector search"
        network = "projects/${ProjectId}/global/networks/default"
    } | ConvertTo-Json -Compress

    try {
        $response = Invoke-RestMethod -Uri $url -Method Post -Headers @{
            "Authorization" = "Bearer $AccessToken"
            "Content-Type" = "application/json"
        } -Body $body -ErrorAction Stop

        Write-Success "Index Endpoint '$DisplayName' created successfully."
        Write-Success "Endpoint name: $($response.name)"
        return $response.name
    } catch {
        Write-Error "Error creating Index Endpoint $DisplayName`: $($_.Exception.Message)"
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

# Main execution
function Main {
    Write-Status "Starting Index Endpoints creation for CoolBits.ai..."
    Write-Status "Project: $ProjectId"
    Write-Status "Location: $Location"
    Write-Status ""

    $accessToken = Get-AccessToken
    if (-not $accessToken) {
        Write-Error "Cannot proceed without an access token."
        return
    }

    # RAG systems that have Vector Search indexes
    $ragSystems = @(
        @{Id="ai_board"; Name="AI Board"},
        @{Id="business"; Name="Business AI Council"},
        @{Id="agritech"; Name="AgTech"},
        @{Id="banking"; Name="Banking"},
        @{Id="saas_b2b"; Name="SaaS B2B"},
        @{Id="healthcare"; Name="Healthcare"},
        @{Id="agency"; Name="Agency"},
        @{Id="user"; Name="User"}
    )

    $successCount = 0
    $totalCount = $ragSystems.Count

    Write-Status "Creating Index Endpoints for $totalCount RAG systems..."
    Write-Status ""

    foreach ($rag in $ragSystems) {
        Write-Status "=================================================="
        Write-Status "Processing: $($rag.Name) ($($rag.Id))"
        Write-Status "=================================================="

        # Create Index Endpoint
        $endpointName = Create-IndexEndpoint -RagId $rag.Id -DisplayName $rag.Name -AccessToken $accessToken
        if ($endpointName) {
            Write-Success "Successfully created Index Endpoint for $($rag.Name)"
            $successCount++
        } else {
            Write-Warning "Failed to create Index Endpoint for $($rag.Name)"
        }

        Write-Status ""
    }

    Write-Status "==========================================================="
    Write-Status "=== FINAL SUMMARY ==="
    Write-Status "==========================================================="
    Write-Success "Total RAG systems processed: $totalCount"
    Write-Success "Successful Index Endpoint creations: $successCount"
    Write-Success "Failed creations: $($totalCount - $successCount)"
    
    if ($successCount -eq $totalCount) {
        Write-Success "All Index Endpoints created successfully!"
    } else {
        Write-Warning "Some Index Endpoints had issues - check logs above"
    }

    Write-Status ""
    Write-Status "NEXT STEPS:"
    Write-Status "==========="
    Write-Host "1. Wait for Vector Search indexes to be ready (5-10 minutes)" -ForegroundColor $Yellow
    Write-Host "2. Deploy indexes to endpoints using gcloud CLI" -ForegroundColor $Green
    Write-Host "3. Upload industry-specific documents to buckets" -ForegroundColor $Green
    Write-Host "4. Test vector search queries through endpoints" -ForegroundColor $Green
    Write-Host "5. Integrate with Agent Garden and Agent Engine" -ForegroundColor $Green
    Write-Host "6. Configure monitoring and analytics" -ForegroundColor $Green

    Write-Status ""
    Write-Status "DEPLOYMENT COMMANDS:"
    Write-Status "==================="
    Write-Host "After indexes are ready, deploy them to endpoints:" -ForegroundColor $Cyan
    Write-Host "gcloud ai index-endpoints deploy-index INDEX_ENDPOINT_ID --index=INDEX_ID --deployed-index-id=DEPLOYED_INDEX_ID --project=coolbits-ai --region=europe-west4" -ForegroundColor $Yellow
}

# Run the main function
Main
