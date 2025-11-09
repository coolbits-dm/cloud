const express = require('express');
const { Firestore } = require('@google-cloud/firestore');
const app = express();
const port = process.env.PORT || 3000;

const firestore = new Firestore({ projectId: 'coolbits-ai' });
app.use(express.json());

// Agency Panel - Agency management and c-bit wall
const PANEL_TYPE = 'agency';
const PANEL_NAME = 'Agency Panel';
const PANEL_TOKENS = 10000; // Monthly cbT allowance

// Health endpoint
app.get('/api/v1/health', (req, res) => res.json({ 
  status: 'GREEN', 
  panel: PANEL_TYPE,
  name: PANEL_NAME,
  tokens: PANEL_TOKENS,
  timestamp: new Date().toISOString()
}));

// Agency wall - client management & campaigns
app.get('/api/wall', async (req, res) => {
  try {
    const agencyId = req.query.agencyId || 'default-agency';
    
    // Get agency campaigns and client data
    const agencyData = await firestore
      .collection('agency_campaigns')
      .where('agencyId', '==', agencyId)
      .orderBy('timestamp', 'desc')
      .limit(20)
      .get();
    
    const wallData = [];
    agencyData.forEach(doc => {
      wallData.push({
        ...doc.data(),
        id: doc.id
      });
    });
    
    // Add mock agency data if no data exists
    if (wallData.length === 0) {
      wallData.push(
        {
          type: 'campaign',
          client: 'TechCorp',
          campaign: 'Q4 Digital Marketing',
          status: 'active',
          budget: '$50,000',
          timestamp: new Date()
        },
        {
          type: 'client',
          client: 'StartupXYZ',
          service: 'Google Ads Management',
          performance: '+23% ROI',
          timestamp: new Date()
        },
        {
          type: 'announcement',
          content: 'New client onboarding: FashionBrand Inc.',
          priority: 'high',
          timestamp: new Date()
        }
      );
    }
    
    res.json({
      panel: PANEL_TYPE,
      agencyId,
      wall: wallData,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to get agency wall' });
  }
});

// Agency AI chat - with cbT tracking
app.post('/api/ai/chat', async (req, res) => {
  try {
    const { message, agent = 'agency-manager', agencyId = 'default-agency' } = req.body;
    const cbtCost = 3; // Agency agents cost more
    
    // Check agency cbT balance
    const agencyDoc = await firestore.collection('agency_tokens').doc(agencyId).get();
    const currentTokens = agencyDoc.exists ? agencyDoc.data().tokens || 0 : PANEL_TOKENS;
    
    if (currentTokens < cbtCost) {
      return res.status(402).json({ 
        error: 'Insufficient cbT', 
        current: currentTokens, 
        required: cbtCost,
        panel: PANEL_TYPE
      });
    }
    
    // Agency AI agents
    const agencyAgents = {
      'agency-manager': 'Agency Manager',
      'campaign-specialist': 'Campaign Specialist',
      'client-success': 'Client Success Manager',
      'media-buyer': 'Media Buyer',
      'analytics-expert': 'Analytics Expert',
      'creative-director': 'Creative Director',
      'mcc-manager': 'MCC Manager'
    };
    
    const agentName = agencyAgents[agent] || 'Agency Assistant';
    const response = {
      panel: PANEL_TYPE,
      agent,
      agentName,
      agencyId,
      message,
      response: `[${agentName}] ${message}`,
      cbT: currentTokens - cbtCost,
      timestamp: new Date().toISOString()
    };
    
    // Log to agency activity
    await firestore.collection('agency_activity').add({
      type: 'chat',
      agencyId,
      agent,
      message,
      response: response.response,
      cbTUsed: cbtCost,
      timestamp: new Date()
    });
    
    // Deduct cbT
    await firestore.collection('agency_tokens').doc(agencyId).set({
      tokens: currentTokens - cbtCost,
      lastUpdated: new Date(),
      monthlyAllowance: PANEL_TOKENS
    }, { merge: true });
    
    res.json(response);
  } catch (error) {
    res.status(500).json({ error: 'Agency chat failed' });
  }
});

// Agency profile and settings
app.get('/api/profile', async (req, res) => {
  try {
    const agencyId = req.query.agencyId || 'default-agency';
    
    const agencyDoc = await firestore.collection('agency_profiles').doc(agencyId).get();
    const tokenDoc = await firestore.collection('agency_tokens').doc(agencyId).get();
    
    const profile = {
      panel: PANEL_TYPE,
      agencyId,
      profile: agencyDoc.exists ? agencyDoc.data() : {
        name: 'Cool Bits Agency',
        type: 'Digital Marketing',
        clients: 15,
        website: 'https://coolbits.ai/agency',
        description: 'Full-service digital marketing agency',
        mccAccess: true,
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
    res.status(500).json({ error: 'Failed to get agency profile' });
  }
});

// Agency analytics and client management
app.get('/api/analytics', async (req, res) => {
  try {
    const agencyId = req.query.agencyId || 'default-agency';
    
    // Get agency activity stats
    const activityStats = await firestore
      .collection('agency_activity')
      .where('agencyId', '==', agencyId)
      .get();
    
    const stats = {
      panel: PANEL_TYPE,
      agencyId,
      totalActivities: activityStats.size,
      cbTUsed: 0,
      topAgents: {},
      clients: {
        total: 15,
        active: 12,
        new: 3,
        revenue: '$125,000'
      },
      campaigns: {
        active: 8,
        completed: 24,
        performance: '+18.5%'
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
    res.status(500).json({ error: 'Failed to get agency analytics' });
  }
});

// MCC integration endpoint
app.get('/api/mcc/status', async (req, res) => {
  try {
    const agencyId = req.query.agencyId || 'default-agency';
    
    const mccStatus = {
      panel: PANEL_TYPE,
      agencyId,
      mccAccess: true,
      accounts: 15,
      totalSpend: '$45,000',
      performance: '+23%',
      timestamp: new Date().toISOString()
    };
    
    res.json(mccStatus);
  } catch (error) {
    res.status(500).json({ error: 'Failed to get MCC status' });
  }
});

app.listen(port, () => console.log(`🎯 ${PANEL_NAME} running on port ${port}`));
