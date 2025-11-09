# Gateway dependencies and clients
import os
import logging
from typing import Optional, Dict, Any
import openai
import anthropic
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
DB_DSN = os.getenv("DB_DSN", "postgresql://localhost/coolbits_dev")

# OpenAI client
openai_client = None
if OPENAI_API_KEY:
    openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
    logger.info("OpenAI client initialized")
else:
    logger.warning("OpenAI API key not provided")

# Anthropic client
anthropic_client = None
if ANTHROPIC_API_KEY:
    anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    logger.info("Anthropic client initialized")
else:
    logger.warning("Anthropic API key not provided")

# Redis client
redis_client = None
try:
    redis_client = redis.from_url(REDIS_URL)
    redis_client.ping()  # Test connection
    logger.info("Redis client initialized")
except Exception as e:
    logger.warning(f"Redis connection failed: {e}")
    redis_client = None

# Database engine
db_engine = None
try:
    db_engine = create_engine(DB_DSN)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    logger.info("Database engine initialized")
except Exception as e:
    logger.error(f"Database connection failed: {e}")
    db_engine = None

def get_db_session():
    """Get database session"""
    if not db_engine:
        raise Exception("Database not available")
    return SessionLocal()

def get_redis():
    """Get Redis client"""
    if not redis_client:
        raise Exception("Redis not available")
    return redis_client

def get_openai():
    """Get OpenAI client"""
    if not openai_client:
        raise Exception("OpenAI not available")
    return openai_client

def get_anthropic():
    """Get Anthropic client"""
    if not anthropic_client:
        raise Exception("Anthropic not available")
    return anthropic_client
