# Enhanced RAG Corpus Creation Script for CoolBits.ai using PowerShell
# Fixed version with better error handling and debugging

param(
    [string]$ProjectId = "coolbits-ai",
    [string]$Location = "global",
    [string]$Region = "europe-west1",
    [string]$BucketPrefix = "coolbits-rag"
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

function Write-Debug {
    param([string]$Message)
    Write-Host "[DEBUG] $Message" -ForegroundColor Gray
}

# Function to get access token
function Get-AccessToken {
    try {
        $token = gcloud auth print-access-token 2>$null
        if ($LASTEXITCODE -eq 0 -and $token) {
            return $token.Trim()
        } else {
            Write-Error "Failed to get access token"
            return $null
        }
    } catch {
        Write-Error "Error getting access token: $($_.Exception.Message)"
        return $null
    }
}

# Function to test API access
function Test-APIAccess {
    $AccessToken = Get-AccessToken
    if (-not $AccessToken) {
        return $false
    }
    
    Write-Debug "Testing API access..."
    
    $TestUrl = "https://discoveryengine.googleapis.com/v1beta/projects/${ProjectId}/locations/${Location}/dataStores"
    
    try {
        $Response = Invoke-RestMethod -Uri $TestUrl -Headers @{
            "Authorization" = "Bearer ${AccessToken}"
            "Content-Type" = "application/json"
        } -Method Get -ErrorAction Stop
        
        Write-Success "API access test successful"
        return $true
    } catch {
        Write-Error "API access test failed: $($_.Exception.Message)"
        if ($_.Exception.Response) {
            $StatusCode = $_.Exception.Response.StatusCode
            Write-Error "HTTP Status: $StatusCode"
        }
        return $false
    }
}

# Function to create Cloud Storage bucket
function New-Bucket {
    param([string]$RagId)
    
    $BucketName = "${BucketPrefix}-${RagId}-${ProjectId}"
    
    Write-Processing "Creating bucket: ${BucketName}"
    
    # Check if bucket already exists
    try {
        $ExistingBuckets = gcloud storage buckets list --filter="name:${BucketName}" --format="value(name)" 2>$null
        if ($ExistingBuckets -and $ExistingBuckets.Contains($BucketName)) {
            Write-Warning "Bucket ${BucketName} already exists, skipping..."
            return $true
        }
    } catch {
        Write-Debug "Error checking existing buckets: $($_.Exception.Message)"
    }
    
    # Create bucket
    try {
        Write-Debug "Creating bucket with command: gcloud storage buckets create gs://${BucketName} --project=${ProjectId} --location=${Region}"
        $Result = gcloud storage buckets create gs://${BucketName} --project=${ProjectId} --location=${Region} 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Created bucket: ${BucketName}"
            return $true
        } else {
            Write-Error "Failed to create bucket: ${BucketName}"
            Write-Error "Command output: $Result"
            return $false
        }
    } catch {
        Write-Error "Error creating bucket ${BucketName}: $($_.Exception.Message)"
        return $false
    }
}

# Function to create data store using REST API
function New-DataStore {
    param(
        [string]$RagId,
        [string]$RagName,
        [string]$RagDescription
    )
    
    $DataStoreName = "${RagId}-corpus"
    $DataStoreId = "${RagId}_corpus"
    
    Write-Processing "Creating data store: ${DataStoreName}"
    
    $AccessToken = Get-AccessToken
    if (-not $AccessToken) {
        Write-Error "No access token available"
        return $null
    }
    
    # Check if data store already exists
    $CheckUrl = "https://discoveryengine.googleapis.com/v1beta/projects/${ProjectId}/locations/${Location}/dataStores"
    
    try {
        Write-Debug "Checking existing data stores..."
        $ExistingStores = Invoke-RestMethod -Uri "${CheckUrl}?filter=displayName%3D%22${DataStoreName}%22" -Headers @{
            "Authorization" = "Bearer ${AccessToken}"
            "Content-Type" = "application/json"
        } -Method Get -ErrorAction Stop
        
        if ($ExistingStores.dataStores -and $ExistingStores.dataStores.Count -gt 0) {
            foreach ($store in $ExistingStores.dataStores) {
                if ($store.displayName -eq $DataStoreName) {
                    Write-Warning "Data store ${DataStoreName} already exists, skipping..."
                    return $store.name
                }
            }
        }
    } catch {
        Write-Debug "Error checking existing data stores: $($_.Exception.Message)"
    }
    
    # Create data store
    $CreateUrl = "https://discoveryengine.googleapis.com/v1beta/projects/${ProjectId}/locations/${Location}/dataStores?dataStoreId=${DataStoreId}"
    
    $Payload = @{
        displayName = $DataStoreName
        industryVertical = "GENERIC"
        solutionTypes = @("SOLUTION_TYPE_SEARCH")
        contentConfig = "CONTENT_REQUIRED"
    } | ConvertTo-Json -Depth 10
    
    Write-Debug "Creating data store with URL: $CreateUrl"
    Write-Debug "Payload: $Payload"
    
    try {
        $Response = Invoke-RestMethod -Uri $CreateUrl -Headers @{
            "Authorization" = "Bearer ${AccessToken}"
            "Content-Type" = "application/json"
        } -Method Post -Body $Payload -ErrorAction Stop
        
        if ($Response.name) {
            Write-Success "Created data store: ${DataStoreName} (Path: $($Response.name))"
            return $Response.name
        } else {
            Write-Error "Failed to create data store: ${DataStoreName} - No name in response"
            return $null
        }
    } catch {
        Write-Error "Error creating data store ${DataStoreName}: $($_.Exception.Message)"
        if ($_.Exception.Response) {
            $StatusCode = $_.Exception.Response.StatusCode
            Write-Error "HTTP Status: $StatusCode"
            
            # Try to get more details from the response
            try {
                $ErrorResponse = $_.Exception.Response.GetResponseStream()
                $Reader = New-Object System.IO.StreamReader($ErrorResponse)
                $ErrorBody = $Reader.ReadToEnd()
                Write-Error "Error details: $ErrorBody"
            } catch {
                Write-Debug "Could not read error response details"
            }
        }
        return $null
    }
}

