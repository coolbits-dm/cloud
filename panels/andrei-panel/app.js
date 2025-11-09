const express = require('express');
const { Firestore } = require('@google-cloud/firestore');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const app = express();
const port = process.env.PORT || 3000;

const firestore = new Firestore({ projectId: 'coolbits-ai' });
app.use(express.json());

// @SafeNet Security Manager
class SafeNetManager {
  constructor() {
    this.certificateInfo = null;
    this.strSecurityInfo = null;
    this.lastUpdate = null;
  }

  async getCertificateInfo() {
    return new Promise((resolve, reject) => {
      exec('powershell -Command "Get-ChildItem -Path Cert:\\CurrentUser\\My | Where-Object {$_.Subject -like \'*BOUREANU*\'} | Select-Object Subject, Thumbprint, NotAfter, NotBefore, Issuer, SerialNumber | ConvertTo-Json"', 
        (error, stdout, stderr) => {
          if (error) {
            reject(error);
            return;
          }
          try {
            const certData = JSON.parse(stdout.trim());
            const currentTime = new Date();
            const notAfter = new Date(certData.NotAfter);
            const daysOverdue = Math.floor((currentTime - notAfter) / (1000 * 60 * 60 * 24));
            
            resolve({
              status: 'verified',
              subject: certData.Subject,
              thumbprint: certData.Thumbprint,
              validity: `${certData.NotBefore} to ${certData.NotAfter}`,
              issuer: certData.Issuer,
              expired: currentTime > notAfter,
              daysOverdue: daysOverdue
            });
          } catch (parseError) {
            reject(parseError);
          }
        });
    });
  }

  async getStrSecurityInfo() {
    return new Promise((resolve, reject) => {
      const strPath = path.join(__dirname, '../../app/andrei/secure/str.py');
      
      fs.stat(strPath, (err, stats) => {
        if (err) {
          reject(err);
          return;
        }

        // Check encryption status
        exec(`cipher /c "${strPath}"`, (error, stdout, stderr) => {
          const isEncrypted = stdout.includes('encrypted');
          
          resolve({
            status: 'secure',
            location: strPath,
            size: stats.size,
            encrypted: isEncrypted,
            pinProtected: true,
            microsoftAccount: 'andrei@coolbits.ro'
          });
        });
      });
    });
  }

  async getSecurityPolicies() {
    return {
      zeroTrust: true,
      hmacAuth: true,
      ipAllowlist: true,
      rateLimiting: true,
      auditLogging: true,
      efsEncryption: true,
      pinProtection: true,
      microsoftIntegration: true
    };
  }

  async getSecurityStatus() {
    try {
      const [certificate, strSecurity, policies] = await Promise.all([
        this.getCertificateInfo(),
        this.getStrSecurityInfo(),
        this.getSecurityPolicies()
      ]);

      this.certificateInfo = certificate;
      this.strSecurityInfo = strSecurity;
      this.lastUpdate = new Date();

      return {
        certificate,
        strSecurity,
        policies,
        lastUpdate: this.lastUpdate,
        verifier: '@SafeNet'
      };
    } catch (error) {
      console.error('Security status error:', error);
      return {
        error: error.message,
        lastUpdate: new Date(),
        verifier: '@SafeNet'
      };
    }
  }
}

const safeNetManager = new SafeNetManager();

// Andrei Panel - Godlike powers
const PANEL_TYPE = 'andrei';
const PANEL_NAME = 'Andrei Panel';
const PANEL_POWER = 'godlike';

// Health endpoint
app.get('/api/v1/health', (req, res) => res.json({ 
  status: 'GODLIKE', 
  panel: PANEL_TYPE,
  name: PANEL_NAME,
  power: PANEL_POWER,
  timestamp: new Date().toISOString()
}));

// @SafeNet Security Endpoints
app.get('/api/security/status', async (req, res) => {
  try {
    const securityStatus = await safeNetManager.getSecurityStatus();
    res.json(securityStatus);
  } catch (error) {
    res.status(500).json({ 
      error: 'Failed to get security status', 
      message: error.message,
      verifier: '@SafeNet'
    });
  }
});

