# Embedding worker for RAG chunks
import os
import logging
import hashlib
import math
import random
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
import openai
from .db import RAGChunk, RAGEmbedding, get_db_session
from .deps import get_openai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
EMBED_DIM = int(os.getenv("EMBED_DIM", "1536"))
BATCH_SIZE = int(os.getenv("EMBED_BATCH_SIZE", "64"))

def fake_embed(text: str, dim: int = 1536) -> List[float]:
    """Deterministic fallback embedding"""
    h = hashlib.sha256(text.encode('utf-8')).digest()
    rnd = random.Random(h)
    vec = [rnd.uniform(-1, 1) for _ in range(dim)]
    norm = math.sqrt(sum(x*x for x in vec)) or 1.0
    return [x/norm for x in vec]

def get_real_embedding(text: str, openai_client) -> List[float]:
    """Get real OpenAI embedding"""
    try:
        response = openai_client.embeddings.create(
            model=EMBED_MODEL,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"OpenAI embedding error: {e}")
        raise

def get_pending_chunks(db: Session, limit: int = BATCH_SIZE) -> List[RAGChunk]:
    """Get chunks without embeddings"""
    return db.query(RAGChunk).filter(
        ~RAGChunk.id.in_(
            db.query(RAGEmbedding.chunk_id)
        )
    ).limit(limit).all()

def process_batch(chunks: List[RAGChunk], openai_client=None) -> int:
    """Process batch of chunks"""
    db = get_db_session()
    try:
        embeddings = []
        
        for chunk in chunks:
            try:
                if openai_client:
                    embedding = get_real_embedding(chunk.text, openai_client)
                    logger.info(f"Real embedding for chunk {chunk.id}")
                else:
                    embedding = fake_embed(chunk.text, EMBED_DIM)
                    logger.info(f"Fake embedding for chunk {chunk.id}")
                
                embeddings.append({
                    'chunk_id': chunk.id,
                    'embedding': str(embedding)
                })
                
            except Exception as e:
                logger.error(f"Failed to embed chunk {chunk.id}: {e}")
                # Use fake embedding as fallback
                embedding = fake_embed(chunk.text, EMBED_DIM)
                embeddings.append({
                    'chunk_id': chunk.id,
                    'embedding': str(embedding)
                })
        
        # Insert embeddings
        for emb_data in embeddings:
            rag_embedding = RAGEmbedding(
                chunk_id=emb_data['chunk_id'],
                embedding=emb_data['embedding']
            )
            db.add(rag_embedding)
        
        db.commit()
        logger.info(f"Processed {len(embeddings)} embeddings")
        return len(embeddings)
        
    except Exception as e:
        logger.error(f"Batch processing error: {e}")
        db.rollback()
        return 0
    finally:
        db.close()

def get_pending_count(db: Session) -> int:
    """Get count of pending chunks"""
    result = db.execute(text("""
        SELECT COUNT(*) 
        FROM rag_chunks c 
        LEFT JOIN rag_embeddings e ON c.id = e.chunk_id 
        WHERE e.chunk_id IS NULL
    """)).scalar()
    return result or 0

def run_embedding_worker():
    """Main worker loop"""
    logger.info("Starting embedding worker")
    
    openai_client = None
    try:
        openai_client = get_openai()
        logger.info("Using real OpenAI embeddings")
    except Exception as e:
        logger.warning(f"OpenAI not available, using fake embeddings: {e}")
    
    total_processed = 0
    
    while True:
        db = get_db_session()
        try:
            pending_count = get_pending_count(db)
            logger.info(f"Pending chunks: {pending_count}")
            
            if pending_count == 0:
                logger.info("No pending chunks, worker finished")
                break
            
            # Get batch
            chunks = get_pending_chunks(db, BATCH_SIZE)
            if not chunks:
                logger.info("No chunks to process")
                break
            
            # Process batch
            processed = process_batch(chunks, openai_client)
            total_processed += processed
            
            logger.info(f"Processed {processed} chunks, total: {total_processed}")
            
        except Exception as e:
            logger.error(f"Worker error: {e}")
        finally:
            db.close()
    
    logger.info(f"Embedding worker completed. Total processed: {total_processed}")

if __name__ == "__main__":
    run_embedding_worker()
