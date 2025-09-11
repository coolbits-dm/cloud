#!/usr/bin/env powershell
# Create Vertex AI Search corpus using REST API
# This creates real corpus for each industry

param(
    [string]$ProjectId = "coolbits-ai",
    [string]$Location = "global"
)

Write-Host "Creating Vertex AI Search corpus for industries..." -ForegroundColor Green
Write-Host "Project: $ProjectId" -ForegroundColor Yellow
Write-Host "Location: $Location" -ForegroundColor Yellow

# Industry definitions
$industries = @(
    @{id="agritech"; name="AgTech"; description="Agricultural Technology and Innovation"},
    @{id="banking"; name="Banking"; description="Commercial and Retail Banking Services"},
    @{id="saas_b2b"; name="SaaS B2B"; description="Business-to-Business Software as a Service"},
    @{id="healthcare"; name="Healthcare"; description="Healthcare Services and Medical Technology"},
    @{id="exchanges"; name="Cryptocurrency Exchanges"; description="Cryptocurrency Trading Platforms and Exchanges"}
)

$results = @{}
$successful = 0
$total = $industries.Count

Write-Host "`nProcessing $total industries..." -ForegroundColor Cyan

# Get access token
Write-Host "Getting access token..." -ForegroundColor Gray
$accessToken = gcloud auth print-access-token
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to get access token" -ForegroundColor Red
    exit 1
}

foreach ($industry in $industries) {
    $industryId = $industry.id
    $industryName = $industry.name
    $bucketName = "coolbits-rag-$industryId-$ProjectId"
    
    Write-Host "`nProcessing: $industryName ($industryId)" -ForegroundColor Yellow
    
    $result = @{
        industry_id = $industryId
        industry_name = $industryName
        bucket_name = $bucketName
        corpus_name = $null
        search_app_name = $null
        success = $false
    }
    
    try {
        # 1. Create Corpus using REST API
        Write-Host "  Creating corpus..." -ForegroundColor Gray
        $corpusId = "$industryId-corpus"
        $corpusName = "projects/$ProjectId/locations/$Location/corpus/$corpusId"
        
        $corpusBody = @{
            displayName = "$industryName Corpus"
            description = "RAG corpus for $industryName industry"
            inputDataConfig = @{
                gcsInputUris = @("gs://$bucketName/sample_document.txt")
            }
        } | ConvertTo-Json -Depth 3
        
        $corpusUrl = "https://discoveryengine.googleapis.com/v1beta/projects/$ProjectId/locations/$Location/corpus"
        
        $corpusResponse = Invoke-RestMethod -Uri $corpusUrl -Method POST -Headers @{
            "Authorization" = "Bearer $accessToken"
            "Content-Type" = "application/json"
        } -Body $corpusBody
        
        if ($corpusResponse) {
            Write-Host "  Corpus created: $corpusId" -ForegroundColor Green
            $result.corpus_name = $corpusName
        } else {
            Write-Host "  Failed to create corpus: $corpusId" -ForegroundColor Red
            $results[$industryId] = $result
            continue
        }
        
        # 2. Create Search App using REST API
        Write-Host "  Creating search app..." -ForegroundColor Gray
        $searchAppId = "$industryId-search-app"
        $searchAppName = "projects/$ProjectId/locations/$Location/searchApps/$searchAppId"
        
        $searchAppBody = @{
            displayName = "$industryName Search App"
            description = "Search app for $industryName industry"
            dataStoreIds = @($corpusId)
        } | ConvertTo-Json -Depth 3
        
        $searchAppUrl = "https://discoveryengine.googleapis.com/v1beta/projects/$ProjectId/locations/$Location/searchApps"
        
        $searchAppResponse = Invoke-RestMethod -Uri $searchAppUrl -Method POST -Headers @{
            "Authorization" = "Bearer $accessToken"
            "Content-Type" = "application/json"
        } -Body $searchAppBody
        
        if ($searchAppResponse) {
            Write-Host "  Search app created: $searchAppId" -ForegroundColor Green
            $result.search_app_name = $searchAppName
        } else {
            Write-Host "  Failed to create search app: $searchAppId" -ForegroundColor Red
        }
        
        $result.success = $true
        Write-Host "  Successfully configured: $industryName" -ForegroundColor Green
        $successful++
        
    } catch {
        Write-Host "  Error processing $industryName : $($_.Exception.Message)" -ForegroundColor Red
    }
    
    $results[$industryId] = $result
    
    # Add delay between requests
    Start-Sleep -Seconds 2
}

# Print summary
Write-Host "`nRAG Setup Summary:" -ForegroundColor Cyan
Write-Host "Successful: $successful/$total" -ForegroundColor Green
Write-Host "Failed: $($total - $successful)/$total" -ForegroundColor Red

if ($successful -gt 0) {
    Write-Host "`nSuccessfully created RAG infrastructure for $successful industries!" -ForegroundColor Green
    Write-Host "`nCreated resources:" -ForegroundColor Yellow
    foreach ($industryId in $results.Keys) {
        $result = $results[$industryId]
        if ($result.success) {
            Write-Host "  $($result.industry_name):" -ForegroundColor White
            Write-Host "    - Bucket: $($result.bucket_name)" -ForegroundColor Gray
            Write-Host "    - Corpus: $($result.corpus_name)" -ForegroundColor Gray
            Write-Host "    - Search App: $($result.search_app_name)" -ForegroundColor Gray
        }
    }
}

# Save results to file
$results | ConvertTo-Json -Depth 3 | Out-File -FilePath "corpus_setup_results.json" -Encoding UTF8
Write-Host "`nResults saved to: corpus_setup_results.json" -ForegroundColor Cyan

Write-Host "`nRAG infrastructure setup complete!" -ForegroundColor Green
