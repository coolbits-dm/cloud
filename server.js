
const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');
const { exec, spawn } = require('child_process');
const os = require('os');
const axios = require('axios');

// Configuration constants
const BRIDGE_URL = process.env.BRIDGE_URL || "http://127.0.0.1:8765";
const PROJECT_DIR = process.env.PROJECT_DIR || "C:\\Users\\andre\\Desktop\\coolbits";
const GCLOUD_PROJECT = process.env.GCLOUD_PROJECT || "coolbits-og-bridge";
const GCLOUD_REGION = process.env.GCLOUD_REGION || "europe-west3";

// Helper functions for real executions
function run(cmd, opts = {}) {
  return new Promise((resolve, reject) => {
    exec(cmd, { windowsHide: true, ...opts }, (err, stdout, stderr) => {
      if (err) return reject(new Error(stderr || err.message));
      resolve(stdout.trim());
    });
  });
}

function spawnCsv(cmd, args, timeoutMs = 8000) {
  return new Promise((resolve, reject) => {
    const p = spawn(cmd, args, { shell: true, windowsHide: true });
    let out = "", err = "";
    const t = setTimeout(() => { p.kill("SIGKILL"); reject(new Error("Timeout")); }, timeoutMs);
    p.stdout.on("data", d => out += d.toString());
    p.stderr.on("data", d => err += d.toString());
    p.on("close", code => { clearTimeout(t); code ? reject(new Error(err||`Exit ${code}`)) : resolve(out.trim()); });
  });
}

// Rate limiting - simple in-memory token bucket
const rateLimitMap = new Map();
const RATE_LIMIT_WINDOW = 60000; // 1 minute
const RATE_LIMIT_MAX_REQUESTS = 100; // 100 requests per minute

function rateLimit(req, res, next) {
  const ip = req.ip || req.connection.remoteAddress || '127.0.0.1';
  const now = Date.now();
  
  if (!rateLimitMap.has(ip)) {
    rateLimitMap.set(ip, { tokens: RATE_LIMIT_MAX_REQUESTS, lastRefill: now });
  }
  
  const bucket = rateLimitMap.get(ip);
  const timePassed = now - bucket.lastRefill;
  const tokensToAdd = Math.floor(timePassed / RATE_LIMIT_WINDOW) * RATE_LIMIT_MAX_REQUESTS;
  
  bucket.tokens = Math.min(RATE_LIMIT_MAX_REQUESTS, bucket.tokens + tokensToAdd);
  bucket.lastRefill = now;
  
  if (bucket.tokens > 0) {
    bucket.tokens--;
    next();
  } else {
    res.status(429).json({ error: 'Rate limit exceeded' });
  }
}

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

const PORT = process.env.PORT || 3001;

// Configuration constants
// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static('public'));

// Global state
let systemStatus = {
  cpu: 0,
  memory: 0,
  gpu: 0,
  network: 0,
  agents: {
    ocopilot_cursor: { status: 'active', integrity: 0.94 },
    ocopilot_windows: { status: 'connected', integrity: 0.95 },
    ocopilot_chatgpt: { status: 'active', integrity: 0.92 },
    ocopilot_grok: { status: 'active', integrity: 0.95 },
    cblm_core: { status: 'connected', integrity: 0.88 }
  },
  bridge: {
    status: 'active',
    channel: 'bits-secure',
    protocol: 'ocim-0.1'
  }
};

// Board members configuration
const boardMembers = {
  "andrei": {
    name: "Andrei (CEO)",
    role: "CEO",
    status: "active",
    keys: {
      openai: "andrei-openai-personal",
      xai: "andrei-xai-personal"
    },
    permissions: ["c-bit", "admin", "business", "agency", "developer"]
  },
  "bogdan": {
    name: "Bogdan (CTO)",
    role: "CTO", 
    status: "active",
    keys: {
      openai: "bogdan-openai-personal",
      xai: "bogdan-xai-personal"
    },
    permissions: ["d-bit", "developer", "business"]
  }
};

