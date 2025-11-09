# Comprehensive RAG Integration Script for CoolBits.ai
# Integrates Vector Search, Discovery Engine, and Agent Builder components

param(
    [string]$ProjectId = "coolbits-ai",
    [string]$VectorSearchLocation = "us-central1",
    [string]$DiscoveryEngineLocation = "global"
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

# Function to create Cloud Storage bucket for RAG documents
function Create-RagBucket {
    param(
        [string]$RagId,
        [string]$AccessToken
    )

    $bucketName = "coolbits-rag-${RagId}-${ProjectId}"
    Write-Processing "Creating Cloud Storage bucket: $bucketName"

    $url = "https://storage.googleapis.com/storage/v1/b"
    $body = @{
        name = $bucketName
        location = "US"
        storageClass = "STANDARD"
    } | ConvertTo-Json -Compress

    try {
        $response = Invoke-RestMethod -Uri $url -Method Post -Headers @{
            "Authorization" = "Bearer $AccessToken"
            "Content-Type" = "application/json"
        } -Body $body -ErrorAction Stop

        Write-Success "Bucket '$bucketName' created successfully."
        return $bucketName
    } catch {
        if ($_.Exception.Response.StatusCode -eq 409) {
            Write-Warning "Bucket '$bucketName' already exists."
            return $bucketName
        } else {
            Write-Error "Error creating bucket $bucketName`: $($_.Exception.Message)"
            return $null
        }
    }
}

# Function to create Vector Search Index
function Create-VectorSearchIndex {
    param(
        [string]$RagId,
        [string]$DisplayName,
        [string]$Description,
        [string]$AccessToken
    )

    Write-Processing "Creating Vector Search Index: $DisplayName"

    $url = "https://${VectorSearchLocation}-aiplatform.googleapis.com/v1/projects/${ProjectId}/locations/${VectorSearchLocation}/indexes"
    
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

    try {
        $response = Invoke-RestMethod -Uri $url -Method Post -Headers @{
            "Authorization" = "Bearer $AccessToken"
            "Content-Type" = "application/json"
        } -Body $body -ErrorAction Stop

        Write-Success "Vector Search Index '$DisplayName' created successfully."
        return $response.name
    } catch {
        Write-Error "Error creating Vector Search Index $DisplayName`: $($_.Exception.Message)"
        return $null
    }
}

# Function to create Discovery Engine Data Store
function Create-DataStore {
    param(
        [string]$RagId,
        [string]$DisplayName,
        [string]$Description,
        [string]$BucketName,
        [string]$AccessToken
    )

    Write-Processing "Creating Discovery Engine Data Store: $DisplayName"

    $url = "https://discoveryengine.googleapis.com/v1beta/projects/${ProjectId}/locations/${DiscoveryEngineLocation}/dataStores"
    
    $body = @{
        displayName = $DisplayName
        industryVertical = "GENERIC"
        solutionTypes = @("SOLUTION_TYPE_SEARCH")
        contentConfig = "CONTENT_REQUIRED"
        documentProcessingConfig = @{
            name = "default_config"
            defaultParsingConfig = @{
                digitalParsingConfig = @{}
                ocrParsingConfig = @{
                    useNativeText = $true
                }
            }
        }
    } | ConvertTo-Json -Depth 10

    try {
        $response = Invoke-RestMethod -Uri $url -Method Post -Headers @{
            "Authorization" = "Bearer $AccessToken"
            "Content-Type" = "application/json"
        } -Body $body -ErrorAction Stop

        Write-Success "Data Store '$DisplayName' created successfully."
        return $response.name
    } catch {
        Write-Error "Error creating Data Store $DisplayName`: $($_.Exception.Message)"
        return $null
    }
}

# Function to create Search App
function Create-SearchApp {
    param(
        [string]$RagId,
        [string]$DisplayName,
        [string]$DataStoreId,
        [string]$AccessToken
    )

    Write-Processing "Creating Search App: $DisplayName"

    $url = "https://discoveryengine.googleapis.com/v1beta/projects/${ProjectId}/locations/${DiscoveryEngineLocation}/searchApps"
    
    $body = @{
        displayName = $DisplayName
        dataStoreIds = @($DataStoreId)
        searchConfig = @{
            searchTier = "SEARCH_TIER_STANDARD"
            searchAddOns = @("SEARCH_ADD_ON_LLM")
        }
    } | ConvertTo-Json -Compress

    try {
        $response = Invoke-RestMethod -Uri $url -Method Post -Headers @{
            "Authorization" = "Bearer $AccessToken"
            "Content-Type" = "application/json"
        } -Body $body -ErrorAction Stop

        Write-Success "Search App '$DisplayName' created successfully."
        return $response.name
    } catch {
        Write-Error "Error creating Search App $DisplayName`: $($_.Exception.Message)"
        return $null
    }
}

# Main execution
function Main {
    Write-Status "🚀 Starting comprehensive RAG integration for CoolBits.ai..."
    Write-Status "Project: $ProjectId"
    Write-Status "Vector Search Location: $VectorSearchLocation"
    Write-Status "Discovery Engine Location: $DiscoveryEngineLocation"
    Write-Status ""

    $accessToken = Get-AccessToken
    if (-not $accessToken) {
        Write-Error "Cannot proceed without an access token."
        return
    }

    # High Priority RAGs to create
    $highPriorityRags = @(
        @{Id="ai_board"; Name="AI Board"; Description="RAG system for AI Board management and coordination"},
        @{Id="business"; Name="Business AI Council"; Description="RAG system for business strategy and decision making"},
        @{Id="agritech"; Name="AgTech"; Description="RAG system for agricultural technology and innovation"},
        @{Id="banking"; Name="Banking"; Description="RAG system for banking and financial services"},
        @{Id="saas_b2b"; Name="SaaS B2B"; Description="RAG system for B2B SaaS solutions"}
    )

    $successCount = 0
    $totalCount = $highPriorityRags.Count

    Write-Status "Creating $totalCount high-priority RAG systems..."
    Write-Status ""

    foreach ($rag in $highPriorityRags) {
        Write-Status "=================================================="
        Write-Status "Processing: $($rag.Name) ($($rag.Id))"
        Write-Status "=================================================="

        # 1. Create Cloud Storage bucket
        $bucketName = Create-RagBucket -RagId $rag.Id -AccessToken $accessToken
        if (-not $bucketName) {
            Write-Error "Failed to create bucket for $($rag.Name)"
            continue
        }

        # 2. Create Vector Search Index
        $indexName = Create-VectorSearchIndex -RagId $rag.Id -DisplayName "$($rag.Name) Vector Index" -Description $rag.Description -AccessToken $accessToken
        if (-not $indexName) {
            Write-Warning "Failed to create Vector Search Index for $($rag.Name), continuing..."
        }

        # 3. Create Discovery Engine Data Store
        $dataStoreName = Create-DataStore -RagId $rag.Id -DisplayName "$($rag.Name) Data Store" -Description $rag.Description -BucketName $bucketName -AccessToken $accessToken
        if (-not $dataStoreName) {
            Write-Error "Failed to create Data Store for $($rag.Name)"
            continue
        }

        # Extract Data Store ID from the full name
        $dataStoreId = $dataStoreName.Split('/')[-1]

        # 4. Create Search App
        $searchAppName = Create-SearchApp -RagId $rag.Id -DisplayName "$($rag.Name) Search App" -DataStoreId $dataStoreId -AccessToken $accessToken
        if ($searchAppName) {
            Write-Success "✅ Successfully created complete RAG infrastructure for $($rag.Name)"
            $successCount++
        } else {
            Write-Warning "⚠️ Partial success for $($rag.Name) - some components may not be created"
        }

        Write-Status ""
    }

    Write-Status "==========================================================="
    Write-Status "=== FINAL SUMMARY ==="
    Write-Status "==========================================================="
    Write-Success "Total RAGs processed: $totalCount"
    Write-Success "Successful creations: $successCount"
    Write-Success "Failed creations: $($totalCount - $successCount)"
    
    if ($successCount -eq $totalCount) {
        Write-Success "🎉 All RAG systems created successfully!"
    } else {
        Write-Warning "⚠️ Some RAG systems had issues - check logs above"
    }

    Write-Status ""
    Write-Status "🎯 NEXT STEPS:"
    Write-Status "=============="
    Write-Host "1. Upload industry-specific documents to Cloud Storage buckets" -ForegroundColor $Green
    Write-Host "2. Wait for Vector Search indexes to be ready (5-10 minutes)" -ForegroundColor $Yellow
    Write-Host "3. Configure Agent Garden and Agent Engine components" -ForegroundColor $Green
    Write-Host "4. Test RAG queries through Search Apps" -ForegroundColor $Green
    Write-Host "5. Integrate with Business Panel and other applications" -ForegroundColor $Green
    Write-Host "6. Set up monitoring and analytics for RAG performance" -ForegroundColor $Green
}

# Run the main function
Main
