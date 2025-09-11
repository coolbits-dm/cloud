const express = require('express');
const { Firestore } = require('@google-cloud/firestore');
const app = express();
const port = process.env.PORT || 3000;

const firestore = new Firestore({ projectId: 'coolbits-ai' });
app.use(express.json());

// User Panel - Personal AI agents and u-bit wall
const PANEL_TYPE = 'user';
const PANEL_NAME = 'User Panel';
const PANEL_TOKENS = 1000; // Monthly cbT allowance

// Health endpoint
app.get('/api/v1/health', (req, res) => res.json({ 
  status: 'GREEN', 
  panel: PANEL_TYPE,
  name: PANEL_NAME,
  tokens: PANEL_TOKENS,
  timestamp: new Date().toISOString()
}));

// User wall - personal activity feed
app.get('/api/wall', async (req, res) => {
  try {
    const userId = req.query.userId || 'default-user';
    
    // Get user's personal activity
    const userActivity = await firestore
      .collection('user_activity')
      .where('userId', '==', userId)
      .orderBy('timestamp', 'desc')
      .limit(20)
      .get();
    
    const wallData = [];
    userActivity.forEach(doc => {
      wallData.push({
        ...doc.data(),
        id: doc.id
      });
    });
    
    res.json({
      panel: PANEL_TYPE,
      userId,
      wall: wallData,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to get user wall' });
  }
});

// Personal AI chat - with cbT tracking
app.post('/api/ai/chat', async (req, res) => {
  try {
    const { message, agent = 'personal-assistant', userId = 'default-user' } = req.body;
    const cbtCost = 1;
    
    // Check user's cbT balance
    const userDoc = await firestore.collection('user_tokens').doc(userId).get();
    const currentTokens = userDoc.exists ? userDoc.data().tokens || 0 : PANEL_TOKENS;
    
    if (currentTokens < cbtCost) {
      return res.status(402).json({ 
        error: 'Insufficient cbT', 
        current: currentTokens, 
        required: cbtCost,
        panel: PANEL_TYPE
      });
    }
    
    // Personal AI agents
    const personalAgents = {
      'personal-assistant': 'Personal Assistant',
      'productivity-coach': 'Productivity Coach', 
      'learning-buddy': 'Learning Buddy',
      'health-advisor': 'Health Advisor',
      'finance-helper': 'Finance Helper'
    };
    
    const agentName = personalAgents[agent] || 'Personal Assistant';
    const response = {
      panel: PANEL_TYPE,
      agent,
      agentName,
      userId,
      message,
      response: `[${agentName}] ${message}`,
      cbT: currentTokens - cbtCost,
      timestamp: new Date().toISOString()
    };
    
    // Log to user activity
    await firestore.collection('user_activity').add({
      type: 'chat',
      userId,
      agent,
      message,
      response: response.response,
      cbTUsed: cbtCost,
      timestamp: new Date()
    });
    
    // Deduct cbT
    await firestore.collection('user_tokens').doc(userId).set({
      tokens: currentTokens - cbtCost,
      lastUpdated: new Date(),
      monthlyAllowance: PANEL_TOKENS
    }, { merge: true });
    
    res.json(response);
  } catch (error) {
    res.status(500).json({ error: 'User chat failed' });
  }
});

// User profile and settings
app.get('/api/profile', async (req, res) => {
  try {
    const userId = req.query.userId || 'default-user';
    
    const userDoc = await firestore.collection('user_profiles').doc(userId).get();
    const tokenDoc = await firestore.collection('user_tokens').doc(userId).get();
    
    const profile = {
      panel: PANEL_TYPE,
      userId,
      profile: userDoc.exists ? userDoc.data() : {
        name: 'User',
        email: `${userId}@coolbits.ai`,
        preferences: {},
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
    res.status(500).json({ error: 'Failed to get user profile' });
  }
});

// Update user profile
app.post('/api/profile', async (req, res) => {
  try {
    const { userId = 'default-user', ...profileData } = req.body;
    
    await firestore.collection('user_profiles').doc(userId).set({
      ...profileData,
      updatedAt: new Date()
    }, { merge: true });
    
    res.json({
      panel: PANEL_TYPE,
      userId,
      message: 'Profile updated successfully',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to update profile' });
  }
});

// User analytics
app.get('/api/analytics', async (req, res) => {
  try {
    const userId = req.query.userId || 'default-user';
    
    // Get user activity stats
    const activityStats = await firestore
      .collection('user_activity')
      .where('userId', '==', userId)
      .get();
    
    const stats = {
      panel: PANEL_TYPE,
      userId,
      totalActivities: activityStats.size,
      cbTUsed: 0,
      topAgents: {},
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
    res.status(500).json({ error: 'Failed to get analytics' });
  }
});

app.listen(port, () => console.log(`👤 ${PANEL_NAME} running on port ${port}`));
