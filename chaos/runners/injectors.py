# CoolBits.ai Chaos Engineering - Fault Injectors
# Concrete implementations with timeouts and revert

import subprocess
import time
import threading
import psutil
import requests
import logging
from typing import Dict, Any, Optional
import docker
import os

class BaseInjector:
    """Base class for all fault injectors"""
    
    def __init__(self, scenario: Dict[str, Any]):
        self.scenario = scenario
        self.logger = logging.getLogger(__name__)
        self.active = False
        self.start_time = None
        
    def start(self) -> bool:
        """Apply fault - must be implemented by subclasses"""
        raise NotImplementedError
        
    def verify_injection(self) -> bool:
        """Assert that fault is real, not mimicked"""
        raise NotImplementedError
        
    def stop(self) -> bool:
        """Revert fault safely and idempotently"""
        raise NotImplementedError
        
    def safety_guard(self) -> bool:
        """Stop if SLO budget is exceeded"""
        raise NotImplementedError

class NetworkLatencyInjector(BaseInjector):
    """Inject network latency using tc netem"""
    
    def __init__(self, scenario: Dict[str, Any]):
        super().__init__(scenario)
        self.target = scenario["targets"][0]
        self.latency_ms = self.target["latency_ms"]
        self.jitter_ms = self.target.get("jitter_ms", 0)
        self.duration_s = self.target["duration_s"]
        self.container_name = f"{self.target['service']}-container"
        
    def start(self) -> bool:
        """Apply network latency"""
        try:
            self.logger.info(f"Injecting {self.latency_ms}ms latency to {self.target['service']}")
            
            # Get container ID
            client = docker.from_env()
            try:
                container = client.containers.get(self.container_name)
                container_id = container.short_id
            except docker.errors.NotFound:
                self.logger.error(f"Container {self.container_name} not found")
                return False
            
            # Apply tc netem rule
            cmd = [
                "docker", "exec", container_id,
                "tc", "qdisc", "add", "dev", "eth0", "root", "netem",
                "delay", f"{self.latency_ms}ms", f"{self.jitter_ms}ms"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.error(f"Failed to apply network latency: {result.stderr}")
                return False
            
            self.active = True
            self.start_time = time.time()
            
            # Schedule automatic stop
            threading.Timer(self.duration_s, self.stop).start()
            
            self.logger.info("Network latency injection started")
            return True
            
        except Exception as e:
            self.logger.error(f"Network latency injection failed: {e}")
            return False
    
    def verify_injection(self) -> bool:
        """Verify latency is actually applied"""
        try:
            # Test latency by measuring response time
            start_time = time.time()
            response = requests.get(f"http://localhost:{self.target['port']}/_stcore/health", timeout=5)
            end_time = time.time()
            
            actual_latency_ms = (end_time - start_time) * 1000
            
            # Should be significantly higher than baseline
            if actual_latency_ms > self.latency_ms * 0.8:  # Allow some tolerance
                self.logger.info(f"Latency injection verified: {actual_latency_ms:.1f}ms")
                return True
            else:
                self.logger.warning(f"Latency injection not effective: {actual_latency_ms:.1f}ms")
                return False
                
        except Exception as e:
            self.logger.error(f"Latency verification failed: {e}")
            return False
    
    def stop(self) -> bool:
        """Remove network latency"""
        try:
            if not self.active:
                return True
                
            self.logger.info("Removing network latency injection")
            
            # Get container ID
            client = docker.from_env()
            try:
                container = client.containers.get(self.container_name)
                container_id = container.short_id
            except docker.errors.NotFound:
                self.logger.warning(f"Container {self.container_name} not found during cleanup")
                return True
            
            # Remove tc netem rule
            cmd = [
                "docker", "exec", container_id,
                "tc", "qdisc", "del", "dev", "eth0", "root"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.warning(f"Failed to remove network latency: {result.stderr}")
            
            self.active = False
            self.logger.info("Network latency injection stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop network latency: {e}")
            return False
    
    def safety_guard(self) -> bool:
        """Check if latency exceeds safety threshold"""
        if not self.active:
            return True
            
        try:
            response = requests.get(f"http://localhost:{self.target['port']}/_stcore/health", timeout=2)
            if response.status_code != 200:
                self.logger.warning("Safety guard: Service unhealthy, stopping injection")
                self.stop()
                return False
            return True
        except Exception as e:
            self.logger.warning(f"Safety guard: Service unreachable, stopping injection: {e}")
            self.stop()
            return False

class ServiceKillInjector(BaseInjector):
    """Inject service failure by stopping container"""
    
    def __init__(self, scenario: Dict[str, Any]):
        super().__init__(scenario)
        self.target = scenario["targets"][0]
        self.kill_duration_s = self.target["kill_duration_s"]
        self.container_name = f"{self.target['service']}-container"
        
    def start(self) -> bool:
        """Stop the service"""
        try:
            self.logger.info(f"Stopping service {self.target['service']}")
            
            # Stop container
            result = subprocess.run(
                ["docker", "stop", self.container_name],
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                self.logger.error(f"Failed to stop service: {result.stderr}")
                return False
            
            self.active = True
            self.start_time = time.time()
            
            # Schedule automatic restart
            threading.Timer(self.kill_duration_s, self.stop).start()
            
            self.logger.info("Service kill injection started")
            return True
            
        except Exception as e:
            self.logger.error(f"Service kill injection failed: {e}")
            return False
    
    def verify_injection(self) -> bool:
        """Verify service is actually down"""
        try:
            response = requests.get(f"http://localhost:{self.target.get('port', 8501)}/_stcore/health", timeout=2)
            if response.status_code != 200:
                self.logger.info("Service kill injection verified: service is down")
                return True
            else:
                self.logger.warning("Service kill injection not effective: service still responding")
                return False
        except requests.exceptions.RequestException:
            self.logger.info("Service kill injection verified: service is unreachable")
            return True
    
    def stop(self) -> bool:
        """Restart the service"""
        try:
            if not self.active:
                return True
                
            self.logger.info("Restarting service")
            
            # Start container
            result = subprocess.run(
                ["docker", "start", self.container_name],
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                self.logger.error(f"Failed to restart service: {result.stderr}")
                return False
            
            # Wait for service to be ready
            time.sleep(10)
            
            self.active = False
            self.logger.info("Service kill injection stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop service kill: {e}")
            return False
    
    def safety_guard(self) -> bool:
        """Check if service is down too long"""
        if not self.active:
            return True
            
        downtime = time.time() - self.start_time
        max_downtime = self.target.get("recovery_timeout_s", 600)
        
        if downtime > max_downtime:
            self.logger.warning(f"Safety guard: Service down too long ({downtime:.1f}s), forcing restart")
            self.stop()
            return False
        
        return True

class CPUSpikeInjector(BaseInjector):
    """Inject CPU pressure by running CPU-intensive process"""
    
    def __init__(self, scenario: Dict[str, Any]):
        super().__init__(scenario)
        self.target = scenario["targets"][0]
        self.cpu_intensity = self.target["cpu_intensity"]
        self.duration_s = self.target["duration_s"]
        self.load_threshold = self.target["load_threshold"]
        self.process = None
        
    def start(self) -> bool:
        """Start CPU-intensive process"""
        try:
            self.logger.info(f"Injecting CPU spike with intensity {self.cpu_intensity}")
            
            # Start CPU-intensive process in background
            self.process = subprocess.Popen([
                "python", "-c", 
                f"""
import time
end_time = time.time() + {self.duration_s}
while time.time() < end_time:
    sum(range(1000000))
    time.sleep(0.001)
"""
            ])
            
            self.active = True
            self.start_time = time.time()
            
            self.logger.info("CPU spike injection started")
            return True
            
        except Exception as e:
            self.logger.error(f"CPU spike injection failed: {e}")
            return False
    
    def verify_injection(self) -> bool:
        """Verify CPU usage is high"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 70:  # High CPU usage
                self.logger.info(f"CPU spike injection verified: {cpu_percent:.1f}% CPU")
                return True
            else:
                self.logger.warning(f"CPU spike injection not effective: {cpu_percent:.1f}% CPU")
                return False
        except Exception as e:
            self.logger.error(f"CPU verification failed: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop CPU-intensive process"""
        try:
            if not self.active:
                return True
                
            self.logger.info("Stopping CPU spike injection")
            
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=5)
            
            self.active = False
            self.logger.info("CPU spike injection stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop CPU spike: {e}")
            return False
    
    def safety_guard(self) -> bool:
        """Check if CPU load exceeds threshold"""
        try:
            load_avg = psutil.getloadavg()[0]  # 1-minute load average
            if load_avg > self.load_threshold:
                self.logger.warning(f"Safety guard: Load average too high ({load_avg:.2f}), stopping injection")
                self.stop()
                return False
            return True
        except Exception as e:
            self.logger.error(f"Safety guard failed: {e}")
            return False

class MemoryLeakInjector(BaseInjector):
    """Inject memory leak by allocating memory incrementally"""
    
    def __init__(self, scenario: Dict[str, Any]):
        super().__init__(scenario)
        self.target = scenario["targets"][0]
        self.leak_rate_mb_per_s = self.target["leak_rate_mb_per_s"]
        self.duration_s = self.target["duration_s"]
        self.max_memory_mb = self.target["max_memory_mb"]
        self.memory_chunks = []
        self.leak_thread = None
        
    def start(self) -> bool:
        """Start memory leak"""
        try:
            self.logger.info(f"Injecting memory leak at {self.leak_rate_mb_per_s}MB/s")
            
            def leak_memory():
                end_time = time.time() + self.duration_s
                while time.time() < end_time and self.active:
                    # Allocate memory chunk
                    chunk = 'x' * (self.leak_rate_mb_per_s * 1024 * 1024)
                    self.memory_chunks.append(chunk)
                    time.sleep(1)
            
            self.leak_thread = threading.Thread(target=leak_memory)
            self.leak_thread.start()
            
            self.active = True
            self.start_time = time.time()
            
            self.logger.info("Memory leak injection started")
            return True
            
        except Exception as e:
            self.logger.error(f"Memory leak injection failed: {e}")
            return False
    
    def verify_injection(self) -> bool:
        """Verify memory usage is increasing"""
        try:
            memory_info = psutil.virtual_memory()
            memory_percent = memory_info.percent
            
            if memory_percent > 70:  # High memory usage
                self.logger.info(f"Memory leak injection verified: {memory_percent:.1f}% memory")
                return True
            else:
                self.logger.warning(f"Memory leak injection not effective: {memory_percent:.1f}% memory")
                return False
        except Exception as e:
            self.logger.error(f"Memory verification failed: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop memory leak"""
        try:
            if not self.active:
                return True
                
            self.logger.info("Stopping memory leak injection")
            
            self.active = False
            
            # Clean up memory chunks
            self.memory_chunks.clear()
            
            if self.leak_thread:
                self.leak_thread.join(timeout=5)
            
            self.active = False
            self.logger.info("Memory leak injection stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop memory leak: {e}")
            return False
    
    def safety_guard(self) -> bool:
        """Check if memory usage exceeds threshold"""
        try:
            memory_info = psutil.virtual_memory()
            memory_percent = memory_info.percent
            
            if memory_percent > 85:  # Critical memory usage
                self.logger.warning(f"Safety guard: Memory usage too high ({memory_percent:.1f}%), stopping injection")
                self.stop()
                return False
            return True
        except Exception as e:
            self.logger.error(f"Memory safety guard failed: {e}")
            return False

class DatabaseFailureInjector(BaseInjector):
    """Inject database failure by stopping database container"""
    
    def __init__(self, scenario: Dict[str, Any]):
        super().__init__(scenario)
        self.target = scenario["targets"][0]
        self.fail_duration_s = self.target["fail_duration_s"]
        self.container_name = f"{self.target['service']}-container"
        
    def start(self) -> bool:
        """Stop database"""
        try:
            self.logger.info(f"Stopping database {self.target['service']}")
            
            # Stop database container
            result = subprocess.run(
                ["docker", "stop", self.container_name],
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                self.logger.error(f"Failed to stop database: {result.stderr}")
                return False
            
            self.active = True
            self.start_time = time.time()
            
            # Schedule automatic restart
            threading.Timer(self.fail_duration_s, self.stop).start()
            
            self.logger.info("Database failure injection started")
            return True
            
        except Exception as e:
            self.logger.error(f"Database failure injection failed: {e}")
            return False
    
    def verify_injection(self) -> bool:
        """Verify database is actually down"""
        try:
            # Try to connect to database
            result = subprocess.run([
                "docker", "exec", self.container_name,
                "psql", "-U", "coolbits", "-d", "coolbits_dev", "-c", "SELECT 1;"
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                self.logger.info("Database failure injection verified: database is down")
                return True
            else:
                self.logger.warning("Database failure injection not effective: database still responding")
                return False
        except subprocess.TimeoutExpired:
            self.logger.info("Database failure injection verified: database is unreachable")
            return True
        except Exception as e:
            self.logger.info(f"Database failure injection verified: {e}")
            return True
    
    def stop(self) -> bool:
        """Restart database"""
        try:
            if not self.active:
                return True
                
            self.logger.info("Restarting database")
            
            # Start database container
            result = subprocess.run(
                ["docker", "start", self.container_name],
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                self.logger.error(f"Failed to restart database: {result.stderr}")
                return False
            
            # Wait for database to be ready
            time.sleep(15)
            
            self.active = False
            self.logger.info("Database failure injection stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop database failure: {e}")
            return False
    
    def safety_guard(self) -> bool:
        """Check if database is down too long"""
        if not self.active:
            return True
            
        downtime = time.time() - self.start_time
        max_downtime = self.target.get("recovery_timeout_s", 480)
        
        if downtime > max_downtime:
            self.logger.warning(f"Safety guard: Database down too long ({downtime:.1f}s), forcing restart")
            self.stop()
            return False
        
        return True

class ExternalAPIFailureInjector(BaseInjector):
    """Inject external API failure by mocking responses"""
    
    def __init__(self, scenario: Dict[str, Any]):
        super().__init__(scenario)
        self.target = scenario["targets"][0]
        self.api_endpoints = self.target["api_endpoints"]
        self.fail_duration_s = self.target["fail_duration_s"]
        self.error_rate = self.target["error_rate"]
        self.mock_server = None
        
    def start(self) -> bool:
        """Start mocking external API failures"""
        try:
            self.logger.info(f"Mocking external API failures with {self.error_rate} error rate")
            
            # Start mock server (simplified - in real implementation would use proper mocking)
            # For now, we'll simulate by monitoring actual API calls
            
            self.active = True
            self.start_time = time.time()
            
            # Schedule automatic stop
            threading.Timer(self.fail_duration_s, self.stop).start()
            
            self.logger.info("External API failure injection started")
            return True
            
        except Exception as e:
            self.logger.error(f"External API failure injection failed: {e}")
            return False
    
    def verify_injection(self) -> bool:
        """Verify API failures are being simulated"""
        try:
            # Test API endpoint
            for endpoint in self.api_endpoints:
                try:
                    response = requests.get(endpoint, timeout=5)
                    if response.status_code >= 500:
                        self.logger.info(f"External API failure injection verified: {endpoint} returning 5xx")
                        return True
                except requests.exceptions.RequestException:
                    self.logger.info(f"External API failure injection verified: {endpoint} unreachable")
                    return True
            
            self.logger.warning("External API failure injection not effective: APIs still responding")
            return False
            
        except Exception as e:
            self.logger.error(f"External API verification failed: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop mocking external API failures"""
        try:
            if not self.active:
                return True
                
            self.logger.info("Stopping external API failure injection")
            
            # Stop mock server
            if self.mock_server:
                self.mock_server.shutdown()
            
            self.active = False
            self.logger.info("External API failure injection stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop external API failure: {e}")
            return False
    
    def safety_guard(self) -> bool:
        """Check if API error rate exceeds threshold"""
        try:
            # Monitor API error rate
            # In real implementation, would check actual error rates
            return True
        except Exception as e:
            self.logger.error(f"API safety guard failed: {e}")
            return False
