# Vector Search Index Creation Script for CoolBits.ai
# Creates Vector Search indexes in the correct region (europe-west4) to match bucket locations

param(
    [string]$ProjectId = "coolbits-ai",
    [string]$Location = "europe-west4"  # Matching bucket locations
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

# Main execution
function Main {
    Write-Status "Starting Vector Search Index creation for CoolBits.ai..."
    Write-Status "Project: $ProjectId"
    Write-Status "Location: $Location (matching bucket locations)"
    Write-Status ""

    $accessToken = Get-AccessToken
    if (-not $accessToken) {
        Write-Error "Cannot proceed without an access token."
        return
    }

    # Existing buckets from your infrastructure (in europe-west4)
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

    Write-Status "Creating Vector Search indexes for $totalCount existing RAG buckets..."
    Write-Status ""

    foreach ($rag in $existingBuckets) {
        Write-Status "=================================================="
        Write-Status "Processing: $($rag.Name) ($($rag.Id))"
        Write-Status "Bucket: $($rag.Bucket)"
        Write-Status "=================================================="

        # Create Vector Search Index for existing bucket
        $indexName = Create-VectorSearchIndexForBucket -RagId $rag.Id -DisplayName $rag.Name -BucketName $rag.Bucket -AccessToken $accessToken
        if ($indexName) {
            Write-Success "Successfully created Vector Search Index for $($rag.Name)"
            $successCount++
        } else {
            Write-Warning "Failed to create Vector Search Index for $($rag.Name)"
        }

        Write-Status ""
    }

    Write-Status "==========================================================="
    Write-Status "=== FINAL SUMMARY ==="
    Write-Status "==========================================================="
    Write-Success "Total RAG buckets processed: $totalCount"
    Write-Success "Successful Vector Search Index creations: $successCount"
    Write-Success "Failed creations: $($totalCount - $successCount)"
    
    if ($successCount -eq $totalCount) {
        Write-Success "All Vector Search indexes created successfully!"
    } else {
        Write-Warning "Some Vector Search indexes had issues - check logs above"
    }

    Write-Status ""
    Write-Status "NEXT STEPS:"
    Write-Status "==========="
    Write-Host "1. Wait for Vector Search indexes to be ready (5-10 minutes)" -ForegroundColor $Yellow
    Write-Host "2. Upload industry-specific documents to buckets" -ForegroundColor $Green
    Write-Host "3. Create Index Endpoints for serving queries" -ForegroundColor $Green
    Write-Host "4. Deploy indexes to endpoints" -ForegroundColor $Green
    Write-Host "5. Test vector search queries" -ForegroundColor $Green
    Write-Host "6. Integrate with Agent Garden and Agent Engine" -ForegroundColor $Green
    Write-Host "7. Configure monitoring and analytics" -ForegroundColor $Green

    Write-Status ""
    Write-Status "INTEGRATION WITH EXISTING INFRASTRUCTURE:"
    Write-Status "=========================================="
    Write-Host "Your existing cblm-search app can now use Vector Search" -ForegroundColor $Cyan
    Write-Host "Vector Search indexes provide semantic search capabilities" -ForegroundColor $Cyan
    Write-Host "Agent Garden can orchestrate multiple RAG systems" -ForegroundColor $Cyan
    Write-Host "Agent Engine can provide conversational interfaces" -ForegroundColor $Cyan
    Write-Host "Each industry/role has dedicated vector search capabilities" -ForegroundColor $Cyan
}

# Run the main function
Main
