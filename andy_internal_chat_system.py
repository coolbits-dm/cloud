#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Andy Internal Chat System
SC COOL BITS SRL - Internal chat system with RAG and Vertex AI compatibility
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid

# Import our internal systems
from andy_core_engine import process_andy_request


class AndyChatMessage:
    """Individual chat message structure"""

    def __init__(
        self,
        sender: str,
        content: str,
        message_type: str = "text",
        metadata: Optional[Dict] = None,
    ):
        self.id = str(uuid.uuid4())
        self.sender = sender
        self.content = content
        self.message_type = message_type
        self.timestamp = datetime.now()
        self.metadata = metadata or {}
        self.processed = False
        self.response_id = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "id": self.id,
            "sender": self.sender,
            "content": self.content,
            "message_type": self.message_type,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "processed": self.processed,
            "response_id": self.response_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AndyChatMessage":
        """Create message from dictionary"""
        message = cls(
            sender=data["sender"],
            content=data["content"],
            message_type=data.get("message_type", "text"),
            metadata=data.get("metadata", {}),
        )
        message.id = data["id"]
        message.timestamp = datetime.fromisoformat(data["timestamp"])
        message.processed = data.get("processed", False)
        message.response_id = data.get("response_id")
        return message


class AndyChatSession:
    """Chat session management"""

    def __init__(self, session_id: str = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.start_time = datetime.now()
        self.messages: List[AndyChatMessage] = []
        self.context: Dict[str, Any] = {}
        self.active = True
        self.last_activity = datetime.now()

    def add_message(self, message: AndyChatMessage) -> None:
        """Add message to session"""
        self.messages.append(message)
        self.last_activity = datetime.now()

    def get_messages(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get messages from session"""
        messages = self.messages[-limit:] if limit else self.messages
        return [msg.to_dict() for msg in messages]

    def get_context(self) -> Dict[str, Any]:
        """Get session context"""
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "message_count": len(self.messages),
            "active": self.active,
            "context": self.context,
        }

    def update_context(self, key: str, value: Any) -> None:
        """Update session context"""
        self.context[key] = value
        self.last_activity = datetime.now()


class AndyRAGService:
    """RAG Service for Andy's chat system"""

    def __init__(self):
        self.status = "active"
        self.knowledge_base = {
            "project_docs": {
                "coolbits_ai": "Main AI platform with multi-agent system",
                "cblm_ai": "Language model platform",
                "architecture": "4-pillar architecture: User, Business, Agency, Development",
                "ports": "8100-8106 range for all services",
                "hardware": "AMD Ryzen 7 2700X, NVIDIA RTX 2060, 32GB RAM",
            },
            "code_repositories": {
                "main_bridge": "Port 8100 - Main CoolBits Bridge",
                "multi_agent_chat": "Port 8101 - Multi-Agent Chat System",
                "enhanced_chat": "Port 8102 - Enhanced Multi-Agent Chat",
                "agent_portal": "Port 8103 - Individual Agent Portal",
                "cursor_root": "Port 8104 - Cursor AI Assistant Root Console",
                "complete_dashboard": "Port 8105 - Complete Dashboard",
                "google_cloud_agent": "Port 8106 - Google Cloud CLI Agent",
            },
            "system_configs": {
                "python_version": "3.x",
                "os": "Windows 11",
                "dependencies": ["FastAPI", "Uvicorn", "WebSocket", "psutil", "GPUtil"],
                "secrets_system": "Internal encrypted secrets management",
            },
        }

        # RAG processing capabilities
        self.capabilities = [
            "semantic_search",
            "code_analysis",
            "document_retrieval",
            "context_understanding",
            "real_time_updates",
        ]

    async def process_query(
        self, query: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process RAG query"""
        query_lower = query.lower()
        results = []

        # Search through knowledge base
        for category, items in self.knowledge_base.items():
            for key, value in items.items():
                if query_lower in str(value).lower() or query_lower in key.lower():
                    results.append(
                        {
                            "category": category,
                            "key": key,
                            "value": value,
                            "relevance": (
                                "high"
                                if query_lower in str(value).lower()
                                else "medium"
                            ),
                            "confidence": (
                                0.9 if query_lower in str(value).lower() else 0.7
                            ),
                        }
                    )

        # Generate response based on results
        if results:
            response = self._generate_response(query, results, context)
        else:
            response = self._generate_fallback_response(query, context)

        return {
            "query": query,
            "response": response,
            "results": results[:5],  # Top 5 results
            "total_found": len(results),
            "capabilities_used": self.capabilities,
            "timestamp": datetime.now().isoformat(),
        }

    def _generate_response(
        self, query: str, results: List[Dict], context: Dict[str, Any] = None
    ) -> str:
        """Generate response based on RAG results"""
        if not results:
            return "I don't have specific information about that topic in my knowledge base."

        # Sort by relevance and confidence
        results.sort(
            key=lambda x: (x["relevance"] == "high", x["confidence"]), reverse=True
        )

        top_result = results[0]

        if top_result["relevance"] == "high":
            return f"Based on my knowledge base, {top_result['value']}. This information is from the {top_result['category']} category."
        else:
            return f"I found some related information: {top_result['value']}. This is from the {top_result['category']} category."

    def _generate_fallback_response(
        self, query: str, context: Dict[str, Any] = None
    ) -> str:
        """Generate fallback response when no results found"""
        return f"I don't have specific information about '{query}' in my current knowledge base, but I can help you with CoolBits.ai project structure, system architecture, or any other questions about our ecosystem."

    def get_status(self) -> Dict[str, Any]:
        """Get RAG service status"""
        return {
            "status": self.status,
            "knowledge_categories": len(self.knowledge_base),
            "total_items": sum(len(items) for items in self.knowledge_base.values()),
            "capabilities": self.capabilities,
        }


class AndyChatSystem:
    """Main Andy Chat System"""

    def __init__(self):
        self.company = "SC COOL BITS SRL"
        self.ceo = "Andrei"
        self.ai_assistant = "Andy - Personal 1:1 Agent"
        self.contract_date = "2025-09-06"

        # System components
        self.rag_service = AndyRAGService()
        self.sessions: Dict[str, AndyChatSession] = {}
        self.active_sessions = 0

        # Chat processing pipeline
        self.processing_pipeline = [
            "message_validation",
            "context_analysis",
            "rag_processing",
            "response_generation",
            "context_update",
        ]

        # Vertex AI compatibility
        self.vertex_ai_compatible = True
        self.vertex_ai_endpoints = {
            "chat": "/api/chat",
            "rag": "/api/rag",
            "status": "/api/status",
            "sessions": "/api/sessions",
        }

    async def process_message(
        self, session_id: str, message: AndyChatMessage
    ) -> AndyChatMessage:
        """Process incoming message through chat system"""
        # Get or create session
        if session_id not in self.sessions:
            self.sessions[session_id] = AndyChatSession(session_id)
            self.active_sessions += 1

        session = self.sessions[session_id]

        # Add user message to session
        session.add_message(message)

        # Process through RAG service
        rag_result = await self.rag_service.process_query(
            message.content, session.context
        )

        # Generate Andy's response
        andy_response = await self._generate_andy_response(message, rag_result, session)

        # Add Andy's response to session
        session.add_message(andy_response)

        # Update session context
        session.update_context("last_query", message.content)
        session.update_context("last_response", andy_response.content)
        session.update_context("rag_results", rag_result["total_found"])

        return andy_response

    async def _generate_andy_response(
        self,
        user_message: AndyChatMessage,
        rag_result: Dict[str, Any],
        session: AndyChatSession,
    ) -> AndyChatMessage:
        """Generate Andy's response"""
        # Use core engine for processing
        request = {
            "type": "chat_message",
            "content": user_message.content,
            "session_id": session.session_id,
            "rag_results": rag_result,
        }

        core_result = await process_andy_request(request)

        # Generate response content
        if core_result["success"]:
            response_content = core_result["result"]["response"]
        else:
            response_content = "I'm processing your message. Let me get back to you with a proper response."

        # Add RAG context if available
        if rag_result["total_found"] > 0:
            response_content += f"\n\nI found {rag_result['total_found']} relevant pieces of information in my knowledge base."

        # Create Andy's response message
        andy_response = AndyChatMessage(
            sender="Andy",
            content=response_content,
            message_type="text",
            metadata={
                "rag_results": rag_result["total_found"],
                "core_engine": "processed",
                "session_id": session.session_id,
                "processing_time": datetime.now().isoformat(),
            },
        )

        # Link response to user message
        andy_response.response_id = user_message.id
        user_message.processed = True

        return andy_response

    def get_session(self, session_id: str) -> Optional[AndyChatSession]:
        """Get chat session by ID"""
        return self.sessions.get(session_id)

    def create_session(self, session_id: str = None) -> AndyChatSession:
        """Create new chat session"""
        session = AndyChatSession(session_id)
        self.sessions[session.session_id] = session
        self.active_sessions += 1
        return session

    def get_system_status(self) -> Dict[str, Any]:
        """Get chat system status"""
        return {
            "system": "Andy Internal Chat System",
            "status": "active",
            "active_sessions": self.active_sessions,
            "total_sessions": len(self.sessions),
            "rag_service": self.rag_service.get_status(),
            "processing_pipeline": self.processing_pipeline,
            "vertex_ai_compatible": self.vertex_ai_compatible,
            "vertex_ai_endpoints": self.vertex_ai_endpoints,
            "timestamp": datetime.now().isoformat(),
        }


# Initialize Andy Chat System
andy_chat_system = AndyChatSystem()


# Main functions
async def send_message_to_andy(
    session_id: str, message_content: str, sender: str = "User"
) -> Dict[str, Any]:
    """💬 Send message to Andy and get response"""
    message = AndyChatMessage(sender=sender, content=message_content)
    response = await andy_chat_system.process_message(session_id, message)

    return {
        "user_message": message.to_dict(),
        "andy_response": response.to_dict(),
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
    }


def create_chat_session(session_id: str = None) -> str:
    """💬 Create new chat session"""
    session = andy_chat_system.create_session(session_id)
    return session.session_id


def get_chat_session(session_id: str) -> Optional[Dict[str, Any]]:
    """💬 Get chat session data"""
    session = andy_chat_system.get_session(session_id)
    if session:
        return {
            "session": session.get_context(),
            "messages": session.get_messages(),
            "status": "active",
        }
    return None


def get_chat_system_status() -> Dict[str, Any]:
    """💬 Get chat system status"""
    return andy_chat_system.get_system_status()


def chat_system_status():
    """💬 Print chat system status"""
    status = get_chat_system_status()

    print("=" * 80)
    print("💬 ANDY INTERNAL CHAT SYSTEM STATUS")
    print("🏢 SC COOL BITS SRL - Internal Chat with RAG")
    print("=" * 80)
    print(f"👤 CEO: {andy_chat_system.ceo}")
    print(f"🤖 AI Assistant: {andy_chat_system.ai_assistant}")
    print(f"📅 Contract Date: {andy_chat_system.contract_date}")
    print("=" * 80)
    print(f"💬 Chat System Status: {status['status']}")
    print(f"📊 Active Sessions: {status['active_sessions']}")
    print(f"📈 Total Sessions: {status['total_sessions']}")
    print("=" * 80)
    print("🧠 RAG SERVICE:")
    rag_status = status["rag_service"]
    print(f"  • Status: {rag_status['status']}")
    print(f"  • Knowledge Categories: {rag_status['knowledge_categories']}")
    print(f"  • Total Items: {rag_status['total_items']}")
    print(f"  • Capabilities: {', '.join(rag_status['capabilities'])}")
    print("=" * 80)
    print("🔄 PROCESSING PIPELINE:")
    for step in status["processing_pipeline"]:
        print(f"  • {step.replace('_', ' ').title()}")
    print("=" * 80)
    print("🔌 VERTEX AI COMPATIBILITY:")
    print(f"  • Compatible: {'✅ Yes' if status['vertex_ai_compatible'] else '❌ No'}")
    print("  • Endpoints:")
    for endpoint, path in status["vertex_ai_endpoints"].items():
        print(f"    - {endpoint}: {path}")
    print("=" * 80)


if __name__ == "__main__":
    print("=" * 80)
    print("💬 ANDY INTERNAL CHAT SYSTEM")
    print("🏢 SC COOL BITS SRL - Internal Chat with RAG")
    print("=" * 80)
    print(f"👤 CEO: {andy_chat_system.ceo}")
    print(f"🤖 AI Assistant: {andy_chat_system.ai_assistant}")
    print(f"📅 Contract Date: {andy_chat_system.contract_date}")
    print("=" * 80)
    print("🚀 Available Commands:")
    print("  • send_message_to_andy(session_id, message) - Send message to Andy")
    print("  • create_chat_session(session_id) - Create new chat session")
    print("  • get_chat_session(session_id) - Get chat session data")
    print("  • get_chat_system_status() - Get system status")
    print("  • chat_system_status() - Print system status")
    print("=" * 80)
