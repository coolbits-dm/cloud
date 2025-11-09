# NHA (Natural Human Assistant) implementations
import logging
import os
import time
from typing import Dict, Any, Optional
import json
import uuid
from datetime import datetime
from .deps import get_openai, get_anthropic, get_redis
from .db import Invocation, Comment, Post, get_db_session

logger = logging.getLogger(__name__)

# Environment variables
CB_TARIFF_JSON = os.getenv("CB_TARIFF_JSON", '{"sentiment":-2,"summarize":-2,"tagging":-1,"scribe":-3}')
CB_BILLING_MODE = os.getenv("CB_BILLING_MODE", "dev")

# Parse tariff
try:
    CB_TARIFF = json.loads(CB_TARIFF_JSON)
except:
    CB_TARIFF = {"sentiment": -2, "summarize": -2, "tagging": -1, "scribe": -3}

class NHAAdapter:
    """Base class for NHA adapters"""
    
    def __init__(self, role: str):
        self.role = role
        self.cost_cbT = CB_TARIFF.get(role, -2)
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return result"""
        raise NotImplementedError

class SentimentAdapter(NHAAdapter):
    """Sentiment analysis adapter"""
    
    def __init__(self):
        super().__init__("sentiment")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        text = input_data.get("text", "")
        
        try:
            openai_client = get_openai()
            
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a sentiment analysis expert. Analyze the sentiment of the given text and respond with a JSON object containing 'label' (positive/negative/neutral), 'score' (0-1), and 'rationale' (brief explanation)."},
                    {"role": "user", "content": f"Analyze sentiment: {text}"}
                ],
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                "label": result.get("label", "neutral"),
                "score": float(result.get("score", 0.5)),
                "rationale": result.get("rationale", ""),
                "model": "gpt-4o-mini",
                "usage": response.usage.dict() if response.usage else {}
            }
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            # Fallback
            return {
                "label": "neutral",
                "score": 0.5,
                "rationale": f"[FAKE] Fallback analysis: {e}",
                "model": "fallback",
                "error": str(e)
            }

class SummarizeAdapter(NHAAdapter):
    """Text summarization adapter"""
    
    def __init__(self):
        super().__init__("summarize")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        text = input_data.get("text", "")
        
        try:
            openai_client = get_openai()
            
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a summarization expert. Create a concise 3-5 sentence summary of the given text. Focus on key points without adding information not present in the original."},
                    {"role": "user", "content": f"Summarize: {text}"}
                ],
                temperature=0.1
            )
            
            summary = response.choices[0].message.content
            return {
                "summary": summary,
                "word_count": len(text.split()),
                "compression_ratio": len(summary.split()) / max(len(text.split()), 1),
                "model": "gpt-4o-mini",
                "usage": response.usage.dict() if response.usage else {}
            }
        except Exception as e:
            logger.error(f"Summarization error: {e}")
            # Fallback: first few sentences
            sentences = text.split('.')[:3]
            fallback_summary = '. '.join(sentences) + '.'
            return {
                "summary": f"[FAKE] {fallback_summary}",
                "word_count": len(text.split()),
                "compression_ratio": 0.3,
                "model": "fallback",
                "error": str(e)
            }

class TaggingAdapter(NHAAdapter):
    """Content tagging adapter"""
    
    def __init__(self):
        super().__init__("tagging")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        text = input_data.get("text", "")
        
        try:
            openai_client = get_openai()
            
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a content tagging expert. Analyze the text and return a JSON array of up to 5 relevant tags. Tags should be concise, lowercase, and descriptive."},
                    {"role": "user", "content": f"Tag this content: {text}"}
                ],
                temperature=0.1
            )
            
            tags = json.loads(response.choices[0].message.content)
            return {
                "tags": tags if isinstance(tags, list) else [tags],
                "confidence": 0.8,
                "model": "gpt-4o-mini",
                "usage": response.usage.dict() if response.usage else {}
            }
        except Exception as e:
            logger.error(f"Tagging error: {e}")
            # Fallback: simple keywords
            words = text.lower().split()
            common_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
            tags = [w for w in words if len(w) > 3 and w not in common_words][:5]
            return {
                "tags": tags,
                "confidence": 0.5,
                "model": "fallback",
                "error": str(e)
            }

class ScribeAdapter(NHAAdapter):
    """Meeting scribe adapter"""
    
    def __init__(self):
        super().__init__("scribe")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        messages = input_data.get("messages", [])
        
        try:
            openai_client = get_openai()
            
            # Convert messages to text
            text = "\n".join([f"{msg.get('role', 'unknown')}: {msg.get('content', '')}" for msg in messages])
            
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a meeting scribe. Extract key points, decisions, and action items from the conversation. Return a JSON object with 'minutes' (key points), 'action_items' (list), and 'participants' (list)."},
                    {"role": "user", "content": f"Transcribe meeting: {text}"}
                ],
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                "minutes": result.get("minutes", "Meeting minutes extracted"),
                "action_items": result.get("action_items", []),
                "participants": result.get("participants", []),
                "duration_minutes": len(messages) * 2,  # Estimate
                "model": "gpt-4o-mini",
                "usage": response.usage.dict() if response.usage else {}
            }
        except Exception as e:
            logger.error(f"Scribe error: {e}")
            return {
                "minutes": "[FAKE] Meeting minutes placeholder",
                "action_items": ["Follow up on project status"],
                "participants": ["Unknown"],
                "duration_minutes": 30,
                "model": "fallback",
                "error": str(e)
            }

# NHA Registry
NHA_ADAPTERS = {
    "sentiment": SentimentAdapter(),
    "summarize": SummarizeAdapter(),
    "tagging": TaggingAdapter(),
    "scribe": ScribeAdapter()
}

def get_nha_adapter(role: str) -> Optional[NHAAdapter]:
    """Get NHA adapter by role"""
    return NHA_ADAPTERS.get(role)

def extract_nha_mentions(text: str) -> list:
    """Extract @nha:* mentions from text"""
    import re
    mentions = re.findall(r'@nha:(\w+)', text)
    return [m for m in mentions if m in NHA_ADAPTERS]

def queue_nha_invocation(
    post_id: str,
    agent_id: str,
    trace_id: str,
    cost_cbT: float = 0
) -> str:
    """Queue NHA invocation"""
    
    invocation_id = str(uuid.uuid4())
    
    # Create invocation record
    db = get_db_session()
    try:
        invocation = Invocation(
            id=invocation_id,
            post_id=post_id,
            agent_id=agent_id,
            role=agent_id,
            status="queued",
            cost_cbT=cost_cbT,
            trace_id=trace_id
        )
        db.add(invocation)
        db.commit()
        
        # Queue in Redis (if available)
        redis_client = get_redis()
        if redis_client:
            job_data = {
                "invocation_id": invocation_id,
                "post_id": post_id,
                "agent_id": agent_id,
                "trace_id": trace_id
            }
            redis_client.xadd("nha:jobs", job_data)
            logger.info(f"Queued NHA invocation {invocation_id}")
        
        return invocation_id
        
    except Exception as e:
        logger.error(f"Failed to queue NHA invocation: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def process_nha_invocation(invocation_id: str) -> Dict[str, Any]:
    """Process NHA invocation"""
    
    db = get_db_session()
    try:
        invocation = db.query(Invocation).filter(Invocation.id == invocation_id).first()
        if not invocation:
            raise Exception(f"Invocation {invocation_id} not found")
        
        # Idempotency check
        if invocation.status != "queued":
            logger.warning(f"Invocation {invocation_id} already processed: {invocation.status}")
            return {"status": invocation.status}
        
        # Update status to running
        invocation.status = "running"
        db.commit()
        
        # Get adapter
        adapter = get_nha_adapter(invocation.agent_id)
        if not adapter:
            raise Exception(f"No adapter for agent {invocation.agent_id}")
        
        # Get post text
        post = db.query(Post).filter(Post.id == invocation.post_id).first()
        if not post:
            raise Exception(f"Post {invocation.post_id} not found")
        
        # Process
        start_time = time.time()
        result = adapter.process({"text": post.text})
        took_ms = int((time.time() - start_time) * 1000)
        
        # Add timing to result
        result["took_ms"] = took_ms
        
        # Create comment
        comment = Comment(
            post_id=invocation.post_id,
            author=f"@nha:{invocation.agent_id}",
            text=json.dumps(result),
            meta={
                "agent": invocation.agent_id,
                "trace_id": invocation.trace_id,
                "model": result.get("model", "unknown"),
                "usage": result.get("usage", {}),
                "took_ms": took_ms
            }
        )
        db.add(comment)
        
        # Update with result
        invocation.status = "done"
        invocation.result_ref = result
        db.commit()
        
        logger.info(f"Processed NHA invocation {invocation_id} in {took_ms}ms")
        return result
        
    except Exception as e:
        logger.error(f"Failed to process NHA invocation {invocation_id}: {e}")
        if 'invocation' in locals():
            invocation.status = "error"
            invocation.error = str(e)
            db.commit()
        raise
    finally:
        db.close()
