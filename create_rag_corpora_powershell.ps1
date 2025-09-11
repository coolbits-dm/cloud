# Enhanced RAG Corpus Creation Script for CoolBits.ai using PowerShell and REST API
# Creates buckets first, then RAG infrastructure

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

# Function to get access token
function Get-AccessToken {
    gcloud auth print-access-token
}

# Function to create Cloud Storage bucket
function New-Bucket {
    param([string]$RagId)
    
    $BucketName = "${BucketPrefix}-${RagId}-${ProjectId}"
    
    Write-Processing "Creating bucket: ${BucketName}"
    
    # Check if bucket already exists
    try {
        $ExistingBuckets = gcloud storage buckets list --filter="name:${BucketName}" --format="value(name)" 2>$null
        if ($ExistingBuckets) {
            Write-Warning "Bucket ${BucketName} already exists, skipping..."
            return $true
        }
    } catch {
        # Continue if check fails
    }
    
    # Create bucket
    try {
        $Result = gcloud storage buckets create gs://${BucketName} --project=$ProjectId --location=$Region
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Created bucket: ${BucketName}"
            return $true
        } else {
            Write-Error "Failed to create bucket: ${BucketName}"
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
    
    # Check if data store already exists
    $AccessToken = Get-AccessToken
    $CheckUrl = "https://discoveryengine.googleapis.com/v1beta/projects/${ProjectId}/locations/${Location}/dataStores"
    
    try {
        $ExistingStores = Invoke-RestMethod -Uri "${CheckUrl}?filter=displayName%3D%22${DataStoreName}%22" -Headers @{
            "Authorization" = "Bearer ${AccessToken}"
            "Content-Type" = "application/json"
        } -Method Get
        
        if ($ExistingStores.dataStores -and $ExistingStores.dataStores.displayName -contains $DataStoreName) {
            Write-Warning "Data store ${DataStoreName} already exists, skipping..."
            return $true
        }
    } catch {
        # Continue if check fails
    }
    
    # Create data store
    $CreateUrl = "https://discoveryengine.googleapis.com/v1beta/projects/${ProjectId}/locations/${Location}/dataStores?dataStoreId=${DataStoreId}"
    
    $Payload = @{
        displayName = $DataStoreName
        industryVertical = "GENERIC"
        solutionTypes = @("SOLUTION_TYPE_SEARCH")
        contentConfig = "CONTENT_REQUIRED"
    } | ConvertTo-Json
    
    try {
        $Response = Invoke-RestMethod -Uri $CreateUrl -Headers @{
            "Authorization" = "Bearer ${AccessToken}"
            "Content-Type" = "application/json"
        } -Method Post -Body $Payload
        
        if ($Response.name) {
            Write-Success "Created data store: ${DataStoreName} (Path: $($Response.name))"
            return $Response.name
        } else {
            Write-Error "Failed to create data store: ${DataStoreName}"
            return $null
        }
    } catch {
        Write-Error "Error creating data store ${DataStoreName}: $($_.Exception.Message)"
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
    
    # Check if connector already exists
    $AccessToken = Get-AccessToken
    $CheckUrl = "https://discoveryengine.googleapis.com/v1beta/${DataStorePath}/connectors"
    
    try {
        $ExistingConnectors = Invoke-RestMethod -Uri $CheckUrl -Headers @{
            "Authorization" = "Bearer ${AccessToken}"
            "Content-Type" = "application/json"
        } -Method Get
        
        if ($ExistingConnectors.connectors -and $ExistingConnectors.connectors.displayName -contains $ConnectorName) {
            Write-Warning "Connector ${ConnectorName} already exists, skipping..."
            return $true
        }
    } catch {
        # Continue if check fails
    }
    
    # Create GCS connector
    $CreateUrl = "https://discoveryengine.googleapis.com/v1beta/${DataStorePath}/connectors?connectorId=${ConnectorId}"
    
    $Payload = @{
        displayName = $ConnectorName
        gcsSource = @{
            inputUris = @("gs://${BucketName}/*")
            dataSchema = "content"
        }
    } | ConvertTo-Json
    
    try {
        $Response = Invoke-RestMethod -Uri $CreateUrl -Headers @{
            "Authorization" = "Bearer ${AccessToken}"
            "Content-Type" = "application/json"
        } -Method Post -Body $Payload
        
        if ($Response.name) {
            Write-Success "Created GCS connector: ${ConnectorName}"
            return $true
        } else {
            Write-Error "Failed to create GCS connector: ${ConnectorName}"
            return $false
        }
    } catch {
        Write-Error "Error creating GCS connector ${ConnectorName}: $($_.Exception.Message)"
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
    
    # Check if search app already exists
    $AccessToken = Get-AccessToken
    $CheckUrl = "https://discoveryengine.googleapis.com/v1beta/projects/${ProjectId}/locations/${Location}/engines"
    
    try {
        $ExistingApps = Invoke-RestMethod -Uri "${CheckUrl}?filter=displayName%3D%22${SearchAppName}%22" -Headers @{
            "Authorization" = "Bearer ${AccessToken}"
            "Content-Type" = "application/json"
        } -Method Get
        
        if ($ExistingApps.engines -and $ExistingApps.engines.displayName -contains $SearchAppName) {
            Write-Warning "Search app ${SearchAppName} already exists, skipping..."
            return $true
        }
    } catch {
        # Continue if check fails
    }
    
    # Create search app
    $CreateUrl = "https://discoveryengine.googleapis.com/v1beta/projects/${ProjectId}/locations/${Location}/engines?engineId=${SearchAppId}"
    
    $Payload = @{
        displayName = $SearchAppName
        solutionType = "SOLUTION_TYPE_SEARCH"
        searchEngineConfig = @{
            searchTier = "SEARCH_TIER_STANDARD"
            searchAddOns = @("SEARCH_ADD_ON_LLM")
        }
        dataStoreIds = @($DataStorePath.Split('/')[-1])
    } | ConvertTo-Json
    
    try {
        $Response = Invoke-RestMethod -Uri $CreateUrl -Headers @{
            "Authorization" = "Bearer ${AccessToken}"
            "Content-Type" = "application/json"
        } -Method Post -Body $Payload
        
        if ($Response.name) {
            Write-Success "Created search app: ${SearchAppName} (Path: $($Response.name))"
            return $Response.name
        } else {
            Write-Error "Failed to create search app: ${SearchAppName}"
            return $null
        }
    } catch {
        Write-Error "Error creating search app ${SearchAppName}: $($_.Exception.Message)"
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
    Write-Status "Total RAGs to create: 10 (Phase 1 + 2)"
    
    $Successful = 0
    $Total = 0
    
    # Phase 1: High Priority RAGs (5 RAGs)
    Write-Status "Phase 1: Creating high priority RAGs..."
    
    $Phase1Rags = @(
        @{Id="ai_board"; Name="AI Board"; Description="AI Board management and coordination"},
        @{Id="business"; Name="Business AI Council"; Description="Business AI Council for strategic decisions"},
        @{Id="agritech"; Name="AgTech"; Description="Agricultural Technology and Innovation"},
        @{Id="banking"; Name="Banking"; Description="Commercial and Retail Banking Services"},
        @{Id="saas_b2b"; Name="SaaS B2B"; Description="Business-to-Business Software as a Service"}
    )
    
    foreach ($RagInfo in $Phase1Rags) {
        $Total++
        
        Write-Host ""
        Write-Status "=================================================="
        Write-Status "Processing: $($RagInfo.Name) ($($RagInfo.Id))"
        Write-Status "=================================================="
        
        if (New-RAGComplete -RagId $RagInfo.Id -RagName $RagInfo.Name -RagDescription $RagInfo.Description) {
            $Successful++
        }
        
        # Add delay between creations to avoid rate limiting
        Start-Sleep -Seconds 2
    }
    
    # Phase 2: Medium Priority RAGs (5 RAGs)
    Write-Status "Phase 2: Creating medium priority RAGs..."
    
    $Phase2Rags = @(
        @{Id="healthcare"; Name="Healthcare"; Description="Healthcare Services and Medical Technology"},
        @{Id="exchanges"; Name="Exchanges"; Description="Cryptocurrency Exchanges"},
        @{Id="user"; Name="User"; Description="Personal AI Assistant for users"},
        @{Id="agency"; Name="Agency"; Description="Agency Management AI"},
        @{Id="dev"; Name="Dev"; Description="Developer Tools AI"}
    )
    
    foreach ($RagInfo in $Phase2Rags) {
        $Total++
        
        Write-Host ""
        Write-Status "=================================================="
        Write-Status "Processing: $($RagInfo.Name) ($($RagInfo.Id))"
        Write-Status "=================================================="
        
        if (New-RAGComplete -RagId $RagInfo.Id -RagName $RagInfo.Name -RagDescription $RagInfo.Description) {
            $Successful++
        }
        
        # Add delay between creations to avoid rate limiting
        Start-Sleep -Seconds 2
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
        Write-Success "🎉 All RAG corpora created successfully!"
    } else {
        Write-Warning "⚠️  Some RAG creations failed. Check logs above."
    }
    
    Write-Status "Next steps:"
    Write-Status "1. Upload industry-specific documents to Cloud Storage buckets"
    Write-Status "2. Wait for corpus indexing to complete"
    Write-Status "3. Test RAG queries through API endpoints"
    Write-Status "4. Integrate with Business Panel"
}

# Run the main function
Start-RAGCreation
