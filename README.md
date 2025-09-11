# CoolBits.ai - Enterprise AI Platform

## 🚀 Quick Start (20 minutes)

### Prerequisites
- **Git** - Version control
- **Docker** - Containerization
- **Python 3.11+** - Runtime environment
- **Google Cloud CLI** - Cloud integration
- **VS Code** - Development environment

### One-Command Setup

#### Windows (PowerShell)
```powershell
# Clone repository
git clone https://github.com/coolbits-ai/coolbits.git
cd coolbits

# Setup development environment
.\scripts\dev-setup.ps1

# Start development
.\scripts\dev-workflow.ps1 start
```

#### Linux/macOS (Bash)
```bash
# Clone repository
git clone https://github.com/coolbits-ai/coolbits.git
cd coolbits

# Setup development environment
./scripts/dev-setup.sh

# Start development
./scripts/dev-workflow.sh start
```

### Verify Installation
```bash
# Check health
curl http://localhost:8501/_stcore/health

# Open application
open http://localhost:8501
```

## 📚 Documentation

### Core Documentation
- [**API Documentation**](docs/api.md) - Complete API reference
- [**Troubleshooting Guide**](docs/troubleshooting.md) - Common issues & solutions
- [**Development Workflow**](docs/development.md) - Development best practices
- [**Deployment Guide**](docs/deployment.md) - Production deployment

### Architecture
- [**Infrastructure Overview**](docs/architecture.md) - System architecture
- [**Security Model**](docs/security.md) - Security implementation
- [**Monitoring & Observability**](docs/monitoring.md) - Monitoring setup

## 🛠️ Development

### Daily Workflow
```bash
# Start development environment
./scripts/dev-workflow.sh start

# Run tests
./scripts/dev-workflow.sh test

# Format code
./scripts/dev-workflow.sh format

# Deploy to staging
./scripts/dev-workflow.sh deploy-staging

# View logs
./scripts/dev-workflow.sh logs
```

### Available Commands
- `start` - Start development environment
- `stop` - Stop development environment
- `test` - Run test suite
- `lint` - Run code linting
- `format` - Format code with Black
- `deploy-staging` - Deploy to staging environment
- `logs` - View application logs
- `shell` - Open container shell
- `clean` - Clean up resources

## 🏗️ Architecture

### Core Components
- **Frontend**: Streamlit web application
- **Backend**: Python FastAPI services
- **Database**: PostgreSQL with Redis caching
- **AI/ML**: OpenAI, xAI, Vertex AI integration
- **Infrastructure**: Google Cloud Platform

### Security Features
- **Encryption**: CMEK for all data at rest
- **Authentication**: OAuth 2.0 + JWT tokens
- **Authorization**: Role-based access control
- **Monitoring**: Comprehensive security monitoring
- **Compliance**: GDPR, SOC 2 ready

## 🚀 Deployment

### Environments
- **Development**: Local Docker environment
- **Staging**: Google Cloud Run staging
- **Production**: Google Cloud Run production

### Deployment Process
```bash
# Deploy to staging
./scripts/deploy-staging.sh

# Deploy to production
./scripts/deploy-production.sh

# Verify deployment
./scripts/health-check.sh
```

## 📊 Monitoring

### Health Checks
- **Application**: `/api/v1/health`
- **Database**: Connection and query performance
- **External APIs**: OpenAI, xAI availability
- **Infrastructure**: Cloud Run, Cloud SQL status

### Metrics
- **Performance**: Response time, throughput
- **Errors**: Error rate, exception tracking
- **Resources**: CPU, memory, disk usage
- **Business**: User activity, feature usage

## 🆘 Support

### Getting Help
1. **Documentation**: Check this README and docs/
2. **Issues**: Search GitHub Issues
3. **Slack**: #dev-help channel
4. **Email**: dev-support@coolbits.ai

### Troubleshooting
- [**Common Issues**](docs/troubleshooting.md#common-issues)
- [**Performance Problems**](docs/troubleshooting.md#performance)
- [**Deployment Issues**](docs/troubleshooting.md#deployment)
- [**Security Concerns**](docs/troubleshooting.md#security)

## 🔧 Configuration

### Environment Variables
```bash
# Core configuration
OPIPE_ENV=development
GOOGLE_CLOUD_PROJECT=coolbits-ai
DEBUG=true

# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Redis
REDIS_URL=redis://host:port

# API Keys (use Secret Manager in production)
OPENAI_API_KEY=sk-...
XAI_API_KEY=xai-...
```

### Secrets Management
- **Development**: `.env` file
- **Staging/Production**: Google Secret Manager
- **CI/CD**: GitHub Secrets

## 🧪 Testing

### Test Suite
```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_api.py

# Run with coverage
pytest --cov=. tests/

# Run security tests
bandit -r .
safety check
```

### Test Types
- **Unit Tests**: Individual component testing
- **Integration Tests**: API and database testing
- **Security Tests**: Vulnerability scanning
- **Performance Tests**: Load and stress testing

## 📈 Performance

### Optimization
- **Caching**: Redis for frequently accessed data
- **CDN**: Cloud CDN for static content
- **Database**: Connection pooling and query optimization
- **Monitoring**: Real-time performance tracking

### Scaling
- **Horizontal**: Auto-scaling Cloud Run instances
- **Vertical**: Resource optimization
- **Geographic**: Multi-region deployment
- **Load Balancing**: Global load balancer

## 🔒 Security

### Security Features
- **Encryption**: End-to-end encryption
- **Authentication**: Multi-factor authentication
- **Authorization**: Fine-grained permissions
- **Monitoring**: Security event logging
- **Compliance**: GDPR, SOC 2 compliance

### Security Scanning
- **Code**: Static analysis with Bandit
- **Dependencies**: Vulnerability scanning with Safety
- **Secrets**: Secret detection with Gitleaks
- **Containers**: CVE scanning with Trivy

## 📝 Contributing

### Development Process
1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** your changes
5. **Submit** a pull request

### Code Standards
- **Formatting**: Black code formatter
- **Linting**: Flake8 and MyPy
- **Testing**: Pytest with coverage
- **Documentation**: Docstrings and README updates

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT models
- **xAI** for Grok models
- **Google Cloud** for infrastructure
- **Streamlit** for web framework
- **Community** for contributions

---

**CoolBits.ai** - Enterprise AI Platform for the Modern World

For more information, visit [coolbits.ai](https://coolbits.ai) or contact [support@coolbits.ai](mailto:support@coolbits.ai)