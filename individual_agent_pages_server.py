#!/usr/bin/env python3
"""
🤖 CoolBits.ai Individual Agent Pages Server
Backend API for individual agent pages with chat, training, and self-learning

Author: oCopilot (oCursor)
Date: September 6, 2025
"""

import logging
import sqlite3
from typing import Dict, List, Any
from datetime import datetime
import uuid
import requests

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configuration
class AgentPageConfig(BaseModel):
    base_port: int = 8099
    max_tokens_per_cycle: int = 1000
    max_learning_cycles: int = 20
    rag_api_url: str = "http://localhost:8098"

    # Agent definitions with their roles and RAG access
    agents: Dict[str, Dict[str, Any]] = {
        "ceo": {
            "name": "CEO Agent",
            "role": "Chief Executive Officer",
            "api_provider": "openai",
            "api_key_secret": "ogpt01",
            "rag_access": ["ceo-rag"],
            "description": "Strategic leadership and business development",
        },
        "cto": {
            "name": "CTO Agent",
            "role": "Chief Technology Officer",
            "api_provider": "openai",
            "api_key_secret": "ogpt02",
            "rag_access": ["cto-rag"],
            "description": "Technical architecture and development",
        },
        "cmo": {
            "name": "CMO Agent",
            "role": "Chief Marketing Officer",
            "api_provider": "openai",
            "api_key_secret": "ogpt03",
            "rag_access": ["cmo-rag"],
            "description": "Marketing strategy and brand management",
        },
        "cfo": {
            "name": "CFO Agent",
            "role": "Chief Financial Officer",
            "api_provider": "openai",
            "api_key_secret": "ogpt04",
            "rag_access": ["cfo-rag"],
            "description": "Financial planning and analysis",
        },
        "coo": {
            "name": "COO Agent",
            "role": "Chief Operating Officer",
            "api_provider": "openai",
            "api_key_secret": "ogpt05",
            "rag_access": ["coo-rag"],
            "description": "Operations and process optimization",
        },
        "vp_engineering": {
            "name": "VP Engineering Agent",
            "role": "VP of Engineering",
            "api_provider": "openai",
            "api_key_secret": "ogpt06",
            "rag_access": ["vp_engineering-rag"],
            "description": "Engineering team leadership and technical direction",
        },
        "vp_sales": {
            "name": "VP Sales Agent",
            "role": "VP of Sales",
            "api_provider": "openai",
            "api_key_secret": "ogpt07",
            "rag_access": ["vp_sales-rag"],
            "description": "Sales strategy and client acquisition",
        },
        "vp_product": {
            "name": "VP Product Agent",
            "role": "VP of Product",
            "api_provider": "openai",
            "api_key_secret": "ogpt08",
            "rag_access": ["vp_product-rag"],
            "description": "Product strategy and roadmap",
        },
        "head_ai": {
            "name": "Head of AI Agent",
            "role": "Head of AI",
            "api_provider": "openai",
            "api_key_secret": "ogpt09",
            "rag_access": ["head_ai-rag"],
            "description": "AI strategy and implementation",
        },
        "head_data": {
            "name": "Head of Data Agent",
            "role": "Head of Data",
            "api_provider": "openai",
            "api_key_secret": "ogpt10",
            "rag_access": ["head_data-rag"],
            "description": "Data strategy and analytics",
        },
        "head_security": {
            "name": "Head of Security Agent",
            "role": "Head of Security",
            "api_provider": "openai",
            "api_key_secret": "ogpt11",
            "rag_access": ["head_security-rag"],
            "description": "Cybersecurity and compliance",
        },
        "head_hr": {
            "name": "Head of HR Agent",
            "role": "Head of Human Resources",
            "api_provider": "openai",
            "api_key_secret": "ogpt12",
            "rag_access": ["head_hr-rag"],
            "description": "Human resources and talent management",
        },
        "research_director": {
            "name": "Research Director Agent",
            "role": "Research Director",
            "api_provider": "openai",
            "api_key_secret": "ogpt13",
            "rag_access": ["research_director-rag"],
            "description": "Research and development leadership",
        },
        "security_lead": {
            "name": "Security Lead Agent",
            "role": "Security Lead",
            "api_provider": "openai",
            "api_key_secret": "ogpt14",
            "rag_access": ["security_lead-rag"],
            "description": "Security implementation and monitoring",
        },
        "finance_manager": {
            "name": "Finance Manager Agent",
            "role": "Finance Manager",
            "api_provider": "openai",
            "api_key_secret": "ogpt15",
            "rag_access": ["finance_manager-rag"],
            "description": "Financial operations and reporting",
        },
        "operations_manager": {
            "name": "Operations Manager Agent",
            "role": "Operations Manager",
            "api_provider": "openai",
            "api_key_secret": "ogpt16",
            "rag_access": ["operations_manager-rag"],
            "description": "Operational efficiency and process management",
        },
        "marketing_specialist": {
            "name": "Marketing Specialist Agent",
            "role": "Marketing Specialist",
            "api_provider": "openai",
            "api_key_secret": "ogpt17",
            "rag_access": ["marketing_specialist-rag"],
            "description": "Marketing campaigns and content creation",
        },
        "sales_specialist": {
            "name": "Sales Specialist Agent",
            "role": "Sales Specialist",
            "api_provider": "openai",
            "api_key_secret": "ogpt18",
            "rag_access": ["sales_specialist-rag"],
            "description": "Sales execution and client relations",
        },
        "hr_specialist": {
            "name": "HR Specialist Agent",
            "role": "HR Specialist",
            "api_provider": "openai",
            "api_key_secret": "ogpt19",
            "rag_access": ["hr_specialist-rag"],
            "description": "Human resources operations and support",
        },
        "product_specialist": {
            "name": "Product Specialist Agent",
            "role": "Product Specialist",
            "api_provider": "openai",
            "api_key_secret": "ogpt20",
            "rag_access": ["product_specialist-rag"],
            "description": "Product development and feature management",
        },
    }


