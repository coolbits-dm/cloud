#!/usr/bin/env node
/**
 * CoolBits.ai Offline AI Board - Node.js Version
 * CEO: Andrei - andrei@coolbits.ro
 * Managed by: oCursor (Local Development)
 */

const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');

class CoolBitsAIBoard {
    constructor(port = 8082) {
        this.port = port;
        this.app = express();
        this.server = http.createServer(this.app);
        this.io = socketIo(this.server, {
            cors: {
                origin: "*",
                methods: ["GET", "POST"]
            }
        });
        
        // Initialize organizational structure
        this.initializeOrganizationalStructure();
        this.initializePanelSystem();
        this.initializeBitsFramework();
        this.initializeCbtEconomy();
        
        // Setup middleware and routes
        this.setupMiddleware();
        this.setupRoutes();
        this.setupSocketIo();
    }
    
    initializeOrganizationalStructure() {
        this.roles = {
            "executive": {
                "ceo": {"name": "CEO", "email": "ceo@coolbits.ai", "status": "ACTIVE"},
                "strategy-office-cso": {"name": "CSO", "email": "cso@coolbits.ai", "status": "ACTIVE"},
                "board": {"name": "Board", "email": "board@coolbits.ai", "status": "ACTIVE"}
            },
            "technology": {
                "cto": {"name": "CTO", "email": "cto@coolbits.ai", "status": "ACTIVE"},
                "engineering": {
                    "backend": {"name": "Backend Engineering", "email": "backend@coolbits.ai", "status": "ACTIVE"},
                    "frontend": {"name": "Frontend Engineering", "email": "frontend@coolbits.ai", "status": "ACTIVE"},
                    "mobile": {"name": "Mobile Engineering", "email": "mobile@coolbits.ai", "status": "ACTIVE"},
                    "platform": {"name": "Platform Engineering", "email": "platform@coolbits.ai", "status": "ACTIVE"},
                    "architecture": {"name": "Architecture", "email": "architecture@coolbits.ai", "status": "ACTIVE"}
                },
                "devops-sre": {"name": "DevOps/SRE", "email": "devops@coolbits.ai", "status": "ACTIVE"},
                "qa-quality": {"name": "QA/Quality", "email": "qa@coolbits.ai", "status": "ACTIVE"},
                "research-rnd": {"name": "R&D", "email": "rnd@coolbits.ai", "status": "ACTIVE"}
            },
            "product": {
                "cpo": {"name": "CPO", "email": "cpo@coolbits.ai", "status": "ACTIVE"},
                "product-management": {"name": "Product Management", "email": "pm@coolbits.ai", "status": "ACTIVE"},
                "product-ops": {"name": "Product Ops", "email": "productops@coolbits.ai", "status": "ACTIVE"},
                "design-ux": {"name": "Design/UX", "email": "design@coolbits.ai", "status": "ACTIVE"},
                "ux-research": {"name": "UX Research", "email": "ux@coolbits.ai", "status": "ACTIVE"},
                "docs": {"name": "Documentation", "email": "docs@coolbits.ai", "status": "ACTIVE"}
            },
            "data": {
                "cdo": {"name": "CDO", "email": "cdo@coolbits.ai", "status": "ACTIVE"},
                "data-engineering": {"name": "Data Engineering", "email": "dataeng@coolbits.ai", "status": "ACTIVE"},
                "analytics-bi": {"name": "Analytics/BI", "email": "analytics@coolbits.ai", "status": "ACTIVE"},
                "ml-ai": {"name": "ML/AI", "email": "ml@coolbits.ai", "status": "ACTIVE"}
            },
            "security": {
                "ciso": {"name": "CISO", "email": "ciso@coolbits.ai", "status": "ACTIVE"},
                "appsec": {"name": "AppSec", "email": "appsec@coolbits.ai", "status": "ACTIVE"},
                "secops": {"name": "SecOps", "email": "secops@coolbits.ai", "status": "ACTIVE"},
                "grc": {"name": "GRC", "email": "grc@coolbits.ai", "status": "ACTIVE"},
                "compliance": {"name": "Compliance", "email": "compliance@coolbits.ai", "status": "ACTIVE"}
            },
            "it": {
                "cio": {"name": "CIO", "email": "cio@coolbits.ai", "status": "ACTIVE"},
                "helpdesk": {"name": "Helpdesk", "email": "helpdesk@coolbits.ai", "status": "ACTIVE"},
                "identity-access": {"name": "Identity/Access", "email": "iam@coolbits.ai", "status": "ACTIVE"},
                "networking": {"name": "Networking", "email": "networking@coolbits.ai", "status": "ACTIVE"},
                "endpoint-management": {"name": "Endpoint Management", "email": "endpoint@coolbits.ai", "status": "ACTIVE"}
            },
            "operations": {
                "coo": {"name": "COO", "email": "coo@coolbits.ai", "status": "ACTIVE"},
                "pmo-program-management": {"name": "PMO", "email": "pmo@coolbits.ai", "status": "ACTIVE"},
                "procurement": {"name": "Procurement", "email": "procurement@coolbits.ai", "status": "ACTIVE"},
                "facilities": {"name": "Facilities", "email": "facilities@coolbits.ai", "status": "ACTIVE"},
                "logistics": {"name": "Logistics", "email": "logistics@coolbits.ai", "status": "ACTIVE"}
            },
            "finance": {
                "cfo": {"name": "CFO", "email": "cfo@coolbits.ai", "status": "ACTIVE"},
                "accounting": {"name": "Accounting", "email": "accounting@coolbits.ai", "status": "ACTIVE"},
                "fpa": {"name": "FPA", "email": "fpa@coolbits.ai", "status": "ACTIVE"},
                "treasury": {"name": "Treasury", "email": "treasury@coolbits.ai", "status": "ACTIVE"},
                "payroll": {"name": "Payroll", "email": "payroll@coolbits.ai", "status": "ACTIVE"}
            },
            "people": {
                "chro": {"name": "CHRO", "email": "chro@coolbits.ai", "status": "ACTIVE"},
                "recruiting-talent": {"name": "Recruiting", "email": "recruiting@coolbits.ai", "status": "ACTIVE"},
                "people-ops-hr": {"name": "People Ops", "email": "peopleops@coolbits.ai", "status": "ACTIVE"},
                "learning-development": {"name": "L&D", "email": "ld@coolbits.ai", "status": "ACTIVE"},
                "comp-benefits": {"name": "Comp/Benefits", "email": "comp@coolbits.ai", "status": "ACTIVE"}
            },
            "revenue": {
                "cro": {"name": "CRO", "email": "cro@coolbits.ai", "status": "ACTIVE"},
                "sales": {"name": "Sales", "email": "sales@coolbits.ai", "status": "ACTIVE"},
                "sales-ops": {"name": "Sales Ops", "email": "salesops@coolbits.ai", "status": "ACTIVE"},
                "partnerships": {"name": "Partnerships", "email": "partnerships@coolbits.ai", "status": "ACTIVE"},
                "customer-success": {"name": "Customer Success", "email": "cs@coolbits.ai", "status": "ACTIVE"}
            },
            "marketing": {
                "cmo": {"name": "CMO", "email": "cmo@coolbits.ai", "status": "ACTIVE"},
                "brand": {"name": "Brand", "email": "brand@coolbits.ai", "status": "ACTIVE"},
                "performance-growth": {"name": "Performance/Growth", "email": "growth@coolbits.ai", "status": "ACTIVE"},
                "content": {"name": "Content", "email": "content@coolbits.ai", "status": "ACTIVE"},
                "pr-comms": {"name": "PR/Comms", "email": "pr@coolbits.ai", "status": "ACTIVE"},
                "events": {"name": "Events", "email": "events@coolbits.ai", "status": "ACTIVE"}
            },
            "legal": {
                "clo-gc": {"name": "CLO/GC", "email": "legal@coolbits.ai", "status": "ACTIVE"},
                "contracts": {"name": "Contracts", "email": "contracts@coolbits.ai", "status": "ACTIVE"},
                "privacy": {"name": "Privacy", "email": "privacy@coolbits.ai", "status": "ACTIVE"},
                "ip": {"name": "IP", "email": "ip@coolbits.ai", "status": "ACTIVE"},
                "regulatory": {"name": "Regulatory", "email": "regulatory@coolbits.ai", "status": "ACTIVE"}
            },
            "customer": {
                "cco": {"name": "CCO", "email": "cco@coolbits.ai", "status": "ACTIVE"},
                "support": {"name": "Support", "email": "support@coolbits.ai", "status": "ACTIVE"},
                "training-education": {"name": "Training", "email": "training@coolbits.ai", "status": "ACTIVE"},
                "community": {"name": "Community", "email": "community@coolbits.ai", "status": "ACTIVE"}
            }
        };
        
        console.log(`Initialized organizational structure with ${this.countTotalRoles()} roles`);
    }
    
