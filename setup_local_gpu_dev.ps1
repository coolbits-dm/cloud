# Local GPU Development Environment Setup
# Configures local development environment with NVIDIA RTX 2060 GPU

param(
    [string]$PythonVersion = "3.11",
    [string]$ProjectName = "coolbits-local-dev"
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

# Function to check if Python is installed
function Test-PythonInstallation {
    Write-Processing "Checking Python installation..."
    
    $pythonPaths = @(
        "python",
        "python3",
        "py",
        "C:\Python311\python.exe",
        "C:\Python310\python.exe",
        "C:\Python39\python.exe",
        "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python311\python.exe",
        "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python310\python.exe"
    )
    
    foreach ($path in $pythonPaths) {
        try {
            $version = & $path --version 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Found Python: $path - $version"
                return $path
            }
        } catch {
            continue
        }
    }
    
    Write-Warning "Python not found in common locations"
    return $null
}

# Function to install Python via winget
function Install-PythonWinget {
    Write-Processing "Installing Python via winget..."
    
    try {
        winget install Python.Python.3.11 --accept-package-agreements --accept-source-agreements
        Write-Success "Python installed successfully via winget"
        return $true
    } catch {
        Write-Error "Failed to install Python via winget: $($_.Exception.Message)"
        return $false
    }
}

# Function to create virtual environment
function New-VirtualEnvironment {
    param([string]$PythonPath, [string]$EnvName)
    
    Write-Processing "Creating virtual environment: $EnvName"
    
    try {
        & $PythonPath -m venv $EnvName
        Write-Success "Virtual environment created: $EnvName"
        return $true
    } catch {
        Write-Error "Failed to create virtual environment: $($_.Exception.Message)"
        return $false
    }
}

# Function to install GPU packages
function Install-GPUPackages {
    param([string]$PythonPath)
    
    Write-Processing "Installing GPU packages..."
    
    $packages = @(
        "torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121",
        "ray[gpu]",
        "transformers",
        "sentence-transformers",
        "chromadb",
        "faiss-cpu",
        "numpy",
        "pandas",
        "scikit-learn",
        "jupyter",
        "streamlit"
    )
    
    foreach ($package in $packages) {
        Write-Processing "Installing: $package"
        try {
            & $PythonPath -m pip install $package
            Write-Success "Installed: $package"
        } catch {
            Write-Warning "Failed to install: $package"
        }
    }
}

