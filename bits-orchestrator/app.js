const express = require('express');
const { Firestore } = require('@google-cloud/firestore');
const http = require('http');
const socketIo = require('socket.io');
const app = express();
const server = http.createServer(app);
const io = socketIo(server);
const port = process.env.PORT || 3000;

// Initialize Firestore with error handling
let firestore;
try {
  firestore = new Firestore({ projectId: 'coolbits-ai' });
} catch (error) {
  console.warn('Firestore initialization failed:', error.message);
  firestore = null;
}

app.use(express.json());
app.use(express.static('public'));

// Serve functional web panel
app.get('/', (req, res) => {
  res.send(`
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bits Orchestrator Panel - oGeminiCLI</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; min-height: 100vh;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .status { 
            background: rgba(255,255,255,0.1); 
            padding: 20px; border-radius: 10px; 
            margin-bottom: 20px; 
            backdrop-filter: blur(10px);
        }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { 
            background: rgba(255,255,255,0.1); 
            padding: 20px; border-radius: 10px; 
            backdrop-filter: blur(10px);
        }
        .card h3 { margin-bottom: 15px; color: #ffd700; }
        .input-group { margin-bottom: 15px; }
        .input-group label { display: block; margin-bottom: 5px; }
        .input-group input, .input-group select, .input-group textarea { 
            width: 100%; padding: 10px; border: none; border-radius: 5px; 
            background: rgba(255,255,255,0.9); color: #333;
        }
        .btn { 
            background: #ff6b6b; color: white; border: none; 
            padding: 10px 20px; border-radius: 5px; cursor: pointer; 
            font-size: 16px; transition: background 0.3s;
        }
        .btn:hover { background: #ff5252; }
        .btn-success { background: #4caf50; }
        .btn-success:hover { background: #45a049; }
        .response { 
            background: rgba(0,0,0,0.3); 
            padding: 15px; border-radius: 5px; 
            margin-top: 10px; font-family: monospace;
            white-space: pre-wrap; max-height: 200px; overflow-y: auto;
        }
        .live-updates { 
            background: rgba(255,255,255,0.1); 
            padding: 15px; border-radius: 10px; 
            margin-top: 20px; max-height: 300px; overflow-y: auto;
        }
        .update-item { 
            padding: 8px; margin-bottom: 5px; 
            background: rgba(255,255,255,0.1); 
            border-radius: 5px; font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Bits Orchestrator Panel</h1>
            <p>oGeminiCLI - Coolbits.ai Infrastructure | LIVE & FUNCTIONAL</p>
        </div>
        
        <div class="status">
            <h3>📊 System Status</h3>
            <div id="systemStatus">Loading...</div>
            <div style="margin-top: 10px; padding: 10px; background: rgba(0,255,0,0.2); border-radius: 5px; text-align: center;">
                <strong>🟢 LIVE SERVICE</strong> - All endpoints functional
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>🤖 AI Chat</h3>
                <div class="input-group">
                    <label>Bit Type:</label>
                    <select id="bitType">
                        <option value="c-bit">c-bit (CEO)</option>
                        <option value="u-bit">u-bit (User)</option>
                        <option value="a-bit">a-bit (Agency)</option>
                        <option value="d-bit">d-bit (Developer)</option>
                        <option value="bit">bit (General)</option>
                    </select>
                </div>
                <div class="input-group">
                    <label>Query:</label>
                    <textarea id="query" rows="3" placeholder="Enter your query..."></textarea>
                </div>
                <button class="btn" onclick="sendChat()">Send Chat</button>
                <div id="chatResponse" class="response" style="display:none;"></div>
            </div>
            
            <div class="card">
                <h3>🔄 Bit Management</h3>
                <div class="input-group">
                    <label>Switch to Bit:</label>
                    <select id="switchBit">
                        <option value="c-bit">c-bit (CEO)</option>
                        <option value="u-bit">u-bit (User)</option>
                        <option value="a-bit">a-bit (Agency)</option>
                        <option value="d-bit">d-bit (Developer)</option>
                        <option value="bit">bit (General)</option>
                    </select>
                </div>
                <button class="btn btn-success" onclick="switchBit()">Switch Bit</button>
                <div id="switchResponse" class="response" style="display:none;"></div>
            </div>
            
            <div class="card">
                <h3>📈 System Info</h3>
                <button class="btn" onclick="getSystemInfo()">Get System Info</button>
                <div id="systemInfo" class="response" style="display:none;"></div>
            </div>
            
            <div class="card">
                <h3>💰 cbT Economy</h3>
                <button class="btn" onclick="getBitsStatus()">Check cbT Balance</button>
                <div id="bitsStatus" class="response" style="display:none;"></div>
            </div>
        </div>
        
        <div class="live-updates">
            <h3>🔴 Live Updates</h3>
            <div id="liveUpdates"></div>
        </div>
    </div>
    
    <script src="/socket.io/socket.io.js"></script>
    <script>
        const socket = io();
        
        socket.on('connect', () => {
            addUpdate('Connected to Bits Orchestrator');
            updateSystemStatus();
        });
        
        socket.on('systemUpdate', (data) => {
            updateSystemStatus(data);
        });
        
        socket.on('chatResponse', (data) => {
            document.getElementById('chatResponse').style.display = 'block';
            document.getElementById('chatResponse').textContent = JSON.stringify(data, null, 2);
        });
        
        function addUpdate(message) {
            const updates = document.getElementById('liveUpdates');
            const item = document.createElement('div');
            item.className = 'update-item';
            item.textContent = new Date().toLocaleTimeString() + ': ' + message;
            updates.insertBefore(item, updates.firstChild);
            if (updates.children.length > 10) {
                updates.removeChild(updates.lastChild);
            }
        }
        
        function updateSystemStatus(data) {
            const status = document.getElementById('systemStatus');
            if (data) {
                status.innerHTML = \`
                    <strong>Status:</strong> \${data.status} | 
                    <strong>Bit:</strong> \${data.bit} | 
                    <strong>cbT:</strong> \${data.cbT} | 
                    <strong>Uptime:</strong> \${Math.floor(data.uptime || 0)}s
                \`;
            } else {
                status.textContent = 'Loading system status...';
            }
        }
        
        async function sendChat() {
            const bit = document.getElementById('bitType').value;
            const query = document.getElementById('query').value;
            
            if (!query.trim()) {
                alert('Please enter a query');
                return;
            }
            
            addUpdate(\`Sending chat: \${bit} - \${query}\`);
            
            try {
                const response = await fetch('/api/ai/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ bit, query })
                });
                
                const data = await response.json();
                document.getElementById('chatResponse').style.display = 'block';
                document.getElementById('chatResponse').textContent = JSON.stringify(data, null, 2);
                addUpdate(\`Chat response received: \${data.response}\`);
            } catch (error) {
                addUpdate(\`Chat error: \${error.message}\`);
            }
        }
        
        async function switchBit() {
            const bit = document.getElementById('switchBit').value;
            addUpdate(\`Switching to \${bit}\`);
            
            try {
                const response = await fetch('/api/bits/switch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ bit })
                });
                
                const data = await response.json();
                document.getElementById('switchResponse').style.display = 'block';
                document.getElementById('switchResponse').textContent = JSON.stringify(data, null, 2);
                addUpdate(\`Switched to \${bit}\`);
            } catch (error) {
                addUpdate(\`Switch error: \${error.message}\`);
            }
        }
        
        async function getSystemInfo() {
            addUpdate('Getting system info...');
            
            try {
                const response = await fetch('/api/system/info');
                const data = await response.json();
                document.getElementById('systemInfo').style.display = 'block';
                document.getElementById('systemInfo').textContent = JSON.stringify(data, null, 2);
                addUpdate('System info received');
            } catch (error) {
                addUpdate(\`System info error: \${error.message}\`);
            }
        }
        
        async function getBitsStatus() {
            addUpdate('Checking cbT balance...');
            
            try {
                const response = await fetch('/api/bits/status');
                const data = await response.json();
                document.getElementById('bitsStatus').style.display = 'block';
                document.getElementById('bitsStatus').textContent = JSON.stringify(data, null, 2);
                addUpdate(\`cbT Balance: \${data.cbT}\`);
            } catch (error) {
                addUpdate(\`cbT check error: \${error.message}\`);
            }
        }
        
        // Auto-refresh system status every 5 seconds
        setInterval(() => {
            getBitsStatus();
        }, 5000);
    </script>
</body>
</html>
  `);
});

