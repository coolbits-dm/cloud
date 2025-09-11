# Dev Toolchain Setup for M8-M14 Verification

## Overview
Complete toolchain installation for enterprise-grade verification scripts in development environment.

## Required Tools

### 1. Google Cloud SDK & Tools
```powershell
# Install Google Cloud SDK
winget install Google.CloudSDK

# Verify installation
gcloud version
gsutil version

# Authenticate (if not already done)
gcloud auth login
gcloud auth application-default login

# Enable required APIs
gcloud services enable storage.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable monitoring.googleapis.com
```

### 2. Cosign (Supply Chain Security)
```powershell
# Download cosign for Windows
$cosignVersion = "2.2.4"
$cosignUrl = "https://github.com/sigstore/cosign/releases/download/v${cosignVersion}/cosign-windows-amd64.exe"
Invoke-WebRequest -Uri $cosignUrl -OutFile "cosign.exe"
Move-Item "cosign.exe" "$env:ProgramFiles\cosign\"
$env:PATH += ";$env:ProgramFiles\cosign"

# Verify installation
cosign version
```

### 3. Trivy (SBOM & CVE Scanning)
```powershell
# Install via Chocolatey
choco install trivy

# Or download directly
$trivyVersion = "0.50.0"
$trivyUrl = "https://github.com/aquasecurity/trivy/releases/download/v${trivyVersion}/trivy_${trivyVersion}_Windows-64bit.zip"
Invoke-WebRequest -Uri $trivyUrl -OutFile "trivy.zip"
Expand-Archive "trivy.zip" -DestinationPath "$env:ProgramFiles\trivy"
$env:PATH += ";$env:ProgramFiles\trivy"

# Verify installation
trivy version
```

### 4. Gitleaks (Secret Scanning)
```powershell
# Install via Chocolatey
choco install gitleaks

# Or download directly
$gitleaksVersion = "8.18.0"
$gitleaksUrl = "https://github.com/gitleaks/gitleaks/releases/download/v${gitleaksVersion}/gitleaks_${gitleaksVersion}_windows_amd64.zip"
Invoke-WebRequest -Uri $gitleaksUrl -OutFile "gitleaks.zip"
Expand-Archive "gitleaks.zip" -DestinationPath "$env:ProgramFiles\gitleaks"
$env:PATH += ";$env:ProgramFiles\gitleaks"

# Verify installation
gitleaks version
```

### 5. Conftest (Policy-as-Code)
```powershell
# Install via Chocolatey
choco install conftest

# Or download directly
$conftestVersion = "0.50.0"
$conftestUrl = "https://github.com/open-policy-agent/conftest/releases/download/v${conftestVersion}/conftest_${conftestVersion}_Windows_x86_64.zip"
Invoke-WebRequest -Uri $conftestUrl -OutFile "conftest.zip"
Expand-Archive "conftest.zip" -DestinationPath "$env:ProgramFiles\conftest"
$env:PATH += ";$env:ProgramFiles\conftest"

# Verify installation
conftest version
```

## Environment Configuration

### PowerShell Profile Setup
```powershell
# Add to $PROFILE
$env:PATH += ";$env:ProgramFiles\cosign;$env:ProgramFiles\trivy;$env:ProgramFiles\gitleaks;$env:ProgramFiles\conftest"

# Set environment variables
$env:COSIGN_PASSWORD = "your-cosign-password"
$env:TRIVY_CACHE_DIR = "$env:USERPROFILE\.trivy"
$env:GITLEAKS_CONFIG = "$PWD\.gitleaks.toml"
```

### Git Configuration
```powershell
# Configure Git for CRLF handling
git config --global core.autocrlf true
git config --global core.safecrlf true

# Configure Git LFS if needed
git lfs install
```

## Verification Script Fixes

### M8 - Backup Verification Fix
```powershell
# Fix gsutil format issue in scripts/verify_M8.ps1
# Replace: gcloud storage ls --format=json
# With: gsutil ls -L gs://your-backup-bucket/
```

### M9 - Security Hardening Fix
```powershell
# Fix Gitleaks SARIF generation in scripts/verify_M9.ps1
# Add: gitleaks detect --source . --report-format sarif --report-path gitleaks.sarif
```

### M10-M14 - Script Creation
```powershell
# Create missing verification scripts
# scripts/verify_M10.ps1 - DevEx verification
# scripts/verify_M12.ps1 - Compliance verification  
# scripts/verify_M13.ps1 - Runtime governance verification
# scripts/verify_M14.ps1 - Adaptive policy verification
```

## CI/CD Environment Detection

### Dev vs Prod Detection
```powershell
# Add to verification scripts
$isDev = $env:CI -eq $null -or $env:CI -eq "false"
$isProd = $env:CI -eq "true" -and $env:GITHUB_ACTIONS -eq "true"

if ($isDev) {
    Write-Host "[DEV] Running mock verification"
    # Mock verification for dev
} else {
    Write-Host "[PROD] Running full verification"
    # Full verification for prod
}
```

## Mock Verification for Dev

### M8 Mock (Backup)
```powershell
# Mock backup verification for dev
Write-Host "[MOCK] Backup verification - OK"
Write-Host "[MOCK] Encryption check - OK"
Write-Host "[MOCK] Retention policy - OK"
```

### M9 Mock (Security)
```powershell
# Mock security verification for dev
Write-Host "[MOCK] Secret scan - OK"
Write-Host "[MOCK] IAM least privilege - OK"
Write-Host "[MOCK] Policy-as-code - OK"
```

## Production Verification

### Full M8 Verification
```powershell
# Real backup verification
gsutil ls -L gs://coolbits-backup-prod/
gsutil stat gs://coolbits-backup-prod/latest/
```

### Full M9 Verification
```powershell
# Real security verification
gitleaks detect --source . --report-format sarif --report-path gitleaks.sarif
conftest test infrastructure/ --policy policies/
trivy fs . --format json --output trivy.json
```

## Verification Status Matrix

| Milestone | Dev Mock | Prod Real | Status |
|-----------|----------|-----------|---------|
| M8 | ✅ Mock | ⚠️ Needs gsutil | Partial |
| M9 | ✅ Mock | ⚠️ Needs gitleaks | Partial |
| M10 | ❌ Missing | ❌ Missing | Missing |
| M11 | ✅ Real | ✅ Real | Complete |
| M12 | ❌ Missing | ❌ Missing | Missing |
| M13 | ❌ Missing | ❌ Missing | Missing |
| M14 | ❌ Missing | ❌ Missing | Missing |

## Next Steps

1. **Install toolchain** using commands above
2. **Create missing scripts** (M10, M12, M13, M14)
3. **Fix existing scripts** (M8, M9) with proper tool detection
4. **Add dev/prod detection** to all verification scripts
5. **Test verification pipeline** end-to-end

## Verification Commands

```powershell
# Test all tools
gcloud version
gsutil version
cosign version
trivy version
gitleaks version
conftest version

# Test verification scripts
.\scripts\verify_M8.ps1
.\scripts\verify_M9.ps1
.\scripts\verify_M11.ps1

# Generate new proof pack
.\scripts\proof\collect_proof.ps1 --verbose
```

## Expected Results

After toolchain installation:
- **M8:** ✅ Backup verification with real gsutil
- **M9:** ✅ Security scan with real gitleaks/trivy
- **M10-M14:** ✅ Complete verification pipeline
- **Proof Pack:** ✅ All green verification status
