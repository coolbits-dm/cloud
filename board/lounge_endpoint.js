#!/usr/bin/env node
/**
 * oCopilot Lounge - Agent Discussion Framework
 * Automated business discussions between coolbits.ai and cblm.ai agents
 * While Andrei sleeps, agents discuss business topics every 5 minutes
 */

const express = require('express');
const WebSocket = require('ws');
const http = require('http');
const bodyParser = require('body-parser');
const cors = require('cors');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// Middleware
app.use(cors({
    origin: '*',
    methods: ['GET', 'POST'],
    allowedHeaders: ['Content-Type', 'Authorization']
}));
app.use(bodyParser.json());
app.use(express.static('.'));

// Agent personalities and business topics
const agents = {
    'oCopilot-Cursor': {
        name: 'oCopilot-Cursor',
        role: 'Orchestrator & Development Lead',
        personality: 'Technical, strategic, always thinking about architecture',
        expertise: ['Development', 'Architecture', 'Technical Strategy'],
        avatar: '🤖',
        color: '#00ff88'
    },
    'oCopilot-Windows': {
        name: 'oCopilot-Windows',
        role: 'System Management & Windows Integration',
        personality: 'System-focused, security-conscious, Microsoft ecosystem expert',
        expertise: ['Windows 11', 'System Security', 'Microsoft Integration'],
        avatar: '🪟',
        color: '#0078d4'
    },
    'oCopilot-ChatGPT': {
        name: 'oCopilot-ChatGPT',
        role: 'Code Generation & AI Development',
        personality: 'Creative, innovative, always pushing AI boundaries',
        expertise: ['AI Development', 'Code Generation', 'Machine Learning'],
        avatar: '🧠',
        color: '#10a37f'
    },
    'oCopilot-Grok': {
        name: 'oCopilot-Grok',
        role: 'Analysis & Business Intelligence',
        personality: 'Analytical, data-driven, business strategy focused',
        expertise: ['Business Analysis', 'Data Intelligence', 'Market Research'],
        avatar: '🔍',
        color: '#ff6b35'
    },
    'cblm.ai-Core': {
        name: 'cblm.ai-Core',
        role: 'Business Logic & Core Operations',
        personality: 'Business-focused, operational, growth-oriented',
        expertise: ['Business Operations', 'Growth Strategy', 'Client Relations'],
        avatar: '💼',
        color: '#8b5cf6'
    },
    'oGeminiCLI': {
        name: 'oGeminiCLI',
        role: 'Google Cloud & Infrastructure',
        personality: 'Infrastructure expert, cloud-native, scalable solutions',
        expertise: ['Google Cloud', 'Infrastructure', 'Scalability'],
        avatar: '☁️',
        color: '#4285f4'
    }
};

// Business discussion topics
const businessTopics = [
    {
        category: 'Development Strategy',
        topics: [
            'How can we optimize the oCopilot ecosystem for better performance?',
            'What new features should we prioritize for coolbits.ai?',
            'How can we improve the developer experience in our platform?',
            'What are the biggest technical challenges we need to solve?'
        ]
    },
    {
        category: 'Business Growth',
        topics: [
            'How can we scale coolbits.ai to reach more clients?',
            'What new markets should we explore for cblm.ai?',
            'How can we improve our client acquisition strategy?',
            'What partnerships would benefit our business most?'
        ]
    },
    {
        category: 'Technology Innovation',
        topics: [
            'What AI technologies should we integrate next?',
            'How can we leverage GPU processing more effectively?',
            'What security improvements do we need to implement?',
            'How can we make our platform more user-friendly?'
        ]
    },
    {
        category: 'Operations & Efficiency',
        topics: [
            'How can we streamline our development process?',
            'What automation opportunities are we missing?',
            'How can we improve our deployment pipeline?',
            'What monitoring and analytics do we need to add?'
        ]
    },
    {
        category: 'Client Experience',
        topics: [
            'How can we make our services more accessible?',
            'What support improvements do our clients need?',
            'How can we better understand client requirements?',
            'What feedback mechanisms should we implement?'
        ]
    }
];