# Function to create GCS connector using REST API
function New-GCSConnector {
    param(
        [string]$DataStorePath,
        [string]$RagId
    )
    
    $BucketName = "${BucketPrefix}-${RagId}-${ProjectId}"
    $ConnectorName = "${RagId}-gcs-connector"
    $ConnectorId = "${RagId}_gcs_connector"
    
    Write-Processing "Creating GCS connector for bucket: ${BucketName}"
    
    $AccessToken = Get-AccessToken
    if (-not $AccessToken) {
        Write-Error "No access token available"
        return $false
    }
    
    # Check if connector already exists
    $CheckUrl = "https://discoveryengine.googleapis.com/v1beta/${DataStorePath}/connectors"
    
    try {
        Write-Debug "Checking existing connectors..."
        $ExistingConnectors = Invoke-RestMethod -Uri $CheckUrl -Headers @{
            "Authorization" = "Bearer ${AccessToken}"
            "Content-Type" = "application/json"
        } -Method Get -ErrorAction Stop
        
        if ($ExistingConnectors.connectors -and $ExistingConnectors.connectors.Count -gt 0) {
            foreach ($connector in $ExistingConnectors.connectors) {
                if ($connector.displayName -eq $ConnectorName) {
                    Write-Warning "Connector ${ConnectorName} already exists, skipping..."
                    return $true
                }
            }
        }
    } catch {
        Write-Debug "Error checking existing connectors: $($_.Exception.Message)"
    }
    
    # Create GCS connector
    $CreateUrl = "https://discoveryengine.googleapis.com/v1beta/${DataStorePath}/connectors?connectorId=${ConnectorId}"
    
    $Payload = @{
        displayName = $ConnectorName
        gcsSource = @{
            inputUris = @("gs://${BucketName}/*")
            dataSchema = "content"
        }
    } | ConvertTo-Json -Depth 10
    
    Write-Debug "Creating GCS connector with URL: $CreateUrl"
    Write-Debug "Payload: $Payload"
    
    try {
        $Response = Invoke-RestMethod -Uri $CreateUrl -Headers @{
            "Authorization" = "Bearer ${AccessToken}"
            "Content-Type" = "application/json"
        } -Method Post -Body $Payload -ErrorAction Stop
        
        if ($Response.name) {
            Write-Success "Created GCS connector: ${ConnectorName}"
            return $true
        } else {
            Write-Error "Failed to create GCS connector: ${ConnectorName} - No name in response"
            return $false
        }
    } catch {
        Write-Error "Error creating GCS connector ${ConnectorName}: $($_.Exception.Message)"
        if ($_.Exception.Response) {
            $StatusCode = $_.Exception.Response.StatusCode
            Write-Error "HTTP Status: $StatusCode"
        }
        return $false
    }
}

