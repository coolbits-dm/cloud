# Generate HMAC keys for oGPT roles
$PROJECT = "coolbits-og-bridge"

Write-Host "Generating HMAC keys for oGPT roles in project: $PROJECT" -ForegroundColor Green

for ($i = 1; $i -le 12; $i++) {
    $roleNumber = $i.ToString('00')
    $secretName = "bridge_webhook_hmac_ogpt$roleNumber"
    
    # Generate 64-character hex string
    $hmac = -join ((48..57) + (97..102) | Get-Random -Count 64 | ForEach-Object {[char]$_})
    
    Write-Host "Creating secret: $secretName" -ForegroundColor Yellow
    
    try {
        echo $hmac | gcloud secrets create $secretName --replication-policy=automatic --data-file=- --project=$PROJECT
        Write-Host "✅ Successfully created $secretName" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Failed to create $secretName" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
}

Write-Host "HMAC key generation complete!" -ForegroundColor Green
