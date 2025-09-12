# Queue abstraction (Redis dev / PubSub prod)
import logging
import json
import time
from typing import Dict, Any, Optional
from .deps import get_redis

logger = logging.getLogger(__name__)

class QueueManager:
    """Queue manager abstraction"""
    
    def __init__(self):
        self.redis_client = None
        try:
            self.redis_client = get_redis()
        except Exception as e:
            logger.warning(f"Redis not available: {e}")
    
    def push(self, queue_name: str, data: Dict[str, Any]) -> bool:
        """Push data to queue"""
        if not self.redis_client:
            logger.warning("Redis not available, using fallback")
            return False
        
        try:
            self.redis_client.lpush(queue_name, json.dumps(data))
            return True
        except Exception as e:
            logger.error(f"Failed to push to queue {queue_name}: {e}")
            return False
    
    def pop(self, queue_name: str, timeout: int = 0) -> Optional[Dict[str, Any]]:
        """Pop data from queue"""
        if not self.redis_client:
            return None
        
        try:
            result = self.redis_client.brpop(queue_name, timeout=timeout)
            if result:
                _, data = result
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Failed to pop from queue {queue_name}: {e}")
            return None
    
    def get_queue_length(self, queue_name: str) -> int:
        """Get queue length"""
        if not self.redis_client:
            return 0
        
        try:
            return self.redis_client.llen(queue_name)
        except Exception as e:
            logger.error(f"Failed to get queue length for {queue_name}: {e}")
            return 0

# Global queue manager
queue_manager = QueueManager()

def queue_nha_job(job_data: Dict[str, Any]) -> bool:
    """Queue NHA job"""
    return queue_manager.push("nha_queue", job_data)

def get_nha_job(timeout: int = 5) -> Optional[Dict[str, Any]]:
    """Get NHA job from queue"""
    return queue_manager.pop("nha_queue", timeout)

def get_queue_status() -> Dict[str, int]:
    """Get queue status"""
    return {
        "nha_queue": queue_manager.get_queue_length("nha_queue"),
        "orchestrator_queue": queue_manager.get_queue_length("orchestrator_queue")
    }
