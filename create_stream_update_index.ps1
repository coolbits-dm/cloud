# Create STREAM_UPDATE Index for RAG Engine Corpus
# Creates a STREAM_UPDATE type index required for Vertex AI RAG Engine corpus creation

param(
    [string]$ProjectId = "coolbits-ai",
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

# Function to create STREAM_UPDATE index
function Create-StreamUpdateIndex {
    param(
        [string]$DisplayName,
        [string]$Description,
        [string]$AccessToken
    )

    Write-Processing "Creating STREAM_UPDATE index: $DisplayName"

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
                    streamUpdateConfig = @{
                        enableStreamUpdate = $true
                    }
                }
            }
        }
    } | ConvertTo-Json -Depth 10

    try {
        $response = Invoke-RestMethod -Uri $url -Method Post -Headers @{
            "Authorization" = "Bearer $AccessToken"
            "Content-Type" = "application/json"
        } -Body $body -ErrorAction Stop

        Write-Success "STREAM_UPDATE index '$DisplayName' created successfully."
        Write-Success "Index name: $($response.name)"
        return $response.name
    } catch {
        Write-Error "Error creating STREAM_UPDATE index $DisplayName`: $($_.Exception.Message)"
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

# Function to create Index Endpoint for STREAM_UPDATE index
function Create-StreamUpdateIndexEndpoint {
    param(
        [string]$DisplayName,
        [string]$AccessToken
    )

    Write-Processing "Creating Index Endpoint for STREAM_UPDATE index: $DisplayName"

    $url = "https://${Location}-aiplatform.googleapis.com/v1/projects/${ProjectId}/locations/${Location}/indexEndpoints"
    
    $body = @{
        displayName = "$DisplayName Stream Endpoint"
        description = "Index endpoint for $DisplayName STREAM_UPDATE index"
        network = "projects/271190369805/global/networks/default"
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
        return $null
    }
}

# Main execution
function Main {
    Write-Status "Creating STREAM_UPDATE index for RAG Engine corpus..."
    Write-Status "Project: $ProjectId"
    Write-Status "Location: $Location"
    Write-Status ""

    $accessToken = Get-AccessToken
    if (-not $accessToken) {
        Write-Error "Cannot proceed without an access token."
        return
    }

    # Create STREAM_UPDATE index for RAG Engine
    $indexName = Create-StreamUpdateIndex -DisplayName "RAG Engine Stream Index" -Description "STREAM_UPDATE index for Vertex AI RAG Engine corpus creation" -AccessToken $accessToken
    
    if ($indexName) {
        Write-Success "✅ STREAM_UPDATE index created successfully!"
        
        # Create Index Endpoint
        $endpointName = Create-StreamUpdateIndexEndpoint -DisplayName "RAG Engine Stream Index" -AccessToken $accessToken
        
        if ($endpointName) {
            Write-Success "✅ Index Endpoint created successfully!"
        }
    } else {
        Write-Error "❌ Failed to create STREAM_UPDATE index"
    }

    Write-Status ""
    Write-Status "SOLUTION FOR RAG ENGINE CORPUS:"
    Write-Status "=============================="
    Write-Host "1. Use this STREAM_UPDATE index when creating corpus in GUI" -ForegroundColor $Green
    Write-Host "2. Select 'STREAM_UPDATE' type when prompted" -ForegroundColor $Green
    Write-Host "3. This index supports real-time updates for corpus" -ForegroundColor $Green
    Write-Host "4. Perfect for RAG Engine corpus creation" -ForegroundColor $Green

    Write-Status ""
    Write-Status "NEXT STEPS:"
    Write-Status "==========="
    Write-Host "1. Wait for STREAM_UPDATE index to be ready (5-10 minutes)" -ForegroundColor $Yellow
    Write-Host "2. Go to Vertex AI RAG Engine > Create Corpus" -ForegroundColor $Green
    Write-Host "3. Select the STREAM_UPDATE index when creating corpus" -ForegroundColor $Green
    Write-Host "4. Upload documents to your bucket" -ForegroundColor $Green
    Write-Host "5. Test corpus functionality" -ForegroundColor $Green

    Write-Status ""
    Write-Status "ALTERNATIVE SOLUTION:"
    Write-Status "==================="
    Write-Host "If STREAM_UPDATE doesn't work, try:" -ForegroundColor $Cyan
    Write-Host "1. Use Discovery Engine instead of RAG Engine" -ForegroundColor $Yellow
    Write-Host "2. Create Data Store in Discovery Engine" -ForegroundColor $Yellow
    Write-Host "3. Use existing cblm-search app" -ForegroundColor $Yellow
    Write-Host "4. Integrate with Vector Search indexes" -ForegroundColor $Yellow
}

# Run the main function
Main