# Function to create local RAG development script
function New-LocalRAGScript {
    param([string]$ScriptPath)
    
    $scriptContent = @"
#!/usr/bin/env python3
"""
Local RAG Development Environment
Uses local GPU for development and testing
"""

import torch
import ray
from sentence_transformers import SentenceTransformer
import chromadb
import numpy as np
from typing import List, Dict
import json

class LocalRAGSystem:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.embedding_model = None
        self.vector_db = None
        self.ray_initialized = False
        
        print(f"🚀 Initializing Local RAG System")
        print(f"📱 Device: {self.device}")
        print(f"🎮 GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
        
    def initialize_ray(self):
        """Initialize Ray cluster for distributed processing"""
        if not self.ray_initialized:
            ray.init(
                num_gpus=1 if torch.cuda.is_available() else 0,
                num_cpus=4,
                ignore_reinit_error=True
            )
            self.ray_initialized = True
            print("✅ Ray cluster initialized")
    
    def load_embedding_model(self, model_name: str = "all-MiniLM-L6-v2"):
        """Load sentence transformer model"""
        print(f"🔄 Loading embedding model: {model_name}")
        self.embedding_model = SentenceTransformer(model_name)
        if torch.cuda.is_available():
            self.embedding_model = self.embedding_model.to(self.device)
        print("✅ Embedding model loaded")
    
    def initialize_vector_db(self):
        """Initialize ChromaDB for vector storage"""
        print("🔄 Initializing vector database...")
        self.vector_db = chromadb.Client()
        self.collection = self.vector_db.create_collection("coolbits_documents")
        print("✅ Vector database initialized")
    
    def add_documents(self, documents: List[Dict]):
        """Add documents to vector database"""
        if not self.embedding_model:
            self.load_embedding_model()
        
        if not self.vector_db:
            self.initialize_vector_db()
        
        print(f"🔄 Adding {len(documents)} documents...")
        
        texts = [doc["text"] for doc in documents]
        embeddings = self.embedding_model.encode(texts)
        
        ids = [doc["id"] for doc in documents]
        metadatas = [{"source": doc.get("source", "unknown")} for doc in documents]
        
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✅ Added {len(documents)} documents")
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search for similar documents"""
        if not self.embedding_model:
            self.load_embedding_model()
        
        if not self.vector_db:
            self.initialize_vector_db()
        
        print(f"🔍 Searching for: {query}")
        
        query_embedding = self.embedding_model.encode([query])
        
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results
        )
        
        formatted_results = []
        for i in range(len(results["documents"][0])):
            formatted_results.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })
        
        print(f"✅ Found {len(formatted_results)} results")
        return formatted_results
    
    def test_gpu_performance(self):
        """Test GPU performance"""
        if not torch.cuda.is_available():
            print("❌ CUDA not available")
            return
        
        print("🧪 Testing GPU performance...")
        
        # Test tensor operations
        device = torch.device("cuda")
        x = torch.randn(1000, 1000, device=device)
        y = torch.randn(1000, 1000, device=device)
        
        import time
        start_time = time.time()
        
        for _ in range(100):
            z = torch.matmul(x, y)
        
        torch.cuda.synchronize()
        end_time = time.time()
        
        print(f"✅ GPU test completed in {end_time - start_time:.2f} seconds")
        print(f"🎮 GPU Memory: {torch.cuda.memory_allocated() / 1024**2:.1f} MB")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.ray_initialized:
            ray.shutdown()
            print("✅ Ray cluster shutdown")

def main():
    """Main function for testing"""
    print("=" * 60)
    print("🎯 Local RAG Development Environment")
    print("=" * 60)
    
    # Initialize RAG system
    rag = LocalRAGSystem()
    
    # Test GPU performance
    rag.test_gpu_performance()
    
    # Initialize Ray
    rag.initialize_ray()
    
    # Load embedding model
    rag.load_embedding_model()
    
    # Initialize vector database
    rag.initialize_vector_db()
    
    # Sample documents
    sample_docs = [
        {
            "id": "doc1",
            "text": "CoolBits.ai is an AI-powered platform for business automation",
            "source": "company_info"
        },
        {
            "id": "doc2", 
            "text": "cbLM.ai provides enterprise AI solutions and RAG systems",
            "source": "company_info"
        },
        {
            "id": "doc3",
            "text": "Ray on Vertex AI enables distributed computing for AI workloads",
            "source": "technical_docs"
        }
    ]
    
    # Add documents
    rag.add_documents(sample_docs)
    
    # Test search
    results = rag.search("What is CoolBits.ai?", n_results=3)
    
    print("\n📋 Search Results:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['text']}")
        print(f"   Source: {result['metadata']['source']}")
        print(f"   Distance: {result['distance']:.3f}")
        print()
    
    # Cleanup
    rag.cleanup()
    
    print("🎉 Local RAG development environment ready!")

if __name__ == "__main__":
    main()
"@
    
    Write-Processing "Creating local RAG development script..."
    try {
        Set-Content -Path $ScriptPath -Value $scriptContent -Encoding UTF8
        Write-Success "Local RAG script created: $ScriptPath"
        return $true
    } catch {
        Write-Error "Failed to create script: $($_.Exception.Message)"
        return $false
    }
}

# Main execution
function Main {
    Write-Status "Setting up Local GPU Development Environment..."
    Write-Status "Project: $ProjectName"
    Write-Status "Python Version: $PythonVersion"
    Write-Status "GPU: NVIDIA GeForce RTX 2060 (6GB VRAM)"
    Write-Status ""
    
    # Check Python installation
    $pythonPath = Test-PythonInstallation
    
    if (-not $pythonPath) {
        Write-Warning "Python not found. Installing via winget..."
        $installed = Install-PythonWinget
        if ($installed) {
            $pythonPath = Test-PythonInstallation
        }
        
        if (-not $pythonPath) {
            Write-Error "Could not install or find Python. Please install manually."
            return
        }
    }
    
    # Create project directory
    Write-Processing "Creating project directory..."
    if (-not (Test-Path $ProjectName)) {
        New-Item -ItemType Directory -Path $ProjectName -Force | Out-Null
        Write-Success "Project directory created: $ProjectName"
    }
    
    # Create virtual environment
    $envPath = Join-Path $ProjectName "venv"
    $venvPython = Join-Path $envPath "Scripts\python.exe"
    
    if (-not (Test-Path $venvPython)) {
        $created = New-VirtualEnvironment -PythonPath $pythonPath -EnvName $envPath
        if (-not $created) {
            Write-Error "Failed to create virtual environment"
            return
        }
    }
    
    # Install GPU packages
    Install-GPUPackages -PythonPath $venvPython
    
    # Create local RAG script
    $scriptPath = Join-Path $ProjectName "local_rag_dev.py"
    New-LocalRAGScript -ScriptPath $scriptPath
    
    # Create requirements.txt
    $requirementsPath = Join-Path $ProjectName "requirements.txt"
    $requirements = @"
torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
ray[gpu]
transformers
sentence-transformers
chromadb
faiss-cpu
numpy
pandas
scikit-learn
jupyter
streamlit
google-cloud-aiplatform
google-cloud-storage
"@
    
    Set-Content -Path $requirementsPath -Value $requirements -Encoding UTF8
    Write-Success "Requirements file created: $requirementsPath"
    
    Write-Status ""
    Write-Status "==========================================================="
    Write-Status "=== LOCAL GPU DEVELOPMENT ENVIRONMENT READY ==="
    Write-Status "==========================================================="
    
    Write-Success "✅ Python environment configured"
    Write-Success "✅ GPU packages installed"
    Write-Success "✅ Local RAG script created"
    Write-Success "✅ Virtual environment ready"
    
    Write-Status ""
    Write-Status "NEXT STEPS:"
    Write-Status "==========="
    Write-Host "1. Activate virtual environment:" -ForegroundColor $Cyan
    Write-Host "   cd $ProjectName" -ForegroundColor $Yellow
    Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor $Yellow
    Write-Host ""
    Write-Host "2. Run local RAG development:" -ForegroundColor $Cyan
    Write-Host "   python local_rag_dev.py" -ForegroundColor $Yellow
    Write-Host ""
    Write-Host "3. Test GPU performance:" -ForegroundColor $Cyan
    Write-Host "   python -c \"import torch; print(f'CUDA available: {torch.cuda.is_available()}')\"" -ForegroundColor $Yellow
    Write-Host ""
    Write-Host "4. Start Jupyter notebook:" -ForegroundColor $Cyan
    Write-Host "   jupyter notebook" -ForegroundColor $Yellow
    
    Write-Status ""
    Write-Status "ADVANTAGES OF LOCAL DEVELOPMENT:"
    Write-Status "================================"
    Write-Host "• Zero cost for development" -ForegroundColor $Green
    Write-Host "• Low latency (no network overhead)" -ForegroundColor $Green
    Write-Host "• Full control over resources" -ForegroundColor $Green
    Write-Host "• Rapid iteration and testing" -ForegroundColor $Green
    Write-Host "• Easy debugging and profiling" -ForegroundColor $Green
}

# Run the main function
Main
