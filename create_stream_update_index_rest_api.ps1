# Create STREAM_UPDATE Index using REST API
# Creates a proper STREAM_UPDATE index required for RAG Engine corpus creation

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

# Function to create STREAM_UPDATE index using REST API
function Create-StreamUpdateIndexRestApi {
    param(
        [string]$DisplayName,
        [string]$Description,
        [string]$AccessToken
    )

    Write-Processing "Creating STREAM_UPDATE index using REST API: $DisplayName"

    $url = "https://${Location}-aiplatform.googleapis.com/v1/projects/${ProjectId}/locations/${Location}/indexes"
    
    # Try different approaches for STREAM_UPDATE
    $approaches = @(
        @{
            name = "Approach 1 - Direct STREAM_UPDATE"
            body = @{
                displayName = $DisplayName
                description = $Description
                metadata = @{
                    contentsDeltaUri = ""
                    config = @{
                        dimensions = 768
                        approximateNeighborsCount = 150
                        distanceMeasureType = "DOT_PRODUCT_DISTANCE"
                        indexUpdateMethod = "STREAM_UPDATE"
                        algorithmConfig = @{
                            treeAhConfig = @{
                                leafNodeEmbeddingCount = 500
                                leafNodesToSearchPercent = 7
                            }
                        }
                    }
                }
            }
        },
        @{
            name = "Approach 2 - Matching Engine Config"
            body = @{
                displayName = "$DisplayName - Matching Engine"
                description = $Description
                metadata = @{
                    contentsDeltaUri = ""
                    config = @{
                        dimensions = 768
                        approximateNeighborsCount = 150
                        distanceMeasureType = "DOT_PRODUCT_DISTANCE"
                        matchingEngineConfig = @{
                            indexUpdateMethod = "STREAM_UPDATE"
                        }
                        algorithmConfig = @{
                            treeAhConfig = @{
                                leafNodeEmbeddingCount = 500
                                leafNodesToSearchPercent = 7
                            }
                        }
                    }
                }
            }
        },
        @{
            name = "Approach 3 - Minimal STREAM_UPDATE"
            body = @{
                displayName = "$DisplayName - Minimal"
                description = $Description
                metadata = @{
                    contentsDeltaUri = ""
                    config = @{
                        dimensions = 768
                        distanceMeasureType = "DOT_PRODUCT_DISTANCE"
                        indexUpdateMethod = "STREAM_UPDATE"
                    }
                }
            }
        }
    )

    foreach ($approach in $approaches) {
        Write-Status "Trying $($approach.name)..."
        
        $body = $approach.body | ConvertTo-Json -Depth 10

        try {
            $response = Invoke-RestMethod -Uri $url -Method Post -Headers @{
                "Authorization" = "Bearer $AccessToken"
                "Content-Type" = "application/json"
            } -Body $body -ErrorAction Stop

            Write-Success "✅ STREAM_UPDATE index '$($approach.name)' created successfully!"
            Write-Success "Index name: $($response.name)"
            return $response.name
        } catch {
            Write-Warning "❌ $($approach.name) failed: $($_.Exception.Message)"
            if ($_.Exception.Response) {
                $errorResponse = $_.Exception.Response.GetResponseStream()
                $reader = New-Object System.IO.StreamReader($errorResponse)
                $responseBody = $reader.ReadToEnd()
                Write-Warning "Error details: $responseBody"
            }
            continue
        }
    }
    
    Write-Error "All STREAM_UPDATE approaches failed"
    return $null
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

    # Try to create STREAM_UPDATE index
    $indexName = Create-StreamUpdateIndexRestApi -DisplayName "RAG Engine STREAM_UPDATE Index" -Description "STREAM_UPDATE index for Vertex AI RAG Engine corpus creation" -AccessToken $accessToken
    
    if ($indexName) {
        Write-Success "✅ STREAM_UPDATE index created successfully!"
    } else {
        Write-Warning "⚠️ Could not create STREAM_UPDATE index via REST API"
    }

    Write-Status ""
    Write-Status "ALTERNATIVE SOLUTIONS:"
    Write-Status "===================="
    Write-Host "Since STREAM_UPDATE index creation is complex:" -ForegroundColor $Cyan
    Write-Host ""
    Write-Host "1. USE DISCOVERY ENGINE (Recommended):" -ForegroundColor $Green
    Write-Host "   • Go to Discovery Engine > Data Stores" -ForegroundColor $Yellow
    Write-Host "   • Create new Data Store" -ForegroundColor $Yellow
    Write-Host "   • Connect to your Cloud Storage bucket" -ForegroundColor $Yellow
    Write-Host "   • Use existing cblm-search app" -ForegroundColor $Yellow
    Write-Host ""
    Write-Host "2. USE CLOUD SHELL WITH PYTHON:" -ForegroundColor $Green
    Write-Host "   • Open Cloud Shell" -ForegroundColor $Yellow
    Write-Host "   • Run: pip install google-cloud-aiplatform" -ForegroundColor $Yellow
    Write-Host "   • Run the Python script" -ForegroundColor $Yellow
    Write-Host ""
    Write-Host "3. USE EXISTING INFRASTRUCTURE:" -ForegroundColor $Green
    Write-Host "   • Use cblm-search app" -ForegroundColor $Yellow
    Write-Host "   • Use Vector Search indexes" -ForegroundColor $Yellow
    Write-Host "   • Use Discovery Engine Data Stores" -ForegroundColor $Yellow

    Write-Status ""
    Write-Status "RECOMMENDED NEXT STEPS:"
    Write-Status "======================"
    Write-Host "1. Go to Discovery Engine > Data Stores" -ForegroundColor $Green
    Write-Host "2. Create new Data Store" -ForegroundColor $Green
    Write-Host "3. Connect to cblm-search bucket" -ForegroundColor $Green
    Write-Host "4. Use existing cblm-search app" -ForegroundColor $Green
    Write-Host "5. This approach is more reliable than RAG Engine" -ForegroundColor $Green
}

# Run the main function
Main
