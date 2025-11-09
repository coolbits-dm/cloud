#!/usr/bin/env python3
"""
🤖 CoolBits.ai Agent Pages Generator
Generate individual pages for all 20 business roles

Author: oCopilot (oCursor)
Date: September 6, 2025
"""

import os
import json
from typing import Dict

# Agent definitions
agents = {
    "ceo": {
        "name": "CEO Agent",
        "role": "Chief Executive Officer",
        "api_provider": "openai",
        "api_key_secret": "ogpt01",
        "rag_access": ["b-rag", "a-rag"],
        "description": "Strategic leadership and business development",
    },
    "cto": {
        "name": "CTO Agent",
        "role": "Chief Technology Officer",
        "api_provider": "openai",
        "api_key_secret": "ogpt02",
        "rag_access": ["d-rag", "b-rag"],
        "description": "Technical architecture and development",
    },
    "cmo": {
        "name": "CMO Agent",
        "role": "Chief Marketing Officer",
        "api_provider": "openai",
        "api_key_secret": "ogpt03",
        "rag_access": ["b-rag", "a-rag"],
        "description": "Marketing strategy and brand management",
    },
    "cfo": {
        "name": "CFO Agent",
        "role": "Chief Financial Officer",
        "api_provider": "openai",
        "api_key_secret": "ogpt04",
        "rag_access": ["b-rag"],
        "description": "Financial planning and analysis",
    },
    "coo": {
        "name": "COO Agent",
        "role": "Chief Operating Officer",
        "api_provider": "openai",
        "api_key_secret": "ogpt05",
        "rag_access": ["b-rag", "a-rag"],
        "description": "Operations and process optimization",
    },
    "vp_engineering": {
        "name": "VP Engineering Agent",
        "role": "VP of Engineering",
        "api_provider": "openai",
        "api_key_secret": "ogpt06",
        "rag_access": ["d-rag"],
        "description": "Engineering team leadership and technical direction",
    },
    "vp_sales": {
        "name": "VP Sales Agent",
        "role": "VP of Sales",
        "api_provider": "openai",
        "api_key_secret": "ogpt07",
        "rag_access": ["b-rag", "a-rag"],
        "description": "Sales strategy and client acquisition",
    },
    "vp_product": {
        "name": "VP Product Agent",
        "role": "VP of Product",
        "api_provider": "openai",
        "api_key_secret": "ogpt08",
        "rag_access": ["b-rag", "d-rag"],
        "description": "Product strategy and roadmap",
    },
    "head_ai": {
        "name": "Head of AI Agent",
        "role": "Head of AI",
        "api_provider": "openai",
        "api_key_secret": "ogpt09",
        "rag_access": ["d-rag", "b-rag"],
        "description": "AI strategy and implementation",
    },
    "head_data": {
        "name": "Head of Data Agent",
        "role": "Head of Data",
        "api_provider": "openai",
        "api_key_secret": "ogpt10",
        "rag_access": ["d-rag"],
        "description": "Data strategy and analytics",
    },
    "head_security": {
        "name": "Head of Security Agent",
        "role": "Head of Security",
        "api_provider": "openai",
        "api_key_secret": "ogpt11",
        "rag_access": ["d-rag", "b-rag"],
        "description": "Cybersecurity and compliance",
    },
    "head_hr": {
        "name": "Head of HR Agent",
        "role": "Head of Human Resources",
        "api_provider": "openai",
        "api_key_secret": "ogpt12",
        "rag_access": ["b-rag", "a-rag"],
        "description": "Human resources and talent management",
    },
    "research_director": {
        "name": "Research Director Agent",
        "role": "Research Director",
        "api_provider": "openai",
        "api_key_secret": "ogpt13",
        "rag_access": ["d-rag", "b-rag"],
        "description": "Research and development leadership",
    },
    "security_lead": {
        "name": "Security Lead Agent",
        "role": "Security Lead",
        "api_provider": "openai",
        "api_key_secret": "ogpt14",
        "rag_access": ["d-rag"],
        "description": "Security implementation and monitoring",
    },
    "finance_manager": {
        "name": "Finance Manager Agent",
        "role": "Finance Manager",
        "api_provider": "openai",
        "api_key_secret": "ogpt15",
        "rag_access": ["b-rag"],
        "description": "Financial operations and reporting",
    },
    "operations_manager": {
        "name": "Operations Manager Agent",
        "role": "Operations Manager",
        "api_provider": "openai",
        "api_key_secret": "ogpt16",
        "rag_access": ["b-rag", "a-rag"],
        "description": "Operational efficiency and process management",
    },
    "marketing_specialist": {
        "name": "Marketing Specialist Agent",
        "role": "Marketing Specialist",
        "api_provider": "openai",
        "api_key_secret": "ogpt17",
        "rag_access": ["b-rag", "a-rag"],
        "description": "Marketing campaigns and content creation",
    },
    "sales_specialist": {
        "name": "Sales Specialist Agent",
        "role": "Sales Specialist",
        "api_provider": "openai",
        "api_key_secret": "ogpt18",
        "rag_access": ["b-rag", "a-rag"],
        "description": "Sales execution and client relations",
    },
    "hr_specialist": {
        "name": "HR Specialist Agent",
        "role": "HR Specialist",
        "api_provider": "openai",
        "api_key_secret": "ogpt19",
        "rag_access": ["b-rag", "a-rag"],
        "description": "Human resources operations and support",
    },
    "product_specialist": {
        "name": "Product Specialist Agent",
        "role": "Product Specialist",
        "api_provider": "openai",
        "api_key_secret": "ogpt20",
        "rag_access": ["b-rag", "d-rag"],
        "description": "Product development and feature management",
    },
}