    countTotalRoles() {
        let count = 0;
        for (const category in this.roles) {
            for (const roleKey in this.roles[category]) {
                const roleData = this.roles[category][roleKey];
                if (roleData.name) {
                    count++;
                } else if (typeof roleData === 'object') {
                    for (const subRoleKey in roleData) {
                        if (roleData[subRoleKey].name) {
                            count++;
                        }
                    }
                }
            }
        }
        return count;
    }
    
    initializePanelSystem() {
        this.panels = {
            "user": {
                "name": "User Panel",
                "description": "General user dashboard",
                "access_level": "USER",
                "features": ["basic_ai_chat", "personal_dashboard", "user_settings"],
                "status": "ACTIVE"
            },
            "business": {
                "name": "Business Panel", 
                "description": "Business management dashboard",
                "access_level": "BUSINESS",
                "features": ["business_ai_council", "multi_business_select", "business_analytics"],
                "status": "ACTIVE"
            },
            "agency": {
                "name": "Agency Panel",
                "description": "Digital marketing agency panel with MCC connects",
                "access_level": "AGENCY", 
                "features": ["mcc_connects", "agency_tools", "client_management"],
                "status": "ACTIVE"
            },
            "dev": {
                "name": "Developer Panel",
                "description": "Developer panel with all developer tools",
                "access_level": "DEVELOPER",
                "features": ["cursor_integration", "google_cloud", "github", "api_tools"],
                "status": "ACTIVE"
            },
            "admin": {
                "name": "Admin Panel",
                "description": "User admin panel",
                "access_level": "ADMIN",
                "features": ["user_management", "system_settings", "admin_tools"],
                "status": "ACTIVE"
            },
            "andrei": {
                "name": "Andrei God Mode",
                "description": "CEO God mode panel with dedicated API keys",
                "access_level": "GOD_MODE",
                "features": ["full_access", "dedicated_openai", "dedicated_grok", "system_control"],
                "status": "ACTIVE"
            }
        };
        
        console.log(`Initialized panel system with ${Object.keys(this.panels).length} panels`);
    }
    
