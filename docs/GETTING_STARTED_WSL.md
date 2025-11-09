# 🚀 GETTING STARTED WSL - CoolBits.ai & CBLM.ai
## Complete Windows Backbone Setup Guide

---

## ✅ **SYSTEM STATUS: FULLY OPERATIONAL**

**Date:** September 8, 2025  
**Status:** ✅ COMPLETE AND OPERATIONAL  
**Environment:** Windows 11 + WSL Ubuntu 24.04 + Docker + GPU

---

## 🏗️ **ARCHITECTURE OVERVIEW**

### **🖥️ Windows Backbone Infrastructure:**
```
Windows Machine (Backbone)
├── RTX 2060 (6GB VRAM) ✅
├── CUDA 12.6 ✅
├── Docker 28.3.3 ✅
├── WSL Ubuntu 24.04 ✅
├── Python 3.12.3 ✅
└── Project: coolbits-ai & cblm-ai ✅
```

### **☁️ Google Cloud Integration:**
```
Google Cloud Platform
├── Vertex AI (RAG Engine)
├── Cloud Run Services
├── Cloud Storage Buckets
├── 88 RAG Corpora
└── API Endpoints
```

---

## 🛠️ **INSTALLATION VERIFIED**

### **✅ Docker Installation:**
- **Version:** 28.3.3
- **Status:** Installed and functional
- **WSL Integration:** Enabled for Ubuntu
- **Test:** `docker run hello-world` ✅ PASSED

### **✅ WSL Ubuntu Setup:**
- **Distribution:** Ubuntu 24.04
- **User:** andrei
- **Status:** Running (WSL2)
- **Working Directory:** `/mnt/c/Users/andre/Desktop/coolbits`

### **✅ GPU Configuration:**
- **GPU:** NVIDIA GeForce RTX 2060
- **VRAM:** 6GB GDDR6
- **CUDA Version:** 12.6
- **WSL Visibility:** ✅ `nvidia-smi` works
- **Docker GPU Support:** ✅ Ready

### **✅ Python Environment:**
- **Python Version:** 3.12.3
- **Virtual Environment:** `.venv` created
- **Dependencies:** All installed via `requirements.txt`
- **Streamlit:** Running on port 8501

---

## 📁 **PROJECT STRUCTURE**

### **✅ Complete Directory Structure:**
```
coolbits/
├── app/                    # Application code
├── agents/                 # AI agents
├── rag/                    # RAG system
├── ops/                    # Operations
├── configs/                # Configuration files
├── scripts/                # Automation scripts
├── docs/                   # Documentation
├── tests/                  # Test files
├── data/                   # Data storage
├── logs/                   # Log files
├── .venv/                  # Python virtual environment
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # Docker configuration
├── coolbits_web_app.py     # Main Streamlit app
└── README.md              # Project documentation
```

---

## 🚀 **QUICK START COMMANDS**

### **1. Access WSL Ubuntu:**
```bash
wsl -d Ubuntu
```

### **2. Navigate to Project:**
```bash
cd /mnt/c/Users/andre/Desktop/coolbits
```

### **3. Activate Virtual Environment:**
```bash
source .venv/bin/activate
```

### **4. Run Streamlit App:**
```bash
streamlit run coolbits_web_app.py --server.port 8501
```

### **5. Access Application:**
- **URL:** http://localhost:8501
- **Status:** ✅ OPERATIONAL

---

## 🔧 **DEVELOPMENT WORKFLOW**

### **Daily Development:**
1. **Start WSL:** `wsl -d Ubuntu`
2. **Navigate:** `cd /mnt/c/Users/andre/Desktop/coolbits`
3. **Activate:** `source .venv/bin/activate`
4. **Develop:** Edit files in Windows, run in WSL
5. **Test:** `streamlit run coolbits_web_app.py`

### **Docker Development:**
1. **Build:** `docker build -t coolbits-app .`
2. **Run:** `docker run -p 8501:8501 coolbits-app`
3. **GPU Support:** `docker run --gpus all coolbits-app`

---

## 📊 **SYSTEM MONITORING**

### **GPU Status:**
```bash
nvidia-smi
```

### **Docker Status:**
```bash
docker --version
docker ps
```

### **WSL Status:**
```bash
wsl --list --verbose
```

### **Python Environment:**
```bash
python3 --version
pip list
```

---

## 🎯 **NEXT STEPS**

### **Week 1 (Sept 9-15):** User Roles & ACL Integration
- Implement user authentication system
- Create role-based access control
- Integrate ACL in UI components

### **Week 2 (Sept 16-22):** RAG v1.1 Implementation
- Implement 4-layer ingest system
- Create retrieval optimization
- Deploy RAG corpora

### **Week 3 (Sept 23-29):** oPipe® Agent Registry
- Create agent registry system
- Implement transcript logging
- Deploy agent management

### **Week 4 (Sept 30-Oct 6):** Job Automation & Health Dashboard
- Implement job scheduling
- Create health monitoring
- Deploy automation system

---

## 🎯 **MILESTONE TARGETS**

### **Milestone 1: Docker + ACL (Sept 22, 2025)**
- ✅ Docker environment operational
- 🔄 ACL system implementation
- 🔄 User roles integration
- 🔄 Security framework

### **Milestone 2: RAG v1.1 (Oct 6, 2025)**
- 🔄 4-layer ingest system
- 🔄 Retrieval optimization
- 🔄 Performance monitoring

---

## 🔍 **TROUBLESHOOTING**

### **Common Issues:**

#### **WSL Access Issues:**
```bash
# Restart WSL
wsl --shutdown
wsl -d Ubuntu
```

#### **Docker Permission Issues:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### **GPU Not Visible:**
```bash
# Check GPU in WSL
nvidia-smi
# If not visible, restart WSL
```

#### **Python Environment Issues:**
```bash
# Recreate virtual environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 📞 **SUPPORT**

### **System Status:**
- **Windows Backbone:** ✅ OPERATIONAL
- **WSL Ubuntu:** ✅ OPERATIONAL
- **Docker:** ✅ OPERATIONAL
- **GPU:** ✅ OPERATIONAL
- **Python:** ✅ OPERATIONAL
- **Streamlit:** ✅ OPERATIONAL

### **Contact:**
- **CEO:** Andrei (andrei@coolbits.ro)
- **Project:** CoolBits.ai & CBLM.ai
- **Environment:** Windows Development Backbone

---

## 🎉 **READY FOR DEVELOPMENT!**

The Windows backbone with WSL Ubuntu is now fully operational and ready for CoolBits.ai and CBLM.ai development. All systems are verified and functional.

**Next:** Begin Week 1 development with User Roles & ACL integration.

---

*Documentation generated: September 8, 2025*  
*System Status: FULLY OPERATIONAL*  
*Ready for: CoolBits.ai & CBLM.ai Development*
