# GPU Development Guide

## 🎮 **NVIDIA RTX 2060 Development Environment**

### **Overview**
This guide covers GPU development using the NVIDIA GeForce RTX 2060 (6GB VRAM) for CoolBits.ai and cbLM.ai projects.

---

## 🖥️ **GPU Specifications**

### **Hardware Details**
- **Model**: NVIDIA GeForce RTX 2060
- **VRAM**: 6GB GDDR6
- **CUDA Cores**: 1920
- **Base Clock**: 1365 MHz
- **Boost Clock**: 1680 MHz
- **Memory Bandwidth**: 336 GB/s

### **Software Support**
- **CUDA Version**: 12.6
- **Driver Version**: 560.94
- **PyTorch Support**: CUDA 12.1+
- **TensorFlow Support**: CUDA 12.1+

---

## 🚀 **Development Workflow**

### **Local Development**
```
Local GPU (RTX 2060) → Algorithm Development → Testing → Optimization
```

### **Production Deployment**
```
Local Development → Cloud Production → Monitoring → Scaling
```

### **Integration**
```
Local GPU ↔ Cloud GPU (via ogpt-bridge-service)
```

---

## 🔧 **GPU Configuration**

### **CUDA Environment**
```bash
# Set CUDA device
set CUDA_VISIBLE_DEVICES=0

# Set memory fraction
set CUDA_MEMORY_FRACTION=0.8
```

### **PyTorch Configuration**
```python
import torch

# Check CUDA availability
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
print(f"GPU name: {torch.cuda.get_device_name(0)}")

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")
```

### **Memory Management**
```python
# Monitor GPU memory
def print_gpu_memory():
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / 1024**2
        cached = torch.cuda.memory_reserved() / 1024**2
        print(f"GPU Memory - Allocated: {allocated:.1f} MB, Cached: {cached:.1f} MB")

# Clear cache when needed
torch.cuda.empty_cache()
```

---

## 🧪 **GPU Testing**

### **Performance Benchmark**
```python
import torch
import time

def benchmark_gpu():
    if not torch.cuda.is_available():
        print("❌ CUDA not available")
        return
    
    device = torch.device("cuda")
    
    # Test matrix multiplication
    sizes = [100, 500, 1000, 2000]
    
    for size in sizes:
        x = torch.randn(size, size, device=device)
        y = torch.randn(size, size, device=device)
        
        # Warmup
        for _ in range(10):
            _ = torch.matmul(x, y)
        
        torch.cuda.synchronize()
        
        # Benchmark
        start_time = time.time()
        for _ in range(100):
            z = torch.matmul(x, y)
        torch.cuda.synchronize()
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 100
        print(f"Size {size}x{size}: {avg_time*1000:.2f} ms")

benchmark_gpu()
```

### **RAG Performance Test**
```python
from sentence_transformers import SentenceTransformer
import torch

def test_rag_performance():
    # Load model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    if torch.cuda.is_available():
        model = model.to('cuda')
        print("✅ Model loaded on GPU")
    else:
        print("❌ Model loaded on CPU")
    
    # Test embedding generation
    texts = [
        "CoolBits.ai is an AI-powered platform",
        "cbLM.ai provides enterprise AI solutions",
        "Ray on Vertex AI enables distributed computing"
    ]
    
    import time
    start_time = time.time()
    
    embeddings = model.encode(texts)
    
    end_time = time.time()
    print(f"✅ Generated {len(embeddings)} embeddings in {end_time - start_time:.2f} seconds")
    print(f"📊 Embedding shape: {embeddings.shape}")

test_rag_performance()
```

---

## 🔗 **Ray GPU Integration**

### **Ray Cluster Setup**
```python
import ray

# Initialize Ray with GPU support
ray.init(
    num_gpus=1,
    num_cpus=4,
    ignore_reinit_error=True
)

@ray.remote
def gpu_task(data):
    import torch
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Process data on GPU
    tensor = torch.tensor(data, device=device)
    result = tensor * 2
    
    return result.cpu().numpy()

# Test GPU task
data = [1, 2, 3, 4, 5]
result = ray.get(gpu_task.remote(data))
print(f"GPU task result: {result}")

# Shutdown Ray
ray.shutdown()
```

### **Distributed RAG Processing**
```python
import ray
from sentence_transformers import SentenceTransformer

@ray.remote
def process_documents_gpu(documents):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    if torch.cuda.is_available():
        model = model.to('cuda')
    
    embeddings = model.encode(documents)
    return embeddings

# Process documents in parallel
documents = [
    "Document 1 content...",
    "Document 2 content...",
    "Document 3 content..."
]

# Split documents into batches
batch_size = 1
batches = [documents[i:i+batch_size] for i in range(0, len(documents), batch_size)]

# Process batches in parallel
futures = [process_documents_gpu.remote(batch) for batch in batches]
results = ray.get(futures)

print(f"✅ Processed {len(results)} batches")
```

