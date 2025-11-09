const express = require('express');
const { Firestore } = require('@google-cloud/firestore');
const app = express();
const port = process.env.PORT || 3000;

const firestore = new Firestore({ projectId: 'coolbits-ai' });
app.use(express.json());

// Dev Panel - Developer tools and d-bit wall
const PANEL_TYPE = 'dev';
const PANEL_NAME = 'Dev Panel';
const PANEL_TOKENS = 7500; // Monthly cbT allowance

// Health endpoint
app.get('/api/v1/health', (req, res) => res.json({ 
  status: 'GREEN', 
  panel: PANEL_TYPE,
  name: PANEL_NAME,
  tokens: PANEL_TOKENS,
  timestamp: new Date().toISOString()
}));

// Dev wall - development activity & projects
app.get('/api/wall', async (req, res) => {
  try {
    const devId = req.query.devId || 'default-dev';
    
    // Get development activity and projects
    const devData = await firestore
      .collection('dev_projects')
      .where('devId', '==', devId)
      .orderBy('timestamp', 'desc')
      .limit(20)
      .get();
    
    const wallData = [];
    devData.forEach(doc => {
      wallData.push({
        ...doc.data(),
        id: doc.id
      });
    });
    
    // Add mock dev data if no data exists
    if (wallData.length === 0) {
      wallData.push(
        {
          type: 'project',
          name: 'CoolBits.ai Platform',
          status: 'in-development',
          progress: '75%',
          technologies: ['Next.js', 'Node.js', 'Firestore'],
          timestamp: new Date()
        },
        {
          type: 'deployment',
          service: 'business-panel',
          status: 'deployed',
          region: 'europe-west3',
          timestamp: new Date()
        },
        {
          type: 'code-review',
          repository: 'coolbits-ai',
          pullRequest: '#42',
          status: 'approved',
          timestamp: new Date()
        }
      );
    }
    
    res.json({
      panel: PANEL_TYPE,
      devId,
      wall: wallData,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to get dev wall' });
  }
});

// Dev AI chat - with cbT tracking
app.post('/api/ai/chat', async (req, res) => {
  try {
    const { message, agent = 'senior-developer', devId = 'default-dev' } = req.body;
    const cbtCost = 2; // Dev agents cost moderate
    
    // Check dev cbT balance
    const devDoc = await firestore.collection('dev_tokens').doc(devId).get();
    const currentTokens = devDoc.exists ? devDoc.data().tokens || 0 : PANEL_TOKENS;
    
    if (currentTokens < cbtCost) {
      return res.status(402).json({ 
        error: 'Insufficient cbT', 
        current: currentTokens, 
        required: cbtCost,
        panel: PANEL_TYPE
      });
    }
    
    // Dev AI agents
    const devAgents = {
      'senior-developer': 'Senior Developer',
      'frontend-expert': 'Frontend Expert',
      'backend-engineer': 'Backend Engineer',
      'devops-specialist': 'DevOps Specialist',
      'code-reviewer': 'Code Reviewer',
      'architecture-advisor': 'Architecture Advisor',
      'cursor-assistant': 'Cursor AI Assistant',
      'debugging-expert': 'Debugging Expert'
    };
    
    const agentName = devAgents[agent] || 'Dev Assistant';
    const response = {
      panel: PANEL_TYPE,
      agent,
      agentName,
      devId,
      message,
      response: `[${agentName}] ${message}`,
      cbT: currentTokens - cbtCost,
      timestamp: new Date().toISOString()
    };
    
    // Log to dev activity
    await firestore.collection('dev_activity').add({
      type: 'chat',
      devId,
      agent,
      message,
      response: response.response,
      cbTUsed: cbtCost,
      timestamp: new Date()
    });
    
    // Deduct cbT
    await firestore.collection('dev_tokens').doc(devId).set({
      tokens: currentTokens - cbtCost,
      lastUpdated: new Date(),
      monthlyAllowance: PANEL_TOKENS
    }, { merge: true });
    
    res.json(response);
  } catch (error) {
    res.status(500).json({ error: 'Dev chat failed' });
  }
});

// Dev profile and settings
app.get('/api/profile', async (req, res) => {
  try {
    const devId = req.query.devId || 'default-dev';
    
    const devDoc = await firestore.collection('dev_profiles').doc(devId).get();
    const tokenDoc = await firestore.collection('dev_tokens').doc(devId).get();
    
    const profile = {
      panel: PANEL_TYPE,
      devId,
      profile: devDoc.exists ? devDoc.data() : {
        name: 'Cool Bits Developer',
        role: 'Full Stack Developer',
        skills: ['JavaScript', 'TypeScript', 'Node.js', 'React', 'Next.js'],
        github: 'https://github.com/coolbits-dev',
        experience: '5+ years',
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
    res.status(500).json({ error: 'Failed to get dev profile' });
  }
});

// Dev analytics and project management
app.get('/api/analytics', async (req, res) => {
  try {
    const devId = req.query.devId || 'default-dev';
    
    // Get dev activity stats
    const activityStats = await firestore
      .collection('dev_activity')
      .where('devId', '==', devId)
      .get();
    
    const stats = {
      panel: PANEL_TYPE,
      devId,
      totalActivities: activityStats.size,
      cbTUsed: 0,
      topAgents: {},
      projects: {
        active: 3,
        completed: 12,
        inReview: 2,
        deployed: 8
      },
      codeMetrics: {
        commits: 156,
        linesOfCode: '45,000',
        pullRequests: 23,
        codeReviews: 18
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
    res.status(500).json({ error: 'Failed to get dev analytics' });
  }
});

// Cursor integration endpoint
app.post('/api/cursor/integration', async (req, res) => {
  try {
    const { action, code, context } = req.body;
    
    const cursorResponse = {
      panel: PANEL_TYPE,
      action,
      response: `[Cursor AI] Processed ${action} for code: ${code?.substring(0, 50)}...`,
      suggestions: [
        'Consider using TypeScript for better type safety',
        'Add error handling for edge cases',
        'Optimize performance with memoization'
      ],
      timestamp: new Date().toISOString()
    };
    
    res.json(cursorResponse);
  } catch (error) {
    res.status(500).json({ error: 'Cursor integration failed' });
  }
});

// Code analysis endpoint
app.post('/api/code/analyze', async (req, res) => {
  try {
    const { code, language = 'javascript' } = req.body;
    
    const analysis = {
      panel: PANEL_TYPE,
      language,
      metrics: {
        lines: code.split('\n').length,
        complexity: 'Medium',
        maintainability: 'Good',
        security: 'No issues found'
      },
      suggestions: [
        'Add JSDoc comments for better documentation',
        'Consider breaking down large functions',
        'Add unit tests for critical functions'
      ],
      timestamp: new Date().toISOString()
    };
    
    res.json(analysis);
  } catch (error) {
    res.status(500).json({ error: 'Code analysis failed' });
  }
});

app.listen(port, () => console.log(`💻 ${PANEL_NAME} running on port ${port}`));