def generate_agent_page(agent_id: str, agent_data: Dict) -> str:
    """Generate individual agent page HTML"""

    # Read template
    with open("agent_page_template.html", "r", encoding="utf-8") as f:
        template = f.read()

    # Replace placeholders
    html_content = template.replace("{{agent_id}}", agent_id)
    html_content = html_content.replace("{{agent_name}}", agent_data["name"])
    html_content = html_content.replace("{{agent_role}}", agent_data["role"])
    html_content = html_content.replace("{{api_provider}}", agent_data["api_provider"])

    return html_content


def create_agent_index_page() -> str:
    """Create index page with links to all agents"""

    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CoolBits.ai Agent Portal - All Agents</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }

        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            text-align: center;
        }

        .header h1 {
            color: #2c3e50;
            font-size: 2.5rem;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .agents-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .agent-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
        }

        .agent-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        }

        .agent-name {
            font-size: 1.3rem;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 8px;
        }

        .agent-role {
            font-size: 1rem;
            color: #7f8c8d;
            margin-bottom: 12px;
        }

        .agent-description {
            font-size: 0.9rem;
            color: #34495e;
            margin-bottom: 15px;
            line-height: 1.4;
        }

        .agent-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.8rem;
            color: #95a5a6;
        }

        .rag-access {
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
        }

        .rag-tag {
            background: #3498db;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.7rem;
        }

        .footer {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }

        .footer a {
            color: #667eea;
            text-decoration: none;
            margin: 0 15px;
            font-weight: bold;
        }

        .footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 CoolBits.ai Agent Portal</h1>
            <p>Access individual pages for all 20 business roles</p>
        </div>

        <div class="agents-grid">"""

    for agent_id, agent_data in agents.items():
        html_content += f"""
            <div class="agent-card" onclick="openAgentPage('{agent_id}')">
                <div class="agent-name">{agent_data["name"]}</div>
                <div class="agent-role">{agent_data["role"]}</div>
                <div class="agent-description">{agent_data["description"]}</div>
                <div class="agent-meta">
                    <span>Provider: {agent_data["api_provider"].upper()}</span>
                    <div class="rag-access">
                        {"".join([f'<span class="rag-tag">{rag}</span>' for rag in agent_data["rag_access"]])}
                    </div>
                </div>
            </div>"""

    html_content += """
        </div>

        <div class="footer">
            <a href="http://localhost:8090/">🏠 Multi-Agent Chat</a>
            <a href="http://localhost:8097/">📚 RAG System</a>
            <a href="http://localhost:8098/">⚙️ Admin Panel</a>
            <a href="http://localhost:8100/">🔧 Services</a>
        </div>
    </div>

    <script>
        function openAgentPage(agentId) {
            window.open(`http://localhost:8099/agent/${agentId}`, '_blank');
        }
    </script>
</body>
</html>"""

    return html_content


def main():
    """Generate all agent pages"""
    print("🤖 Generating CoolBits.ai Individual Agent Pages...")

    # Create agents directory
    os.makedirs("agents", exist_ok=True)

    # Generate individual pages
    for agent_id, agent_data in agents.items():
        print(f"📄 Generating page for {agent_data['name']}...")

        html_content = generate_agent_page(agent_id, agent_data)

        # Save individual page
        with open(f"agents/{agent_id}.html", "w", encoding="utf-8") as f:
            f.write(html_content)

    # Generate index page
    print("📋 Generating index page...")
    index_html = create_agent_index_page()

    with open("agents/index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    # Generate agent list JSON
    print("📊 Generating agent list JSON...")
    agent_list = {"total_agents": len(agents), "agents": agents}

    with open("agents/agents.json", "w", encoding="utf-8") as f:
        json.dump(agent_list, f, indent=2)

    print(f"✅ Generated {len(agents)} individual agent pages!")
    print("📁 Files created:")
    print("  • agents/index.html - Main index page")
    print("  • agents/agents.json - Agent definitions")
    for agent_id in agents.keys():
        print(f"  • agents/{agent_id}.html - {agents[agent_id]['name']} page")

    print("\n🌐 Access points:")
    print("  • Index: http://localhost:8099/agents/index.html")
    print("  • Individual pages: http://localhost:8099/agent/{agent_id}")
    print("  • API: http://localhost:8099/")


if __name__ == "__main__":
    main()