    initializeBitsFramework() {
        this.bitsFramework = {
            "c-bit": {
                "name": "Cool Bits (Admin Bits)",
                "description": "Secret internal CEO level bits",
                "access_level": "CEO_ONLY",
                "features": ["system_control", "god_mode_access", "all_permissions"],
                "status": "ACTIVE"
            },
            "u-bit": {
                "name": "User Bits",
                "description": "User level bits and permissions",
                "access_level": "USER",
                "features": ["personal_ai", "user_dashboard", "basic_features"],
                "status": "ACTIVE"
            },
            "b-bit": {
                "name": "Business Bits", 
                "description": "Business level bits and permissions",
                "access_level": "BUSINESS",
                "features": ["business_ai_council", "multi_business", "business_analytics"],
                "status": "ACTIVE"
            },
            "a-bit": {
                "name": "Agency Bits",
                "description": "Agency level bits and permissions", 
                "access_level": "AGENCY",
                "features": ["mcc_connects", "agency_tools", "client_management"],
                "status": "ACTIVE"
            },
            "d-bit": {
                "name": "Developer Bits",
                "description": "Developer level bits and permissions",
                "access_level": "DEVELOPER", 
                "features": ["dev_tools", "api_access", "integration_tools"],
                "status": "ACTIVE"
            }
        };
        
        console.log(`Initialized bits framework with ${Object.keys(this.bitsFramework).length} bit types`);
    }
    
