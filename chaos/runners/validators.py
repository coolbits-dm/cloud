# CoolBits.ai Chaos Engineering - SLO Validators and Auto-heal
# SLO gates, auto-heal, and monitoring integration

import requests
import time
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class SLOThresholds:
    """SLO threshold configuration"""
    p95_ms: float
    error_rate: float
    availability: float

@dataclass
class SLOMeasurement:
    """SLO measurement result"""
    p95_ms: float
    error_rate: float
    availability: float
    timestamp: datetime
    sample_size: int

class SLOValidator:
    """SLO validation and monitoring"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for SLO validation"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('chaos/slo_validation.log'),
                logging.StreamHandler()
            ]
        )
    
    def fetch_slo_window(self, service: str, minutes: int = 10) -> SLOMeasurement:
        """Fetch SLO metrics from Cloud Monitoring API"""
        try:
            # In real implementation, would query Google Cloud Monitoring API
            # For now, simulate by making requests to the service
            
            self.logger.info(f"Fetching SLO metrics for {service} over {minutes} minutes")
            
            # Simulate SLO measurement
            response_times = []
            errors = 0
            total_requests = 0
            
            # Make sample requests
            for _ in range(100):  # Sample 100 requests
                try:
                    start_time = time.time()
                    response = requests.get(f"http://localhost:8501/_stcore/health", timeout=5)
                    end_time = time.time()
                    
                    response_time_ms = (end_time - start_time) * 1000
                    response_times.append(response_time_ms)
                    
                    if response.status_code >= 500:
                        errors += 1
                    
                    total_requests += 1
                    
                except requests.exceptions.RequestException:
                    errors += 1
                    total_requests += 1
                
                time.sleep(0.1)  # Small delay between requests
            
            # Calculate metrics
            if response_times:
                response_times.sort()
                p95_index = int(len(response_times) * 0.95)
                p95_ms = response_times[p95_index] if p95_index < len(response_times) else response_times[-1]
            else:
                p95_ms = 0
            
            error_rate = errors / total_requests if total_requests > 0 else 0
            availability = 1.0 - error_rate
            
            measurement = SLOMeasurement(
                p95_ms=p95_ms,
                error_rate=error_rate,
                availability=availability,
                timestamp=datetime.now(),
                sample_size=total_requests
            )
            
            self.logger.info(f"SLO measurement: p95={p95_ms:.1f}ms, error_rate={error_rate:.3f}, availability={availability:.3f}")
            
            return measurement
            
        except Exception as e:
            self.logger.error(f"Failed to fetch SLO metrics: {e}")
            # Return default measurement
            return SLOMeasurement(
                p95_ms=0,
                error_rate=1.0,
                availability=0.0,
                timestamp=datetime.now(),
                sample_size=0
            )
    
    def slo_ok(self, measurement: SLOMeasurement, thresholds: SLOThresholds) -> bool:
        """Check if SLO metrics meet thresholds"""
        try:
            self.logger.info(f"Checking SLO: p95={measurement.p95_ms:.1f}ms <= {thresholds.p95_ms}ms")
            self.logger.info(f"Checking SLO: error_rate={measurement.error_rate:.3f} <= {thresholds.error_rate}")
            self.logger.info(f"Checking SLO: availability={measurement.availability:.3f} >= {thresholds.availability}")
            
            p95_ok = measurement.p95_ms <= thresholds.p95_ms
            error_rate_ok = measurement.error_rate <= thresholds.error_rate
            availability_ok = measurement.availability >= thresholds.availability
            
            overall_ok = p95_ok and error_rate_ok and availability_ok
            
            if overall_ok:
                self.logger.info("SLO check PASSED")
            else:
                self.logger.error("SLO check FAILED")
                if not p95_ok:
                    self.logger.error(f"p95 threshold violated: {measurement.p95_ms:.1f}ms > {thresholds.p95_ms}ms")
                if not error_rate_ok:
                    self.logger.error(f"Error rate threshold violated: {measurement.error_rate:.3f} > {thresholds.error_rate}")
                if not availability_ok:
                    self.logger.error(f"Availability threshold violated: {measurement.availability:.3f} < {thresholds.availability}")
            
            return overall_ok
            
        except Exception as e:
            self.logger.error(f"SLO check failed: {e}")
            return False
    
    def check_auto_heal_trigger(self, measurement: SLOMeasurement, scenario: Dict[str, Any]) -> bool:
        """Check if auto-heal should be triggered"""
        try:
            rollback_config = scenario.get("rollback", {})
            trigger_threshold = rollback_config.get("trigger_threshold", 0.05)
            
            if measurement.error_rate > trigger_threshold:
                self.logger.warning(f"Auto-heal trigger: error_rate {measurement.error_rate:.3f} > {trigger_threshold}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Auto-heal check failed: {e}")
            return False

class AutoHealManager:
    """Auto-heal and rollback management"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for auto-heal"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('chaos/auto_heal.log'),
                logging.StreamHandler()
            ]
        )
    
    def canary_rollback(self, scenario: Dict[str, Any]) -> bool:
        """Execute canary rollback"""
        try:
            self.logger.info("Executing canary rollback")
            
            # In real implementation, would use gcloud to rollback Cloud Run service
            # For now, simulate by restarting the service
            
            service_name = scenario["targets"][0]["service"]
            container_name = f"{service_name}-container"
            
            # Restart service
            result = subprocess.run([
                "docker", "restart", container_name
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"Canary rollback failed: {result.stderr}")
                return False
            
            # Wait for service to be ready
            time.sleep(10)
            
            # Verify rollback
            if self.verify_rollback(service_name):
                self.logger.info("Canary rollback completed successfully")
                return True
            else:
                self.logger.error("Canary rollback verification failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Canary rollback failed: {e}")
            return False
    
    def verify_rollback(self, service_name: str) -> bool:
        """Verify rollback was successful"""
        try:
            # Check if service is healthy
            response = requests.get("http://localhost:8501/_stcore/health", timeout=10)
            
            if response.status_code == 200:
                self.logger.info("Rollback verification: service is healthy")
                return True
            else:
                self.logger.error(f"Rollback verification: service unhealthy (status {response.status_code})")
                return False
                
        except Exception as e:
            self.logger.error(f"Rollback verification failed: {e}")
            return False
    
    def emergency_stop(self, scenario: Dict[str, Any]) -> bool:
        """Emergency stop all chaos experiments"""
        try:
            self.logger.warning("Executing emergency stop")
            
            # Stop all running containers
            result = subprocess.run([
                "docker", "stop", "$(docker ps -q)"
            ], shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"Emergency stop failed: {result.stderr}")
                return False
            
            # Restart services
            result = subprocess.run([
                "docker-compose", "-f", "docker-compose.dev.yml", "up", "-d"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"Service restart failed: {result.stderr}")
                return False
            
            self.logger.info("Emergency stop completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Emergency stop failed: {e}")
            return False

class ChaosMonitor:
    """Chaos experiment monitoring and observability"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for chaos monitoring"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('chaos/chaos_monitor.log'),
                logging.StreamHandler()
            ]
        )
    
    def log_experiment_start(self, scenario: Dict[str, Any]):
        """Log experiment start"""
        try:
            log_entry = {
                "event": "experiment_start",
                "scenario": scenario["name"],
                "timestamp": datetime.now().isoformat(),
                "targets": scenario["targets"],
                "slo": scenario["slo"]
            }
            
            self.logger.info(f"Chaos experiment started: {scenario['name']}")
            self._write_audit_log(log_entry)
            
        except Exception as e:
            self.logger.error(f"Failed to log experiment start: {e}")
    
    def log_experiment_end(self, scenario: Dict[str, Any], result: Dict[str, Any]):
        """Log experiment end"""
        try:
            log_entry = {
                "event": "experiment_end",
                "scenario": scenario["name"],
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
            
            self.logger.info(f"Chaos experiment ended: {scenario['name']} - {result.get('verdict', 'UNKNOWN')}")
            self._write_audit_log(log_entry)
            
        except Exception as e:
            self.logger.error(f"Failed to log experiment end: {e}")
    
    def log_slo_measurement(self, scenario: Dict[str, Any], measurement: SLOMeasurement):
        """Log SLO measurement"""
        try:
            log_entry = {
                "event": "slo_measurement",
                "scenario": scenario["name"],
                "timestamp": datetime.now().isoformat(),
                "measurement": {
                    "p95_ms": measurement.p95_ms,
                    "error_rate": measurement.error_rate,
                    "availability": measurement.availability,
                    "sample_size": measurement.sample_size
                }
            }
            
            self.logger.info(f"SLO measurement: p95={measurement.p95_ms:.1f}ms, error_rate={measurement.error_rate:.3f}")
            self._write_audit_log(log_entry)
            
        except Exception as e:
            self.logger.error(f"Failed to log SLO measurement: {e}")
    
    def log_auto_heal(self, scenario: Dict[str, Any], action: str, success: bool):
        """Log auto-heal action"""
        try:
            log_entry = {
                "event": "auto_heal",
                "scenario": scenario["name"],
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "success": success
            }
            
            self.logger.info(f"Auto-heal action: {action} - {'SUCCESS' if success else 'FAILED'}")
            self._write_audit_log(log_entry)
            
        except Exception as e:
            self.logger.error(f"Failed to log auto-heal: {e}")
    
    def _write_audit_log(self, log_entry: Dict[str, Any]):
        """Write audit log entry"""
        try:
            # Create logs directory if it doesn't exist
            import os
            os.makedirs("logs", exist_ok=True)
            
            # Write to monthly log file
            log_file = f"logs/chaos-{datetime.now().strftime('%Y%m')}.jsonl"
            
            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
                
        except Exception as e:
            self.logger.error(f"Failed to write audit log: {e}")
    
    def generate_chaos_report(self, scenario: Dict[str, Any], result: Dict[str, Any]) -> str:
        """Generate chaos experiment report"""
        try:
            report = f"""
# Chaos Experiment Report

**Scenario**: {scenario['name']}
**Description**: {scenario.get('description', 'N/A')}
**Timestamp**: {datetime.now().isoformat()}

## Results

- **Verdict**: {result.get('verdict', 'UNKNOWN')}
- **Duration**: {result.get('stop', 0) - result.get('start', 0):.1f} seconds
- **SLO Before**: {result.get('slo_before', {})}
- **SLO After**: {result.get('slo_after', {})}

## Actions Taken

{result.get('actions', 'None')}

## Recommendations

{self._generate_recommendations(scenario, result)}
"""
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            return f"Report generation failed: {e}"
    
    def _generate_recommendations(self, scenario: Dict[str, Any], result: Dict[str, Any]) -> str:
        """Generate recommendations based on results"""
        recommendations = []
        
        if result.get('verdict') == 'FAIL':
            recommendations.append("- Investigate root cause of SLO violations")
            recommendations.append("- Review auto-heal mechanisms")
            recommendations.append("- Consider adjusting SLO thresholds")
        
        if result.get('slo_after', {}).get('p95_ms', 0) > scenario.get('slo', {}).get('p95_ms', 0):
            recommendations.append("- Optimize application performance")
            recommendations.append("- Review resource allocation")
        
        if result.get('slo_after', {}).get('error_rate', 0) > scenario.get('slo', {}).get('error_rate', 0):
            recommendations.append("- Improve error handling")
            recommendations.append("- Review monitoring and alerting")
        
        return "\n".join(recommendations) if recommendations else "- No specific recommendations"