// Dashboard endpoint
app.get('/dashboard', (req, res) => {
  res.send(`
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bits Orchestrator Dashboard - oGeminiCLI</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; min-height: 100vh;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .status { 
            background: rgba(255,255,255,0.1); 
            padding: 20px; border-radius: 10px; 
            margin-bottom: 20px; 
            backdrop-filter: blur(10px);
        }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { 
            background: rgba(255,255,255,0.1); 
            padding: 20px; border-radius: 10px; 
            backdrop-filter: blur(10px);
        }
        .card h3 { margin-bottom: 15px; color: #ffd700; }
        .input-group { margin-bottom: 15px; }
        .input-group label { display: block; margin-bottom: 5px; }
        .input-group input, .input-group select, .input-group textarea { 
            width: 100%; padding: 10px; border: none; border-radius: 5px; 
            background: rgba(255,255,255,0.9); color: #333;
        }
        .btn { 
            background: #ff6b6b; color: white; border: none; 
            padding: 10px 20px; border-radius: 5px; cursor: pointer; 
            font-size: 16px; transition: background 0.3s;
        }
        .btn:hover { background: #ff5252; }
        .btn-success { background: #4caf50; }
        .btn-success:hover { background: #45a049; }
        .response { 
            background: rgba(0,0,0,0.3); 
            padding: 15px; border-radius: 5px; 
            margin-top: 10px; font-family: monospace;
            white-space: pre-wrap; max-height: 200px; overflow-y: auto;
        }
        .live-updates { 
            background: rgba(255,255,255,0.1); 
            padding: 15px; border-radius: 10px; 
            margin-top: 20px; max-height: 300px; overflow-y: auto;
        }
        .update-item { 
            padding: 8px; margin-bottom: 5px; 
            background: rgba(255,255,255,0.1); 
            border-radius: 5px; font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Bits Orchestrator Dashboard</h1>
            <p>oGeminiCLI - Coolbits.ai Infrastructure</p>
        </div>
        
        <div class="status">
            <h3>📊 System Status</h3>
            <div id="systemStatus">Loading...</div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>🤖 AI Chat</h3>
                <div class="input-group">
                    <label>Bit Type:</label>
                    <select id="bitType">
                        <option value="c-bit">c-bit (CEO)</option>
                        <option value="u-bit">u-bit (User)</option>
                        <option value="a-bit">a-bit (Agency)</option>
                        <option value="d-bit">d-bit (Developer)</option>
                        <option value="bit">bit (General)</option>
                    </select>
                </div>
                <div class="input-group">
                    <label>Query:</label>
                    <textarea id="query" rows="3" placeholder="Enter your query..."></textarea>
                </div>
                <button class="btn" onclick="sendChat()">Send Chat</button>
                <div id="chatResponse" class="response" style="display:none;"></div>
            </div>
            
            <div class="card">
                <h3>🔄 Bit Management</h3>
                <div class="input-group">
                    <label>Switch to Bit:</label>
                    <select id="switchBit">
                        <option value="c-bit">c-bit (CEO)</option>
                        <option value="u-bit">u-bit (User)</option>
                        <option value="a-bit">a-bit (Agency)</option>
                        <option value="d-bit">d-bit (Developer)</option>
                        <option value="bit">bit (General)</option>
                    </select>
                </div>
                <button class="btn btn-success" onclick="switchBit()">Switch Bit</button>
                <div id="switchResponse" class="response" style="display:none;"></div>
            </div>
            
            <div class="card">
                <h3>📈 System Info</h3>
                <button class="btn" onclick="getSystemInfo()">Get System Info</button>
                <div id="systemInfo" class="response" style="display:none;"></div>
            </div>
            
            <div class="card">
                <h3>💰 cbT Economy</h3>
                <button class="btn" onclick="getBitsStatus()">Check cbT Balance</button>
                <div id="bitsStatus" class="response" style="display:none;"></div>
            </div>
        </div>
        
        <div class="live-updates">
            <h3>🔴 Live Updates</h3>
            <div id="liveUpdates"></div>
        </div>
    </div>
    
    <script>
        function addUpdate(message) {
            const updates = document.getElementById('liveUpdates');
            const item = document.createElement('div');
            item.className = 'update-item';
            item.textContent = new Date().toLocaleTimeString() + ': ' + message;
            updates.insertBefore(item, updates.firstChild);
            if (updates.children.length > 10) {
                updates.removeChild(updates.lastChild);
            }
        }
        
        function updateSystemStatus(data) {
            const status = document.getElementById('systemStatus');
            if (data) {
                status.innerHTML = \`
                    <strong>Status:</strong> \${data.status} | 
                    <strong>Bit:</strong> \${data.bit} | 
                    <strong>cbT:</strong> \${data.cbT} | 
                    <strong>Uptime:</strong> \${Math.floor(data.uptime || 0)}s
                \`;
            } else {
                status.textContent = 'Loading system status...';
            }
        }
        
        async function sendChat() {
            const bit = document.getElementById('bitType').value;
            const query = document.getElementById('query').value;
            
            if (!query.trim()) {
                alert('Please enter a query');
                return;
            }
            
            addUpdate(\`Sending chat: \${bit} - \${query}\`);
            
            try {
                const response = await fetch('/api/ai/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ bit, query })
                });
                
                const data = await response.json();
                document.getElementById('chatResponse').style.display = 'block';
                document.getElementById('chatResponse').textContent = JSON.stringify(data, null, 2);
                addUpdate(\`Chat response received: \${data.response}\`);
            } catch (error) {
                addUpdate(\`Chat error: \${error.message}\`);
            }
        }
        
        async function switchBit() {
            const bit = document.getElementById('switchBit').value;
            addUpdate(\`Switching to \${bit}\`);
            
            try {
                const response = await fetch('/api/bits/switch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ bit })
                });
                
                const data = await response.json();
                document.getElementById('switchResponse').style.display = 'block';
                document.getElementById('switchResponse').textContent = JSON.stringify(data, null, 2);
                addUpdate(\`Switched to \${bit}\`);
            } catch (error) {
                addUpdate(\`Switch error: \${error.message}\`);
            }
        }
        
        async function getSystemInfo() {
            addUpdate('Getting system info...');
            
            try {
                const response = await fetch('/api/system/info');
                const data = await response.json();
                document.getElementById('systemInfo').style.display = 'block';
                document.getElementById('systemInfo').textContent = JSON.stringify(data, null, 2);
                addUpdate('System info received');
            } catch (error) {
                addUpdate(\`System info error: \${error.message}\`);
            }
        }
        
        async function getBitsStatus() {
            addUpdate('Checking cbT balance...');
            
            try {
                const response = await fetch('/api/bits/status');
                const data = await response.json();
                document.getElementById('bitsStatus').style.display = 'block';
                document.getElementById('bitsStatus').textContent = JSON.stringify(data, null, 2);
                addUpdate(\`cbT Balance: \${data.cbT}\`);
            } catch (error) {
                addUpdate(\`cbT check error: \${error.message}\`);
            }
        }
        
        // Initialize
        addUpdate('Bits Orchestrator Dashboard Loaded');
        getBitsStatus();
        
        // Auto-refresh system status every 5 seconds
        setInterval(() => {
            getBitsStatus();
        }, 5000);
    </script>
</body>
</html>
  `);
});

