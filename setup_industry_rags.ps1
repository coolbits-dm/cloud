# Setup RAG infrastructure for all industries in CoolBits.ai
# PowerShell version for Windows

param(
    [string]$ProjectId = "coolbits-ai",
    [string]$Region = "europe-west3",
    [string]$BucketPrefix = "coolbits-rag"
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"

# Function to print colored output
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

# Function to create Cloud Storage bucket
function New-IndustryBucket {
    param(
        [string]$IndustryId
    )
    
    $BucketName = "$BucketPrefix-$IndustryId-$ProjectId"
    
    Write-Status "Creating bucket for $IndustryId : $BucketName"
    
    try {
        # Check if bucket exists
        $ExistingBuckets = gcloud storage buckets list --filter="name:$BucketName" --format="value(name)" 2>$null
        if ($ExistingBuckets) {
            Write-Warning "Bucket $BucketName already exists"
            return $true
        }
        
        # Create bucket
        $Result = gcloud storage buckets create gs://$BucketName --project=$ProjectId --location=$Region
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Created bucket: $BucketName"
            return $true
        } else {
            Write-Error "Failed to create bucket: $BucketName"
            return $false
        }
    } catch {
        Write-Error "Error creating bucket $BucketName : $($_.Exception.Message)"
        return $false
    }
}

# Function to upload sample documents
function Add-IndustryDocuments {
    param(
        [string]$IndustryId
    )
    
    $BucketName = "$BucketPrefix-$IndustryId-$ProjectId"
    
    Write-Status "Uploading sample documents for $IndustryId"
    
    try {
        # Create sample document content
        $SampleDoc = "sample_${IndustryId}_document.txt"
        $Content = @"
# $($IndustryId.ToUpper()) Industry Documentation

## Industry Overview
This is a sample document for the $IndustryId industry RAG system.

## Key Topics
- Industry-specific knowledge
- Best practices
- Market trends
- Regulatory information

## Sample Content
This document contains placeholder content for RAG integration.
Replace with actual industry-specific documentation.

Generated on: $(Get-Date)
"@
        
        $Content | Out-File -FilePath $SampleDoc -Encoding UTF8
        
        # Upload to bucket
        $Result = gcloud storage cp $SampleDoc gs://$BucketName/
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Uploaded sample document for $IndustryId"
            Remove-Item $SampleDoc
            return $true
        } else {
            Write-Error "Failed to upload document for $IndustryId"
            Remove-Item $SampleDoc -ErrorAction SilentlyContinue
            return $false
        }
    } catch {
        Write-Error "Error uploading documents for $IndustryId : $($_.Exception.Message)"
        return $false
    }
}

# Function to create Vertex AI Search app
function New-SearchApp {
    param(
        [string]$IndustryId
    )
    
    Write-Status "Creating Vertex AI Search app for $IndustryId"
    
    # This would create a Vertex AI Search app
    # Implementation depends on Vertex AI Search API
    Write-Warning "Vertex AI Search app creation not implemented yet"
    return $true
}

# Function to set up RAG for a single industry
function Set-IndustryRAG {
    param(
        [string]$IndustryId
    )
    
    Write-Status "Setting up RAG for industry: $IndustryId"
    
    # Create bucket
    if (-not (New-IndustryBucket $IndustryId)) {
        return $false
    }
    
    # Upload documents
    if (-not (Add-IndustryDocuments $IndustryId)) {
        return $false
    }
    
    # Create search app
    if (-not (New-SearchApp $IndustryId)) {
        return $false
    }
    
    Write-Success "RAG setup complete for $IndustryId"
    return $true
}

# Function to check prerequisites
function Test-Prerequisites {
    try {
        # Check if gcloud is installed
        $GcloudVersion = gcloud version 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Error "gcloud CLI is not installed"
            return $false
        }
        
        # Check if gsutil is installed
        $GsutilVersion = gcloud storage --version 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Error "gcloud storage is not available"
            return $false
        }
        
        # Check authentication
        $AuthStatus = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
        if (-not $AuthStatus) {
            Write-Error "No active gcloud authentication found"
            return $false
        }
        
        Write-Success "Prerequisites check passed"
        return $true
    } catch {
        Write-Error "Error checking prerequisites: $($_.Exception.Message)"
        return $false
    }
}

# Main execution
function Start-IndustryRAGSetup {
    Write-Status "Starting RAG setup for all industries..."
    
    # List of all industries
    $Industries = @(
        "agritech", "agri_inputs", "food_bev_mfg", "foodservice",
        "oil_gas", "power_gen", "renewables", "water_wastewater",
        "industrial_equipment", "electronics_mfg", "automation_robotics",
        "residential_construction", "commercial_construction", "proptech_realestate",
        "freight_logistics", "maritime_ports", "rail_logistics", "auto_oem", "ev_charging", "aftermarket_service",
        "commercial_aviation", "defense", "space_newspace",
        "hospitals_clinics", "med_devices", "digital_health", "pharma_branded", "generics", "biotech_cro_cdmo",
        "grocery_retail", "fashion_retail", "marketplaces_d2c", "personal_care_fmcg", "household_fmcg", "beverages_snacks",
        "hotels_resorts", "airlines_travel", "otas_traveltech",
        "saas_b2b", "devtools_cloud", "ai_ml_platforms", "data_infra",
        "mobile_operators", "fixed_isp", "network_equipment",
        "banking", "payments_fintech", "wealth_asset", "capital_markets", "pnc_insurance", "life_health_insurance", "insurtech",
        "streaming_ott", "publishing", "music_sports_media",
        "k12_edtech", "higher_ed",
        "gov_services", "intl_aid", "foundations", "faith_based",
        "law_firms", "regtech_ediscovery", "ip_patents", "consulting", "accounting_audit", "hr_staffing", "marketing_agencies",
        "mssp", "identity_access", "threat_intel", "physical_security",
        "waste_management", "recycling_circular", "carbon_esg",
        "mining_metals", "cement_glass", "specialty_chem",
        "clubs_leagues", "fitness_wellness", "gaming_esports", "beauty_cosmetics", "home_improvement", "smart_home",
        "exchanges", "defi", "wallets_infra"
    )
    
    $Successful = 0
    $Total = $Industries.Count
    
    Write-Status "Setting up RAG for $Total industries..."
    
    foreach ($Industry in $Industries) {
        if (Set-IndustryRAG $Industry) {
            $Successful++
        } else {
            Write-Error "Failed to set up RAG for $Industry"
        }
    }
    
    Write-Status "RAG setup complete!"
    Write-Success "Successfully configured: $Successful/$Total industries"
    
    if ($Successful -eq $Total) {
        Write-Success "All industries configured successfully! 🎉"
    } else {
        Write-Warning "Some industries failed to configure. Check logs above."
    }
}

# Run the script
Write-Host "🚀 Setting up RAG infrastructure for all industries..." -ForegroundColor $Green

if (Test-Prerequisites) {
    Start-IndustryRAGSetup
} else {
    Write-Error "Prerequisites check failed. Exiting."
    exit 1
}