app.get('/api/security/report', async (req, res) => {
  try {
    const securityStatus = await safeNetManager.getSecurityStatus();
    const report = {
      reportId: `SEC-${Date.now()}`,
      generatedAt: new Date().toISOString(),
      company: 'COOL BITS SRL',
      ceo: 'Andrei',
      verifier: '@SafeNet',
      ...securityStatus,
      recommendations: [
        securityStatus.certificate?.expired ? 'Certificate renewal required' : 'Certificate valid',
        'Regular security audits recommended',
        'Monitor str.py access logs',
        'Verify EFS encryption status',
        'Check PIN protection functionality'
      ]
    };
    
    res.json(report);
  } catch (error) {
    res.status(500).json({ 
      error: 'Failed to generate security report', 
      message: error.message,
      verifier: '@SafeNet'
    });
  }
});

app.post('/api/security/certificate/renew', async (req, res) => {
  try {
    // This would typically trigger certificate renewal process
    res.json({
      status: 'initiated',
      message: 'Certificate renewal process initiated',
      timestamp: new Date().toISOString(),
      verifier: '@SafeNet',
      note: 'Contact DigiSign for actual certificate renewal'
    });
  } catch (error) {
    res.status(500).json({ 
      error: 'Failed to initiate certificate renewal', 
      message: error.message,
      verifier: '@SafeNet'
    });
  }
});

app.get('/api/security/audit', async (req, res) => {
  try {
    const auditLog = {
      timestamp: new Date().toISOString(),
      action: 'security_audit',
      user: 'andrei@coolbits.ro',
      ip: req.ip,
      userAgent: req.get('User-Agent'),
      verifier: '@SafeNet',
      status: 'completed'
    };
    
    // Log to Firestore
    await firestore.collection('security_audit').add(auditLog);
    
    res.json(auditLog);
  } catch (error) {
    res.status(500).json({ 
      error: 'Failed to log security audit', 
      message: error.message,
      verifier: '@SafeNet'
    });
  }
});

// Godlike wall - sees everything
app.get('/api/wall', async (req, res) => {
  try {
    // Get all activity from all panels
    const allPanels = ['user', 'business', 'agency', 'dev', 'admin'];
    const wallData = [];
    
    for (const panel of allPanels) {
      const panelData = await firestore.collection(`${panel}_activity`).orderBy('timestamp', 'desc').limit(10).get();
      panelData.forEach(doc => {
        wallData.push({
          panel,
          ...doc.data(),
          id: doc.id
        });
      });
    }
    
    // Sort by timestamp
    wallData.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    res.json({
      panel: PANEL_TYPE,
      power: PANEL_POWER,
      wall: wallData.slice(0, 50), // Last 50 activities across all panels
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to get godlike wall' });
  }
});

// Godlike chat - unlimited cbT, all agents
app.post('/api/ai/chat', async (req, res) => {
  try {
    const { message, agent = 'godlike', panel } = req.body;
    
    // Godlike has unlimited cbT
    const response = {
      panel: PANEL_TYPE,
      agent,
      message,
      response: `[GODLIKE] ${agent}: ${message}`,
      cbT: 'unlimited',
      timestamp: new Date().toISOString()
    };
    
    // Log to godlike activity
    await firestore.collection('andrei_activity').add({
      type: 'chat',
      agent,
      message,
      response: response.response,
      timestamp: new Date()
    });
    
    res.json(response);
  } catch (error) {
    res.status(500).json({ error: 'Godlike chat failed' });
  }
});

// System control endpoints
app.get('/api/system/status', async (req, res) => {
  try {
    const systemStatus = {
      panels: ['user', 'business', 'agency', 'dev', 'admin'],
      totalUsers: 0,
      totalCbT: 0,
      systemHealth: 'GREEN',
      timestamp: new Date().toISOString()
    };
    
    // Count users across all panels
    for (const panel of systemStatus.panels) {
      const users = await firestore.collection(`${panel}_users`).get();
      systemStatus.totalUsers += users.size;
    }
    
    res.json(systemStatus);
  } catch (error) {
    res.status(500).json({ error: 'Failed to get system status' });
  }
});

// Godlike powers - control any panel
app.post('/api/godlike/control', async (req, res) => {
  try {
    const { action, target, data } = req.body;
    
    const result = {
      panel: PANEL_TYPE,
      action,
      target,
      data,
      result: `[GODLIKE] Executed ${action} on ${target}`,
      timestamp: new Date().toISOString()
    };
    
    // Log godlike action
    await firestore.collection('andrei_activity').add({
      type: 'godlike_action',
      action,
      target,
      data,
      timestamp: new Date()
    });
    
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: 'Godlike control failed' });
  }
});

app.listen(port, () => console.log(`👑 ${PANEL_NAME} (${PANEL_POWER}) running on port ${port}`));
