# Flow Worker - processes orchestrator jobs from Redis stream
import os
import logging
import time
import signal
import sys
from typing import Dict, Any
from .deps import get_redis, get_db_session
from .orchestrator import process_flow_run

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
WORKER_TIMEOUT = int(os.getenv("WORKER_TIMEOUT", "15"))
WORKER_RETRY_COUNT = int(os.getenv("WORKER_RETRY_COUNT", "2"))
WORKER_BATCH_SIZE = int(os.getenv("WORKER_BATCH_SIZE", "1"))

class FlowWorker:
    """Flow Worker that processes orchestrator jobs from Redis stream"""
    
    def __init__(self):
        self.running = True
        self.redis_client = None
        self.consumer_group = "flows:cg"
        self.consumer_name = f"flow-worker-{os.getpid()}"
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def _setup_redis(self):
        """Setup Redis connection and consumer group"""
        try:
            self.redis_client = get_redis()
            
            # Create consumer group if it doesn't exist
            try:
                self.redis_client.xgroup_create("flows:jobs", self.consumer_group, id="0", mkstream=True)
                logger.info(f"Created consumer group {self.consumer_group}")
            except Exception as e:
                if "BUSYGROUP" not in str(e):
                    logger.warning(f"Consumer group creation: {e}")
            
            return True
        except Exception as e:
            logger.error(f"Redis setup failed: {e}")
            return False
    
    def _get_pending_jobs(self) -> list:
        """Get pending jobs from Redis stream"""
        try:
            # Read from consumer group
            messages = self.redis_client.xreadgroup(
                self.consumer_group,
                self.consumer_name,
                {"flows:jobs": ">"},
                count=WORKER_BATCH_SIZE,
                block=1000  # 1 second timeout
            )
            
            jobs = []
            for stream, msgs in messages:
                for msg_id, fields in msgs:
                    job = {
                        "id": msg_id,
                        "run_id": fields.get(b"run_id", b"").decode(),
                        "flow_id": fields.get(b"flow_id", b"").decode(),
                        "version": fields.get(b"version", b"").decode(),
                        "mode": fields.get(b"mode", b"live").decode(),
                        "trace_id": fields.get(b"trace_id", b"").decode()
                    }
                    jobs.append(job)
            
            return jobs
        except Exception as e:
            logger.error(f"Failed to get jobs: {e}")
            return []
    
    def _ack_job(self, job_id: str):
        """Acknowledge job completion"""
        try:
            self.redis_client.xack("flows:jobs", self.consumer_group, job_id)
            logger.debug(f"Acknowledged job {job_id}")
        except Exception as e:
            logger.error(f"Failed to ack job {job_id}: {e}")
    
    def _process_job(self, job: Dict[str, Any]) -> bool:
        """Process a single job"""
        run_id = job["run_id"]
        flow_id = job["flow_id"]
        mode = job["mode"]
        
        logger.info(f"Processing job {job['id']}: flow {flow_id}, run {run_id}, mode {mode}")
        
        try:
            # Process with timeout
            start_time = time.time()
            result = process_flow_run(run_id)
            took_ms = int((time.time() - start_time) * 1000)
            
            logger.info(f"Job {job['id']} completed in {took_ms}ms: {result}")
            return True
            
        except Exception as e:
            logger.error(f"Job {job['id']} failed: {e}")
            return False
    
    def run(self):
        """Main worker loop"""
        logger.info(f"Starting Flow worker {self.consumer_name}")
        
        if not self._setup_redis():
            logger.error("Failed to setup Redis, exiting")
            return
        
        processed_count = 0
        error_count = 0
        
        while self.running:
            try:
                # Get pending jobs
                jobs = self._get_pending_jobs()
                
                if not jobs:
                    # No jobs, sleep briefly
                    time.sleep(0.1)
                    continue
                
                # Process jobs
                for job in jobs:
                    if not self.running:
                        break
                    
                    success = self._process_job(job)
                    
                    if success:
                        self._ack_job(job["id"])
                        processed_count += 1
                    else:
                        error_count += 1
                        # Don't ack failed jobs, let them retry
                
                # Log stats every 100 jobs
                if (processed_count + error_count) % 100 == 0:
                    logger.info(f"Stats: processed={processed_count}, errors={error_count}")
                
            except Exception as e:
                logger.error(f"Worker loop error: {e}")
                time.sleep(1)
        
        logger.info(f"Flow worker {self.consumer_name} stopped. Processed: {processed_count}, Errors: {error_count}")

def main():
    """Main entry point"""
    worker = FlowWorker()
    worker.run()

if __name__ == "__main__":
    main()
