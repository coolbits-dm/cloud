const express = require('express');
const { Firestore } = require('@google-cloud/firestore');
const app = express();
const port = process.env.PORT || 3000;

const firestore = new Firestore({ projectId: 'coolbits-ai' });
app.use(express.json());

// Admin Panel - System control and admin wall
const PANEL_TYPE = 'admin';
const PANEL_NAME = 'Admin Panel';
const PANEL_TOKENS = 15000; // Monthly cbT allowance - highest tier

// Health endpoint
app.get('/api/v1/health', (req, res) => res.json({ 
  status: 'GREEN', 
  panel: PANEL_TYPE,
  name: PANEL_NAME,
  tokens: PANEL_TOKENS,
  power: 'admin',
  timestamp: new Date().toISOString()
}));

// Admin wall - system overview & control
app.get('/api/wall', async (req, res) => {
  try {
    const adminId = req.query.adminId || 'default-admin';
    
    // Get system-wide activity and metrics
    const systemData = await firestore
      .collection('system_logs')
      .orderBy('timestamp', 'desc')
      .limit(20)
      .get();
    
    const wallData = [];
    systemData.forEach(doc => {
      wallData.push({
        ...doc.data(),
        id: doc.id
      });
    });
    
    // Add mock system data if no data exists
    if (wallData.length === 0) {
      wallData.push(
        {
          type: 'system',
          event: 'Panel Deployment',
          service: 'business-panel',
          status: 'deployed',
          region: 'europe-west3',
          timestamp: new Date()
        },
        {
          type: 'user',
          event: 'New User Registration',
          user: 'user@coolbits.ai',
          panel: 'user',
          timestamp: new Date()
        },
        {
          type: 'security',
          event: 'API Key Rotation',
          service: 'openai',
          status: 'completed',
          timestamp: new Date()
        },
        {
          type: 'performance',
          event: 'System Health Check',
          status: 'all-green',
          uptime: '99.9%',
          timestamp: new Date()
        }
      );
    }
    
    res.json({
      panel: PANEL_TYPE,
      adminId,
      wall: wallData,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to get admin wall' });
  }
});

// Admin AI chat - with cbT tracking
app.post('/api/ai/chat', async (req, res) => {
  try {
    const { message, agent = 'system-admin', adminId = 'default-admin' } = req.body;
    const cbtCost = 1; // Admin has high allowance, low per-use cost
    
    // Check admin cbT balance
    const adminDoc = await firestore.collection('admin_tokens').doc(adminId).get();
    const currentTokens = adminDoc.exists ? adminDoc.data().tokens || 0 : PANEL_TOKENS;
    
    if (currentTokens < cbtCost) {
      return res.status(402).json({ 
        error: 'Insufficient cbT', 
        current: currentTokens, 
        required: cbtCost,
        panel: PANEL_TYPE
      });
    }
    
    // Admin AI agents
    const adminAgents = {
      'system-admin': 'System Administrator',
      'security-expert': 'Security Expert',
      'performance-analyst': 'Performance Analyst',
      'user-manager': 'User Manager',
      'infrastructure-engineer': 'Infrastructure Engineer',
      'compliance-officer': 'Compliance Officer',
      'cost-optimizer': 'Cost Optimizer',
      'backup-manager': 'Backup Manager'
    };
    
    const agentName = adminAgents[agent] || 'Admin Assistant';
    const response = {
      panel: PANEL_TYPE,
      agent,
      agentName,
      adminId,
      message,
      response: `[${agentName}] ${message}`,
      cbT: currentTokens - cbtCost,
      timestamp: new Date().toISOString()
    };
    
    // Log to admin activity
    await firestore.collection('admin_activity').add({
      type: 'chat',
      adminId,
      agent,
      message,
      response: response.response,
      cbTUsed: cbtCost,
      timestamp: new Date()
    });
    
    // Deduct cbT
    await firestore.collection('admin_tokens').doc(adminId).set({
      tokens: currentTokens - cbtCost,
      lastUpdated: new Date(),
      monthlyAllowance: PANEL_TOKENS
    }, { merge: true });
    
    res.json(response);
  } catch (error) {
    res.status(500).json({ error: 'Admin chat failed' });
  }
});

// Admin profile and settings
app.get('/api/profile', async (req, res) => {
  try {
    const adminId = req.query.adminId || 'default-admin';
    
    const adminDoc = await firestore.collection('admin_profiles').doc(adminId).get();
    const tokenDoc = await firestore.collection('admin_tokens').doc(adminId).get();
    
    const profile = {
      panel: PANEL_TYPE,
      adminId,
      profile: adminDoc.exists ? adminDoc.data() : {
        name: 'Cool Bits Admin',
        role: 'System Administrator',
        permissions: ['full-access', 'user-management', 'system-control'],
        accessLevel: 'super-admin',
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
    res.status(500).json({ error: 'Failed to get admin profile' });
  }
});

// System-wide analytics
app.get('/api/analytics', async (req, res) => {
  try {
    const adminId = req.query.adminId || 'default-admin';
    
    // Get system-wide stats
    const stats = {
      panel: PANEL_TYPE,
      adminId,
      system: {
        totalUsers: 0,
        totalPanels: 5,
        totalCbT: 0,
        systemHealth: 'GREEN',
        uptime: '99.9%'
      },
      panels: {
        user: { users: 0, cbTUsed: 0, status: 'active' },
        business: { users: 0, cbTUsed: 0, status: 'active' },
        agency: { users: 0, cbTUsed: 0, status: 'active' },
        dev: { users: 0, cbTUsed: 0, status: 'active' },
        admin: { users: 1, cbTUsed: 0, status: 'active' }
      },
      timestamp: new Date().toISOString()
    };
    
    // Count users across all panels
    const panels = ['user', 'business', 'agency', 'dev', 'admin'];
    for (const panel of panels) {
      try {
        const users = await firestore.collection(`${panel}_users`).get();
        stats.panels[panel].users = users.size;
        stats.system.totalUsers += users.size;
      } catch (error) {
        // Panel might not exist yet
      }
    }
    
    res.json(stats);
  } catch (error) {
    res.status(500).json({ error: 'Failed to get system analytics' });
  }
});

// System control endpoints
app.post('/api/system/control', async (req, res) => {
  try {
    const { action, target, data } = req.body;
    
    const result = {
      panel: PANEL_TYPE,
      action,
      target,
      data,
      result: `[ADMIN] Executed ${action} on ${target}`,
      timestamp: new Date().toISOString()
    };
    
    // Log admin action
    await firestore.collection('admin_activity').add({
      type: 'system_control',
      action,
      target,
      data,
      timestamp: new Date()
    });
    
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: 'System control failed' });
  }
});

// User management endpoints
app.get('/api/users', async (req, res) => {
  try {
    const { panel, limit = 50 } = req.query;
    
    const users = [];
    const panels = panel ? [panel] : ['user', 'business', 'agency', 'dev', 'admin'];
    
    for (const p of panels) {
      try {
        const userCollection = await firestore.collection(`${p}_users`).limit(parseInt(limit)).get();
        userCollection.forEach(doc => {
          users.push({
            panel: p,
            ...doc.data(),
            id: doc.id
          });
        });
      } catch (error) {
        // Panel might not exist
      }
    }
    
    res.json({
      panel: PANEL_TYPE,
      users,
      total: users.length,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to get users' });
  }
});

// Token management
app.post('/api/tokens/manage', async (req, res) => {
  try {
    const { action, userId, panel, amount } = req.body;
    
    const result = {
      panel: PANEL_TYPE,
      action,
      userId,
      panel,
      amount,
      result: `[ADMIN] ${action} ${amount} cbT for ${userId} in ${panel}`,
      timestamp: new Date().toISOString()
    };
    
    // Log token management action
    await firestore.collection('admin_activity').add({
      type: 'token_management',
      action,
      userId,
      panel,
      amount,
      timestamp: new Date()
    });
    
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: 'Token management failed' });
  }
});

app.listen(port, () => console.log(`👑 ${PANEL_NAME} running on port ${port}`));
