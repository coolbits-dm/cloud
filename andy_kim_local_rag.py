#!/usr/bin/env python3
"""
Andy & Kim Local RAG System
CoolBits.ai - Personal 1:1 Agent RAG Implementation
"""

import asyncio
import json
import sqlite3
import logging
import hashlib
import os
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import pickle
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGAgent(Enum):
    """RAG Agents"""

    ANDY = "andy"
    KIM = "kim"


@dataclass
class RAGDocument:
    """RAG Document structure"""

    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None
    agent: RAGAgent = RAGAgent.ANDY
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class RAGQuery:
    """RAG Query structure"""

    query: str
    agent: RAGAgent
    context: Dict[str, Any]
    max_results: int = 5
    similarity_threshold: float = 0.7


@dataclass
class RAGResult:
    """RAG Result structure"""

    document: RAGDocument
    similarity_score: float
    relevance_score: float
    context: Dict[str, Any]


class LocalRAGSystem:
    """Local RAG System for Andy and Kim"""

    def __init__(self):
        self.db_path = "andy_kim_rag.db"
        self.embeddings_path = "rag_embeddings.pkl"
        self.knowledge_base_path = "knowledge_base/"
        self.embeddings_cache = {}
        self.init_database()
        self.init_knowledge_base()
        self.load_embeddings()

    def init_database(self):
        """Initialize RAG database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create documents table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS rag_documents (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                metadata TEXT,
                agent TEXT NOT NULL,
                embedding BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create queries table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS rag_queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                agent TEXT NOT NULL,
                context TEXT,
                results_count INTEGER,
                processing_time_ms INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create knowledge categories table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS knowledge_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT UNIQUE NOT NULL,
                description TEXT,
                agent TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.commit()
        conn.close()

    def init_knowledge_base(self):
        """Initialize knowledge base directories"""
        os.makedirs(self.knowledge_base_path, exist_ok=True)
        os.makedirs(f"{self.knowledge_base_path}/andy", exist_ok=True)
        os.makedirs(f"{self.knowledge_base_path}/kim", exist_ok=True)

        # Initialize default knowledge
        self.init_default_knowledge()

    def init_default_knowledge(self):
        """Initialize default knowledge for Andy and Kim"""

        # Andy's knowledge base
        andy_knowledge = [
            {
                "category": "company_info",
                "content": "CoolBits.ai is an AI platform specializing in intelligent solutions and development services. The platform focuses on creating intelligent systems and AI-powered applications.",
                "metadata": {"source": "company_docs", "priority": "high"},
            },
            {
                "category": "project_structure",
                "content": "The coolbits.ai project uses a hybrid architecture with local Windows 11 processing and Google Cloud integration. Ports 8101 and 8102 are reserved for local services.",
                "metadata": {"source": "project_docs", "priority": "high"},
            },
            {
                "category": "development",
                "content": "Development follows agile methodologies with focus on AI integration, real-time communication, and scalable architecture. The tech stack includes Python, FastAPI, WebSocket, and various AI models.",
                "metadata": {"source": "dev_docs", "priority": "medium"},
            },
            {
                "category": "cblm_platform",
                "content": "cblm.ai is our AI platform providing intelligent solutions for various business needs. It integrates with multiple AI models and provides comprehensive AI services.",
                "metadata": {"source": "platform_docs", "priority": "high"},
            },
        ]

        # Kim's knowledge base
        kim_knowledge = [
            {
                "category": "reasoning_methods",
                "content": "Kim uses advanced reasoning algorithms including multi-step problem solving, context analysis, strategic thinking, and comprehensive analysis across multiple domains.",
                "metadata": {"source": "reasoning_docs", "priority": "high"},
            },
            {
                "category": "analysis_framework",
                "content": "Kim's analysis framework includes data analysis, pattern recognition, strategic planning, risk assessment, and comprehensive evaluation of complex scenarios.",
                "metadata": {"source": "analysis_docs", "priority": "high"},
            },
            {
                "category": "research_methods",
                "content": "Kim employs systematic research methods including literature review, data collection, analysis, synthesis, and evidence-based recommendations.",
                "metadata": {"source": "research_docs", "priority": "medium"},
            },
        ]

        # Add knowledge to database
        for knowledge in andy_knowledge:
            self.add_document(
                content=knowledge["content"],
                metadata=knowledge["metadata"],
                agent=RAGAgent.ANDY,
                category=knowledge["category"],
            )

        for knowledge in kim_knowledge:
            self.add_document(
                content=knowledge["content"],
                metadata=knowledge["metadata"],
                agent=RAGAgent.KIM,
                category=knowledge["category"],
            )

    def add_document(
        self,
        content: str,
        metadata: Dict[str, Any],
        agent: RAGAgent,
        category: str = "general",
    ):
        """Add document to RAG system"""
        doc_id = hashlib.md5(f"{content}_{agent.value}_{category}".encode()).hexdigest()

        # Generate embedding
        embedding = self.generate_embedding(content)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Add document
        cursor.execute(
            """
            INSERT OR REPLACE INTO rag_documents 
            (id, content, metadata, agent, embedding, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
            (
                doc_id,
                content,
                json.dumps(metadata),
                agent.value,
                pickle.dumps(embedding),
            ),
        )

        # Add category if not exists
        cursor.execute(
            """
            INSERT OR IGNORE INTO knowledge_categories (category, agent)
            VALUES (?, ?)
        """,
            (category, agent.value),
        )

        conn.commit()
        conn.close()

        # Update embeddings cache
        self.embeddings_cache[doc_id] = embedding

        logger.info(f"Added document to {agent.value} RAG system: {category}")

    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text (simplified version)"""
        # In a real implementation, this would use a proper embedding model
        # For now, we'll use a simple hash-based embedding

        # Clean text
        text = re.sub(r"[^\w\s]", "", text.lower())
        words = text.split()

        # Create simple embedding vector
        embedding = np.zeros(128)  # 128-dimensional embedding

        for i, word in enumerate(words):
            word_hash = hash(word) % 128
            embedding[word_hash] += 1.0 / len(words)

        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding

    def load_embeddings(self):
        """Load embeddings from cache"""
        if os.path.exists(self.embeddings_path):
            try:
                with open(self.embeddings_path, "rb") as f:
                    self.embeddings_cache = pickle.load(f)
                logger.info(
                    f"Loaded {len(self.embeddings_cache)} embeddings from cache"
                )
            except Exception as e:
                logger.error(f"Failed to load embeddings: {e}")

    def save_embeddings(self):
        """Save embeddings to cache"""
        try:
            with open(self.embeddings_path, "wb") as f:
                pickle.dump(self.embeddings_cache, f)
            logger.info(f"Saved {len(self.embeddings_cache)} embeddings to cache")
        except Exception as e:
            logger.error(f"Failed to save embeddings: {e}")

    async def query_rag(self, rag_query: RAGQuery) -> List[RAGResult]:
        """Query RAG system"""
        start_time = datetime.now()

        # Generate query embedding
        query_embedding = self.generate_embedding(rag_query.query)

        # Get documents for agent
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, content, metadata, embedding FROM rag_documents
            WHERE agent = ?
        """,
            (rag_query.agent.value,),
        )

        documents = cursor.fetchall()
        conn.close()

        # Calculate similarities
        results = []
        for doc_id, content, metadata, embedding_blob in documents:
            if embedding_blob:
                doc_embedding = pickle.loads(embedding_blob)
                similarity = self.calculate_similarity(query_embedding, doc_embedding)

                if similarity >= rag_query.similarity_threshold:
                    # Calculate relevance score
                    relevance_score = self.calculate_relevance(rag_query.query, content)

                    # Create RAG result
                    result = RAGResult(
                        document=RAGDocument(
                            id=doc_id,
                            content=content,
                            metadata=json.loads(metadata),
                            embedding=doc_embedding,
                            agent=rag_query.agent,
                        ),
                        similarity_score=similarity,
                        relevance_score=relevance_score,
                        context=rag_query.context,
                    )
                    results.append(result)

        # Sort by combined score
        results.sort(
            key=lambda x: (x.similarity_score + x.relevance_score) / 2, reverse=True
        )

        # Limit results
        results = results[: rag_query.max_results]

        # Log query
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        await self.log_query(rag_query, len(results), processing_time)

        return results

    def calculate_similarity(
        self, embedding1: np.ndarray, embedding2: np.ndarray
    ) -> float:
        """Calculate cosine similarity between embeddings"""
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def calculate_relevance(self, query: str, content: str) -> float:
        """Calculate relevance score based on keyword matching"""
        query_words = set(re.findall(r"\w+", query.lower()))
        content_words = set(re.findall(r"\w+", content.lower()))

        if not query_words:
            return 0.0

        overlap = len(query_words.intersection(content_words))
        return overlap / len(query_words)

    async def log_query(
        self, rag_query: RAGQuery, results_count: int, processing_time: float
    ):
        """Log RAG query"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO rag_queries 
            (query, agent, context, results_count, processing_time_ms)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                rag_query.query,
                rag_query.agent.value,
                json.dumps(rag_query.context),
                results_count,
                processing_time,
            ),
        )

        conn.commit()
        conn.close()

    async def get_rag_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get document counts
        cursor.execute("SELECT agent, COUNT(*) FROM rag_documents GROUP BY agent")
        doc_counts = dict(cursor.fetchall())

        # Get query counts
        cursor.execute("SELECT agent, COUNT(*) FROM rag_queries GROUP BY agent")
        query_counts = dict(cursor.fetchall())

        # Get category counts
        cursor.execute(
            "SELECT agent, COUNT(*) FROM knowledge_categories GROUP BY agent"
        )
        category_counts = dict(cursor.fetchall())

        conn.close()

        return {
            "documents": doc_counts,
            "queries": query_counts,
            "categories": category_counts,
            "embeddings_cache_size": len(self.embeddings_cache),
            "timestamp": datetime.now().isoformat(),
        }

    async def search_knowledge(
        self, query: str, agent: RAGAgent, max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search knowledge base"""
        rag_query = RAGQuery(
            query=query,
            agent=agent,
            context={"search_type": "knowledge_search"},
            max_results=max_results,
        )

        results = await self.query_rag(rag_query)

        return [
            {
                "id": result.document.id,
                "content": result.document.content,
                "metadata": result.document.metadata,
                "similarity_score": result.similarity_score,
                "relevance_score": result.relevance_score,
                "agent": result.document.agent.value,
            }
            for result in results
        ]

    async def add_knowledge_from_file(
        self, file_path: str, agent: RAGAgent, category: str = "file_import"
    ):
        """Add knowledge from file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            self.add_document(
                content=content,
                metadata={"source": file_path, "type": "file_import"},
                agent=agent,
                category=category,
            )

            logger.info(f"Added knowledge from file: {file_path}")

        except Exception as e:
            logger.error(f"Failed to add knowledge from file {file_path}: {e}")

    async def export_knowledge(self, agent: RAGAgent, output_path: str):
        """Export knowledge base"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT content, metadata FROM rag_documents
            WHERE agent = ?
        """,
            (agent.value,),
        )

        documents = cursor.fetchall()
        conn.close()

        export_data = {
            "agent": agent.value,
            "export_timestamp": datetime.now().isoformat(),
            "documents": [
                {"content": doc[0], "metadata": json.loads(doc[1])} for doc in documents
            ],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        logger.info(
            f"Exported {len(documents)} documents for {agent.value} to {output_path}"
        )


# Global RAG system instance
local_rag_system = LocalRAGSystem()


async def main():
    """Test the RAG system"""
    print("🤖 Andy & Kim Local RAG System - Testing")

    # Test Andy RAG
    print("\n📝 Testing Andy RAG:")
    andy_query = RAGQuery(
        query="What is COOL BITS SRL?", agent=RAGAgent.ANDY, context={"test": True}
    )

    andy_results = await local_rag_system.query_rag(andy_query)
    for result in andy_results:
        print(f"📄 {result.document.content[:100]}...")
        print(
            f"🎯 Similarity: {result.similarity_score:.3f}, Relevance: {result.relevance_score:.3f}"
        )

    # Test Kim RAG
    print("\n🧠 Testing Kim RAG:")
    kim_query = RAGQuery(
        query="How does Kim analyze complex problems?",
        agent=RAGAgent.KIM,
        context={"test": True},
    )

    kim_results = await local_rag_system.query_rag(kim_query)
    for result in kim_results:
        print(f"📄 {result.document.content[:100]}...")
        print(
            f"🎯 Similarity: {result.similarity_score:.3f}, Relevance: {result.relevance_score:.3f}"
        )

    # Get stats
    stats = await local_rag_system.get_rag_stats()
    print(f"\n📊 RAG Stats: {stats}")


if __name__ == "__main__":
    asyncio.run(main())
