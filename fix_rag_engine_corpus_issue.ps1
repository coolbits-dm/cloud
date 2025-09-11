# Fix RAG Engine Corpus Creation Issue
# Creates a compatible index for Vertex AI RAG Engine corpus creation

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

# Function to create RAG Engine compatible index
function Create-RagEngineCompatibleIndex {
    param(
        [string]$DisplayName,
        [string]$Description,
        [string]$AccessToken
    )

    Write-Processing "Creating RAG Engine compatible index: $DisplayName"

    $url = "https://${Location}-aiplatform.googleapis.com/v1/projects/${ProjectId}/locations/${Location}/indexes"
    
    # Try different configurations for RAG Engine compatibility
    $configurations = @(
        @{
            name = "Config1 - Brute Force"
            config = @{
                dimensions = 768
                approximateNeighborsCount = 150
                distanceMeasureType = "DOT_PRODUCT_DISTANCE"
                algorithmConfig = @{
                    bruteForceConfig = @{}
                }
            }
        },
        @{
            name = "Config2 - TreeAH with different params"
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
        },
        @{
            name = "Config3 - Minimal config"
            config = @{
                dimensions = 768
                distanceMeasureType = "DOT_PRODUCT_DISTANCE"
            }
        }
    )

    foreach ($config in $configurations) {
        Write-Status "Trying $($config.name)..."
        
        $body = @{
            displayName = "$DisplayName - $($config.name)"
            description = $Description
            metadata = @{
                contentsDeltaUri = ""
                config = $config.config
            }
        } | ConvertTo-Json -Depth 10

        try {
            $response = Invoke-RestMethod -Uri $url -Method Post -Headers @{
                "Authorization" = "Bearer $AccessToken"
                "Content-Type" = "application/json"
            } -Body $body -ErrorAction Stop

            Write-Success "✅ RAG Engine compatible index '$($config.name)' created successfully!"
            Write-Success "Index name: $($response.name)"
            return $response.name
        } catch {
            Write-Warning "❌ $($config.name) failed: $($_.Exception.Message)"
            continue
        }
    }
    
    Write-Error "All configurations failed"
    return $null
}

# Function to check existing indexes
function Check-ExistingIndexes {
    param([string]$AccessToken)
    
    Write-Processing "Checking existing indexes..."
    
    $url = "https://${Location}-aiplatform.googleapis.com/v1/projects/${ProjectId}/locations/${Location}/indexes"
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Get -Headers @{
            "Authorization" = "Bearer $AccessToken"
            "Content-Type" = "application/json"
        } -ErrorAction Stop
        
        if ($response.indexes) {
            Write-Success "Found $($response.indexes.Count) existing indexes:"
            foreach ($index in $response.indexes) {
                Write-Host "  - Name: $($index.displayName)" -ForegroundColor $Green
                Write-Host "    State: $($index.state)" -ForegroundColor $Yellow
                Write-Host "    Algorithm: $($index.metadata.config.algorithmConfig | ConvertTo-Json -Compress)" -ForegroundColor $Cyan
                Write-Host ""
            }
        } else {
            Write-Warning "No indexes found."
        }
        
        return $response.indexes
    } catch {
        Write-Error "Error checking indexes: $($_.Exception.Message)"
        return $null
    }
}

# Main execution
function Main {
    Write-Status "Fixing RAG Engine corpus creation issue..."
    Write-Status "Project: $ProjectId"
    Write-Status "Location: $Location"
    Write-Status ""

    $accessToken = Get-AccessToken
    if (-not $accessToken) {
        Write-Error "Cannot proceed without an access token."
        return
    }

    # Check existing indexes
    $existingIndexes = Check-ExistingIndexes -AccessToken $accessToken

    # Try to create RAG Engine compatible index
    $indexName = Create-RagEngineCompatibleIndex -DisplayName "RAG Engine Compatible Index" -Description "Index compatible with Vertex AI RAG Engine corpus creation" -AccessToken $accessToken
    
    if ($indexName) {
        Write-Success "✅ RAG Engine compatible index created!"
    } else {
        Write-Warning "⚠️ Could not create new index, but existing indexes might work"
    }

    Write-Status ""
    Write-Status "SOLUTION FOR RAG ENGINE CORPUS:"
    Write-Status "=============================="
    Write-Host "1. Try using existing cblm-index in GUI" -ForegroundColor $Green
    Write-Host "2. If that fails, use Discovery Engine instead" -ForegroundColor $Yellow
    Write-Host "3. Create Data Store in Discovery Engine" -ForegroundColor $Yellow
    Write-Host "4. Use existing cblm-search app" -ForegroundColor $Yellow

    Write-Status ""
    Write-Status "ALTERNATIVE APPROACH - DISCOVERY ENGINE:"
    Write-Status "======================================"
    Write-Host "Since RAG Engine has index compatibility issues:" -ForegroundColor $Cyan
    Write-Host "1. Go to Discovery Engine > Data Stores" -ForegroundColor $Green
    Write-Host "2. Create new Data Store" -ForegroundColor $Green
    Write-Host "3. Connect to your Cloud Storage bucket" -ForegroundColor $Green
    Write-Host "4. Use existing cblm-search app" -ForegroundColor $Green
    Write-Host "5. This approach is more reliable" -ForegroundColor $Green

    Write-Status ""
    Write-Status "NEXT STEPS:"
    Write-Status "==========="
    Write-Host "1. Try creating corpus with existing cblm-index" -ForegroundColor $Yellow
    Write-Host "2. If that fails, use Discovery Engine approach" -ForegroundColor $Green
    Write-Host "3. Create Data Store instead of corpus" -ForegroundColor $Green
    Write-Host "4. Upload documents to bucket" -ForegroundColor $Green
    Write-Host "5. Test with cblm-search app" -ForegroundColor $Green
}

# Run the main function
Main