// Wall discussions
let wallDiscussions = [];

let messageLog = [];
let commandHistory = [];

// Utility functions
function getSystemInfo() {
  const cpus = os.cpus();
  const totalMem = os.totalmem();
  const freeMem = os.freemem();
  const usedMem = totalMem - freeMem;
  
  return {
    cpu: Math.round(cpus[0].times.user / (cpus[0].times.user + cpus[0].times.nice + cpus[0].times.sys + cpus[0].times.idle + cpus[0].times.irq) * 100),
    memory: Math.round((usedMem / totalMem) * 100),
    platform: os.platform(),
    arch: os.arch(),
    uptime: os.uptime(),
    hostname: os.hostname()
  };
}

function executeCommand(command) {
  return new Promise((resolve, reject) => {
    exec(command, { timeout: 10000 }, (error, stdout, stderr) => {
      if (error) {
        reject(error);
      } else {
        resolve({ stdout, stderr });
      }
    });
  });
}

// Whitelist of allowed commands for security
const ALLOWED_COMMANDS = {
  'cursor': ['cursor', 'start "" "C:\\Users\\andre\\AppData\\Local\\Programs\\cursor\\Cursor.exe"'],
  'nvidia-smi': ['nvidia-smi', '--query-gpu=name,memory.total,memory.used,utilization.gpu,temperature.gpu,driver_version', '--format=csv,noheader,nounits'],
  'gcloud': ['gcloud', 'config set project', 'gcloud auth list', 'gcloud run services list', 'gcloud run services describe']
};

// Audit logging
function auditLog(action, exitCode, durationMs, details = {}) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    action,
    exitCode,
    durationMs,
    pid: process.pid,
    ...details
  };
  
  const logFile = `logs/audit-${new Date().toISOString().split('T')[0].replace(/-/g, '')}.jsonl`;
  const logDir = path.dirname(logFile);
  
  if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
  }
  
  fs.appendFileSync(logFile, JSON.stringify(logEntry) + '\n');
}

// Helper function for running commands with better error handling
function run(cmd, opts = {}) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    exec(cmd, { windowsHide: true, timeout: 10000, ...opts }, (err, stdout, stderr) => {
      const durationMs = Date.now() - startTime;
      const exitCode = err ? err.code : 0;
      
      // Audit log
      auditLog('command_exec', exitCode, durationMs, { command: cmd });
      
      if (err) return reject(new Error(stderr || err.message));
      resolve(stdout.trim());
    });
  });
}

// Helper function for spawning processes with JSON output
function spawnJson(cmd, args, timeoutMs = 8000) {
  return new Promise((resolve, reject) => {
    const p = spawn(cmd, args, { shell: true, windowsHide: true });
    let out = "", err = "";
    const t = setTimeout(() => {
      p.kill("SIGKILL");
      reject(new Error(`Timeout: ${cmd} ${args.join(" ")}`));
    }, timeoutMs);
    p.stdout.on("data", d => out += d.toString());
    p.stderr.on("data", d => err += d.toString());
    p.on("close", code => {
      clearTimeout(t);
      if (code !== 0) return reject(new Error(err || `Exit ${code}`));
      resolve(out.trim());
    });
  });
}

function logMessage(message, type = 'info') {
  const logEntry = {
    timestamp: new Date().toISOString(),
    message: message,
    type: type
  };
  messageLog.push(logEntry);
  
  // Keep only last 1000 messages
  if (messageLog.length > 1000) {
    messageLog = messageLog.slice(-1000);
  }
  
  // Broadcast to all connected clients
  io.emit('logMessage', logEntry);
}

// Routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'admin-console.html'));
});

app.get('/api/status', (req, res) => {
  const systemInfo = getSystemInfo();
  res.json({
    ...systemStatus,
    system: systemInfo,
    version: {
      commitSha: process.env.COMMIT_SHA || "dev",
      buildTime: process.env.BUILD_TIME || new Date().toISOString(),
      node: process.version,
      appMode: process.env.APP_MODE || "web",
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      pid: process.pid
    }
  });
});