# Initialize FastAPI app
app = FastAPI(title="CoolBits.ai Individual Agent Pages")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from agents directory
app.mount("/agents", StaticFiles(directory="agents"), name="agents")

# Global variables
config = AgentPageConfig()
agents = config.agents
chat_sessions = {}
agent_status = {}
training_sessions = {}


# Initialize database
def init_database():
    """Initialize SQLite database for chat sessions and training data"""
    conn = sqlite3.connect("agent_pages.db")
    cursor = conn.cursor()

    # Chat sessions table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            user_message TEXT NOT NULL,
            agent_response TEXT NOT NULL,
            tokens_used INTEGER DEFAULT 0,
            timestamp TEXT NOT NULL,
            context TEXT DEFAULT 'individual_chat'
        )
    """
    )

    # Training sessions table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS training_sessions (
            id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            session_type TEXT NOT NULL,
            cycles_completed INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            knowledge_saved TEXT DEFAULT '',
            timestamp TEXT NOT NULL,
            status TEXT DEFAULT 'active'
        )
    """
    )

    # Agent status table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS agent_status (
            agent_id TEXT PRIMARY KEY,
            status TEXT DEFAULT 'online',
            token_usage INTEGER DEFAULT 0,
            token_limit INTEGER DEFAULT 1000,
            training_sessions INTEGER DEFAULT 0,
            last_activity TEXT NOT NULL,
            api_provider TEXT NOT NULL
        )
    """
    )

    conn.commit()
    conn.close()
    logger.info("✅ Database initialized")


# Initialize agent status
def init_agent_status():
    """Initialize agent status in database"""
    conn = sqlite3.connect("agent_pages.db")
    cursor = conn.cursor()

    for agent_id, agent_data in agents.items():
        cursor.execute(
            """
            INSERT OR REPLACE INTO agent_status 
            (agent_id, status, token_usage, token_limit, training_sessions, last_activity, api_provider)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                agent_id,
                "online",
                0,
                1000,
                0,
                datetime.now().isoformat(),
                agent_data["api_provider"],
            ),
        )

    conn.commit()
    conn.close()
    logger.info("✅ Agent status initialized")


