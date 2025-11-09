# PowerShell script to create Vector Search indexes and integrate with RAG infrastructure
# Based on the existing cblm-search app and RAG requirements

param(
    [string]$ProjectId = "coolbits-ai",
    [string]$Location = "us-central1"  # Using us-central1 for Vector Search
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

# Function to create Vector Search Index
function Create-VectorSearchIndex {
    param(
        [string]$IndexId,
        [string]$DisplayName,
        [string]$Description,
        [string]$AccessToken
    )

    Write-Processing "Creating Vector Search Index: $DisplayName"

    $url = "https://${Location}-aiplatform.googleapis.com/v1/projects/${ProjectId}/locations/${Location}/indexes"
    
    $body = @{
        displayName = $DisplayName
        description = $Description
        metadata = @{
            contentsDeltaUri = ""
            config = @{
                dimensions = 768
                approximateNeighborsCount = 150
                distanceMeasureType = "DOT_PRODUCT_DISTANCE"
                algorithmConfig = @{
                    treeAhConfig = @{
                        leafNodeEmbeddingCount = 500
                        leafNodesToSearchPercent = 7
                    }
                }
            }
        }
    } | ConvertTo-Json -Depth 10

    Write-Status "Creating index with URL: $url"
    Write-Status "Payload: $body"

    try {
        $response = Invoke-RestMethod -Uri $url -Method Post -Headers @{
            "Authorization" = "Bearer $AccessToken"
            "Content-Type" = "application/json"
        } -Body $body -ErrorAction Stop

        Write-Success "Vector Search Index '$DisplayName' created successfully."
        Write-Success "Index name: $($response.name)"
        return $response.name
    } catch {
        Write-Error "Error creating Vector Search Index $DisplayName`: $($_.Exception.Message)"
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

# Function to create Index Endpoint
function Create-IndexEndpoint {
    param(
        [string]$EndpointId,
        [string]$DisplayName,
        [string]$AccessToken
    )

    Write-Processing "Creating Index Endpoint: $DisplayName"

    $url = "https://${Location}-aiplatform.googleapis.com/v1/projects/${ProjectId}/locations/${Location}/indexEndpoints"
    
    $body = @{
        displayName = $DisplayName
        description = "Index endpoint for $DisplayName RAG system"
        network = "projects/${ProjectId}/global/networks/default"
    } | ConvertTo-Json -Compress

    Write-Status "Creating endpoint with URL: $url"

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
    Write-Status "🚀 Starting Vector Search infrastructure setup for CoolBits.ai..."
    Write-Status "Project: $ProjectId"
    Write-Status "Location: $Location"
    Write-Status ""

    $accessToken = Get-AccessToken
    if (-not $accessToken) {
        Write-Error "Cannot proceed without an access token."
        return
    }

    # Create Vector Search Index for AI Board (test case)
    $indexId = "ai-board-vector-index"
    $displayName = "AI Board Vector Index"
    $description = "Vector search index for AI Board RAG system using text-embedding-004"

    $indexName = Create-VectorSearchIndex -IndexId $indexId -DisplayName $displayName -Description $description -AccessToken $accessToken
    
    if ($indexName) {
        Write-Success "✅ Vector Search Index created successfully!"
        Write-Status "Next steps:"
        Write-Host "1. Wait for index to be ready (this may take several minutes)" -ForegroundColor $Yellow
        Write-Host "2. Create Index Endpoint" -ForegroundColor $Yellow
        Write-Host "3. Deploy index to endpoint" -ForegroundColor $Yellow
        Write-Host "4. Upload embeddings to the index" -ForegroundColor $Yellow
        Write-Host "5. Test vector search queries" -ForegroundColor $Yellow
    } else {
        Write-Error "❌ Failed to create Vector Search Index"
    }

    Write-Status ""
    Write-Status "🎯 INTEGRATION WITH EXISTING INFRASTRUCTURE:"
    Write-Status "=========================================="
    Write-Host "• Your existing cblm-search app can be enhanced with Vector Search" -ForegroundColor $Green
    Write-Host "• RAG corpora will use these indexes for semantic search" -ForegroundColor $Green
    Write-Host "• Agent Garden and Agent Engine can query these indexes" -ForegroundColor $Green
    Write-Host "• Each industry/role will have its own dedicated index" -ForegroundColor $Green
}

# Run the main function
Main