    initializeCbtEconomy() {
        this.cbtEconomy = {
            "total_supply": 1000000,
            "circulating": 750000,
            "reserved": 250000,
            "allocation": {
                "c-bit": 100000,
                "u-bit": 200000,
                "b-bit": 200000,
                "a-bit": 150000,
                "d-bit": 100000
            },
            "transactions": [],
            "status": "ACTIVE"
        };
        
        console.log("Initialized cbT economy system");
    }
    
    setupMiddleware() {
        this.app.use(cors());
        this.app.use(express.json());
    }
    
    setupRoutes() {
        // Health check
        this.app.get('/health', (req, res) => {
            res.json({
                "status": "healthy",
                "service": "CoolBits.ai Offline AI Board (Node.js)",
                "ceo": "Andrei - andrei@coolbits.ro",
                "timestamp": new Date().toISOString(),
                "port": this.port,
                "roles_count": this.countTotalRoles(),
                "panels_count": Object.keys(this.panels).length,
                "bits_count": Object.keys(this.bitsFramework).length
            });
        });
        
        // Organizational structure
        this.app.get('/organization', (req, res) => {
            res.json({
                "success": true,
                "organization": this.roles,
                "total_roles": this.countTotalRoles(),
                "timestamp": new Date().toISOString()
            });
        });
        
        this.app.get('/roles', (req, res) => {
            res.json({
                "success": true,
                "roles": this.roles,
                "total_roles": this.countTotalRoles(),
                "timestamp": new Date().toISOString()
            });
        });
        
        this.app.get('/roles/:category', (req, res) => {
            const category = req.params.category;
            if (this.roles[category]) {
                res.json({
                    "success": true,
                    "category": category,
                    "roles": this.roles[category],
                    "timestamp": new Date().toISOString()
                });
            } else {
                res.status(404).json({
                    "success": false,
                    "error": `Category '${category}' not found`
                });
            }
        });
        
        // Panel system
        this.app.get('/panels', (req, res) => {
            res.json({
                "success": true,
                "panels": this.panels,
                "total_panels": Object.keys(this.panels).length,
                "timestamp": new Date().toISOString()
            });
        });
        
        this.app.get('/panels/:panelName', (req, res) => {
            const panelName = req.params.panelName;
            if (this.panels[panelName]) {
                res.json({
                    "success": true,
                    "panel": this.panels[panelName],
                    "timestamp": new Date().toISOString()
                });
            } else {
                res.status(404).json({
                    "success": false,
                    "error": `Panel '${panelName}' not found`
                });
            }
        });
        
        // Bits framework
        this.app.get('/bits', (req, res) => {
            res.json({
                "success": true,
                "bits_framework": this.bitsFramework,
                "total_bits": Object.keys(this.bitsFramework).length,
                "timestamp": new Date().toISOString()
            });
        });
        
        this.app.get('/bits/:bitType', (req, res) => {
            const bitType = req.params.bitType;
            if (this.bitsFramework[bitType]) {
                res.json({
                    "success": true,
                    "bit": this.bitsFramework[bitType],
                    "timestamp": new Date().toISOString()
                });
            } else {
                res.status(404).json({
                    "success": false,
                    "error": `Bit type '${bitType}' not found`
                });
            }
        });
        
        // cbT economy
        this.app.get('/cbt', (req, res) => {
            res.json({
                "success": true,
                "cbt_economy": this.cbtEconomy,
                "timestamp": new Date().toISOString()
            });
        });
        
        this.app.post('/cbt/transfer', (req, res) => {
            try {
                const { from, to, amount } = req.body;
                
                const transaction = {
                    "id": this.cbtEconomy.transactions.length + 1,
                    "from": from,
                    "to": to,
                    "amount": amount,
                    "timestamp": new Date().toISOString(),
                    "status": "COMPLETED"
                };
                
                this.cbtEconomy.transactions.push(transaction);
                
                res.json({
                    "success": true,
                    "transaction": transaction,
                    "timestamp": new Date().toISOString()
                });
            } catch (error) {
                res.status(500).json({
                    "success": false,
                    "error": error.message
                });
            }
        });
        
        // AI Board control
        this.app.get('/board', (req, res) => {
            res.json({
                "success": true,
                "board_status": {
                    "roles": this.countTotalRoles(),
                    "panels": Object.keys(this.panels).length,
                    "bits": Object.keys(this.bitsFramework).length,
                    "cbt_total": this.cbtEconomy.total_supply,
                    "status": "ACTIVE",
                    "mode": "OFFLINE"
                },
                "timestamp": new Date().toISOString()
            });
        });
        
        this.app.post('/board/command', (req, res) => {
            try {
                const { command } = req.body;
                const response = this.processBoardCommand({ command });
                
                res.json({
                    "success": true,
                    "command": command,
                    "response": response,
                    "timestamp": new Date().toISOString()
                });
            } catch (error) {
                res.status(500).json({
                    "success": false,
                    "error": error.message
                });
            }
        });
        
        // Serve AI Board HTML
        this.app.get('/', this.serveAiBoard.bind(this));
        this.app.get('/ai-board', this.serveAiBoard.bind(this));
    }
    
