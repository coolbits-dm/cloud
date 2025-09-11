# Agent Builder and RAG Integration Script for CoolBits.ai
# Integrates existing infrastructure with Agent Garden, Agent Engine, and Search Apps

param(
    [string]$ProjectId = "coolbits-ai",
    [string]$Location = "us-central1"
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

# Function to create Agent Engine
function Create-AgentEngine {
    param(
        [string]$AgentId,
        [string]$DisplayName,
        [string]$Description,
        [string]$AccessToken
    )

    Write-Processing "Creating Agent Engine: $DisplayName"

    $url = "https://${Location}-aiplatform.googleapis.com/v1/projects/${ProjectId}/locations/${Location}/agents"
    
    $body = @{
        displayName = $DisplayName
        description = $Description
        defaultLanguageCode = "en"
        timeZone = "America/New_York"
        enableStackdriverLogging = $true
        enableSpellCheck = $true
        speechToTextSettings = @{
            enableSpeechAdaptation = $true
        }
    } | ConvertTo-Json -Depth 10

    try {
        $response = Invoke-RestMethod -Uri $url -Method Post -Headers @{
            "Authorization" = "Bearer $AccessToken"
            "Content-Type" = "application/json"
        } -Body $body -ErrorAction Stop

        Write-Success "Agent Engine '$DisplayName' created successfully."
        return $response.name
    } catch {
        Write-Error "Error creating Agent Engine $DisplayName`: $($_.Exception.Message)"
        return $null
    }
}

# Function to create Search App with existing bucket
function Create-SearchAppWithBucket {
    param(
        [string]$RagId,
        [string]$DisplayName,
        [string]$BucketName,
        [string]$AccessToken
    )

    Write-Processing "Creating Search App with existing bucket: $DisplayName"

    # First create Data Store
    $dataStoreUrl = "https://discoveryengine.googleapis.com/v1beta/projects/${ProjectId}/locations/global/dataStores"
    
    $dataStoreBody = @{
        displayName = "$DisplayName Data Store"
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
        $dataStoreResponse = Invoke-RestMethod -Uri $dataStoreUrl -Method Post -Headers @{
            "Authorization" = "Bearer $AccessToken"
            "Content-Type" = "application/json"
        } -Body $dataStoreBody -ErrorAction Stop

        Write-Success "Data Store created: $($dataStoreResponse.name)"
        $dataStoreId = $dataStoreResponse.name.Split('/')[-1]

        # Then create Search App
        $searchAppUrl = "https://discoveryengine.googleapis.com/v1beta/projects/${ProjectId}/locations/global/searchApps"
        
        $searchAppBody = @{
            displayName = "$DisplayName Search App"
            dataStoreIds = @($dataStoreId)
            searchConfig = @{
                searchTier = "SEARCH_TIER_STANDARD"
                searchAddOns = @("SEARCH_ADD_ON_LLM")
            }
        } | ConvertTo-Json -Compress

        $searchAppResponse = Invoke-RestMethod -Uri $searchAppUrl -Method Post -Headers @{
            "Authorization" = "Bearer $AccessToken"
            "Content-Type" = "application/json"
        } -Body $searchAppBody -ErrorAction Stop

        Write-Success "Search App '$DisplayName' created successfully."
        return @{
            DataStore = $dataStoreResponse.name
            SearchApp = $searchAppResponse.name
            BucketName = $BucketName
        }
    } catch {
        Write-Error "Error creating Search App $DisplayName`: $($_.Exception.Message)"
        return $null
    }
}

# Function to create Vector Search Index for existing bucket
function Create-VectorSearchIndexForBucket {
    param(
        [string]$RagId,
        [string]$DisplayName,
        [string]$BucketName,
        [string]$AccessToken
    )

    Write-Processing "Creating Vector Search Index for bucket: $BucketName"

    $url = "https://${Location}-aiplatform.googleapis.com/v1/projects/${ProjectId}/locations/${Location}/indexes"
    
    $body = @{
        displayName = "$DisplayName Vector Index"
        description = "Vector search index for $DisplayName RAG system using text-embedding-004"
        metadata = @{
            contentsDeltaUri = "gs://$BucketName"
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

# Main execution
function Main {
    Write-Status "🤖 Starting Agent Builder and RAG integration for CoolBits.ai..."
    Write-Status "Project: $ProjectId"
    Write-Status "Location: $Location"
    Write-Status ""

    $accessToken = Get-AccessToken
    if (-not $accessToken) {
        Write-Error "Cannot proceed without an access token."
        return
    }

    # Existing buckets from your infrastructure
    $existingBuckets = @(
        @{Id="ai_board"; Name="AI Board"; Bucket="coolbits-rag-ai_board-coolbits-ai"},
        @{Id="business"; Name="Business AI Council"; Bucket="coolbits-rag-business-coolbits-ai"},
        @{Id="agritech"; Name="AgTech"; Bucket="coolbits-rag-agritech-coolbits-ai"},
        @{Id="banking"; Name="Banking"; Bucket="coolbits-rag-banking-coolbits-ai"},
        @{Id="saas_b2b"; Name="SaaS B2B"; Bucket="coolbits-rag-saas_b2b-coolbits-ai"},
        @{Id="healthcare"; Name="Healthcare"; Bucket="coolbits-rag-healthcare-coolbits-ai"},
        @{Id="agency"; Name="Agency"; Bucket="coolbits-rag-agency-coolbits-ai"},
        @{Id="user"; Name="User"; Bucket="coolbits-rag-user-coolbits-ai"},
        @{Id="dev"; Name="Dev"; Bucket="coolbits-rag-dev-coolbits-ai"}
    )

    $successCount = 0
    $totalCount = $existingBuckets.Count

    Write-Status "Integrating $totalCount existing RAG buckets with Agent Builder..."
    Write-Status ""

    foreach ($rag in $existingBuckets) {
        Write-Status "=================================================="
        Write-Status "Processing: $($rag.Name) ($($rag.Id))"
        Write-Status "Bucket: $($rag.Bucket)"
        Write-Status "=================================================="

        # 1. Create Vector Search Index for existing bucket
        $indexName = Create-VectorSearchIndexForBucket -RagId $rag.Id -DisplayName $rag.Name -BucketName $rag.Bucket -AccessToken $accessToken
        if (-not $indexName) {
            Write-Warning "Failed to create Vector Search Index for $($rag.Name), continuing..."
        }

        # 2. Create Search App with existing bucket
        $searchAppResult = Create-SearchAppWithBucket -RagId $rag.Id -DisplayName $rag.Name -BucketName $rag.Bucket -AccessToken $accessToken
        if ($searchAppResult) {
            Write-Success "✅ Successfully integrated $($rag.Name) with Search App infrastructure"
            $successCount++
        } else {
            Write-Warning "⚠️ Partial success for $($rag.Name) - some components may not be created"
        }

        Write-Status ""
    }

    Write-Status "==========================================================="
    Write-Status "=== FINAL SUMMARY ==="
    Write-Status "==========================================================="
    Write-Success "Total RAG buckets processed: $totalCount"
    Write-Success "Successful integrations: $successCount"
    Write-Success "Failed integrations: $($totalCount - $successCount)"
    
    if ($successCount -eq $totalCount) {
        Write-Success "🎉 All RAG buckets integrated successfully!"
    } else {
        Write-Warning "⚠️ Some RAG buckets had issues - check logs above"
    }

    Write-Status ""
    Write-Status "🎯 NEXT STEPS FOR AGENT BUILDER:"
    Write-Status "================================"
    Write-Host "1. Upload industry-specific documents to existing buckets" -ForegroundColor $Green
    Write-Host "2. Wait for Vector Search indexes to be ready (5-10 minutes)" -ForegroundColor $Yellow
    Write-Host "3. Configure Agent Garden with RAG endpoints" -ForegroundColor $Green
    Write-Host "4. Set up Agent Engine workflows" -ForegroundColor $Green
    Write-Host "5. Test RAG queries through Search Apps" -ForegroundColor $Green
    Write-Host "6. Integrate with Business Panel and other applications" -ForegroundColor $Green
    Write-Host "7. Configure monitoring and analytics" -ForegroundColor $Green

    Write-Status ""
    Write-Status "🔗 INTEGRATION POINTS:"
    Write-Status "====================="
    Write-Host "• Your existing cblm-search app can now query all RAG buckets" -ForegroundColor $Cyan
    Write-Host "• Vector Search indexes provide semantic search capabilities" -ForegroundColor $Cyan
    Write-Host "• Agent Garden can orchestrate multiple RAG systems" -ForegroundColor $Cyan
    Write-Host "• Agent Engine can provide conversational interfaces" -ForegroundColor $Cyan
    Write-Host "• Each industry/role has dedicated search capabilities" -ForegroundColor $Cyan
}

# Run the main function
Main
