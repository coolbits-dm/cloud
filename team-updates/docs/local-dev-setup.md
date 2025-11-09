# Local Development Setup Guide

## 🎯 **CoolBits.ai & cbLM.ai Local GPU Development**

### **Overview**
This guide provides step-by-step instructions for setting up local GPU development environment for CoolBits.ai and cbLM.ai projects.

---

## 🖥️ **System Requirements**

### **Hardware**
- **GPU**: NVIDIA GeForce RTX 2060 (6GB VRAM)
- **RAM**: 16GB+ recommended
- **Storage**: 50GB+ free space
- **OS**: Windows 11

### **Software**
- **CUDA**: Version 12.6
- **Python**: 3.11+
- **Git**: Latest version
- **PowerShell**: Windows PowerShell 5.1+

---

## 🚀 **Quick Setup**

### **Step 1: Run Setup Script**
```powershell
# Navigate to project directory
cd C:\Users\andre\Desktop\coolbits

# Run the setup script
.\setup_local_gpu_dev.ps1
```

### **Step 2: Activate Environment**
```powershell
# Navigate to project directory
cd coolbits-local-dev

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

### **Step 3: Test GPU**
```powershell
# Test CUDA availability
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# Test GPU performance
python local_rag_dev.py
```

---

## 📦 **Package Installation**

### **Core Packages**
```bash
# PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Ray for distributed computing
pip install ray[gpu]

# AI/ML packages
pip install transformers sentence-transformers

# Vector databases
pip install chromadb faiss-cpu

# Data processing
pip install numpy pandas scikit-learn

# Development tools
pip install jupyter streamlit
```

### **Google Cloud Integration**
```bash
# Google Cloud packages
pip install google-cloud-aiplatform google-cloud-storage
```

---

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Set CUDA environment
set CUDA_VISIBLE_DEVICES=0

# Set Python path
set PYTHONPATH=%PYTHONPATH%;C:\Users\andre\Desktop\coolbits\coolbits-local-dev
```

### **GPU Memory Management**
```python
# In your Python scripts
import torch

# Set memory fraction
torch.cuda.set_per_process_memory_fraction(0.8)

# Clear cache when needed
torch.cuda.empty_cache()
```

---

## 🧪 **Testing and Validation**

### **GPU Performance Test**
```python
import torch
import time

def test_gpu_performance():
    if not torch.cuda.is_available():
        print("❌ CUDA not available")
        return
    
    device = torch.device("cuda")
    x = torch.randn(1000, 1000, device=device)
    y = torch.randn(1000, 1000, device=device)
    
    start_time = time.time()
    for _ in range(100):
        z = torch.matmul(x, y)
    
    torch.cuda.synchronize()
    end_time = time.time()
    
    print(f"✅ GPU test completed in {end_time - start_time:.2f} seconds")
    print(f"🎮 GPU Memory: {torch.cuda.memory_allocated() / 1024**2:.1f} MB")

test_gpu_performance()
```

### **Ray Cluster Test**
```python
import ray

# Initialize Ray
ray.init(num_gpus=1, num_cpus=4)

@ray.remote
def gpu_task():
    import torch
    return torch.cuda.is_available()

# Test GPU task
result = ray.get(gpu_task.remote())
print(f"Ray GPU task result: {result}")

# Shutdown Ray
ray.shutdown()
```

---

## 🔗 **Integration with Cloud**

### **ogpt-bridge-service Connection**
```python
import requests

# Test connection to cloud service
service_url = "https://ogpt-bridge-service-271190369805.europe-west1.run.app"

# Health check
response = requests.get(f"{service_url}/api/v1/health")
print(f"Service status: {response.status_code}")

# Chat endpoint test
chat_data = {
    "message": "Hello from local development",
    "role": "ogpt01"
}
response = requests.post(f"{service_url}/api/ai/chat", json=chat_data)
print(f"Chat response: {response.json()}")
```

### **Cloud Storage Integration**
```python
from google.cloud import storage

# Initialize client
client = storage.Client(project="coolbits-ai")

# List buckets
buckets = client.list_buckets()
for bucket in buckets:
    print(f"Bucket: {bucket.name}")
```

---

## 🐛 **Troubleshooting**

### **Common Issues**

#### **CUDA Not Available**
```bash
# Check NVIDIA driver
nvidia-smi

# Reinstall PyTorch with CUDA
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

#### **Memory Issues**
```python
# Reduce batch size
batch_size = 32  # Instead of 64

# Use gradient checkpointing
model.gradient_checkpointing_enable()

# Clear cache
torch.cuda.empty_cache()
```

#### **Ray Initialization Failed**
```python
# Try different Ray configuration
ray.init(
    num_gpus=1,
    num_cpus=4,
    ignore_reinit_error=True,
    local_mode=True  # For debugging
)
```

### **Performance Optimization**

#### **GPU Utilization**
```python
# Monitor GPU usage
import torch
print(f"GPU Memory Allocated: {torch.cuda.memory_allocated() / 1024**2:.1f} MB")
print(f"GPU Memory Cached: {torch.cuda.memory_reserved() / 1024**2:.1f} MB")
```

#### **Batch Processing**
```python
# Process data in batches
def process_batch(data, batch_size=32):
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        # Process batch
        yield process_batch_data(batch)
```

---

## 📚 **Resources**

### **Documentation**
- **PyTorch**: https://pytorch.org/docs/
- **Ray**: https://docs.ray.io/
- **ChromaDB**: https://docs.trychroma.com/
- **Google Cloud**: https://cloud.google.com/docs

### **Tutorials**
- **Local RAG Development**: `local_rag_dev.py`
- **GPU Performance**: `test_gpu_performance.py`
- **Cloud Integration**: `cloud_integration.py`

### **Support**
- **Development Team**: [Contact Info]
- **DevOps Team**: [Contact Info]
- **CEO**: Andrei - andrei@coolbits.ai

---

## 📋 **Checklist**

### **Setup Checklist**
- [ ] NVIDIA driver installed
- [ ] CUDA 12.6 installed
- [ ] Python 3.11+ installed
- [ ] Virtual environment created
- [ ] GPU packages installed
- [ ] Ray cluster working
- [ ] Cloud integration tested

### **Development Checklist**
- [ ] Local RAG system working
- [ ] GPU performance optimized
- [ ] Cloud connectivity tested
- [ ] Documentation updated
- [ ] Team communication sent

---

**Last Updated**: September 5, 2025  
**Next Review**: September 12, 2025  
**Maintained By**: Development Team
