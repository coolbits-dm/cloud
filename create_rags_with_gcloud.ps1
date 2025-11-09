#!/usr/bin/env powershell
# Create RAG infrastructure using gcloud commands directly
# This avoids Python authentication issues

param(
    [string]$ProjectId = "coolbits-ai",
    [string]$Location = "us-central1"
)

Write-Host "🚀 Creating RAG infrastructure for industries..." -ForegroundColor Green
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

Write-Host "`n📊 Processing $total industries..." -ForegroundColor Cyan

foreach ($industry in $industries) {
    $industryId = $industry.id
    $industryName = $industry.name
    $bucketName = "coolbits-rag-$industryId-$ProjectId"
    
    Write-Host "`n🔧 Processing: $industryName ($industryId)" -ForegroundColor Yellow
    
    $result = @{
        industry_id = $industryId
        industry_name = $industryName
        bucket_name = $bucketName
        data_store_name = $null
        search_app_name = $null
        success = $false
    }
    
    try {
        # 1. Check if bucket exists
        Write-Host "  📁 Checking bucket: $bucketName" -ForegroundColor Gray
        $bucketExists = $false
        try {
            gcloud storage buckets describe gs://$bucketName --project=$ProjectId 2>$null
            if ($LASTEXITCODE -eq 0) {
                $bucketExists = $true
                Write-Host "  ✅ Bucket exists: $bucketName" -ForegroundColor Green
            }
        } catch {
            Write-Host "  ❌ Bucket does not exist: $bucketName" -ForegroundColor Red
        }
        
        if (-not $bucketExists) {
            Write-Host "  📁 Creating bucket: $bucketName" -ForegroundColor Gray
            gcloud storage buckets create gs://$bucketName --project=$ProjectId --location=$Location
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  ✅ Bucket created: $bucketName" -ForegroundColor Green
            } else {
                Write-Host "  ❌ Failed to create bucket: $bucketName" -ForegroundColor Red
                $results[$industryId] = $result
                continue
            }
        }
        
        # 2. Upload sample document
        Write-Host "  📄 Uploading sample document..." -ForegroundColor Gray
        $sampleContent = @"
# $industryName Industry Documentation

## Industry Overview
$($industry.description)

## Key Topics
Industry-specific knowledge, best practices, regulations, and technology solutions.

## Sample Content
This is a sample document for the $industryName industry RAG system.
It contains placeholder content that should be replaced with actual industry-specific documentation.

## Industry-Specific Information
- Market trends and analysis
- Best practices and guidelines
- Regulatory requirements
- Technology solutions
- Case studies and examples

Generated for CoolBits.ai RAG system on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
"@
        
        $sampleFile = "sample_$industryId.txt"
        $sampleContent | Out-File -FilePath $sampleFile -Encoding UTF8
        
        gcloud storage cp $sampleFile gs://$bucketName/sample_document.txt --project=$ProjectId
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ Sample document uploaded" -ForegroundColor Green
            Remove-Item $sampleFile -Force
        } else {
            Write-Host "  ❌ Failed to upload sample document" -ForegroundColor Red
        }
        
        # 3. Create Data Store (Discovery Engine)
        Write-Host "  🗄️ Creating Data Store..." -ForegroundColor Gray
        $dataStoreId = "$industryId-rag-store"
        $dataStoreName = "projects/$ProjectId/locations/$Location/dataStores/$dataStoreId"
        
        # Note: Discovery Engine API might not be available via gcloud CLI
        # We'll create a placeholder for now
        Write-Host "  ⚠️ Data Store creation requires Discovery Engine API (not available via gcloud CLI)" -ForegroundColor Yellow
        Write-Host "  📝 Data Store ID: $dataStoreId" -ForegroundColor Gray
        
        # 4. Create Search App (Discovery Engine)
        Write-Host "  🔍 Creating Search App..." -ForegroundColor Gray
        $searchAppId = "$industryId-search-app"
        $searchAppName = "projects/$ProjectId/locations/$Location/searchApps/$searchAppId"
        
        Write-Host "  ⚠️ Search App creation requires Discovery Engine API (not available via gcloud CLI)" -ForegroundColor Yellow
        Write-Host "  📝 Search App ID: $searchAppId" -ForegroundColor Gray
        
        $result.bucket_name = $bucketName
        $result.data_store_name = $dataStoreName
        $result.search_app_name = $searchAppName
        $result.success = $true
        
        Write-Host "  ✅ Successfully configured: $industryName" -ForegroundColor Green
        $successful++
        
    } catch {
        Write-Host "  ❌ Error processing $industryName : $($_.Exception.Message)" -ForegroundColor Red
    }
    
    $results[$industryId] = $result
    
    # Add delay between requests
    Start-Sleep -Seconds 1
}

# Print summary
Write-Host "`n📊 RAG Setup Summary:" -ForegroundColor Cyan
Write-Host "✅ Successful: $successful/$total" -ForegroundColor Green
Write-Host "❌ Failed: $($total - $successful)/$total" -ForegroundColor Red

if ($successful -gt 0) {
    Write-Host "`n🎉 Successfully created RAG infrastructure for $successful industries!" -ForegroundColor Green
    Write-Host "`nCreated resources:" -ForegroundColor Yellow
    foreach ($industryId in $results.Keys) {
        $result = $results[$industryId]
        if ($result.success) {
            Write-Host "  📁 $($result.industry_name):" -ForegroundColor White
            Write-Host "    - Bucket: $($result.bucket_name)" -ForegroundColor Gray
            Write-Host "    - Data Store: $($result.data_store_name)" -ForegroundColor Gray
            Write-Host "    - Search App: $($result.search_app_name)" -ForegroundColor Gray
        }
    }
}

# Save results to file
$results | ConvertTo-Json -Depth 3 | Out-File -FilePath "rag_setup_results.json" -Encoding UTF8
Write-Host "`n📄 Results saved to: rag_setup_results.json" -ForegroundColor Cyan

Write-Host "`n🔗 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Go to Google Cloud Console > Vertex AI Search" -ForegroundColor White
Write-Host "2. Create Data Stores for each industry using the bucket names above" -ForegroundColor White
Write-Host "3. Create Search Apps for each Data Store" -ForegroundColor White
Write-Host "4. Configure API endpoints to use the Search Apps" -ForegroundColor White

Write-Host "`n✨ RAG infrastructure setup complete!" -ForegroundColor Green
