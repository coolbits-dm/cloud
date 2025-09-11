# Vertex AI RAG Engine Script for CoolBits.ai using PowerShell and REST API
# Based on official Google Cloud documentation

param(
    [string]$ProjectId = "coolbits-ai",
    [string]$Location = "us-east1"
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

# Function to create RAG corpus using REST API
function New-RAGCorpus {
    param(
        [string]$DisplayName,
        [string]$Description
    )
    
    Write-Processing "Creating RAG corpus: ${DisplayName}"
    
    $AccessToken = Get-AccessToken
    if (-not $AccessToken) {
        Write-Error "No access token available"
        return $null
    }
    
    # Create RAG corpus
    $CreateUrl = "https://${Location}-aiplatform.googleapis.com/v1beta1/projects/${ProjectId}/locations/${Location}/ragCorpora"
    
    $Payload = @{
        displayName = $DisplayName
        description = $Description
    } | ConvertTo-Json -Depth 10
    
    Write-Status "Creating corpus with URL: $CreateUrl"
    Write-Status "Payload: $Payload"
    
    try {
        $Response = Invoke-RestMethod -Uri $CreateUrl -Headers @{
            "Authorization" = "Bearer ${AccessToken}"
            "Content-Type" = "application/json"
        } -Method Post -Body $Payload -ErrorAction Stop
        
        if ($Response.name) {
            Write-Success "Created RAG corpus: ${DisplayName} (Path: $($Response.name))"
            return $Response.name
        } else {
            Write-Error "Failed to create RAG corpus: ${DisplayName} - No name in response"
            return $null
        }
    } catch {
        Write-Error "Error creating RAG corpus ${DisplayName}: $($_.Exception.Message)"
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
                Write-Status "Could not read error response details"
            }
        }
        return $null
    }
}

# Function to import files to RAG corpus
function Import-FilesToRAGCorpus {
    param(
        [string]$CorpusName,
        [string]$FilePath
    )
    
    Write-Processing "Importing file to RAG corpus: ${FilePath}"
    
    $AccessToken = Get-AccessToken
    if (-not $AccessToken) {
        Write-Error "No access token available"
        return $false
    }
    
    # Read file content
    try {
        $FileContent = Get-Content -Path $FilePath -Raw
        Write-Status "File content length: $($FileContent.Length) characters"
    } catch {
        Write-Error "Failed to read file: ${FilePath}"
        return $false
    }
    
    # Import file to RAG corpus
    $ImportUrl = "https://${Location}-aiplatform.googleapis.com/v1beta1/${CorpusName}:importFiles"
    
    $Payload = @{
        paths = @($FilePath)
        transformationConfig = @{
            chunkingConfig = @{
                chunkSize = 512
                chunkOverlap = 100
            }
        }
    } | ConvertTo-Json -Depth 10
    
    Write-Status "Importing file with URL: $ImportUrl"
    Write-Status "Payload: $Payload"
    
    try {
        $Response = Invoke-RestMethod -Uri $ImportUrl -Headers @{
            "Authorization" = "Bearer ${AccessToken}"
            "Content-Type" = "application/json"
        } -Method Post -Body $Payload -ErrorAction Stop
        
        if ($Response.importedRagFilesCount) {
            Write-Success "Imported $($Response.importedRagFilesCount) files to RAG corpus"
            return $true
        } else {
            Write-Error "Failed to import files to RAG corpus"
            return $false
        }
    } catch {
        Write-Error "Error importing files to RAG corpus: $($_.Exception.Message)"
        if ($_.Exception.Response) {
            $StatusCode = $_.Exception.Response.StatusCode
            Write-Error "HTTP Status: $StatusCode"
        }
        return $false
    }
}

