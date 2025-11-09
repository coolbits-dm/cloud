# PowerShell script to check existing Search Apps and Data Stores
# Based on the cblm-search app you created

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

# Function to check Data Stores
function Get-DataStores {
    param([string]$AccessToken)
    
    Write-Processing "Checking Data Stores in Discovery Engine..."
    
    $url = "https://discoveryengine.googleapis.com/v1beta/projects/${ProjectId}/locations/${Location}/dataStores"
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Get -Headers @{
            "Authorization" = "Bearer $AccessToken"
            "Content-Type" = "application/json"
        } -ErrorAction Stop
        
        if ($response.dataStores) {
            Write-Success "Found $($response.dataStores.Count) Data Stores:"
            foreach ($store in $response.dataStores) {
                Write-Host "  - Name: $($store.displayName)" -ForegroundColor $Green
                Write-Host "    ID: $($store.name)" -ForegroundColor $Cyan
                Write-Host "    Industry: $($store.industryVertical)" -ForegroundColor $Yellow
                Write-Host ""
            }
        } else {
            Write-Warning "No Data Stores found."
        }
        
        return $response.dataStores
    } catch {
        Write-Error "Error checking Data Stores: $($_.Exception.Message)"
        return $null
    }
}

# Function to check Search Apps
function Get-SearchApps {
    param([string]$AccessToken)
    
    Write-Processing "Checking Search Apps in Discovery Engine..."
    
    $url = "https://discoveryengine.googleapis.com/v1beta/projects/${ProjectId}/locations/${Location}/searchApps"
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Get -Headers @{
            "Authorization" = "Bearer $AccessToken"
            "Content-Type" = "application/json"
        } -ErrorAction Stop
        
        if ($response.searchApps) {
            Write-Success "Found $($response.searchApps.Count) Search Apps:"
            foreach ($app in $response.searchApps) {
                Write-Host "  - Name: $($app.displayName)" -ForegroundColor $Green
                Write-Host "    ID: $($app.name)" -ForegroundColor $Cyan
                Write-Host "    Data Stores: $($app.dataStoreIds -join ', ')" -ForegroundColor $Yellow
                Write-Host ""
            }
        } else {
            Write-Warning "No Search Apps found."
        }
        
        return $response.searchApps
    } catch {
        Write-Error "Error checking Search Apps: $($_.Exception.Message)"
        return $null
    }
}

# Function to check Engines
function Get-Engines {
    param([string]$AccessToken)
    
    Write-Processing "Checking Engines in Discovery Engine..."
    
    $url = "https://discoveryengine.googleapis.com/v1beta/projects/${ProjectId}/locations/${Location}/engines"
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Get -Headers @{
            "Authorization" = "Bearer $AccessToken"
            "Content-Type" = "application/json"
        } -ErrorAction Stop
        
        if ($response.engines) {
            Write-Success "Found $($response.engines.Count) Engines:"
            foreach ($engine in $response.engines) {
                Write-Host "  - Name: $($engine.displayName)" -ForegroundColor $Green
                Write-Host "    ID: $($engine.name)" -ForegroundColor $Cyan
                Write-Host "    Solution Type: $($engine.solutionType)" -ForegroundColor $Yellow
                Write-Host ""
            }
        } else {
            Write-Warning "No Engines found."
        }
        
        return $response.engines
    } catch {
        Write-Error "Error checking Engines: $($_.Exception.Message)"
        return $null
    }
}

# Main execution
function Main {
    Write-Status "🔍 Checking existing Discovery Engine infrastructure for CoolBits.ai..."
    Write-Status "Project: $ProjectId"
    Write-Status "Location: $Location"
    Write-Status ""

    $accessToken = Get-AccessToken
    if (-not $accessToken) {
        Write-Error "Cannot proceed without an access token."
        return
    }

    # Check existing infrastructure
    $dataStores = Get-DataStores -AccessToken $accessToken
    $searchApps = Get-SearchApps -AccessToken $accessToken
    $engines = Get-Engines -AccessToken $accessToken

    Write-Status ""
    Write-Status "📊 SUMMARY:"
    Write-Status "==========="
    $dataStoreCount = if ($dataStores) { $dataStores.Count } else { 0 }
    $searchAppCount = if ($searchApps) { $searchApps.Count } else { 0 }
    $engineCount = if ($engines) { $engines.Count } else { 0 }
    
    Write-Host "Data Stores: $dataStoreCount" -ForegroundColor $Blue
    Write-Host "Search Apps: $searchAppCount" -ForegroundColor $Blue
    Write-Host "Engines: $engineCount" -ForegroundColor $Blue
    
    Write-Status ""
    Write-Status "🎯 NEXT STEPS:"
    Write-Status "=============="
    Write-Host "1. If you have existing Search Apps, we can integrate RAG corpora with them" -ForegroundColor $Green
    Write-Host "2. Create Vector Search indexes for RAG embeddings" -ForegroundColor $Green
    Write-Host "3. Set up Agent Garden and Agent Engine components" -ForegroundColor $Green
    Write-Host "4. Configure RAG endpoints for each industry/role" -ForegroundColor $Green
}

# Run the main function
Main
