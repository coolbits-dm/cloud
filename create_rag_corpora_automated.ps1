# Automated RAG Corpus Creation Script for CoolBits.ai (PowerShell)
# Creates all 88 RAG corpora using gcloud CLI

param(
    [string]$ProjectId = "coolbits-ai",
    [string]$Region = "europe-west1",
    [string]$BucketPrefix = "coolbits-rag"
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"
$Cyan = "Cyan"

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

function Write-Processing {
    param([string]$Message)
    Write-Host "[PROCESSING] $Message" -ForegroundColor $Cyan
}

# Function to create a single RAG corpus
function New-RAGCorpus {
    param(
        [string]$RagId,
        [string]$RagName,
        [string]$RagDescription
    )
    
    $CorpusName = "${RagId}-corpus"
    $BucketName = "${BucketPrefix}-${RagId}-${ProjectId}"
    
    Write-Processing "Creating corpus for ${RagName} (${RagId})"
    
    # Check if corpus already exists
    try {
        $ExistingCorpus = gcloud alpha ai rag-corpora list --project=$ProjectId --region=$Region --filter="displayName:${CorpusName}" --format="value(name)" 2>$null
        if ($ExistingCorpus) {
            Write-Warning "Corpus ${CorpusName} already exists, skipping..."
            return $true
        }
    } catch {
        # Continue if check fails
    }
    
    # Create the corpus
    Write-Status "Creating corpus: ${CorpusName}"
    
    try {
        $CorpusId = gcloud alpha ai rag-corpora create `
            --project=$ProjectId `
            --region=$Region `
            --display-name="${CorpusName}" `
            --description="${RagDescription}" `
            --embedding-model-publisher="google" `
            --embedding-model-name="text-embedding-004" `
            --embedding-model-version="1" `
            --format="value(name)" 2>$null
        
        if ($LASTEXITCODE -eq 0 -and $CorpusId) {
            Write-Success "Created corpus: ${CorpusName} (ID: ${CorpusId})"
            
            # Create data source pointing to Cloud Storage bucket
            Write-Status "Creating data source for bucket: ${BucketName}"
            
            try {
                gcloud alpha ai rag-corpora data-sources create `
                    --project=$ProjectId `
                    --region=$Region `
                    --rag-corpus=$CorpusId `
                    --display-name="${RagId}-data-source" `
                    --gcs-source="gs://${BucketName}/" `
                    --file-type="PDF,TXT,DOC,DOCX" `
                    --chunk-size=1024 `
                    --chunk-overlap=200 `
                    --format="value(name)" >$null 2>&1
                
                if ($LASTEXITCODE -eq 0) {
                    Write-Success "Created data source for ${BucketName}"
                } else {
                    Write-Warning "Data source creation failed for ${BucketName} (bucket may not exist yet)"
                }
            } catch {
                Write-Warning "Data source creation failed for ${BucketName}: $($_.Exception.Message)"
            }
            
            return $true
        } else {
            Write-Error "Failed to create corpus: ${CorpusName}"
            return $false
        }
    } catch {
        Write-Error "Error creating corpus ${CorpusName}: $($_.Exception.Message)"
        return $false
    }
}

# Function to create Search App for a corpus
function New-SearchApp {
    param(
        [string]$RagId,
        [string]$RagName
    )
    
    $SearchAppName = "${RagId}-search-app"
    
    Write-Processing "Creating search app for ${RagName} (${RagId})"
    
    # Check if search app already exists
    try {
        $ExistingSearchApp = gcloud alpha ai rag-corpora search-apps list --project=$ProjectId --region=$Region --filter="displayName:${SearchAppName}" --format="value(name)" 2>$null
        if ($ExistingSearchApp) {
            Write-Warning "Search app ${SearchAppName} already exists, skipping..."
            return $true
        }
    } catch {
        # Continue if check fails
    }
    
    # Get corpus ID
    $CorpusName = "${RagId}-corpus"
    try {
        $CorpusId = gcloud alpha ai rag-corpora list --project=$ProjectId --region=$Region --filter="displayName:${CorpusName}" --format="value(name)" 2>$null | Select-Object -First 1
        
        if (-not $CorpusId) {
            Write-Error "Corpus ${CorpusName} not found, cannot create search app"
            return $false
        }
        
        # Create search app
        $SearchAppId = gcloud alpha ai rag-corpora search-apps create `
            --project=$ProjectId `
            --region=$Region `
            --rag-corpus=$CorpusId `
            --display-name="${SearchAppName}" `
            --description="Search app for ${RagName}" `
            --format="value(name)" 2>$null
        
        if ($LASTEXITCODE -eq 0 -and $SearchAppId) {
            Write-Success "Created search app: ${SearchAppName} (ID: ${SearchAppId})"
            return $true
        } else {
            Write-Error "Failed to create search app: ${SearchAppName}"
            return $false
        }
    } catch {
        Write-Error "Error creating search app ${SearchAppName}: $($_.Exception.Message)"
        return $false
    }
}

# Main execution function
function Start-RAGCreation {
    Write-Status "Starting RAG corpus creation for CoolBits.ai..."
    Write-Status "Project: ${ProjectId}"
    Write-Status "Region: ${Region}"
    Write-Status "Total RAGs to create: 88"
    
    $SuccessfulCorpora = 0
    $SuccessfulSearchApps = 0
    $TotalRags = 0
    
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
        $TotalRags++
        
        if (New-RAGCorpus -RagId $RagInfo.Id -RagName $RagInfo.Name -RagDescription $RagInfo.Description) {
            $SuccessfulCorpora++
        }
        
        if (New-SearchApp -RagId $RagInfo.Id -RagName $RagInfo.Name) {
            $SuccessfulSearchApps++
        }
        
        Write-Host ""
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
        $TotalRags++
        
        if (New-RAGCorpus -RagId $RagInfo.Id -RagName $RagInfo.Name -RagDescription $RagInfo.Description) {
            $SuccessfulCorpora++
        }
        
        if (New-SearchApp -RagId $RagInfo.Id -RagName $RagInfo.Name) {
            $SuccessfulSearchApps++
        }
        
        Write-Host ""
    }
    
    # Phase 3: All remaining Industry RAGs (75 RAGs)
    Write-Status "Phase 3: Creating all remaining industry RAGs..."
    
    $IndustryRags = @(
        @{Id="agri_inputs"; Name="Agri Inputs"; Description="Agricultural Inputs and Supplies"},
        @{Id="aftermarket_service"; Name="Aftermarket Service"; Description="Aftermarket Services"},
        @{Id="capital_markets"; Name="Capital Markets"; Description="Capital Markets and Investment Banking"},
        @{Id="payments_fintech"; Name="Payments FinTech"; Description="Payments and Financial Technology"},
        @{Id="wealth_asset"; Name="Wealth Asset"; Description="Wealth and Asset Management"},
        @{Id="insurtech"; Name="InsurTech"; Description="Insurance Technology"},
        @{Id="defi"; Name="DeFi"; Description="Decentralized Finance"},
        @{Id="ai_ml_platforms"; Name="AI ML Platforms"; Description="AI and Machine Learning Platforms"},
        @{Id="devtools_cloud"; Name="DevTools Cloud"; Description="Developer Tools and Cloud Services"},
        @{Id="data_infra"; Name="Data Infrastructure"; Description="Data Infrastructure and Analytics"},
        @{Id="identity_access"; Name="Identity Access"; Description="Identity and Access Management"},
        @{Id="threat_intel"; Name="Threat Intelligence"; Description="Threat Intelligence and Security"},
        @{Id="mssp"; Name="MSSP"; Description="Managed Security Service Providers"},
        @{Id="physical_security"; Name="Physical Security"; Description="Physical Security Solutions"},
        @{Id="digital_health"; Name="Digital Health"; Description="Digital Health Solutions"},
        @{Id="hospitals_clinics"; Name="Hospitals Clinics"; Description="Hospitals and Clinics"},
        @{Id="med_devices"; Name="Medical Devices"; Description="Medical Devices"},
        @{Id="pharma_branded"; Name="Pharma Branded"; Description="Branded Pharmaceuticals"},
        @{Id="generics"; Name="Generics"; Description="Generic Pharmaceuticals"},
        @{Id="biotech_cro_cdmo"; Name="Biotech CRO CDMO"; Description="Biotechnology and Contract Research"},
        @{Id="electronics_mfg"; Name="Electronics Manufacturing"; Description="Electronics Manufacturing"},
        @{Id="automation_robotics"; Name="Automation Robotics"; Description="Automation and Robotics"},
        @{Id="industrial_equipment"; Name="Industrial Equipment"; Description="Industrial Equipment"},
        @{Id="auto_oem"; Name="Auto OEM"; Description="Automotive Original Equipment Manufacturers"},
        @{Id="food_bev_mfg"; Name="Food Bev Manufacturing"; Description="Food and Beverage Manufacturing"},
        @{Id="cement_glass"; Name="Cement Glass"; Description="Cement and Glass Manufacturing"},
        @{Id="specialty_chem"; Name="Specialty Chemicals"; Description="Specialty Chemicals"},
        @{Id="mining_metals"; Name="Mining Metals"; Description="Mining and Metals"},
        @{Id="power_gen"; Name="Power Generation"; Description="Power Generation"},
        @{Id="renewables"; Name="Renewables"; Description="Renewable Energy"},
        @{Id="oil_gas"; Name="Oil Gas"; Description="Oil and Gas"},
        @{Id="water_wastewater"; Name="Water Wastewater"; Description="Water and Wastewater Management"},
        @{Id="waste_management"; Name="Waste Management"; Description="Waste Management"},
        @{Id="recycling_circular"; Name="Recycling Circular"; Description="Recycling and Circular Economy"},
        @{Id="carbon_esg"; Name="Carbon ESG"; Description="Carbon and ESG Solutions"},
        @{Id="ev_charging"; Name="EV Charging"; Description="Electric Vehicle Charging"},
        @{Id="freight_logistics"; Name="Freight Logistics"; Description="Freight and Logistics"},
        @{Id="rail_logistics"; Name="Rail Logistics"; Description="Rail Logistics"},
        @{Id="maritime_ports"; Name="Maritime Ports"; Description="Maritime and Ports"},
        @{Id="commercial_aviation"; Name="Commercial Aviation"; Description="Commercial Aviation"},
        @{Id="airlines_travel"; Name="Airlines Travel"; Description="Airlines and Travel"},
        @{Id="otas_traveltech"; Name="OTAs TravelTech"; Description="Online Travel Agencies and Travel Technology"},
        @{Id="proptech_realestate"; Name="PropTech Real Estate"; Description="Property Technology and Real Estate"},
        @{Id="commercial_construction"; Name="Commercial Construction"; Description="Commercial Construction"},
        @{Id="residential_construction"; Name="Residential Construction"; Description="Residential Construction"},
        @{Id="home_improvement"; Name="Home Improvement"; Description="Home Improvement"},
        @{Id="fashion_retail"; Name="Fashion Retail"; Description="Fashion and Retail"},
        @{Id="grocery_retail"; Name="Grocery Retail"; Description="Grocery Retail"},
        @{Id="marketplaces_d2c"; Name="Marketplaces D2C"; Description="Marketplaces and Direct-to-Consumer"},
        @{Id="beauty_cosmetics"; Name="Beauty Cosmetics"; Description="Beauty and Cosmetics"},
        @{Id="personal_care_fmcg"; Name="Personal Care FMCG"; Description="Personal Care and FMCG"},
        @{Id="household_fmcg"; Name="Household FMCG"; Description="Household FMCG"},
        @{Id="beverages_snacks"; Name="Beverages Snacks"; Description="Beverages and Snacks"},
        @{Id="foodservice"; Name="Food Service"; Description="Food Service"},
        @{Id="gaming_esports"; Name="Gaming Esports"; Description="Gaming and Esports"},
        @{Id="streaming_ott"; Name="Streaming OTT"; Description="Streaming and Over-the-Top Media"},
        @{Id="music_sports_media"; Name="Music Sports Media"; Description="Music, Sports, and Media"},
        @{Id="publishing"; Name="Publishing"; Description="Publishing"},
        @{Id="higher_ed"; Name="Higher Education"; Description="Higher Education"},
        @{Id="k12_edtech"; Name="K12 EdTech"; Description="K-12 Education Technology"},
        @{Id="consulting"; Name="Consulting"; Description="Consulting Services"},
        @{Id="law_firms"; Name="Law Firms"; Description="Law Firms"},
        @{Id="accounting_audit"; Name="Accounting Audit"; Description="Accounting and Audit"},
        @{Id="marketing_agencies"; Name="Marketing Agencies"; Description="Marketing Agencies"},
        @{Id="hr_staffing"; Name="HR Staffing"; Description="Human Resources and Staffing"},
        @{Id="gov_services"; Name="Government Services"; Description="Government Services"},
        @{Id="defense"; Name="Defense"; Description="Defense and Military"},
        @{Id="intl_aid"; Name="International Aid"; Description="International Aid"},
        @{Id="foundations"; Name="Foundations"; Description="Foundations"},
        @{Id="faith_based"; Name="Faith Based"; Description="Faith-Based Organizations"},
        @{Id="wallets_infra"; Name="Wallets Infrastructure"; Description="Cryptocurrency Wallets and Infrastructure"},
        @{Id="smart_home"; Name="Smart Home"; Description="Smart Home Technology"},
        @{Id="fitness_wellness"; Name="Fitness Wellness"; Description="Fitness and Wellness"},
        @{Id="hotels_resorts"; Name="Hotels Resorts"; Description="Hotels and Resorts"},
        @{Id="clubs_leagues"; Name="Clubs Leagues"; Description="Clubs and Leagues"},
        @{Id="ip_patents"; Name="IP Patents"; Description="Intellectual Property and Patents"},
        @{Id="regtech_ediscovery"; Name="RegTech E-Discovery"; Description="Regulatory Technology and E-Discovery"},
        @{Id="space_newspace"; Name="Space NewSpace"; Description="Space and New Space Technology"},
        @{Id="fixed_isp"; Name="Fixed ISP"; Description="Fixed Internet Service Providers"},
        @{Id="mobile_operators"; Name="Mobile Operators"; Description="Mobile Network Operators"},
        @{Id="network_equipment"; Name="Network Equipment"; Description="Network Equipment"}
    )
    
    foreach ($RagInfo in $IndustryRags) {
        $TotalRags++
        
        if (New-RAGCorpus -RagId $RagInfo.Id -RagName $RagInfo.Name -RagDescription $RagInfo.Description) {
            $SuccessfulCorpora++
        }
        
        if (New-SearchApp -RagId $RagInfo.Id -RagName $RagInfo.Name) {
            $SuccessfulSearchApps++
        }
        
        Write-Host ""
    }
    
    # Phase 4: Panel RAGs (6 RAGs)
    Write-Status "Phase 4: Creating panel RAGs..."
    
    $PanelRags = @(
        @{Id="andrei-panel"; Name="Andrei Panel"; Description="RAG for Andrei Panel"},
        @{Id="user-panel"; Name="User Panel"; Description="RAG for User Panel"},
        @{Id="business-panel"; Name="Business Panel"; Description="RAG for Business Panel"},
        @{Id="agency-panel"; Name="Agency Panel"; Description="RAG for Agency Panel"},
        @{Id="dev-panel"; Name="Dev Panel"; Description="RAG for Dev Panel"},
        @{Id="admin-panel"; Name="Admin Panel"; Description="RAG for Admin Panel"}
    )
    
    foreach ($RagInfo in $PanelRags) {
        $TotalRags++
        
        if (New-RAGCorpus -RagId $RagInfo.Id -RagName $RagInfo.Name -RagDescription $RagInfo.Description) {
            $SuccessfulCorpora++
        }
        
        if (New-SearchApp -RagId $RagInfo.Id -RagName $RagInfo.Name) {
            $SuccessfulSearchApps++
        }
        
        Write-Host ""
    }
    
    # Final summary
    Write-Host ""
    Write-Status "=== FINAL SUMMARY ==="
    Write-Success "Total RAGs processed: ${TotalRags}"
    Write-Success "Successful corpora created: ${SuccessfulCorpora}"
    Write-Success "Successful search apps created: ${SuccessfulSearchApps}"
    
    if ($SuccessfulCorpora -eq $TotalRags) {
        Write-Success "🎉 All RAG corpora created successfully!"
    } else {
        Write-Warning "⚠️  Some corpora creation failed. Check logs above."
    }
    
    if ($SuccessfulSearchApps -eq $TotalRags) {
        Write-Success "🎉 All search apps created successfully!"
    } else {
        Write-Warning "⚠️  Some search apps creation failed. Check logs above."
    }
    
    Write-Status "Next steps:"
    Write-Status "1. Upload industry-specific documents to Cloud Storage buckets"
    Write-Status "2. Test RAG queries through API endpoints"
    Write-Status "3. Integrate with Business Panel"
}

# Run the main function
Start-RAGCreation
