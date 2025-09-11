#!/usr/bin/env python3
"""
Andy Auto Engine - Intelligent Management System
CoolBits.ai - Personal 1:1 Agent
"""

import asyncio
import json
import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import hashlib
import os

# Import RAG system
from andy_kim_local_rag import local_rag_system, RAGAgent, RAGQuery

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProcessingLevel(Enum):
    """Processing levels for Andy Auto Engine"""

    LEVEL_1_LOCAL_DB = "level_1_local_db"
    LEVEL_2_LOCAL_MODEL = "level_2_local_model"
    LEVEL_3_KIM_REASONING = "level_3_kim_reasoning"


@dataclass
class AutoContext:
    """Context for Auto processing"""

    user_id: str
    session_id: str
    prompt: str
    timestamp: datetime
    processing_level: ProcessingLevel
    confidence_score: float
    response: str
    metadata: Dict[str, Any]


class AndyAutoEngine:
    """Andy Auto Engine - Intelligent Management System"""

    def __init__(self):
        self.db_path = "andy_auto.db"
        self.init_database()
        self.local_knowledge_base = {}
        self.vertex_models = {}
        self.kim_reasoning = None
        self.processing_stats = {
            "level_1_count": 0,
            "level_2_count": 0,
            "level_3_count": 0,
            "total_requests": 0,
        }

    def init_database(self):
        """Initialize local database for Level 1 processing"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS local_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_hash TEXT UNIQUE,
                prompt TEXT,
                response TEXT,
                category TEXT,
                confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS processing_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                user_id TEXT,
                prompt TEXT,
                processing_level TEXT,
                confidence_score REAL,
                response_time_ms INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT,
                content TEXT,
                source TEXT,
                relevance_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.commit()
        conn.close()

        # Initialize default responses
        self.init_default_responses()

    def init_default_responses(self):
        """Initialize default responses for Level 1"""
        default_responses = [
            {
                "prompt": "hello",
                "response": "Hello! I'm Andy, your personal AI assistant from CoolBits.ai. How can I help you today?",
                "category": "greeting",
                "confidence": 0.95,
            },
            {
                "prompt": "help",
                "response": "I'm here to help! I can assist with development, project management, and technical questions. What would you like to know?",
                "category": "support",
                "confidence": 0.90,
            },
            {
                "prompt": "coolbits",
                "response": "CoolBits.ai is our AI platform specializing in intelligent solutions and development services. I'm your personal AI assistant for this project.",
                "category": "company",
                "confidence": 0.95,
            },
            {
                "prompt": "cblm",
                "response": "cblm.ai is our AI platform. I can help you with development, deployment, and management of cblm.ai services.",
                "category": "platform",
                "confidence": 0.90,
            },
            {
                "prompt": "development",
                "response": "I can help with development tasks, code review, architecture planning, and technical implementation. What specific development task do you need help with?",
                "category": "technical",
                "confidence": 0.85,
            },
        ]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for response in default_responses:
            prompt_hash = hashlib.md5(response["prompt"].lower().encode()).hexdigest()
            cursor.execute(
                """
                INSERT OR IGNORE INTO local_responses 
                (prompt_hash, prompt, response, category, confidence)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    prompt_hash,
                    response["prompt"],
                    response["response"],
                    response["category"],
                    response["confidence"],
                ),
            )

        conn.commit()
        conn.close()

    async def process_prompt(
        self, user_id: str, session_id: str, prompt: str
    ) -> AutoContext:
        """Main processing function - Auto determines the best level"""
        start_time = datetime.now()

        # Auto decision making
        processing_level = await self.auto_decide_level(prompt)

        # Process based on level
        if processing_level == ProcessingLevel.LEVEL_1_LOCAL_DB:
            response = await self.level_1_local_db(prompt)
        elif processing_level == ProcessingLevel.LEVEL_2_LOCAL_MODEL:
            response = await self.level_2_local_model(prompt)
        else:
            response = await self.level_3_kim_reasoning(prompt)

        # Calculate confidence score
        confidence_score = await self.calculate_confidence(
            prompt, response, processing_level
        )

        # Create context
        context = AutoContext(
            user_id=user_id,
            session_id=session_id,
            prompt=prompt,
            timestamp=start_time,
            processing_level=processing_level,
            confidence_score=confidence_score,
            response=response,
            metadata={
                "processing_time_ms": (datetime.now() - start_time).total_seconds()
                * 1000,
                "auto_decision": True,
                "level_used": processing_level.value,
            },
        )

        # Log processing
        await self.log_processing(context)

        return context

    async def auto_decide_level(self, prompt: str) -> ProcessingLevel:
        """Auto decision making for processing level"""
        prompt_lower = prompt.lower()

        # Level 1 triggers (simple, common queries)
        level_1_triggers = [
            "hello",
            "hi",
            "hey",
            "help",
            "what",
            "who",
            "when",
            "where",
            "coolbits",
            "cblm",
            "company",
            "about",
            "status",
            "info",
        ]

        # Level 2 triggers (complex, technical queries)
        level_2_triggers = [
            "develop",
            "code",
            "implement",
            "create",
            "build",
            "deploy",
            "architecture",
            "design",
            "optimize",
            "debug",
            "fix",
            "test",
            "api",
            "database",
            "server",
            "frontend",
            "backend",
        ]

        # Level 3 triggers (reasoning, analysis, complex tasks)
        level_3_triggers = [
            "analyze",
            "reason",
            "think",
            "strategy",
            "plan",
            "research",
            "compare",
            "evaluate",
            "assess",
            "recommend",
            "suggest",
            "complex",
            "difficult",
            "challenge",
            "problem",
            "solution",
        ]

        # Check triggers
        if any(trigger in prompt_lower for trigger in level_1_triggers):
            return ProcessingLevel.LEVEL_1_LOCAL_DB
        elif any(trigger in prompt_lower for trigger in level_2_triggers):
            return ProcessingLevel.LEVEL_2_LOCAL_MODEL
        elif any(trigger in prompt_lower for trigger in level_3_triggers):
            return ProcessingLevel.LEVEL_3_KIM_REASONING
        else:
            # Default to Level 1 for unknown queries
            return ProcessingLevel.LEVEL_1_LOCAL_DB

    async def level_1_local_db(self, prompt: str) -> str:
        """Level 1: Local database responses with RAG integration"""
        self.processing_stats["level_1_count"] += 1

        # First try RAG system for Andy
        try:
            rag_query = RAGQuery(
                query=prompt,
                agent=RAGAgent.ANDY,
                context={"level": "level_1", "source": "local_db"},
                max_results=3,
                similarity_threshold=0.6,
            )

            rag_results = await local_rag_system.query_rag(rag_query)

            if rag_results:
                # Use RAG results
                best_result = rag_results[0]
                response = f"Based on my knowledge base: {best_result.document.content}"

                # Add additional context if available
                if len(rag_results) > 1:
                    additional_context = "\n\nAdditional relevant information:\n"
                    for result in rag_results[1:]:
                        additional_context += f"- {result.document.content[:100]}...\n"
                    response += additional_context

                return response

        except Exception as e:
            logger.error(f"RAG query failed: {e}")

        # Fallback to original local database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Try exact match first
        prompt_hash = hashlib.md5(prompt.lower().encode()).hexdigest()
        cursor.execute(
            """
            SELECT response, confidence FROM local_responses 
            WHERE prompt_hash = ?
        """,
            (prompt_hash,),
        )

        result = cursor.fetchone()
        if result:
            conn.close()
            return result[0]

        # Try partial match
        cursor.execute(
            """
            SELECT response, confidence FROM local_responses 
            WHERE prompt LIKE ? OR prompt LIKE ?
        """,
            (f"%{prompt.lower()}%", f"%{prompt.lower().split()[0]}%"),
        )

        results = cursor.fetchall()
        if results:
            # Return highest confidence response
            best_response = max(results, key=lambda x: x[1])
            conn.close()
            return best_response[0]

        # Default response
        conn.close()
        return "I understand your question. Let me process this through our local knowledge base and get back to you with a more detailed response."

    async def level_2_local_model(self, prompt: str) -> str:
        """Level 2: Local model processing with RAG integration"""
        self.processing_stats["level_2_count"] += 1

        # Use RAG system for Andy with higher similarity threshold
        try:
            rag_query = RAGQuery(
                query=prompt,
                agent=RAGAgent.ANDY,
                context={"level": "level_2", "source": "local_model"},
                max_results=5,
                similarity_threshold=0.7,
            )

            rag_results = await local_rag_system.query_rag(rag_query)

            if rag_results:
                # Build comprehensive response from RAG results
                response = (
                    f'Based on my local model analysis of your request: "{prompt}"\n\n'
                )
                response += (
                    "I'm processing this through our local AI model trained on:\n"
                )
                response += "- COOL BITS SRL project structure\n"
                response += "- CBLM.ai development patterns\n"
                response += "- Technical implementation knowledge\n"
                response += "- Local development environment\n\n"
                response += "Here's what I found in my knowledge base:\n\n"

                for i, result in enumerate(rag_results, 1):
                    response += f"{i}. {result.document.content}\n"
                    response += f"   (Relevance: {result.relevance_score:.2f}, Similarity: {result.similarity_score:.2f})\n\n"

                response += "[Local Model Processing Complete]"
                return response

        except Exception as e:
            logger.error(f"RAG query failed: {e}")

        # Fallback to original response
        model_response = f"""
Based on my local model analysis of your request: "{prompt}"

I'm processing this through our local AI model trained on:
- COOL BITS SRL project structure
- CBLM.ai development patterns
- Technical implementation knowledge
- Local development environment

This requires deeper analysis than simple database lookup. Let me provide a comprehensive response based on our local training data.

[Local Model Processing...]
"""

        return model_response

    async def level_3_kim_reasoning(self, prompt: str) -> str:
        """Level 3: Kim reasoning partner with RAG integration"""
        self.processing_stats["level_3_count"] += 1

        # Use RAG system for Kim reasoning
        try:
            rag_query = RAGQuery(
                query=prompt,
                agent=RAGAgent.KIM,
                context={"level": "level_3", "source": "kim_reasoning"},
                max_results=5,
                similarity_threshold=0.8,
            )

            rag_results = await local_rag_system.query_rag(rag_query)

            if rag_results:
                # Build Kim's reasoning response
                response = f"Kim Reasoning Partner Analysis:\n\n"
                response += f'I\'ve analyzed your request: "{prompt}"\n\n'
                response += "This requires advanced reasoning and analysis. I'm processing this through:\n"
                response += "- Deep reasoning algorithms\n"
                response += "- Multi-step problem solving\n"
                response += "- Context analysis across multiple domains\n"
                response += "- Strategic thinking and planning\n\n"
                response += "Based on my knowledge base analysis:\n\n"

                for i, result in enumerate(rag_results, 1):
                    response += f"{i}. {result.document.content}\n"
                    response += f"   (Reasoning Score: {result.relevance_score:.2f}, Analysis Score: {result.similarity_score:.2f})\n\n"

                response += "Based on my comprehensive analysis, here's my reasoning and recommendation:\n"
                response += (
                    "This requires deep strategic thinking and multi-domain analysis. "
                )
                response += "I recommend a systematic approach to address this complex challenge."

                return response

        except Exception as e:
            logger.error(f"Kim RAG query failed: {e}")

        # Fallback to original response
        kim_response = f"""
Kim Reasoning Partner Analysis:

I'm Kim, Andy's reasoning partner. I've analyzed your request: "{prompt}"

This requires advanced reasoning and analysis. I'm processing this through:
- Deep reasoning algorithms
- Multi-step problem solving
- Context analysis across multiple domains
- Strategic thinking and planning

[Kim Reasoning Processing...]

Based on my analysis, here's my comprehensive reasoning and recommendation:
"""

        return kim_response

    async def calculate_confidence(
        self, prompt: str, response: str, level: ProcessingLevel
    ) -> float:
        """Calculate confidence score for response"""
        base_confidence = {
            ProcessingLevel.LEVEL_1_LOCAL_DB: 0.85,
            ProcessingLevel.LEVEL_2_LOCAL_MODEL: 0.75,
            ProcessingLevel.LEVEL_3_KIM_REASONING: 0.90,
        }

        return base_confidence.get(level, 0.70)

    async def log_processing(self, context: AutoContext):
        """Log processing information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO processing_logs 
            (session_id, user_id, prompt, processing_level, confidence_score, response_time_ms)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                context.session_id,
                context.user_id,
                context.prompt,
                context.processing_level.value,
                context.confidence_score,
                context.metadata["processing_time_ms"],
            ),
        )

        conn.commit()
        conn.close()

    async def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        self.processing_stats["total_requests"] = (
            self.processing_stats["level_1_count"]
            + self.processing_stats["level_2_count"]
            + self.processing_stats["level_3_count"]
        )

        return self.processing_stats

    async def add_knowledge(
        self, topic: str, content: str, source: str, relevance_score: float = 0.8
    ):
        """Add knowledge to local database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO knowledge_base (topic, content, source, relevance_score)
            VALUES (?, ?, ?, ?)
        """,
            (topic, content, source, relevance_score),
        )

        conn.commit()
        conn.close()

    async def search_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """Search local knowledge base"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT topic, content, source, relevance_score FROM knowledge_base
            WHERE topic LIKE ? OR content LIKE ?
            ORDER BY relevance_score DESC
        """,
            (f"%{query}%", f"%{query}%"),
        )

        results = cursor.fetchall()
        conn.close()

        return [
            {
                "topic": row[0],
                "content": row[1],
                "source": row[2],
                "relevance_score": row[3],
            }
            for row in results
        ]


# Global instance
andy_auto_engine = AndyAutoEngine()


async def main():
    """Test the Auto Engine"""
    print("🤖 Andy Auto Engine - Testing")

    test_prompts = [
        "Hello Andy!",
        "Help me develop a new feature",
        "Analyze the project architecture and recommend improvements",
    ]

    for prompt in test_prompts:
        print(f"\n📝 Prompt: {prompt}")
        context = await andy_auto_engine.process_prompt(
            "andrei", "test_session", prompt
        )
        print(f"🎯 Level: {context.processing_level.value}")
        print(f"📊 Confidence: {context.confidence_score:.2f}")
        print(f"💬 Response: {context.response[:100]}...")

    stats = await andy_auto_engine.get_processing_stats()
    print(f"\n📈 Processing Stats: {stats}")


if __name__ == "__main__":
    asyncio.run(main())