# Function to test retrieval from RAG corpus
function Test-RAGRetrieval {
    param(
        [string]$CorpusName,
        [string]$Query
    )
    
    Write-Processing "Testing retrieval with query: ${Query}"
    
    $AccessToken = Get-AccessToken
    if (-not $AccessToken) {
        Write-Error "No access token available"
        return $false
    }
    
    # Test retrieval
    $RetrievalUrl = "https://${Location}-aiplatform.googleapis.com/v1beta1/projects/${ProjectId}/locations/${Location}:retrieveContexts"
    
    $Payload = @{
        vertexRagStore = @{
            ragResources = @{
                ragCorpus = $CorpusName
            }
        }
        query = @{
            text = $Query
            similarityTopK = 3
        }
    } | ConvertTo-Json -Depth 10
    
    Write-Status "Testing retrieval with URL: $RetrievalUrl"
    Write-Status "Payload: $Payload"
    
    try {
        $Response = Invoke-RestMethod -Uri $RetrievalUrl -Headers @{
            "Authorization" = "Bearer ${AccessToken}"
            "Content-Type" = "application/json"
        } -Method Post -Body $Payload -ErrorAction Stop
        
        if ($Response.contexts) {
            Write-Success "Retrieval test successful! Found $($Response.contexts.Count) contexts"
            foreach ($context in $Response.contexts) {
                Write-Status "Context: $($context.text.Substring(0, [Math]::Min(100, $context.text.Length)))..."
            }
            return $true
        } else {
            Write-Warning "No contexts found for query"
            return $false
        }
    } catch {
        Write-Error "Error testing retrieval: $($_.Exception.Message)"
        if ($_.Exception.Response) {
            $StatusCode = $_.Exception.Response.StatusCode
            Write-Error "HTTP Status: $StatusCode"
        }
        return $false
    }
}

# Main execution function
function Start-VertexAIRAGCreation {
    Write-Status "Starting Vertex AI RAG Engine creation for CoolBits.ai..."
    Write-Status "Project: ${ProjectId}"
    Write-Status "Location: ${Location}"
    
    # Step 1: Create RAG corpus
    $CorpusName = New-RAGCorpus -DisplayName "ai-board-corpus" -Description "RAG corpus for AI Board management and coordination"
    if (-not $CorpusName) {
        Write-Error "Failed to create RAG corpus"
        return
    }
    
    # Step 2: Create sample file
    $SampleFile = "ai_board_sample.txt"
    $SampleContent = @"
# AI Board Management Best Practices

## Overview
The AI Board is responsible for overseeing artificial intelligence initiatives and ensuring ethical AI deployment.

## Key Responsibilities
- Strategic AI planning
- Risk assessment and mitigation
- Compliance with AI regulations
- Resource allocation for AI projects

## Best Practices
1. Regular board meetings
2. Clear communication channels
3. Transparent decision making
4. Continuous learning and adaptation

## Governance Framework
- Ethical AI principles
- Data privacy protection
- Algorithmic transparency
- Human oversight requirements
"@
    
    try {
        $SampleContent | Out-File -FilePath $SampleFile -Encoding UTF8
        Write-Success "Created sample file: ${SampleFile}"
    } catch {
        Write-Error "Failed to create sample file: $($_.Exception.Message)"
        return
    }
    
    # Step 3: Import file to RAG corpus
    if (-not (Import-FilesToRAGCorpus -CorpusName $CorpusName -FilePath $SampleFile)) {
        Write-Error "Failed to import files to RAG corpus"
        return
    }
    
    # Step 4: Test retrieval
    if (-not (Test-RAGRetrieval -CorpusName $CorpusName -Query "What are the key responsibilities of the AI Board?")) {
        Write-Warning "Retrieval test failed, but corpus was created"
    }
    
    # Clean up
    try {
        Remove-Item $SampleFile -Force
        Write-Status "Cleaned up sample file"
    } catch {
        Write-Warning "Could not clean up sample file"
    }
    
    # Final summary
    Write-Host ""
    Write-Status "============================================================"
    Write-Status "=== FINAL SUMMARY ==="
    Write-Status "============================================================"
    Write-Success "RAG corpus created successfully!"
    Write-Success "Corpus name: ${CorpusName}"
    Write-Status "Next steps:"
    Write-Status "1. Create more RAG corpora for other industries"
    Write-Status "2. Upload industry-specific documents"
    Write-Status "3. Integrate with Business Panel"
}

# Run the main function
Start-VertexAIRAGCreation
