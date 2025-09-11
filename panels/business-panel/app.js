const express = require('express');
const { Firestore } = require('@google-cloud/firestore');
const app = express();
const port = process.env.PORT || 3000;

const firestore = new Firestore({ projectId: 'coolbits-ai' });
app.use(express.json());

// Business Panel - Business AI agents and b-bit wall
const PANEL_TYPE = 'business';
const PANEL_NAME = 'Business Panel';
const PANEL_TOKENS = 5000; // Monthly cbT allowance

// Health endpoint
app.get('/api/v1/health', (req, res) => res.json({ 
  status: 'GREEN', 
  panel: PANEL_TYPE,
  name: PANEL_NAME,
  tokens: PANEL_TOKENS,
  timestamp: new Date().toISOString()
}));

// Business wall - business metrics & KPIs
app.get('/api/wall', async (req, res) => {
  try {
    const businessId = req.query.businessId || 'default-business';
    
    // Get business metrics and KPIs
    const businessMetrics = await firestore
      .collection('business_metrics')
      .where('businessId', '==', businessId)
      .orderBy('timestamp', 'desc')
      .limit(20)
      .get();
    
    const wallData = [];
    businessMetrics.forEach(doc => {
      wallData.push({
        ...doc.data(),
        id: doc.id
      });
    });
    
    // Add mock business KPIs if no data exists
    if (wallData.length === 0) {
      wallData.push(
        {
          type: 'kpi',
          metric: 'Revenue Growth',
          value: '+15.3%',
          trend: 'up',
          timestamp: new Date()
        },
        {
          type: 'kpi', 
          metric: 'Customer Acquisition',
          value: '127 new customers',
          trend: 'up',
          timestamp: new Date()
        },
        {
          type: 'announcement',
          content: 'Q4 Business Review completed',
          priority: 'high',
          timestamp: new Date()
        }
      );
    }
    
    res.json({
      panel: PANEL_TYPE,
      businessId,
      wall: wallData,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to get business wall' });
  }
});

// Business AI chat - with cbT tracking
app.post('/api/ai/chat', async (req, res) => {
  try {
    const { message, agent = 'ceo', businessId = 'default-business' } = req.body;
    const cbtCost = 2; // Business agents cost more
    
    // Check business cbT balance
    const businessDoc = await firestore.collection('business_tokens').doc(businessId).get();
    const currentTokens = businessDoc.exists ? businessDoc.data().tokens || 0 : PANEL_TOKENS;
    
    if (currentTokens < cbtCost) {
      return res.status(402).json({ 
        error: 'Insufficient cbT', 
        current: currentTokens, 
        required: cbtCost,
        panel: PANEL_TYPE
      });
    }
    
    // Business AI agents
    const businessAgents = {
      'ceo': 'Chief Executive Officer',
      'cto': 'Chief Technology Officer',
      'cmo': 'Chief Marketing Officer', 
      'cfo': 'Chief Financial Officer',
      'hr': 'Human Resources Director',
      'business-analyst': 'Business Analyst',
      'strategy-advisor': 'Strategy Advisor'
    };
    
    const agentName = businessAgents[agent] || 'Business Assistant';
    const response = {
      panel: PANEL_TYPE,
      agent,
      agentName,
      businessId,
      message,
      response: `[${agentName}] ${message}`,
      cbT: currentTokens - cbtCost,
      timestamp: new Date().toISOString()
    };
    
    // Log to business activity
    await firestore.collection('business_activity').add({
      type: 'chat',
      businessId,
      agent,
      message,
      response: response.response,
      cbTUsed: cbtCost,
      timestamp: new Date()
    });
    
    // Deduct cbT
    await firestore.collection('business_tokens').doc(businessId).set({
      tokens: currentTokens - cbtCost,
      lastUpdated: new Date(),
      monthlyAllowance: PANEL_TOKENS
    }, { merge: true });
    
    res.json(response);
  } catch (error) {
    res.status(500).json({ error: 'Business chat failed' });
  }
});

// Business profile and settings
app.get('/api/profile', async (req, res) => {
  try {
    const businessId = req.query.businessId || 'default-business';
    
    const businessDoc = await firestore.collection('business_profiles').doc(businessId).get();
    const tokenDoc = await firestore.collection('business_tokens').doc(businessId).get();
    
    const profile = {
      panel: PANEL_TYPE,
      businessId,
      profile: businessDoc.exists ? businessDoc.data() : {
        name: 'Cool Bits Business',
        industry: 'Technology',
        size: 'Startup',
        website: 'https://coolbits.ai',
        description: 'AI-powered business solutions',
        createdAt: new Date()
      },
      tokens: tokenDoc.exists ? tokenDoc.data() : {
        tokens: PANEL_TOKENS,
        monthlyAllowance: PANEL_TOKENS,
        lastUpdated: new Date()
      },
      timestamp: new Date().toISOString()
    };
    
    res.json(profile);
  } catch (error) {
    res.status(500).json({ error: 'Failed to get business profile' });
  }
});

// Update business profile
app.post('/api/profile', async (req, res) => {
  try {
    const { businessId = 'default-business', ...profileData } = req.body;
    
    await firestore.collection('business_profiles').doc(businessId).set({
      ...profileData,
      updatedAt: new Date()
    }, { merge: true });
    
    res.json({
      panel: PANEL_TYPE,
      businessId,
      message: 'Business profile updated successfully',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to update business profile' });
  }
});

// Business analytics and KPIs
app.get('/api/analytics', async (req, res) => {
  try {
    const businessId = req.query.businessId || 'default-business';
    
    // Get business activity stats
    const activityStats = await firestore
      .collection('business_activity')
      .where('businessId', '==', businessId)
      .get();
    
    const stats = {
      panel: PANEL_TYPE,
      businessId,
      totalActivities: activityStats.size,
      cbTUsed: 0,
      topAgents: {},
      kpis: {
        revenue: '+15.3%',
        customers: '127 new',
        growth: '23.5%',
        efficiency: '87%'
      },
      timestamp: new Date().toISOString()
    };
    
    activityStats.forEach(doc => {
      const data = doc.data();
      if (data.cbTUsed) stats.cbTUsed += data.cbTUsed;
      if (data.agent) {
        stats.topAgents[data.agent] = (stats.topAgents[data.agent] || 0) + 1;
      }
    });
    
    res.json(stats);
  } catch (error) {
    res.status(500).json({ error: 'Failed to get business analytics' });
  }
});

// RAG integration for business intelligence
app.post('/api/rag/search', async (req, res) => {
  try {
    const { query, businessId = 'default-business' } = req.body;
    
    // Mock RAG search for business intelligence
    const ragResults = {
      panel: PANEL_TYPE,
      businessId,
      query,
      results: [
        {
          source: 'Business Intelligence',
          content: `Based on your query "${query}", here are relevant business insights...`,
          relevance: 0.95,
          timestamp: new Date()
        },
        {
          source: 'Market Analysis',
          content: `Market trends related to "${query}" show positive growth...`,
          relevance: 0.87,
          timestamp: new Date()
        }
      ],
      timestamp: new Date().toISOString()
    };
    
    res.json(ragResults);
  } catch (error) {
    res.status(500).json({ error: 'RAG search failed' });
  }
});

app.listen(port, () => console.log(`🏢 ${PANEL_NAME} running on port ${port}`));