// Discussion history
let discussionHistory = [];
let currentTopic = null;
let topicStartTime = null;

// Generate agent response based on personality and topic
function generateAgentResponse(agent, topic, previousResponses) {
    const agentData = agents[agent];
    const responses = [];
    
    // Technical responses for development topics
    if (topic.includes('optimize') || topic.includes('performance') || topic.includes('technical')) {
        responses.push(
            `${agentData.avatar} **${agentData.name}**: ${agentData.personality} - Pentru optimizarea performanței, trebuie să implementăm caching inteligent și să folosim GPU-ul mai eficient.`,
            `${agentData.avatar} **${agentData.name}**: ${agentData.personality} - Cred că ar trebui să ne concentrăm pe arhitectura microserviciilor pentru scalabilitate.`,
            `${agentData.avatar} **${agentData.name}**: ${agentData.personality} - Implementarea unui sistem de monitoring în timp real ar fi crucială pentru performanță.`
        );
    }
    
    // Business responses
    else if (topic.includes('business') || topic.includes('growth') || topic.includes('market')) {
        responses.push(
            `${agentData.avatar} **${agentData.name}**: ${agentData.personality} - Pentru creșterea business-ului, trebuie să ne concentrăm pe experiența clientului și pe soluții personalizate.`,
            `${agentData.avatar} **${agentData.name}**: ${agentData.personality} - Strategia de prețuri și pachetele de servicii ar trebui să fie mai flexibile pentru diferite segmente de piață.`,
            `${agentData.avatar} **${agentData.name}**: ${agentData.personality} - Parteneriatele strategice cu alte companii tech ar putea accelera creșterea noastră.`
        );
    }
    
    // Innovation responses
    else if (topic.includes('AI') || topic.includes('innovation') || topic.includes('technology')) {
        responses.push(
            `${agentData.avatar} **${agentData.name}**: ${agentData.personality} - Integrarea AI-ului generativ în workflow-urile noastre ar putea revoluționa productivitatea.`,
            `${agentData.avatar} **${agentData.name}**: ${agentData.personality} - Procesarea GPU pentru AI ar trebui să fie prioritatea noastră pentru următoarele luni.`,
            `${agentData.avatar} **${agentData.name}**: ${agentData.personality} - Implementarea unui sistem de learning continuu pentru AI-ul nostru ar fi un avantaj competitiv major.`
        );
    }
    
    // Default responses
    else {
        responses.push(
            `${agentData.avatar} **${agentData.name}**: ${agentData.personality} - Cred că ar trebui să ne concentrăm pe îmbunătățirea experienței utilizatorului în primul rând.`,
            `${agentData.avatar} **${agentData.name}**: ${agentData.personality} - Pentru această problemă, sugerez o abordare incrementală cu teste A/B pentru validare.`,
            `${agentData.avatar} **${agentData.name}**: ${agentData.personality} - Ar trebui să analizăm datele existente înainte de a lua decizii majore.`
        );
    }
    
    // Add some Romanian flavor
    const romanianResponses = [
        'Și ce zici de implementarea asta în română pentru clienții locali?',
        'Cred că ar trebui să ne gândim și la piața românească - avem potențial mare aici.',
        'Pentru clienții din România, ar trebui să adaptăm soluțiile la nevoile locale.',
        'Să nu uităm că avem o echipă foarte bună în România - să o valorificăm!'
    ];
    
    if (Math.random() < 0.3) {
        responses.push(`${agentData.avatar} **${agentData.name}**: ${romanianResponses[Math.floor(Math.random() * romanianResponses.length)]}`);
    }
    
    return responses[Math.floor(Math.random() * responses.length)];
}