# Function to create search app using REST API
function New-SearchApp {
    param(
        [string]$DataStorePath,
        [string]$RagId,
        [string]$RagName
    )
    
    $SearchAppName = "${RagId}-search-app"
    $SearchAppId = "${RagId}_search_app"
    
    Write-Processing "Creating search app: ${SearchAppName}"
    
    $AccessToken = Get-AccessToken
    if (-not $AccessToken) {
        Write-Error "No access token available"
        return $null
    }
    
    # Check if search app already exists
    $CheckUrl = "https://discoveryengine.googleapis.com/v1beta/projects/${ProjectId}/locations/${Location}/engines"
    
    try {
        Write-Debug "Checking existing search apps..."
        $ExistingApps = Invoke-RestMethod -Uri "${CheckUrl}?filter=displayName%3D%22${SearchAppName}%22" -Headers @{
            "Authorization" = "Bearer ${AccessToken}"
            "Content-Type" = "application/json"
        } -Method Get -ErrorAction Stop
        
        if ($ExistingApps.engines -and $ExistingApps.engines.Count -gt 0) {
            foreach ($app in $ExistingApps.engines) {
                if ($app.displayName -eq $SearchAppName) {
                    Write-Warning "Search app ${SearchAppName} already exists, skipping..."
                    return $app.name
                }
            }
        }
    } catch {
        Write-Debug "Error checking existing search apps: $($_.Exception.Message)"
    }
    
    # Create search app
    $CreateUrl = "https://discoveryengine.googleapis.com/v1beta/projects/${ProjectId}/locations/${Location}/engines?engineId=${SearchAppId}"
    
    $DataStoreId = $DataStorePath.Split('/')[-1]
    
    $Payload = @{
        displayName = $SearchAppName
        solutionType = "SOLUTION_TYPE_SEARCH"
        searchEngineConfig = @{
            searchTier = "SEARCH_TIER_STANDARD"
            searchAddOns = @("SEARCH_ADD_ON_LLM")
        }
        dataStoreIds = @($DataStoreId)
    } | ConvertTo-Json -Depth 10
    
    Write-Debug "Creating search app with URL: $CreateUrl"
    Write-Debug "Payload: $Payload"
    
    try {
        $Response = Invoke-RestMethod -Uri $CreateUrl -Headers @{
            "Authorization" = "Bearer ${AccessToken}"
            "Content-Type" = "application/json"
        } -Method Post -Body $Payload -ErrorAction Stop
        
        if ($Response.name) {
            Write-Success "Created search app: ${SearchAppName} (Path: $($Response.name))"
            return $Response.name
        } else {
            Write-Error "Failed to create search app: ${SearchAppName} - No name in response"
            return $null
        }
    } catch {
        Write-Error "Error creating search app ${SearchAppName}: $($_.Exception.Message)"
        if ($_.Exception.Response) {
            $StatusCode = $_.Exception.Response.StatusCode
            Write-Error "HTTP Status: $StatusCode"
        }
        return $null
    }
}

# Function to create complete RAG infrastructure
function New-RAGComplete {
    param(
        [string]$RagId,
        [string]$RagName,
        [string]$RagDescription
    )
    
    Write-Processing "Creating complete RAG infrastructure for ${RagName} (${RagId})"
    
    # Step 1: Create Cloud Storage bucket
    if (-not (New-Bucket $RagId)) {
        Write-Error "Failed to create bucket for ${RagId}"
        return $false
    }
    
    # Step 2: Create data store
    $DataStorePath = New-DataStore $RagId $RagName $RagDescription
    if (-not $DataStorePath) {
        Write-Error "Failed to create data store for ${RagId}"
        return $false
    }
    
    # Step 3: Create GCS connector
    if (-not (New-GCSConnector $DataStorePath $RagId)) {
        Write-Error "Failed to create GCS connector for ${RagId}"
        return $false
    }
    
    # Step 4: Create search app
    $SearchAppPath = New-SearchApp $DataStorePath $RagId $RagName
    if (-not $SearchAppPath) {
        Write-Error "Failed to create search app for ${RagId}"
        return $false
    }
    
    Write-Success "✅ Successfully created complete RAG infrastructure for ${RagName} (${RagId})"
    return $true
}

# Main execution function
function Start-RAGCreation {
    Write-Status "Starting RAG corpus creation for CoolBits.ai using PowerShell and REST API..."
    Write-Status "Project: ${ProjectId}"
    Write-Status "Location: ${Location}"
    Write-Status "Total RAGs to create: 1 (Test run)"
    
    # Test API access first
    if (-not (Test-APIAccess)) {
        Write-Error "API access test failed. Please check your permissions and try again."
        return
    }
    
    $Successful = 0
    $Total = 0
    
    # Test with just one RAG first
    Write-Status "Test run: Creating AI Board RAG..."
    
    $TestRag = @{
        Id = "ai_board"
        Name = "AI Board"
        Description = "AI Board management and coordination"
    }
    
    $Total++
    
    Write-Host ""
    Write-Status "=================================================="
    Write-Status "Processing: $($TestRag.Name) ($($TestRag.Id))"
    Write-Status "=================================================="
    
    if (New-RAGComplete -RagId $TestRag.Id -RagName $TestRag.Name -RagDescription $TestRag.Description) {
        $Successful++
    }
    
    # Final summary
    Write-Host ""
    Write-Status "============================================================"
    Write-Status "=== FINAL SUMMARY ==="
    Write-Status "============================================================"
    Write-Success "Total RAGs processed: ${Total}"
    Write-Success "Successful creations: ${Successful}"
    Write-Success "Failed creations: $($Total - $Successful)"
    
    if ($Successful -eq $Total) {
        Write-Success "🎉 Test RAG created successfully! Ready to create all RAGs."
    } else {
        Write-Warning "⚠️  Test RAG creation failed. Check logs above for details."
    }
    
    Write-Status "Next steps:"
    Write-Status "1. If test successful, run full script with all RAGs"
    Write-Status "2. Upload industry-specific documents to Cloud Storage buckets"
    Write-Status "3. Wait for corpus indexing to complete"
    Write-Status "4. Test RAG queries through API endpoints"
}

# Run the main function
Start-RAGCreation
