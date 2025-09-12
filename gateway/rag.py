# RAG implementation with pgvector
import logging
import os
from typing import List, Dict, Any
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import text
from .db import RAGChunk, RAGEmbedding
from .deps import get_openai

logger = logging.getLogger(__name__)

# Environment variables
RAG_TOPK = int(os.getenv("RAG_TOPK", "8"))
RAG_MIN_SCORE = float(os.getenv("RAG_MIN_SCORE", "0.15"))

def get_embedding(text: str, openai_client) -> List[float]:
    """Get OpenAI embedding for text"""
    try:
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        # Return dummy embedding for fallback
        return [0.0] * 1536

def search_rag_chunks(
    db: Session,
    panel: str,
    query: str,
    k: int = RAG_TOPK,
    min_score: float = RAG_MIN_SCORE,
    openai_client=None
) -> List[Dict[str, Any]]:
    """Search RAG chunks using pgvector"""
    
    # Get query embedding
    query_embedding = get_embedding(query, openai_client)
    
    try:
        # pgvector similarity search with cosine similarity
        query_sql = text("""
            WITH cand AS (
                SELECT e.chunk_id, 1 - (e.embedding <=> :query_embedding) AS score
                FROM rag_embeddings e
                JOIN rag_chunks c ON c.id = e.chunk_id
                WHERE c.panel = :panel
                ORDER BY e.embedding <-> :query_embedding
                LIMIT :k_candidates
            )
            SELECT c.id AS chunk_id, c.text, c.source, c.meta, cand.score
            FROM cand
            JOIN rag_chunks c ON c.id = cand.chunk_id
            WHERE cand.score >= :min_score
            ORDER BY cand.score DESC
            LIMIT :k
        """)
        
        result = db.execute(query_sql, {
            "query_embedding": str(query_embedding),
            "panel": panel,
            "k_candidates": k * 4,  # Get more candidates for filtering
            "min_score": min_score,
            "k": k
        })
        
        answers = []
        for row in result:
            answers.append({
                "text": row.text,
                "score": float(row.score),
                "source": row.source,
                "meta": row.meta,
                "chunk_id": row.chunk_id
            })
        
        return answers
        
    except Exception as e:
        logger.error(f"RAG search error: {e}")
        # Fallback to simple text search
        chunks = db.query(RAGChunk).filter(
            RAGChunk.panel == panel,
            RAGChunk.text.ilike(f"%{query}%")
        ).limit(k).all()
        
        return [
            {
                "text": chunk.text,
                "score": 0.8,  # Dummy score
                "source": chunk.source,
                "meta": chunk.meta,
                "chunk_id": chunk.id
            }
            for chunk in chunks
        ]

def ingest_text_to_rag(
    db: Session,
    panel: str,
    source: str,
    text: str,
    meta: Dict[str, Any] = None,
    openai_client=None
) -> str:
    """Ingest text into RAG system"""
    
    # Create chunk
    chunk = RAGChunk(
        panel=panel,
        source=source,
        text=text,
        meta=meta or {}
    )
    db.add(chunk)
    db.flush()  # Get the ID
    
    # Generate embedding
    embedding = get_embedding(text, openai_client)
    
    # Store embedding
    rag_embedding = RAGEmbedding(
        chunk_id=chunk.id,
        embedding=str(embedding)
    )
    db.add(rag_embedding)
    
    db.commit()
    
    logger.info(f"Ingested RAG chunk {chunk.id} for panel {panel}")
    return str(chunk.id)
