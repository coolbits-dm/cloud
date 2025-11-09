# Gemini Vertex AI Integration Guide - CoolBits.ai

## 🤖 Overview

This guide provides complete setup and implementation for Gemini Vertex AI integration with CoolBits.ai, enabling interactive chat sessions directly from your Windows 11 Cursor console.

**Company**: COOL BITS SRL  
**CEO**: Andrei  
**Project ID**: coolbits-ai  
**Region**: europe-west3  

## 🚀 Quick Start

### Step 1: Run Setup Script
```bash
python setup_gemini_vertex_ai.py
```

### Step 2: Start Chat
```bash
python chat_with_gemini_coolbits.py
```

## 📋 Prerequisites

### System Requirements
- **OS**: Windows 11
- **Python**: 3.8 or higher
- **IDE**: Cursor (or any terminal)
- **Google Cloud Account**: Active project with Vertex AI enabled

### Required Packages
- `google-cloud-aiplatform`
- `google-cloud-core`
- `requests`
- `python-dotenv`

## 🔧 Detailed Setup

### 1. Environment Preparation

#### Install Python
Ensure Python 3.8+ is installed on your Windows 11 machine:
- Download from [python.org](https://www.python.org/downloads/)
- Verify installation: `python --version`

#### Install Google Cloud CLI
1. Download from [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
2. Install and verify: `gcloud --version`

### 2. Google Cloud Configuration

#### Authenticate with Google Cloud
```bash
gcloud auth application-default login
```
This opens a browser window for authentication.

#### Set Project and Region
```bash
gcloud config set project coolbits-ai
gcloud config set compute/region europe-west3
```

#### Enable Vertex AI API
```bash
gcloud services enable aiplatform.googleapis.com
```

### 3. Python Environment Setup

#### Install Required Packages
```bash
pip install google-cloud-aiplatform google-cloud-core requests python-dotenv
```

#### Verify Installation
```bash
python -c "import vertexai; print('Vertex AI SDK installed successfully')"
```

## 💬 Chat Implementation

### Basic Chat Script
The main chat script (`chat_with_gemini_coolbits.py`) provides:

- **Interactive chat session** with Gemini model
- **CoolBits.ai integration** with API calls
- **System commands** for chat management
- **Error handling** and logging
- **Context preservation** across conversation turns

### Key Features

#### CoolBits.ai Commands
- `/coolbits info` - Show company information
- `/coolbits status` - Show system status
- `/coolbits api` - Test API integration
- `/coolbits help` - Show help

#### System Commands
- `/help` - Show available commands
- `/clear` - Clear chat history
- `/status` - Show system status
- `/quit` or `/exit` - Exit chat

#### API Integration
The script includes hooks for CoolBits.ai API integration:
```python
def call_coolbits_api(self, user_input: str) -> Optional[str]:
    # Simulate CoolBits.ai API call
    # Replace with actual API implementation
```

## 🧪 Testing

### Test Script
Run the test script to verify setup:
```bash
python test_gemini.py
```

### Chat Test
Start interactive chat:
```bash
python chat_with_gemini_coolbits.py
```

### Example Conversation
```
🤖 COOLBITS.AI GEMINI VERTEX AI CHAT
================================================================================
🏢 Company: COOL BITS SRL
👤 CEO: Andrei
🆔 Project: coolbits-ai
🌍 Region: europe-west3
🤖 Model: gemini-pro
================================================================================
✅ Gemini chat initialized successfully!
💬 Type your message and press Enter to chat with Gemini
🆘 Type '/help' for available commands
🚪 Type 'quit' or 'exit' to end the conversation
--------------------------------------------------------------------------------

👤 You: Hello Gemini, how are you?

🤖 Gemini: Hello! I'm doing well, thank you for asking. I'm here and ready to help you with any questions or tasks you might have. How can I assist you today?

👤 You: /coolbits info

🤖 Gemini: 
🏢 CoolBits.ai Information:
   Company: COOL BITS SRL
   CEO: Andrei
   Project ID: coolbits-ai
   Region: europe-west3
   Model: gemini-pro
   Status: Active

👤 You: quit

👋 Goodbye! Thanks for chatting with CoolBits.ai Gemini!
```

## 🔒 Security & Authentication

### Authentication Methods
- **Application Default Credentials**: Primary authentication method
- **Service Account Keys**: For production deployments
- **OAuth 2.0**: For user-facing applications

### Security Best Practices
- Store credentials securely
- Use environment variables for sensitive data
- Rotate API keys regularly
- Monitor API usage and costs

## 📊 Monitoring & Logging

### Logging Configuration
The script includes comprehensive logging:
```python
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
```

### Monitoring Features
- **Request/Response logging**
- **Error tracking**
- **Performance monitoring**
- **Usage analytics**

## 🚨 Troubleshooting

### Common Issues

#### 1. Authentication Errors
```
❌ Error: 403 Forbidden
💡 Make sure you're authenticated with: gcloud auth application-default login
```
**Solution**: Run `gcloud auth application-default login`

#### 2. Project Not Found
```
❌ Error: Project 'coolbits-ai' not found
```
**Solution**: Verify project ID and permissions

#### 3. Vertex AI Not Enabled
```
❌ Error: Vertex AI API not enabled
```
**Solution**: Run `gcloud services enable aiplatform.googleapis.com`

#### 4. Package Import Errors
```
❌ Vertex AI SDK not available
```
**Solution**: Run `pip install google-cloud-aiplatform`

### Debug Mode
Enable debug logging:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📁 Generated Files

- `chat_with_gemini_coolbits.py` - Main chat script
- `setup_gemini_vertex_ai.py` - Setup script
- `test_gemini.py` - Test script
- `gemini_vertex_config.json` - Configuration file

## 🔄 Advanced Features

### Custom Model Configuration
```python
# Use different Gemini model
model = GenerativeModel("gemini-pro-vision")  # For image analysis
model = GenerativeModel("gemini-1.5-pro")     # Latest model
```

### API Integration Examples
```python
# CoolBits.ai API call
def call_coolbits_api(self, user_input: str):
    response = requests.post(
        f"{self.coolbits_api_config['base_url']}/chat",
        json={"message": user_input},
        headers={"Authorization": "Bearer YOUR_API_KEY"}
    )
    return response.json()
```

### Conversation Context
```python
# Maintain conversation history
chat_session = model.start_chat(history=[
    Part.from_text("You are a helpful AI assistant for CoolBits.ai"),
    Part.from_text("Always be professional and helpful")
])
```

## 📈 Performance Optimization

### Caching
- Cache model responses for repeated queries
- Implement conversation context caching
- Use connection pooling for API calls

### Rate Limiting
- Implement request throttling
- Monitor API quotas
- Handle rate limit errors gracefully

### Error Handling
- Retry failed requests with exponential backoff
- Implement circuit breaker pattern
- Log and monitor error rates

## 🎯 Success Criteria

- ✅ Gemini model responds to user input
- ✅ CoolBits.ai commands work correctly
- ✅ Chat session maintains context
- ✅ Error handling works properly
- ✅ Authentication is successful
- ✅ API integration is functional

## 🚀 Next Steps

1. **Deploy to Production**: Set up production environment
2. **Add More Features**: Implement additional CoolBits.ai integrations
3. **Scale Operations**: Add support for multiple users
4. **Monitor Performance**: Set up comprehensive monitoring
5. **Optimize Costs**: Monitor and optimize API usage

---

**Classification**: Internal Secret - CoolBits.ai Members Only  
**Last Updated**: September 7, 2025  
**Updated by**: @oGemini Vertex AI Integration Manager
