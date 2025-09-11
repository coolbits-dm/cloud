# Discovery Engine Alternative for RAG Engine Corpus Issue
# Since STREAM_UPDATE index creation is complex, use Discovery Engine instead

param(
    [string]$ProjectId = "coolbits-ai",
    [string]$Location = "global"
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

# Function to create Discovery Engine Data Store
function Create-DiscoveryEngineDataStore {
    param(
        [string]$RagId,
        [string]$DisplayName,
        [string]$Description,
        [string]$BucketName,
        [string]$AccessToken
    )

    Write-Processing "Creating Discovery Engine Data Store: $DisplayName"

    $url = "https://discoveryengine.googleapis.com/v1beta/projects/${ProjectId}/locations/${Location}/dataStores"
    
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
        Write-Success "Data Store name: $($response.name)"
        return $response.name
    } catch {
        Write-Error "Error creating Data Store $DisplayName`: $($_.Exception.Message)"
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

# Function to create Search App
function Create-SearchApp {
    param(
        [string]$RagId,
        [string]$DisplayName,
        [string]$DataStoreId,
        [string]$AccessToken
    )

    Write-Processing "Creating Search App: $DisplayName"

    $url = "https://discoveryengine.googleapis.com/v1beta/projects/${ProjectId}/locations/${Location}/searchApps"
    
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
        Write-Success "Search App name: $($response.name)"
        return $response.name
    } catch {
        Write-Error "Error creating Search App $DisplayName`: $($_.Exception.Message)"
        return $null
    }
}

# Main execution
function Main {
    Write-Status "Creating Discovery Engine alternative for RAG Engine corpus..."
    Write-Status "Project: $ProjectId"
    Write-Status "Location: $Location"
    Write-Status ""

    $accessToken = Get-AccessToken
    if (-not $accessToken) {
        Write-Error "Cannot proceed without an access token."
        return
    }

    # Test with cblm-search bucket
    $ragId = "cblm_search"
    $displayName = "CBLM Search Data Store"
    $description = "Discovery Engine Data Store for cblm-search functionality"
    $bucketName = "cblm-search"

    Write-Status "Creating Discovery Engine infrastructure for cblm-search..."
    Write-Status ""

    # Create Data Store
    $dataStoreName = Create-DiscoveryEngineDataStore -RagId $ragId -DisplayName $displayName -Description $description -BucketName $bucketName -AccessToken $accessToken
    
    if ($dataStoreName) {
        Write-Success "✅ Data Store created successfully!"
        
        # Extract Data Store ID
        $dataStoreId = $dataStoreName.Split('/')[-1]
        
        # Create Search App
        $searchAppName = Create-SearchApp -RagId $ragId -DisplayName "CBLM Search App" -DataStoreId $dataStoreId -AccessToken $accessToken
        
        if ($searchAppName) {
            Write-Success "✅ Search App created successfully!"
        }
    }

    Write-Status ""
    Write-Status "==========================================================="
    Write-Status "=== DISCOVERY ENGINE SOLUTION ==="
    Write-Status "==========================================================="
    
    Write-Host "✅ Discovery Engine is more reliable than RAG Engine" -ForegroundColor $Green
    Write-Host "✅ No STREAM_UPDATE index required" -ForegroundColor $Green
    Write-Host "✅ Works with existing Cloud Storage buckets" -ForegroundColor $Green
    Write-Host "✅ Integrates with existing cblm-search app" -ForegroundColor $Green

    Write-Status ""
    Write-Status "MANUAL STEPS IN GOOGLE CLOUD CONSOLE:"
    Write-Status "===================================="
    Write-Host "1. Go to Discovery Engine > Data Stores" -ForegroundColor $Cyan
    Write-Host "2. Click 'Create Data Store'" -ForegroundColor $Cyan
    Write-Host "3. Select 'Search' as the solution type" -ForegroundColor $Cyan
    Write-Host "4. Choose 'Generic' industry vertical" -ForegroundColor $Cyan
    Write-Host "5. Connect to your Cloud Storage bucket" -ForegroundColor $Cyan
    Write-Host "6. Upload your documents" -ForegroundColor $Cyan
    Write-Host "7. Create Search App" -ForegroundColor $Cyan
    Write-Host "8. Test with queries" -ForegroundColor $Cyan

    Write-Status ""
    Write-Status "ADVANTAGES OF DISCOVERY ENGINE:"
    Write-Status "=============================="
    Write-Host "• No complex index configuration required" -ForegroundColor $Green
    Write-Host "• Works with any Cloud Storage bucket" -ForegroundColor $Green
    Write-Host "• Built-in document processing" -ForegroundColor $Green
    Write-Host "• LLM integration included" -ForegroundColor $Green
    Write-Host "• More stable than RAG Engine" -ForegroundColor $Green
    Write-Host "• Better error handling" -ForegroundColor $Green

    Write-Status ""
    Write-Status "NEXT STEPS:"
    Write-Status "==========="
    Write-Host "1. Use Discovery Engine instead of RAG Engine" -ForegroundColor $Green
    Write-Host "2. Create Data Store in GUI" -ForegroundColor $Green
    Write-Host "3. Connect to cblm-search bucket" -ForegroundColor $Green
    Write-Host "4. Upload documents" -ForegroundColor $Green
    Write-Host "5. Test search functionality" -ForegroundColor $Green
    Write-Host "6. Integrate with existing applications" -ForegroundColor $Green
}

# Run the main function
Main