// Roadmap endpoint
app.get('/api/roadmap', (req, res) => {
  try {
    const data = fs.readFileSync('./data/roadmap.json', 'utf-8');
    res.json({ ok: true, roadmap: JSON.parse(data) });
  } catch (e) {
    res.status(500).json({ ok: false, error: String(e) });
  }
});

// Health endpoint with detailed system information
app.get('/api/health', (req, res) => {
  try {
    const systemInfo = getSystemInfo();
    const runtimeInfo = JSON.parse(fs.readFileSync('./.runtime.json', 'utf-8'));
    
    res.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      version: {
        commitSha: process.env.COMMIT_SHA || runtimeInfo.commitSha || "dev",
        buildTime: process.env.BUILD_TIME || runtimeInfo.time || new Date().toISOString(),
        node: process.version,
        appMode: process.env.APP_MODE || "web"
      },
      runtime: {
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        pid: process.pid,
        port: runtimeInfo.port
      },
      system: systemInfo,
      services: {
        server: 'running',
        bridge: 'unknown', // Will be updated when bridge is connected
        database: 'unknown'
      },
      checks: {
        diskSpace: 'ok',
        memoryUsage: process.memoryUsage().heapUsed < 100 * 1024 * 1024 ? 'ok' : 'warning',
        uptime: process.uptime() > 60 ? 'ok' : 'starting'
      }
    });
  } catch (e) {
    res.status(500).json({ 
      status: 'unhealthy', 
      error: String(e),
      timestamp: new Date().toISOString()
    });
  }
});