    setupSocketIo() {
        this.io.on('connection', (socket) => {
            console.log(`AI Board client connected: ${socket.id}`);
            
            socket.emit('board_status', {
                "roles": this.countTotalRoles(),
                "panels": Object.keys(this.panels).length,
                "bits": Object.keys(this.bitsFramework).length,
                "status": "ACTIVE"
            });
            
            socket.on('disconnect', () => {
                console.log(`AI Board client disconnected: ${socket.id}`);
            });
            
            socket.on('board_command', (data) => {
                console.log(`Board command from ${socket.id}:`, data);
                const response = this.processBoardCommand(data);
                socket.emit('board_response', response);
            });
        });
    }
    
    processBoardCommand(data) {
        const command = data.command || '';
        
        switch (command) {
            case 'status':
                return {
                    "roles": this.countTotalRoles(),
                    "panels": Object.keys(this.panels).length,
                    "bits": Object.keys(this.bitsFramework).length,
                    "status": "ACTIVE"
                };
            case 'roles':
                return { "roles": this.roles };
            case 'panels':
                return { "panels": this.panels };
            case 'bits':
                return { "bits": this.bitsFramework };
            case 'cbt':
                return { "cbt": this.cbtEconomy };
            default:
                return { "message": `Command '${command}' processed`, "status": "OK" };
        }
    }
    