---

## 📊 **Performance Monitoring**

### **GPU Utilization**
```python
import torch
import time

def monitor_gpu_usage():
    if not torch.cuda.is_available():
        print("❌ CUDA not available")
        return
    
    print("🎮 GPU Monitoring")
    print("=" * 40)
    
    # Initial state
    print(f"GPU Name: {torch.cuda.get_device_name(0)}")
    print(f"Total Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    
    # Monitor during processing
    for i in range(10):
        # Simulate work
        x = torch.randn(1000, 1000, device='cuda')
        y = torch.randn(1000, 1000, device='cuda')
        z = torch.matmul(x, y)
        
        # Print memory usage
        allocated = torch.cuda.memory_allocated() / 1024**2
        cached = torch.cuda.memory_reserved() / 1024**2
        
        print(f"Step {i+1}: Allocated: {allocated:.1f} MB, Cached: {cached:.1f} MB")
        
        time.sleep(0.1)
    
    # Cleanup
    torch.cuda.empty_cache()
    print("✅ Monitoring complete")

monitor_gpu_usage()
```

### **Performance Profiling**
```python
import torch
import time

def profile_gpu_operations():
    if not torch.cuda.is_available():
        print("❌ CUDA not available")
        return
    
    device = torch.device("cuda")
    
    # Profile different operations
    operations = {
        "Matrix Multiplication": lambda: torch.matmul(torch.randn(1000, 1000, device=device), torch.randn(1000, 1000, device=device)),
        "Element-wise Addition": lambda: torch.randn(1000, 1000, device=device) + torch.randn(1000, 1000, device=device),
        "ReLU Activation": lambda: torch.relu(torch.randn(1000, 1000, device=device)),
        "Softmax": lambda: torch.softmax(torch.randn(1000, 1000, device=device), dim=1)
    }
    
    print("🔍 GPU Operation Profiling")
    print("=" * 40)
    
    for name, operation in operations.items():
        # Warmup
        for _ in range(10):
            operation()
        
        torch.cuda.synchronize()
        
        # Profile
        start_time = time.time()
        for _ in range(100):
            operation()
        torch.cuda.synchronize()
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 100
        print(f"{name}: {avg_time*1000:.2f} ms")

profile_gpu_operations()
```

---

## 🐛 **Troubleshooting**

### **Common Issues**

#### **CUDA Out of Memory**
```python
# Reduce batch size
batch_size = 16  # Instead of 32

# Use gradient checkpointing
model.gradient_checkpointing_enable()

# Clear cache
torch.cuda.empty_cache()

# Use mixed precision
from torch.cuda.amp import autocast, GradScaler
scaler = GradScaler()

with autocast():
    output = model(input)
```

#### **Ray GPU Issues**
```python
# Check Ray GPU detection
ray.init(num_gpus=1)
print(f"Ray GPUs: {ray.cluster_resources().get('GPU', 0)}")

# Use local mode for debugging
ray.init(local_mode=True, num_gpus=1)
```

#### **Performance Issues**
```python
# Enable cuDNN benchmarking
torch.backends.cudnn.benchmark = True

# Use optimized data types
dtype = torch.float16  # Instead of float32

# Profile memory usage
torch.cuda.memory_summary()
```

---

## 📚 **Best Practices**

### **Memory Management**
1. **Monitor memory usage** regularly
2. **Clear cache** when needed
3. **Use appropriate batch sizes**
4. **Enable gradient checkpointing** for large models

### **Performance Optimization**
1. **Use cuDNN benchmarking** for consistent input sizes
2. **Enable mixed precision** training
3. **Profile operations** to identify bottlenecks
4. **Use Ray** for distributed processing

### **Development Workflow**
1. **Develop locally** with GPU
2. **Test algorithms** thoroughly
3. **Optimize performance** before cloud deployment
4. **Monitor costs** in production

---

## 📋 **Resources**

### **Documentation**
- **PyTorch CUDA**: https://pytorch.org/docs/stable/cuda.html
- **Ray GPU**: https://docs.ray.io/en/latest/ray-core/using-ray-with-gpus.html
- **NVIDIA CUDA**: https://docs.nvidia.com/cuda/

### **Tutorials**
- **Local RAG Development**: `local_rag_dev.py`
- **GPU Performance**: `test_gpu_performance.py`
- **Ray Integration**: `ray_gpu_integration.py`

### **Support**
- **Development Team**: [Contact Info]
- **DevOps Team**: [Contact Info]
- **CEO**: Andrei - andrei@coolbits.ai

---

**Last Updated**: September 5, 2025  
**Next Review**: September 12, 2025  
**Maintained By**: Development Team