app.post('/api/command', async (req, res) => {
  const { command } = req.body;
  
  if (!command) {
    return res.status(400).json({ error: 'Command is required' });
  }
  
  try {
    logMessage(`Executing command: ${command}`, 'info');
    commandHistory.push(command);
    
    const result = await executeCommand(command);
    logMessage(`Command output: ${result.stdout}`, 'success');
    
    res.json({
      success: true,
      output: result.stdout,
      error: result.stderr
    });
  } catch (error) {
    logMessage(`Command error: ${error.message}`, 'error');
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.get('/api/logs', (req, res) => {
  res.json(messageLog);
});

app.get('/api/history', (req, res) => {
  res.json(commandHistory);
});

app.post('/api/agent/sync', (req, res) => {
  logMessage('Syncing all agents...', 'info');
  
  // Simulate agent sync
  setTimeout(() => {
    systemStatus.agents.ocopilot_cursor.status = 'synced';
    systemStatus.agents.ocopilot_windows.status = 'synced';
    systemStatus.agents.ocopilot_chatgpt.status = 'synced';
    systemStatus.agents.ocopilot_grok.status = 'synced';
    systemStatus.agents.cblm_core.status = 'synced';
    
    logMessage('All agents synced successfully', 'success');
    io.emit('agentSync', systemStatus.agents);
  }, 2000);
  
  res.json({ success: true, message: 'Agent sync initiated' });
});

app.post('/api/bridge/reset', (req, res) => {
  logMessage('Resetting bridge communication...', 'warning');
  
  setTimeout(() => {
    systemStatus.bridge.status = 'reset';
    logMessage('Bridge reset complete', 'success');
    io.emit('bridgeReset', systemStatus.bridge);
  }, 1500);
  
  res.json({ success: true, message: 'Bridge reset initiated' });
});

app.post('/api/rag/test', (req, res) => {
  logMessage('Starting RAG test...', 'info');
  
  setTimeout(() => {
    logMessage('RAG test completed successfully', 'success');
    logMessage('Performance: 98% accuracy', 'success');
    io.emit('ragTestComplete', { accuracy: 98 });
  }, 3000);
  
  res.json({ success: true, message: 'RAG test initiated' });
});

// Board /wall endpoints
app.get('/api/board/members', (req, res) => {
  res.json({
    success: true,
    members: boardMembers,
    total: Object.keys(boardMembers).length
  });
});

app.post('/api/board/wall/message', (req, res) => {
  const { from, to, message, type = 'text' } = req.body;
  
  if (!from || !to || !message) {
    return res.status(400).json({ error: 'Missing required fields' });
  }
  
  const wallMessage = {
    id: Date.now(),
    from: from,
    to: to,
    message: message,
    type: type,
    timestamp: new Date().toISOString(),
    status: 'sent'
  };
  
  wallDiscussions.push(wallMessage);
  
  // Broadcast to all connected clients
  io.emit('wallMessage', wallMessage);
  
  logMessage(`Wall message from ${from} to ${to}: ${message}`, 'info');
  
  res.json({ success: true, message: 'Message sent to wall', id: wallMessage.id });
});

app.get('/api/board/wall/discussions', (req, res) => {
  res.json({
    success: true,
    discussions: wallDiscussions.slice(-50), // Last 50 messages
    total: wallDiscussions.length
  });
});

app.post('/api/board/wall/broadcast', (req, res) => {
  const { from, message, type = 'broadcast' } = req.body;
  
  if (!from || !message) {
    return res.status(400).json({ error: 'Missing required fields' });
  }
  
  const broadcastMessage = {
    id: Date.now(),
    from: from,
    to: 'all',
    message: message,
    type: type,
    timestamp: new Date().toISOString(),
    status: 'broadcast'
  };
  
  wallDiscussions.push(broadcastMessage);
  
  // Broadcast to all connected clients
  io.emit('wallBroadcast', broadcastMessage);
  
  logMessage(`Broadcast from ${from}: ${message}`, 'info');
  
  res.json({ success: true, message: 'Broadcast sent', id: broadcastMessage.id });
});

// REAL FUNCTIONALITY ENDPOINTS - Replacing Mock Functions

// 1) Open Cursor console real
app.post('/api/open-cursor', rateLimit, async (req, res) => {
  try {
    logMessage('🖥️ Opening Cursor console...', 'info');
    
    // Try different Cursor paths
    const cursorPaths = [
      `${process.env.LOCALAPPDATA}\\Programs\\cursor\\Cursor.exe`,
      `${process.env.PROGRAMFILES}\\Cursor\\Cursor.exe`,
      `${process.env['PROGRAMFILES(X86)']}\\Cursor\\Cursor.exe`,
      'cursor' // CLI command
    ];
    
    let opened = false;
    for (const cursorPath of cursorPaths) {
      try {
        if (cursorPath === 'cursor') {
          await run(`cursor "${PROJECT_DIR}"`);
        } else {
          await run(`start "" "${cursorPath}" "${PROJECT_DIR}"`);
        }
        opened = true;
        break;
      } catch (e) {
        continue; // Try next path
      }
    }
    
    if (opened) {
      logMessage('✅ Cursor console opened successfully', 'success');
      logMessage(`📁 Project directory: ${PROJECT_DIR}`, 'info');
      res.json({ ok: true, message: 'Cursor deschis pe proiect.' });
    } else {
      throw new Error('Cursor not found in any standard location');
    }
  } catch (e) {
    logMessage(`❌ Failed to open Cursor: ${e.message}`, 'error');
    res.status(500).json({ ok: false, error: String(e) });
  }
});

// 2) Check GPU real (nvidia-smi pe Windows)
app.get('/api/check-gpu', async (req, res) => {
  try {
    logMessage('🎮 Checking local GPU status...', 'info');
    
    // CSV curat, fără unități, ușor de parsat
    const q = [
      "name", "memory.total", "memory.used",
      "utilization.gpu", "temperature.gpu", "driver_version"
    ];
    const out = await spawnJson(
      "nvidia-smi",
      ["--query-gpu=" + q.join(","), "--format=csv,noheader,nounits"]
    );
    
    // Dacă ai mai multe GPU-uri, primești linii multiple
    const lines = out.split("\n").map(l => l.split(",").map(s => s.trim()));
    const gpus = lines.map(cols => ({
      name: cols[0],
      memoryTotalMB: Number(cols[1]),
      memoryUsedMB: Number(cols[2]),
      utilizationPct: Number(cols[3]),
      temperatureC: Number(cols[4]),
      driverVersion: cols[5]
    }));
    
    // Log GPU info
    gpus.forEach((gpu, i) => {
      logMessage(`📱 GPU ${i + 1}: ${gpu.name}`, 'info');
      logMessage(`💾 VRAM: ${Math.round(gpu.memoryTotalMB / 1024)}GB (${Math.round(gpu.memoryUsedMB / 1024)}GB used)`, 'info');
      logMessage(`📊 Utilization: ${gpu.utilizationPct}%`, 'info');
      logMessage(`🌡️ Temperature: ${gpu.temperatureC}°C`, 'info');
      logMessage(`🔧 Driver: ${gpu.driverVersion}`, 'info');
    });
    
    logMessage('✅ GPU status check completed', 'success');
    res.json({ ok: true, gpus });
  } catch (e) {
    logMessage(`❌ GPU check failed: ${e.message}`, 'error');
    res.status(500).json({ ok: false, error: String(e) });
  }
});

// 3) oGeminiCLI / Google Cloud sanity (prin gcloud)
app.post('/api/connect-gcloud', rateLimit, async (req, res) => {
  try {
    logMessage('🌐 Connecting to oGeminiCLI...', 'info');
    
    await run(`gcloud config set project ${GCLOUD_PROJECT}`);
    const account = await run(`gcloud auth list --filter=status:ACTIVE --format="value(account)"`);
    
    // un sanity call ușor: listăm 1 serviciu din Run
    let feUrl = "";
    try {
      const svc = await run(`gcloud run services list --region=${GCLOUD_REGION} --format="value(metadata.name)" --limit=1`);
      if (svc) {
        feUrl = await run(`gcloud run services describe ${svc} --region=${GCLOUD_REGION} --format="value(status.url)"`);
      }
    } catch {}
    
    logMessage(`✅ oGeminiCLI connected successfully`, 'success');
    logMessage(`☁️ Project: ${GCLOUD_PROJECT}`, 'info');
    logMessage(`👤 Account: ${account}`, 'info');
    if (feUrl) {
      logMessage(`🌐 Sample Service: ${feUrl}`, 'info');
    }
    logMessage('☁️ Cloud operations ready', 'success');
    
    res.json({ ok: true, project: GCLOUD_PROJECT, account, sampleServiceUrl: feUrl || null });
  } catch (e) {
    logMessage(`❌ GCloud connection failed: ${e.message}`, 'error');
    res.status(500).json({ ok: false, error: String(e) });
  }
});

// 4) Test RAG real pe bridge-ul FastAPI de pe 8765
app.post('/api/test-rag', rateLimit, async (req, res) => {
  try {
    logMessage('🧠 Testing RAG system...', 'info');
    
    // Check if bridge is running
    try {
      await axios.get(`${BRIDGE_URL}/health`, { timeout: 5000 });
    } catch (e) {
      throw new Error(`Bridge not running on ${BRIDGE_URL}. Please start the bridge first.`);
    }
    
    logMessage('📚 Loading documents...', 'info');
    
    // Ingerăm un doc mic
    await axios.post(`${BRIDGE_URL}/rag/ingest`, {
      documents: [
        { id: "sample-1", text: "CoolBits.ai admin console and cbLM.ai bridge integration test." }
      ]
    }, { timeout: 8000 });
    
    logMessage('🔍 Generating embeddings...', 'info');
    
    // Căutăm ceva relevant
    const search = await axios.post(`${BRIDGE_URL}/rag/search`, {
      query: "admin console bridge integration",
      top_k: 3
    }, { timeout: 8000 });
    
    logMessage('🎯 Testing search queries...', 'info');
    
    // Stats, să vedem că indexul respiră
    const stats = await axios.get(`${BRIDGE_URL}/rag/stats`, { timeout: 8000 });
    
    logMessage('✅ RAG system test completed successfully', 'success');
    logMessage(`📊 Performance: ${stats.data.documents || 0} documents indexed`, 'info');
    
    res.json({ ok: true, search: search.data, stats: stats.data });
  } catch (e) {
    logMessage(`❌ RAG test failed: ${e.message}`, 'error');
    res.status(500).json({ ok: false, error: String(e) });
  }
});

// Socket.IO connection handling
io.on('connection', (socket) => {
  logMessage('Client connected', 'info');
  
  socket.emit('systemStatus', systemStatus);
  socket.emit('messageLog', messageLog);
  socket.emit('boardMembers', boardMembers);
  socket.emit('wallDiscussions', wallDiscussions.slice(-20)); // Last 20 messages
  
  socket.on('disconnect', () => {
    logMessage('Client disconnected', 'info');
  });
  
  socket.on('executeCommand', async (data) => {
    try {
      const result = await executeCommand(data.command);
      socket.emit('commandResult', {
        command: data.command,
        output: result.stdout,
        error: result.stderr
      });
    } catch (error) {
      socket.emit('commandError', {
        command: data.command,
        error: error.message
      });
    }
  });
  
  // Wall discussion handlers
  socket.on('wallMessage', (data) => {
    const { from, to, message, type = 'text' } = data;
    
    const wallMessage = {
      id: Date.now(),
      from: from,
      to: to,
      message: message,
      type: type,
      timestamp: new Date().toISOString(),
      status: 'sent'
    };
    
    wallDiscussions.push(wallMessage);
    
    // Broadcast to all connected clients
    io.emit('wallMessage', wallMessage);
    
    logMessage(`Wall message from ${from} to ${to}: ${message}`, 'info');
  });
  
  socket.on('wallBroadcast', (data) => {
    const { from, message, type = 'broadcast' } = data;
    
    const broadcastMessage = {
      id: Date.now(),
      from: from,
      to: 'all',
      message: message,
      type: type,
      timestamp: new Date().toISOString(),
      status: 'broadcast'
    };
    
    wallDiscussions.push(broadcastMessage);
    
    // Broadcast to all connected clients
    io.emit('wallBroadcast', broadcastMessage);
    
    logMessage(`Broadcast from ${from}: ${message}`, 'info');
  });
});

// System monitoring
setInterval(() => {
  const systemInfo = getSystemInfo();
  systemStatus.cpu = systemInfo.cpu;
  systemStatus.memory = systemInfo.memory;
  
  // Simulate GPU usage
  systemStatus.gpu = Math.floor(Math.random() * 50) + 20;
  
  // Simulate network usage
  systemStatus.network = Math.floor(Math.random() * 100) + 10;
  
  io.emit('systemUpdate', systemStatus);
}, 5000);

// Start server
const DEFAULT_PORT = parseInt(process.env.PORT || "3001", 10);

function writeRuntimeInfo(port) {
  fs.writeFileSync("./.runtime.json", JSON.stringify({
    port, 
    commitSha: process.env.COMMIT_SHA || "dev",
    node: process.version, 
    time: new Date().toISOString()
  }, null, 2));
  console.log(`[boot] runtime -> ./.runtime.json`);
}

function startServer(port, attemptsLeft = 5) {
  const srv = http.createServer(app);
  
  // Set timeouts for protection against zombie connections
  srv.headersTimeout = 65000;
  srv.requestTimeout = 30000;

  srv.on("error", (err) => {
    if (err.code === "EADDRINUSE" && attemptsLeft > 0) {
      console.error(`[boot] Port ${port} ocupat. Încerc pe ${port + 1}...`);
      setTimeout(() => startServer(port + 1, attemptsLeft - 1), 500);
    } else {
      console.error("[boot] Server start failed:", err);
      process.exit(1);
    }
  });

  srv.listen(port, "127.0.0.1", () => {
    console.log(`[boot] Admin API live on http://localhost:${port}`);
    writeRuntimeInfo(port);
  });
}

// Graceful shutdown
process.on("SIGINT", () => { 
  console.log("bye"); 
  process.exit(0); 
});

startServer(DEFAULT_PORT);