# Load agent status from database
def load_agent_status():
    """Load agent status from database"""
    conn = sqlite3.connect("agent_pages.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM agent_status")
    rows = cursor.fetchall()

    for row in rows:
        agent_status[row[0]] = {
            "status": row[1],
            "token_usage": row[2],
            "token_limit": row[3],
            "training_sessions": row[4],
            "last_activity": row[5],
            "api_provider": row[6],
        }

    conn.close()
    logger.info(f"✅ Loaded status for {len(agent_status)} agents")


# Get API key from Google Cloud Secrets Manager
async def get_api_key(secret_name: str) -> str:
    """Get API key from Google Cloud Secrets Manager"""
    try:
        import subprocess

        result = subprocess.run(
            [
                "gcloud",
                "secrets",
                "versions",
                "access",
                "latest",
                "--secret",
                secret_name,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception as e:
        logger.error(f"Error getting API key {secret_name}: {e}")
        return ""


# Make API call to OpenAI or xAI (with mock fallback)
async def make_api_call(
    agent_id: str, message: str, context: str = ""
) -> Dict[str, Any]:
    """Make API call to OpenAI or xAI with mock fallback"""
    agent_data = agents.get(agent_id)
    if not agent_data:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

    # For now, use mock responses for testing
    # TODO: Implement real API calls when API keys are properly configured

    mock_responses = {
        "ceo": f"As CEO of CoolBits.ai, I focus on strategic leadership and business development. Regarding your question: '{message}', I would approach this from a high-level strategic perspective, considering market opportunities, team capabilities, and long-term vision for our AI ecosystem.",
        "cto": f"As CTO of CoolBits.ai, I handle technical architecture and development. Your question about '{message}' requires careful technical analysis. I would evaluate the technical feasibility, scalability implications, and integration requirements for our current systems.",
        "cmo": f"As CMO of CoolBits.ai, I manage marketing strategy and brand management. Regarding '{message}', I would focus on market positioning, brand messaging, and customer engagement strategies that align with our AI ecosystem vision.",
        "cfo": f"As CFO of CoolBits.ai, I oversee financial planning and analysis. Your question about '{message}' needs to be evaluated from a financial perspective, considering ROI, budget implications, and financial sustainability.",
        "coo": f"As COO of CoolBits.ai, I handle operations and process optimization. Regarding '{message}', I would focus on operational efficiency, process improvement, and ensuring smooth execution of our business strategies.",
    }

    # Get mock response or default
    response_text = mock_responses.get(
        agent_id,
        f"As {agent_data['name']}, {agent_data['role']} at CoolBits.ai, I would address your question about '{message}' from my perspective of {agent_data['description'].lower()}.",
    )

    # Estimate tokens (rough approximation)
    estimated_tokens = len(response_text.split()) * 1.3

    return {
        "response": response_text,
        "tokens_used": int(estimated_tokens),
        "model": f"mock-{agent_data['api_provider']}",
    }


# Search online for self-training
async def search_online(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Search online for self-training (enhanced mock implementation)"""
    # Enhanced mock results with more realistic content
    mock_results = [
        {
            "title": f"Best Practices for {query} in 2024",
            "content": f"Comprehensive guide covering the latest trends and methodologies in {query}. Industry experts share insights on implementation strategies, common pitfalls to avoid, and emerging technologies that are reshaping the landscape.",
            "url": f"https://industry-insights.com/{query.replace(' ', '-')}-best-practices-2024",
            "relevance": 0.95,
        },
        {
            "title": f"{query}: Strategic Implementation Guide",
            "content": f"Step-by-step framework for implementing {query} in modern organizations. Covers planning, execution, measurement, and optimization phases with real-world case studies and ROI analysis.",
            "url": f"https://strategic-guides.com/{query.replace(' ', '-')}-implementation",
            "relevance": 0.90,
        },
        {
            "title": f"Advanced {query} Techniques and Tools",
            "content": f"Deep dive into advanced techniques for {query}. Explores cutting-edge tools, automation opportunities, and integration with AI/ML technologies for enhanced performance and efficiency.",
            "url": f"https://tech-advances.com/advanced-{query.replace(' ', '-')}-techniques",
            "relevance": 0.85,
        },
        {
            "title": f"{query} Market Analysis and Future Trends",
            "content": f"Market research and trend analysis for {query}. Includes competitive landscape, growth projections, emerging opportunities, and strategic recommendations for businesses.",
            "url": f"https://market-research.com/{query.replace(' ', '-')}-trends-analysis",
            "relevance": 0.80,
        },
        {
            "title": f"Case Studies: Successful {query} Implementations",
            "content": f"Real-world case studies showcasing successful {query} implementations across different industries. Learn from both successes and failures with actionable insights.",
            "url": f"https://case-studies.com/successful-{query.replace(' ', '-')}-implementations",
            "relevance": 0.75,
        },
    ]

    return mock_results[:limit]


# Enhanced self-learning cycle with online research
async def perform_self_learning_cycle(
    agent_id: str, topic: str, cycle_number: int, total_cycles: int
) -> Dict[str, Any]:
    """Perform a single self-learning cycle with online research"""
    try:
        agent_data = config.agents[agent_id]

        # Step 1: Generate research question for this cycle
        research_prompt = f"""
        You are {agent_data["name"]}, a {agent_data["role"]} at CoolBits.ai.
        
        Learning Topic: {topic}
        Current Cycle: {cycle_number} of {total_cycles}
        
        Based on your role and the learning topic, generate ONE specific, focused research question for this cycle.
        The question should be:
        - Directly relevant to your role as {agent_data["role"]}
        - Specific and actionable
        - Different from what might be covered in other cycles
        - Focused on practical application at CoolBits.ai
        
        Generate only the research question, nothing else.
        """

        # Get research question (mock implementation)
        research_question = f"How can {topic} be effectively implemented in {agent_data['role']} responsibilities at CoolBits.ai?"

        # Step 2: Search online for information
        search_results = await search_online(research_question, limit=3)

        # Step 3: Analyze and synthesize the information
        analysis_prompt = f"""
        You are {agent_data["name"]}, a {agent_data["role"]} at CoolBits.ai.
        
        Research Question: {research_question}
        Learning Topic: {topic}
        Cycle: {cycle_number} of {total_cycles}
        
        Based on the following search results, provide a comprehensive analysis:
        
        Search Results:
        {chr(10).join([f"Title: {result['title']}{chr(10)}Content: {result['content']}{chr(10)}" for result in search_results])}
        
        Your analysis should include:
        1. Key insights relevant to your role
        2. How this applies specifically to CoolBits.ai
        3. Actionable recommendations
        4. Implementation strategies
        5. Potential challenges and solutions
        
        Provide a structured, professional response that demonstrates deep understanding.
        """

        # Generate analysis (mock implementation)
        analysis = f"""
        **Key Insights for {agent_data["role"]}:**
        Based on the research about {topic}, several critical insights emerge that are directly applicable to my role at CoolBits.ai.
        
        **Application to CoolBits.ai:**
        The research findings suggest that implementing {topic} in our organization would require a strategic approach that aligns with our AI-focused mission.
        
        **Actionable Recommendations:**
        1. Develop a phased implementation plan for {topic}
        2. Integrate with existing CoolBits.ai infrastructure
        3. Establish metrics for measuring success
        
        **Implementation Strategy:**
        The implementation should follow industry best practices while being tailored to our specific needs and capabilities.
        
        **Challenges and Solutions:**
        Potential challenges include resource allocation and change management. Solutions involve stakeholder engagement and gradual rollout.
        """

        # Step 4: Generate next cycle's focus (if not the last cycle)
        next_focus = ""
        if cycle_number < total_cycles:
            next_focus = f"Next cycle should focus on: Advanced implementation strategies for {topic}"

        return {
            "cycle": cycle_number,
            "research_question": research_question,
            "search_results": search_results,
            "analysis": analysis,
            "next_focus": next_focus,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
        }

    except Exception as e:
        logger.error(
            f"Error in self-learning cycle {cycle_number} for {agent_id}: {str(e)}"
        )
        return {
            "cycle": cycle_number,
            "error": str(e),
            "status": "failed",
            "timestamp": datetime.now().isoformat(),
        }


# Generate questions for self-training
async def generate_questions(
    topic: str, context: str, agent_role: str, limit: int = 3
) -> List[str]:
    """Generate questions for self-training"""
    try:
        # Use a simple agent to generate questions
        questions_prompt = f"""
        As an AI training specialist, generate {limit} specific questions about "{topic}" 
        that would be relevant for someone in the role of "{agent_role}".
        
        Context: {context[:500]}...
        
        Generate questions that are:
        1. Specific to the topic
        2. Relevant to the role
        3. Thought-provoking
        4. Practical
        
        Return only the questions, one per line.
        """

        # Use CEO agent for question generation (has access to business context)
        response = await make_api_call("ceo", questions_prompt, context)
        questions = [q.strip() for q in response["response"].split("\n") if q.strip()]

        return questions[:limit]

    except Exception as e:
        logger.error(f"Error generating questions: {e}")
        return [
            f"What is {topic}?",
            f"How does {topic} relate to {agent_role}?",
            f"What are best practices for {topic}?",
        ]


# Answer question for self-training
async def answer_question(
    question: str, context: str, agent_id: str, agent_role: str
) -> str:
    """Answer a question for self-training"""
    try:
        answer_prompt = f"""
        As {agents[agent_id]["name"]}, {agent_role} at CoolBits.ai, please answer this question:
        
        Question: {question}
        
        Context: {context[:500]}...
        
        Provide a comprehensive, professional answer that reflects your role and expertise.
        """

        response = await make_api_call(agent_id, answer_prompt, context)
        return response["response"]

    except Exception as e:
        logger.error(f"Error answering question: {e}")
        return f"I apologize, but I encountered an error while answering: {question}"


# Save knowledge to RAG
async def save_knowledge_to_rag(filename: str, content: str, agent_id: str) -> bool:
    """Save knowledge to RAG system using agent-specific categories"""
    try:
        agent_data = config.agents[agent_id]

        # Use agent-specific RAG category
        rag_category = agent_data["rag_access"][
            0
        ]  # Get the agent's dedicated RAG category
        subcategory = "self_learning"  # Dedicated subcategory for self-learning
        item = "knowledge_base"  # Item for knowledge base

        # Save to RAG system
        rag_data = {
            "filename": filename,
            "content": content,
            "category": rag_category,
            "subcategory": subcategory,
            "item": item,
            "source": f"self_training:{agent_id}",
        }

        response = requests.post(
            f"{config.rag_api_url}/api/documents/create", json=rag_data, timeout=10
        )

        return response.status_code == 200

    except Exception as e:
        logger.error(f"Error saving to RAG: {e}")
        return False


# Initialize database and load data
init_database()
init_agent_status()
load_agent_status()

# API Endpoints


@app.get("/")
async def root():
    """Root endpoint - redirect to agents index"""
    return FileResponse("agents/index.html")


@app.get("/agent/{agent_id}")
async def get_agent_page(agent_id: str):
    """Serve individual agent page"""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

    agent_data = agents[agent_id]

    # Read template and replace placeholders
    with open("agent_page_template.html", "r", encoding="utf-8") as f:
        template = f.read()

    # Replace placeholders
    html_content = template.replace("{{agent_id}}", agent_id)
    html_content = html_content.replace("{{agent_name}}", agent_data["name"])
    html_content = html_content.replace("{{agent_role}}", agent_data["role"])
    html_content = html_content.replace("{{api_provider}}", agent_data["api_provider"])

    return HTMLResponse(content=html_content)


@app.get("/api/agent/{agent_id}/status")
async def get_agent_status(agent_id: str):
    """Get agent status"""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

    status = agent_status.get(
        agent_id,
        {
            "status": "online",
            "token_usage": 0,
            "token_limit": 1000,
            "training_sessions": 0,
            "last_activity": datetime.now().isoformat(),
            "api_provider": agents[agent_id]["api_provider"],
        },
    )

    return status


@app.get("/api/rag-access")
async def get_rag_access():
    """Get RAG access information"""
    try:
        response = requests.get(f"{config.rag_api_url}/api/categories", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"categories": [], "total_categories": 0}
    except Exception as e:
        logger.error(f"Error getting RAG access: {e}")
        return {"categories": [], "total_categories": 0}


@app.get("/api/chat/{agent_id}/history")
async def get_chat_history(agent_id: str):
    """Get chat history for agent"""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

    conn = sqlite3.connect("agent_pages.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT user_message, agent_response, tokens_used, timestamp
        FROM chat_sessions 
        WHERE agent_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 50
    """,
        (agent_id,),
    )

    rows = cursor.fetchall()
    conn.close()

    messages = []
    for row in rows:
        messages.append({"type": "user", "content": row[0], "timestamp": row[3]})
        messages.append({"type": "agent", "content": row[1], "timestamp": row[3]})

    return {"messages": messages}


@app.post("/api/chat/{agent_id}/send")
async def send_chat_message(agent_id: str, request: Request):
    """Send chat message to agent"""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

    data = await request.json()
    message = data.get("message", "")
    context = data.get("context", "")

    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    try:
        # Make API call
        response = await make_api_call(agent_id, message, context)

        # Save to database
        conn = sqlite3.connect("agent_pages.db")
        cursor = conn.cursor()

        session_id = str(uuid.uuid4())
        cursor.execute(
            """
            INSERT INTO chat_sessions 
            (id, agent_id, user_message, agent_response, tokens_used, timestamp, context)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                session_id,
                agent_id,
                message,
                response["response"],
                response["tokens_used"],
                datetime.now().isoformat(),
                context,
            ),
        )

        # Update agent status
        cursor.execute(
            """
            UPDATE agent_status 
            SET token_usage = token_usage + ?, last_activity = ?
            WHERE agent_id = ?
        """,
            (response["tokens_used"], datetime.now().isoformat(), agent_id),
        )

        conn.commit()
        conn.close()

        # Update in-memory status
        if agent_id in agent_status:
            agent_status[agent_id]["token_usage"] += response["tokens_used"]
            agent_status[agent_id]["last_activity"] = datetime.now().isoformat()

        return {
            "response": response["response"],
            "tokens_used": response["tokens_used"],
            "model": response["model"],
        }

    except Exception as e:
        logger.error(f"Error in chat with {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/search")
async def search_online_endpoint(request: Request):
    """Search online for self-training"""
    data = await request.json()
    query = data.get("query", "")
    limit = data.get("limit", 5)

    if not query:
        raise HTTPException(status_code=400, detail="Query is required")

    try:
        results = await search_online(query, limit)
        return {"results": results}
    except Exception as e:
        logger.error(f"Error searching online: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-questions")
async def generate_questions_endpoint(request: Request):
    """Generate questions for self-training"""
    data = await request.json()
    topic = data.get("topic", "")
    context = data.get("context", "")
    agent_role = data.get("agent_role", "")
    limit = data.get("limit", 3)

    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")

    try:
        questions = await generate_questions(topic, context, agent_role, limit)
        return {"questions": questions}
    except Exception as e:
        logger.error(f"Error generating questions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/answer-question")
async def answer_question_endpoint(request: Request):
    """Answer question for self-training"""
    data = await request.json()
    question = data.get("question", "")
    context = data.get("context", "")
    agent_id = data.get("agent_id", "")
    agent_role = data.get("agent_role", "")

    if not question or not agent_id:
        raise HTTPException(
            status_code=400, detail="Question and agent_id are required"
        )

    try:
        answer = await answer_question(question, context, agent_id, agent_role)
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/rag/documents/create")
async def create_rag_document(request: Request):
    """Create document in RAG system"""
    data = await request.json()

    try:
        response = requests.post(
            f"{config.rag_api_url}/api/documents/create", json=data, timeout=10
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code, detail="RAG system error"
            )

    except Exception as e:
        logger.error(f"Error creating RAG document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("🤖 Starting CoolBits.ai Individual Agent Pages Server")
    print("📚 Serving individual agent pages with chat, training, and self-learning")
    print("🌐 Available at: http://localhost:8099")
    print(f"👥 Total agents: {len(agents)}")

    uvicorn.run(app, host="0.0.0.0", port=8099)
