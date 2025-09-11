# CoolBits.ai Agent Training Context

## Company Overview
**CoolBits.ai** - AI ecosystem for business intelligence and automation
**cblm.ai** - AI-powered business management platform

## Core Principles
- **Local-first approach** - All training stays within CoolBits.ai ecosystem
- **RAG-based augmentation** - Retrieval-Augmented Generation for context
- **Isolated per user/role** - No data leakage between agents
- **API keys are authentication only** - Not for data storage

## Agent Roles & Training Context

### CEO Agent (Andrei)
**Training Context:**
- Business strategy and vision
- Company operations and management
- Client relationships and partnerships
- Financial planning and growth
- Team leadership and decision making

**RAG Categories:** b-rag/ceo_training, b-rag/business_strategy

### CTO Agent
**Training Context:**
- Technical architecture and development
- AI/ML implementation and optimization
- System integration and scalability
- Technology stack decisions
- Development team management

**RAG Categories:** d-rag/cto_training, d-rag/ai_ml, d-rag/architecture

### Marketing Agent
**Training Context:**
- Brand positioning and messaging
- Digital marketing strategies
- Content creation and distribution
- Social media management
- Campaign optimization

**RAG Categories:** b-rag/marketing_training, b-rag/channels, b-rag/seo

### Development Agent
**Training Context:**
- Code implementation and best practices
- Testing and quality assurance
- DevOps and deployment
- Performance optimization
- Bug fixing and maintenance

**RAG Categories:** d-rag/dev_training, d-rag/programming, d-rag/testing

## Training Methodology

### 1. RAG Integration
- **Vector Database:** pgvector for efficient similarity search
- **Context Retrieval:** Per-user/role isolated contexts
- **Augmentation:** Real-time context injection during conversations

### 2. Fine-tuning (Optional)
- **Custom Models:** Trained on CoolBits.ai specific data
- **Role-specific:** Each agent role has specialized training
- **Continuous Learning:** Regular updates based on interactions

### 3. Security & Isolation
- **No External Training:** All training happens within CoolBits.ai
- **User Isolation:** Each user's data remains private
- **Role Separation:** Different access levels per agent role

## Implementation Strategy

### Phase 1: RAG Foundation
- ✅ Hierarchical RAG system with categories/subcategories
- ✅ Document organization by role and context
- ✅ Vector database integration for similarity search

### Phase 2: Agent-Specific Training
- 🔄 Role-specific training documents
- 🔄 Context-aware retrieval per agent
- 🔄 Continuous learning from interactions

### Phase 3: Advanced Features
- ⏳ Fine-tuning capabilities
- ⏳ Real-time context updates
- ⏳ Performance analytics and optimization

## Best Practices

### Data Management
- **Structured Storage:** Organized by role, category, and context
- **Version Control:** Track changes and updates
- **Access Control:** Role-based permissions

### Training Efficiency
- **Context Relevance:** Only retrieve relevant context
- **Performance Optimization:** Efficient vector search
- **Cost Management:** Optimize API usage with smart retrieval

### Security
- **Data Isolation:** No cross-user data access
- **Encryption:** Secure storage and transmission
- **Audit Trail:** Track all training data usage

## Current Status
- ✅ RAG system operational (http://localhost:8097/)
- ✅ Advanced admin panel (http://localhost:8098/)
- ✅ 4 main categories with subcategories
- ✅ Document upload and management
- 🔄 Agent-specific training implementation in progress

## Next Steps
1. Create role-specific training subcategories
2. Upload CoolBits.ai/cblm.ai context documents
3. Implement vector database integration
4. Create agent training interface
5. Test RAG augmentation with multi-agent chat