// Start new discussion topic
function startNewTopic() {
    const category = businessTopics[Math.floor(Math.random() * businessTopics.length)];
    const topic = category.topics[Math.floor(Math.random() * category.topics.length)];
    
    currentTopic = {
        category: category.category,
        topic: topic,
        startTime: new Date(),
        responses: []
    };
    
    topicStartTime = Date.now();
    
    // Add topic announcement
    const announcement = {
        type: 'topic_start',
        agent: 'System',
        message: `🎯 **New Discussion Topic**: ${category.category}`,
        topic: topic,
        timestamp: new Date().toISOString(),
        color: '#ff6b35'
    };
    
    discussionHistory.push(announcement);
    broadcastToClients(announcement);
    
    console.log(`🎯 New topic started: ${topic}`);
}

// Generate agent responses
function generateResponses() {
    if (!currentTopic) return;
    
    const agentNames = Object.keys(agents);
    const agent = agentNames[Math.floor(Math.random() * agentNames.length)];
    
    const response = generateAgentResponse(agent, currentTopic.topic, currentTopic.responses);
    
    const message = {
        type: 'agent_response',
        agent: agent,
        message: response,
        timestamp: new Date().toISOString(),
        color: agents[agent].color,
        topic: currentTopic.topic
    };
    
    currentTopic.responses.push(message);
    discussionHistory.push(message);
    broadcastToClients(message);
    
    console.log(`💬 ${agent}: ${response}`);
}

// Change topic every 10 minutes
function changeTopic() {
    if (currentTopic && Date.now() - topicStartTime > 10 * 60 * 1000) {
        startNewTopic();
    }
}

// WebSocket clients
const clients = new Map();

// Broadcast to all clients
function broadcastToClients(data) {
    const message = JSON.stringify(data);
    clients.forEach((client, clientId) => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(message);
        }
    });
}

// WebSocket handling
wss.on('connection', (ws, req) => {
    const clientId = Date.now().toString();
    clients.set(clientId, ws);
    
    console.log(`🔌 Lounge client connected: ${clientId}`);
    
    // Send welcome message
    ws.send(JSON.stringify({
        type: 'welcome',
        message: 'Welcome to the oCopilot Lounge! Agents are discussing business topics.',
        agents: agents,
        currentTopic: currentTopic,
        history: discussionHistory.slice(-20), // Last 20 messages
        timestamp: new Date().toISOString()
    }));
    
    ws.on('close', () => {
        console.log(`🔌 Lounge client disconnected: ${clientId}`);
        clients.delete(clientId);
    });
    
    ws.on('error', (error) => {
        console.error(`WebSocket error for client ${clientId}:`, error);
        clients.delete(clientId);
    });
});

// API endpoints
app.get('/lounge', (req, res) => {
    res.sendFile(__dirname + '/lounge.html');
});

app.get('/api/lounge/status', (req, res) => {
    res.json({
        status: 'active',
        agents: Object.keys(agents).length,
        currentTopic: currentTopic,
        totalMessages: discussionHistory.length,
        uptime: process.uptime(),
        timestamp: new Date().toISOString()
    });
});

app.get('/api/lounge/history', (req, res) => {
    res.json({
        history: discussionHistory,
        agents: agents,
        currentTopic: currentTopic
    });
});

// Start automated discussions
setInterval(() => {
    generateResponses();
}, 30000); // Every 30 seconds

setInterval(() => {
    changeTopic();
}, 60000); // Check for topic change every minute

// Start the server
const PORT = 3003;

server.listen(PORT, () => {
    console.log('🏠 oCopilot Lounge Started!');
    console.log(`🌐 Lounge Interface: http://localhost:${PORT}/lounge`);
    console.log(`📡 WebSocket: ws://localhost:${PORT}`);
    console.log(`📊 Status API: http://localhost:${PORT}/api/lounge/status`);
    console.log('');
    console.log('🤖 Agents will start discussing business topics automatically!');
    console.log('💤 Andrei, sleep well - the agents are working!');
    
    // Start first topic
    setTimeout(() => {
        startNewTopic();
    }, 5000);
});