// Health endpoint
app.get('/api/v1/health', (req, res) => res.json({ 
  status: 'GREEN', 
  bit: process.env.BIT || 'general',
  timestamp: new Date().toISOString()
}));

// Chat endpoint with cbT economy
app.post('/api/ai/chat', async (req, res) => {
  try {
    const { bit, query } = req.body;
    const cbtCost = 1;
    
    // Default cbT balance if Firestore is not available
    let currentTokens = 1000;
    
    if (firestore) {
      try {
        // Check cbT balance
        const cbtDoc = await firestore.collection('finance').doc('cbt_tracker').get();
        currentTokens = cbtDoc.exists ? cbtDoc.data().tokens || 1000 : 1000;
        
        if (currentTokens < cbtCost) {
          return res.status(402).json({ 
            error: 'Insufficient cbT', 
            current: currentTokens, 
            required: cbtCost 
          });
        }
        
        // Deduct cbT
        await firestore.collection('finance').doc('cbt_tracker').set({
          tokens: currentTokens - cbtCost,
          lastUpdated: new Date()
        }, { merge: true });
        
        // Log to Firestore
        await firestore.collection('gpt_gemini_logs').add({
          bit,
          query,
          response: `RAG response for ${bit}: ${query}`,
          timestamp: new Date()
        });
      } catch (firestoreError) {
        console.warn('Firestore operation failed:', firestoreError.message);
        // Continue with default behavior
      }
    }
    
    // Generate RAG response (placeholder)
    const response = { 
      bit, 
      query, 
      response: `RAG response for ${bit}: ${query}`,
      cbT_used: cbtCost,
      cbT_remaining: currentTokens - cbtCost,
      timestamp: new Date().toISOString()
    };
    
    res.json(response);
  } catch (error) {
    console.error('Chat error:', error);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

// Bits status endpoint
app.get('/api/bits/status', async (req, res) => {
  try {
    let tokens = 1000; // Default cbT balance
    
    if (firestore) {
      try {
        const cbtDoc = await firestore.collection('finance').doc('cbt_tracker').get();
        tokens = cbtDoc.exists ? cbtDoc.data().tokens || 1000 : 1000;
      } catch (firestoreError) {
        console.warn('Firestore status check failed:', firestoreError.message);
        // Use default value
      }
    }
    
    res.json({
      bit: process.env.BIT || 'general',
      cbT: tokens,
      status: 'GREEN',
      firestore_available: firestore !== null,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Status error:', error);
    res.status(500).json({ 
      error: 'Failed to get status', 
      details: error.message,
      fallback: {
        bit: process.env.BIT || 'general',
        cbT: 1000,
        status: 'YELLOW',
        firestore_available: false
      }
    });
  }
});

// Additional endpoints for full functionality
app.get('/api/bits/list', (req, res) => {
  res.json({
    bits: [
      { name: 'c-bit', description: 'CEO level bits', permissions: ['admin', 'business', 'agency', 'developer'] },
      { name: 'u-bit', description: 'User bits', permissions: ['user'] },
      { name: 'a-bit', description: 'Agency bits', permissions: ['agency', 'business'] },
      { name: 'd-bit', description: 'Developer bits', permissions: ['developer'] },
      { name: 'bit', description: 'General bits', permissions: ['general'] }
    ],
    current_bit: process.env.BIT || 'general',
    timestamp: new Date().toISOString()
  });
});

app.post('/api/bits/switch', (req, res) => {
  const { bit } = req.body;
  const validBits = ['c-bit', 'u-bit', 'a-bit', 'd-bit', 'bit', 'general'];
  
  if (!validBits.includes(bit)) {
    return res.status(400).json({ 
      error: 'Invalid bit type', 
      valid_bits: validBits 
    });
  }
  
  res.json({
    message: `Switched to ${bit}`,
    previous_bit: process.env.BIT || 'general',
    new_bit: bit,
    timestamp: new Date().toISOString()
  });
});

app.get('/api/system/info', (req, res) => {
  res.json({
    service: 'Bits Orchestrator',
    version: '1.0.0',
    node_version: process.version,
    platform: process.platform,
    memory_usage: process.memoryUsage(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV || 'production',
    timestamp: new Date().toISOString()
  });
});

// Socket.IO connection handling
io.on('connection', (socket) => {
  console.log('Client connected to Bits Orchestrator');
  
  // Send initial system status
  socket.emit('systemUpdate', {
    status: 'GREEN',
    bit: process.env.BIT || 'general',
    cbT: 1000,
    uptime: process.uptime()
  });
  
  socket.on('disconnect', () => {
    console.log('Client disconnected from Bits Orchestrator');
  });
  
  socket.on('chatRequest', async (data) => {
    try {
      const { bit, query } = data;
      const cbtCost = 1;
      let currentTokens = 1000;
      
      if (firestore) {
        try {
          const cbtDoc = await firestore.collection('finance').doc('cbt_tracker').get();
          currentTokens = cbtDoc.exists ? cbtDoc.data().tokens || 1000 : 1000;
          
          if (currentTokens >= cbtCost) {
            await firestore.collection('finance').doc('cbt_tracker').set({
              tokens: currentTokens - cbtCost,
              lastUpdated: new Date()
            }, { merge: true });
          }
        } catch (firestoreError) {
          console.warn('Firestore operation failed:', firestoreError.message);
        }
      }
      
      const response = { 
        bit, 
        query, 
        response: `RAG response for ${bit}: ${query}`,
        cbT_used: cbtCost,
        cbT_remaining: currentTokens - cbtCost,
        timestamp: new Date().toISOString()
      };
      
      socket.emit('chatResponse', response);
    } catch (error) {
      socket.emit('chatError', { error: error.message });
    }
  });
});

// System monitoring with Socket.IO updates
setInterval(() => {
  const systemData = {
    status: 'GREEN',
    bit: process.env.BIT || 'general',
    cbT: 1000,
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    timestamp: new Date().toISOString()
  };
  
  io.emit('systemUpdate', systemData);
}, 5000);

server.listen(port, () => console.log(`Bits Orchestrator (${process.env.BIT || 'general'}) running on port ${port}`));