    serveAiBoard(req, res) {
        const htmlContent = `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>CoolBits.ai Offline AI Board</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                .container { max-width: 1400px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { text-align: center; margin-bottom: 30px; }
                .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
                .card { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; }
                .status { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
                .status.active { background: #d4edda; color: #155724; }
                .endpoints { background: #e9ecef; padding: 20px; border-radius: 8px; }
                .endpoint { margin: 10px 0; padding: 10px; background: white; border-radius: 4px; }
                .method { display: inline-block; padding: 2px 6px; border-radius: 3px; font-size: 11px; font-weight: bold; margin-right: 10px; }
                .method.get { background: #28a745; color: white; }
                .method.post { background: #007bff; color: white; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 CoolBits.ai Offline AI Board (Node.js)</h1>
                    <p><strong>CEO:</strong> Andrei - andrei@coolbits.ro</p>
                    <p><strong>Managed by:</strong> oCursor (Local Development)</p>
                    <p><strong>Port:</strong> ${this.port} | <strong>Status:</strong> <span class="status active">ACTIVE</span></p>
                </div>
                
                <h2>📊 Organizational Structure</h2>
                <div class="grid">
                    <div class="card">
                        <h3>Executive</h3>
                        <p>CEO, CSO, Board</p>
                        <p><strong>Roles:</strong> 3</p>
                    </div>
                    <div class="card">
                        <h3>Technology</h3>
                        <p>CTO, Engineering, DevOps, QA, R&D</p>
                        <p><strong>Roles:</strong> 9</p>
                    </div>
                    <div class="card">
                        <h3>Product</h3>
                        <p>CPO, Product Management, Design, UX</p>
                        <p><strong>Roles:</strong> 6</p>
                    </div>
                    <div class="card">
                        <h3>Data</h3>
                        <p>CDO, Data Engineering, Analytics, ML/AI</p>
                        <p><strong>Roles:</strong> 4</p>
                    </div>
                    <div class="card">
                        <h3>Security</h3>
                        <p>CISO, AppSec, SecOps, GRC, Compliance</p>
                        <p><strong>Roles:</strong> 5</p>
                    </div>
                    <div class="card">
                        <h3>IT</h3>
                        <p>CIO, Helpdesk, Identity/Access, Networking</p>
                        <p><strong>Roles:</strong> 5</p>
                    </div>
                    <div class="card">
                        <h3>Operations</h3>
                        <p>COO, PMO, Procurement, Facilities</p>
                        <p><strong>Roles:</strong> 5</p>
                    </div>
                    <div class="card">
                        <h3>Finance</h3>
                        <p>CFO, Accounting, FPA, Treasury, Payroll</p>
                        <p><strong>Roles:</strong> 5</p>
                    </div>
                    <div class="card">
                        <h3>People</h3>
                        <p>CHRO, Recruiting, People Ops, L&D</p>
                        <p><strong>Roles:</strong> 5</p>
                    </div>
                    <div class="card">
                        <h3>Revenue</h3>
                        <p>CRO, Sales, Sales Ops, Partnerships</p>
                        <p><strong>Roles:</strong> 5</p>
                    </div>
                    <div class="card">
                        <h3>Marketing</h3>
                        <p>CMO, Brand, Performance, Content, PR</p>
                        <p><strong>Roles:</strong> 6</p>
                    </div>
                    <div class="card">
                        <h3>Legal</h3>
                        <p>CLO/GC, Contracts, Privacy, IP, Regulatory</p>
                        <p><strong>Roles:</strong> 5</p>
                    </div>
                    <div class="card">
                        <h3>Customer</h3>
                        <p>CCO, Support, Training, Community</p>
                        <p><strong>Roles:</strong> 4</p>
                    </div>
                </div>
                
                <h2>🎛️ Panel System</h2>
                <div class="grid">
                    <div class="card">
                        <h3>User Panel</h3>
                        <p>General user dashboard</p>
                        <p><strong>Access:</strong> USER</p>
                    </div>
                    <div class="card">
                        <h3>Business Panel</h3>
                        <p>Business management dashboard</p>
                        <p><strong>Access:</strong> BUSINESS</p>
                    </div>
                    <div class="card">
                        <h3>Agency Panel</h3>
                        <p>Digital marketing agency panel</p>
                        <p><strong>Access:</strong> AGENCY</p>
                    </div>
                    <div class="card">
                        <h3>Developer Panel</h3>
                        <p>Developer tools and integrations</p>
                        <p><strong>Access:</strong> DEVELOPER</p>
                    </div>
                    <div class="card">
                        <h3>Admin Panel</h3>
                        <p>User admin panel</p>
                        <p><strong>Access:</strong> ADMIN</p>
                    </div>
                    <div class="card">
                        <h3>Andrei God Mode</h3>
                        <p>CEO God mode panel</p>
                        <p><strong>Access:</strong> GOD_MODE</p>
                    </div>
                </div>
                
                <h2>🔧 Bits Framework</h2>
                <div class="grid">
                    <div class="card">
                        <h3>c-bit (Cool Bits)</h3>
                        <p>Secret internal CEO level bits</p>
                        <p><strong>Access:</strong> CEO_ONLY</p>
                    </div>
                    <div class="card">
                        <h3>u-bit (User Bits)</h3>
                        <p>User level bits and permissions</p>
                        <p><strong>Access:</strong> USER</p>
                    </div>
                    <div class="card">
                        <h3>b-bit (Business Bits)</h3>
                        <p>Business level bits and permissions</p>
                        <p><strong>Access:</strong> BUSINESS</p>
                    </div>
                    <div class="card">
                        <h3>a-bit (Agency Bits)</h3>
                        <p>Agency level bits and permissions</p>
                        <p><strong>Access:</strong> AGENCY</p>
                    </div>
                    <div class="card">
                        <h3>d-bit (Developer Bits)</h3>
                        <p>Developer level bits and permissions</p>
                        <p><strong>Access:</strong> DEVELOPER</p>
                    </div>
                </div>
                
                <h2>💰 cbT Economy</h2>
                <div class="card">
                    <h3>cbTokens Economy</h3>
                    <p><strong>Total Supply:</strong> 1,000,000 cbT</p>
                    <p><strong>Circulating:</strong> 750,000 cbT</p>
                    <p><strong>Reserved:</strong> 250,000 cbT</p>
                    <p><strong>Status:</strong> <span class="status active">ACTIVE</span></p>
                </div>
                
                <h2>🔗 Available Endpoints</h2>
                <div class="endpoints">
                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <strong>/health</strong> - Health check
                    </div>
                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <strong>/organization</strong> - Complete organizational structure
                    </div>
                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <strong>/roles</strong> - All roles
                    </div>
                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <strong>/panels</strong> - All panels
                    </div>
                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <strong>/bits</strong> - Bits framework
                    </div>
                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <strong>/cbt</strong> - cbT economy status
                    </div>
                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <strong>/board</strong> - AI Board status
                    </div>
                    <div class="endpoint">
                        <span class="method post">POST</span>
                        <strong>/board/command</strong> - Execute board command
                    </div>
                </div>
                
                <h2>🎯 Status Summary</h2>
                <div style="background: #d4edda; padding: 15px; border-radius: 8px; margin-top: 20px;">
                    <p><strong>✅ CoolBits.ai Offline AI Board Operational (Node.js)</strong></p>
                    <p>• Server: Running on port ${this.port}</p>
                    <p>• Roles: ${this.countTotalRoles()} total organizational roles</p>
                    <p>• Panels: 6 panel system active</p>
                    <p>• Bits: 5 bit framework types</p>
                    <p>• Economy: cbT token system active</p>
                    <p>• Mode: OFFLINE (no internet required)</p>
                </div>
            </div>
        </body>
        </html>
        `;
        
        res.send(htmlContent);
    }
    
    start() {
        this.server.listen(this.port, () => {
            console.log("🚀 CoolBits.ai Offline AI Board Starting...");
            console.log(`Server running on http://localhost:${this.port}`);
            console.log(`AI Board: http://localhost:${this.port}/ai-board`);
            console.log(`Roles: ${this.countTotalRoles()}`);
            console.log(`Panels: ${Object.keys(this.panels).length}`);
            console.log(`Bits: ${Object.keys(this.bitsFramework).length}`);
            console.log(`Started at: ${new Date().toLocaleTimeString()}`);
            console.log("Press Ctrl+C to stop the server");
            console.log("=" * 60);
        });
    }
}

// Start the AI Board
const aiBoard = new CoolBitsAIBoard(8082);
aiBoard.start();
