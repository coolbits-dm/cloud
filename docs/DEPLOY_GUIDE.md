# CoolBits.ai Production Deployment Guide

## 🚀 **DEPLOYMENT OPTIONS**

### **Option 1: DigitalOcean Droplet**

#### **Prerequisites**
- DigitalOcean account
- Docker installed on droplet
- GitHub Personal Access Token

#### **Deployment Steps**

1. **Create Droplet**
```bash
# Create Ubuntu 22.04 droplet (minimum 2GB RAM)
# Enable Docker during creation
```

2. **Initial Setup**
```bash
# SSH into droplet
ssh root@your-droplet-ip

# Update system
apt update && apt -y upgrade

# Install Docker (if not pre-installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Add user to docker group
usermod -aG docker $USER
```

3. **Deploy Application**
```bash
# Login to GitHub Container Registry
docker login ghcr.io -u <github_username> -p <github_token>

# Create application directory
mkdir -p /opt/coolbits && cd /opt/coolbits

# Download docker-compose.yml
curl -O https://raw.githubusercontent.com/coolbits-dm/coolbits.ai/main/docker-compose.yml

# Create environment file
cat > .env << EOF
OPIPE_ENV=prod
DB_URL=sqlite:///./data/coolbits.db
AGENTS_ENABLED=mock
EOF

# Pull and start containers
docker compose pull
docker compose up -d

# Verify deployment
docker compose ps
docker compose logs -f --tail=200 web
```

4. **Health Monitoring**
```bash
# Check health status
docker compose ps

# View logs
docker compose logs -f web

# Enable auto-restart
docker update --restart=always coolbits_web
```

5. **Rollback Procedure**
```bash
# Stop current container
docker compose down

# Pull previous version
docker pull ghcr.io/coolbits-dm/coolbits.ai:<previous_tag>

# Start with previous version
docker run -d --name coolbits_web_old \
  -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  ghcr.io/coolbits-dm/coolbits.ai:<previous_tag>
```

---

### **Option 2: AWS Lightsail Container Service**

#### **Prerequisites**
- AWS account
- AWS CLI configured
- Lightsail Container Service enabled

#### **Deployment Steps**

1. **Create Container Service**
```bash
# Create Lightsail container service
aws lightsail create-container-service \
  --service-name coolbits \
  --power small \
  --scale 1
```

2. **Push Image**
```bash
# Push Docker image to Lightsail
aws lightsail push-container-image \
  --service-name coolbits \
  --label web \
  --image ghcr.io/coolbits-dm/coolbits.ai:0.1.0
```

3. **Deploy Service**
```bash
# Create deployment
aws lightsail create-container-service-deployment \
  --service-name coolbits \
  --containers '{
    "web": {
      "image": "ghcr.io/coolbits-dm/coolbits.ai:0.1.0",
      "environment": {
        "OPIPE_ENV": "prod",
        "DB_URL": "sqlite:///./data/coolbits.db",
        "AGENTS_ENABLED": "mock"
      },
      "ports": {
        "8501": "HTTP"
      }
    }
  }' \
  --public-endpoint '{
    "containerName": "web",
    "containerPort": 8501,
    "healthCheck": {
      "path": "/_stcore/health",
      "successCodes": "200"
    }
  }'
```

4. **Monitor Deployment**
```bash
# Check service status
aws lightsail get-container-services

# View logs
aws lightsail get-container-log \
  --service-name coolbits \
  --container-name web
```

---

## 🔧 **CONFIGURATION**

### **Environment Variables**
```bash
OPIPE_ENV=prod                    # Production environment
DB_URL=sqlite:///./data/coolbits.db  # Database URL
AGENTS_ENABLED=mock               # Agent configuration
```

### **Ports**
- **8501** - Streamlit web interface
- **6333** - Qdrant vector database

### **Volumes**
- `./data` - Database and application data
- `./logs` - Application logs
- `./qdrant_storage` - Vector database storage

---

## 📊 **MONITORING**

### **Health Checks**
- **Web Service**: `http://localhost:8501/_stcore/health`
- **Qdrant**: `http://localhost:6333/`

### **Logs**
```bash
# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f web
docker compose logs -f qdrant

# View last 200 lines
docker compose logs --tail=200 web
```

### **Performance Monitoring**
```bash
# Container stats
docker stats

# Disk usage
docker system df

# Volume usage
docker volume ls
```

---

## 🔒 **SECURITY**

### **Container Security**
- Non-root user (appuser)
- Read-only filesystem where possible
- Minimal base image (python:3.12-slim)

### **Network Security**
- Internal network for container communication
- Only necessary ports exposed
- Health check endpoints secured

### **Data Security**
- Persistent volumes for data
- Environment variables for secrets
- Regular security scans with Trivy

---

## 🚨 **TROUBLESHOOTING**

### **Common Issues**

1. **Container won't start**
```bash
# Check logs
docker compose logs web

# Check environment
docker compose config

# Restart service
docker compose restart web
```

2. **Database issues**
```bash
# Check database file
ls -la data/

# Recreate database
docker compose exec web python -m app.core.db
docker compose exec web python -m app.seed.seed_users
```

3. **Port conflicts**
```bash
# Check port usage
netstat -tulpn | grep 8501

# Change port in docker-compose.yml
ports:
  - "8502:8501"  # Use different host port
```

### **Support**
- Check logs: `docker compose logs -f`
- Restart services: `docker compose restart`
- Full restart: `docker compose down && docker compose up -d`
