# CoolBits.ai Health Standardization & SLO Definition
# ==================================================

from datetime import datetime


class HealthStandardization:
    """Standardize health endpoints and define SLOs."""

    def __init__(self):
        self.health_schema = {
            "ok": bool,
            "commitSha": str,
            "buildTime": str,
            "node": str,
            "env": str,
            "appMode": str,
            "schemaVersion": str,
            "uptimeSec": float,
            "timestamp": str,
        }

        self.slo_definitions = {
            "response_time_p95": {
                "target": 400,  # milliseconds
                "measurement": "p95",
                "window": "5m",
            },
            "error_rate_5xx": {
                "target": 1.0,  # percentage
                "measurement": "5xx_percentage",
                "window": "5m",
            },
            "error_budget_monthly": {
                "target": 1.0,  # percentage
                "measurement": "monthly_error_budget",
                "window": "30d",
            },
        }

    def create_standardized_health_endpoint(self):
        """Create standardized health endpoint."""
        print("🏥 CREATING STANDARDIZED HEALTH ENDPOINT")
        print("=" * 45)

        health_endpoint_script = '''
import json
import time
import subprocess
import psutil
from datetime import datetime
from flask import Flask, jsonify

app = Flask(__name__)

class StandardizedHealthEndpoint:
    """Standardized health endpoint for CoolBits.ai."""
    
    def __init__(self):
        self.start_time = time.time()
        self.schema_version = "1.0.0"
    
    def get_commit_sha(self):
        """Get current commit SHA."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()[:8]
            else:
                return "unknown"
        except Exception:
            return "unknown"
    
    def get_build_time(self):
        """Get build timestamp."""
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%ci"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return datetime.now().isoformat()
        except Exception:
            return datetime.now().isoformat()
    
    def get_node_info(self):
        """Get node information."""
        try:
            return f"{psutil.cpu_count()} cores, {psutil.virtual_memory().total // (1024**3)}GB RAM"
        except Exception:
            return "unknown"
    
    def get_uptime_seconds(self):
        """Get uptime in seconds."""
        return time.time() - self.start_time
    
    def generate_health_response(self):
        """Generate standardized health response."""
        return {
            "ok": True,
            "commitSha": self.get_commit_sha(),
            "buildTime": self.get_build_time(),
            "node": self.get_node_info(),
            "env": os.getenv("ENVIRONMENT", "development"),
            "appMode": os.getenv("APP_MODE", "production"),
            "schemaVersion": self.schema_version,
            "uptimeSec": self.get_uptime_seconds(),
            "timestamp": datetime.now().isoformat()
        }

# Initialize health endpoint
health_endpoint = StandardizedHealthEndpoint()

@app.route("/api/health", methods=["GET"])
def health():
    """Standardized health endpoint."""
    return jsonify(health_endpoint.generate_health_response())

@app.route("/api/health/ready", methods=["GET"])
def readiness():
    """Readiness probe."""
    health_data = health_endpoint.generate_health_response()
    
    # Check if all required components are ready
    if health_data["commitSha"] != "unknown" and health_data["uptimeSec"] > 5:
        return jsonify({"status": "ready", "health": health_data}), 200
    else:
        return jsonify({"status": "not_ready", "health": health_data}), 503

@app.route("/api/health/live", methods=["GET"])
def liveness():
    """Liveness probe."""
    return jsonify({"status": "alive", "timestamp": datetime.now().isoformat()}), 200

if __name__ == "__main__":
    print("🏥 Starting CoolBits.ai standardized health endpoint...")
    app.run(host="0.0.0.0", port=8501, debug=False)
'''

        with open("standardized_health_endpoint.py", "w", encoding="utf-8") as f:
            f.write(health_endpoint_script)

        print("✅ Standardized health endpoint created")
        return True

    def create_slo_monitoring(self):
        """Create SLO monitoring system."""
        print("\n📊 CREATING SLO MONITORING")
        print("=" * 30)

        slo_monitoring_script = '''
import json
import time
import requests
import statistics
from datetime import datetime, timedelta
from collections import deque
from pathlib import Path

class SLOMonitor:
    """SLO monitoring for CoolBits.ai."""
    
    def __init__(self):
        self.slo_definitions = {
            "response_time_p95": {
                "target": 400,  # milliseconds
                "measurement": "p95",
                "window": "5m"
            },
            "error_rate_5xx": {
                "target": 1.0,  # percentage
                "measurement": "5xx_percentage",
                "window": "5m"
            },
            "error_budget_monthly": {
                "target": 1.0,  # percentage
                "measurement": "monthly_error_budget",
                "window": "30d"
            }
        }
        
        self.metrics_buffer = deque(maxlen=1000)  # Keep last 1000 measurements
        self.error_budget_file = "error_budget.json"
    
    def record_response_time(self, response_time_ms: float, status_code: int):
        """Record response time and status code."""
        metric = {
            "timestamp": datetime.now().isoformat(),
            "response_time_ms": response_time_ms,
            "status_code": status_code,
            "is_5xx": status_code >= 500
        }
        
        self.metrics_buffer.append(metric)
        
        # Update error budget
        self._update_error_budget(metric)
    
    def _update_error_budget(self, metric):
        """Update monthly error budget."""
        try:
            if Path(self.error_budget_file).exists():
                with open(self.error_budget_file, "r") as f:
                    budget_data = json.load(f)
            else:
                budget_data = {
                    "monthly_requests": 0,
                    "monthly_errors": 0,
                    "start_date": datetime.now().isoformat()
                }
            
            budget_data["monthly_requests"] += 1
            if metric["is_5xx"]:
                budget_data["monthly_errors"] += 1
            
            # Calculate error rate
            if budget_data["monthly_requests"] > 0:
                budget_data["error_rate"] = (budget_data["monthly_errors"] / budget_data["monthly_requests"]) * 100
            
            with open(self.error_budget_file, "w") as f:
                json.dump(budget_data, f, indent=2)
                
        except Exception as e:
            print(f"❌ Error budget update failed: {e}")
    
    def check_slo_response_time(self):
        """Check response time SLO."""
        if len(self.metrics_buffer) < 10:
            return {"status": "insufficient_data", "slo": "response_time_p95"}
        
        # Get last 5 minutes of data
        cutoff_time = datetime.now() - timedelta(minutes=5)
        recent_metrics = [
            m for m in self.metrics_buffer
            if datetime.fromisoformat(m["timestamp"]) > cutoff_time
        ]
        
        if not recent_metrics:
            return {"status": "insufficient_data", "slo": "response_time_p95"}
        
        response_times = [m["response_time_ms"] for m in recent_metrics]
        p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        
        target = self.slo_definitions["response_time_p95"]["target"]
        slo_met = p95_response_time <= target
        
        return {
            "status": "met" if slo_met else "violated",
            "slo": "response_time_p95",
            "current": p95_response_time,
            "target": target,
            "measurements": len(recent_metrics)
        }
    
    def check_slo_error_rate(self):
        """Check error rate SLO."""
        if len(self.metrics_buffer) < 10:
            return {"status": "insufficient_data", "slo": "error_rate_5xx"}
        
        # Get last 5 minutes of data
        cutoff_time = datetime.now() - timedelta(minutes=5)
        recent_metrics = [
            m for m in self.metrics_buffer
            if datetime.fromisoformat(m["timestamp"]) > cutoff_time
        ]
        
        if not recent_metrics:
            return {"status": "insufficient_data", "slo": "error_rate_5xx"}
        
        total_requests = len(recent_metrics)
        error_requests = sum(1 for m in recent_metrics if m["is_5xx"])
        error_rate = (error_requests / total_requests) * 100
        
        target = self.slo_definitions["error_rate_5xx"]["target"]
        slo_met = error_rate <= target
        
        return {
            "status": "met" if slo_met else "violated",
            "slo": "error_rate_5xx",
            "current": error_rate,
            "target": target,
            "total_requests": total_requests,
            "error_requests": error_requests
        }
    
    def check_slo_error_budget(self):
        """Check monthly error budget SLO."""
        try:
            if not Path(self.error_budget_file).exists():
                return {"status": "insufficient_data", "slo": "error_budget_monthly"}
            
            with open(self.error_budget_file, "r") as f:
                budget_data = json.load(f)
            
            if "error_rate" not in budget_data:
                return {"status": "insufficient_data", "slo": "error_budget_monthly"}
            
            current_error_rate = budget_data["error_rate"]
            target = self.slo_definitions["error_budget_monthly"]["target"]
            slo_met = current_error_rate <= target
            
            return {
                "status": "met" if slo_met else "violated",
                "slo": "error_budget_monthly",
                "current": current_error_rate,
                "target": target,
                "monthly_requests": budget_data.get("monthly_requests", 0),
                "monthly_errors": budget_data.get("monthly_errors", 0)
            }
            
        except Exception as e:
            return {"status": "error", "slo": "error_budget_monthly", "error": str(e)}
    
    def check_all_slos(self):
        """Check all SLOs."""
        slo_results = {
            "timestamp": datetime.now().isoformat(),
            "slos": {}
        }
        
        slo_results["slos"]["response_time_p95"] = self.check_slo_response_time()
        slo_results["slos"]["error_rate_5xx"] = self.check_slo_error_rate()
        slo_results["slos"]["error_budget_monthly"] = self.check_slo_error_budget()
        
        # Overall SLO status
        all_met = all(
            slo["status"] == "met" or slo["status"] == "insufficient_data"
            for slo in slo_results["slos"].values()
        )
        
        slo_results["overall_status"] = "met" if all_met else "violated"
        
        return slo_results
    
    def generate_slo_report(self):
        """Generate SLO report."""
        slo_results = self.check_all_slos()
        
        report_file = f"slo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(slo_results, f, indent=2)
        
        print(f"📊 SLO report generated: {report_file}")
        return slo_results

if __name__ == "__main__":
    monitor = SLOMonitor()
    
    # Simulate some metrics
    for i in range(100):
        response_time = 200 + (i % 10) * 50  # 200-700ms
        status_code = 200 if i < 95 else 500  # 5% errors
        monitor.record_response_time(response_time, status_code)
    
    # Generate report
    report = monitor.generate_slo_report()
    print(json.dumps(report, indent=2))
'''

        with open("slo_monitoring.py", "w", encoding="utf-8") as f:
            f.write(slo_monitoring_script)

        print("✅ SLO monitoring system created")
        return True

    def create_canary_slo_integration(self):
        """Create canary deployment with SLO integration."""
        print("\n🚀 CREATING CANARY SLO INTEGRATION")
        print("=" * 40)

        canary_slo_script = '''
import json
import time
import requests
from datetime import datetime, timedelta
from slo_monitoring import SLOMonitor

class CanarySLOIntegration:
    """Canary deployment with SLO integration."""
    
    def __init__(self):
        self.slo_monitor = SLOMonitor()
        self.canary_config = {
            "traffic_percentage": 10,
            "slo_check_duration": 30,  # minutes
            "slo_thresholds": {
                "response_time_p95": 400,
                "error_rate_5xx": 1.0
            }
        }
    
    def run_canary_with_slo_check(self, service_url: str, new_image: str):
        """Run canary deployment with SLO monitoring."""
        print(f"🚀 Starting canary deployment for {service_url}")
        print(f"   New image: {new_image}")
        print(f"   Traffic: {self.canary_config['traffic_percentage']}%")
        
        # Start canary deployment
        canary_start_time = datetime.now()
        
        # Monitor SLOs for specified duration
        slo_check_duration = timedelta(minutes=self.canary_config['slo_check_duration'])
        end_time = canary_start_time + slo_check_duration
        
        print(f"📊 Monitoring SLOs for {self.canary_config['slo_check_duration']} minutes...")
        
        slo_violations = []
        
        while datetime.now() < end_time:
            # Check health endpoint
            try:
                start_time = time.time()
                response = requests.get(f"{service_url}/api/health", timeout=10)
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                
                # Record metric
                self.slo_monitor.record_response_time(response_time, response.status_code)
                
                # Check SLOs
                slo_results = self.slo_monitor.check_all_slos()
                
                if slo_results["overall_status"] == "violated":
                    violation = {
                        "timestamp": datetime.now().isoformat(),
                        "slos": slo_results["slos"]
                    }
                    slo_violations.append(violation)
                    print(f"⚠️ SLO violation detected: {violation}")
                
            except Exception as e:
                print(f"❌ Health check failed: {e}")
                self.slo_monitor.record_response_time(5000, 500)  # Record as error
            
            time.sleep(30)  # Check every 30 seconds
        
        # Evaluate canary success
        if len(slo_violations) == 0:
            print("✅ Canary deployment successful - all SLOs met")
            return self._promote_canary(service_url, new_image)
        else:
            print(f"❌ Canary deployment failed - {len(slo_violations)} SLO violations")
            return self._rollback_canary(service_url)
    
    def _promote_canary(self, service_url: str, new_image: str):
        """Promote canary to production."""
        print(f"🎉 Promoting canary to production: {new_image}")
        
        # Here you would implement actual promotion logic
        # For now, just simulate success
        return {
            "status": "promoted",
            "image": new_image,
            "timestamp": datetime.now().isoformat()
        }
    
    def _rollback_canary(self, service_url: str):
        """Rollback canary deployment."""
        print(f"🔄 Rolling back canary deployment")
        
        # Here you would implement actual rollback logic
        # For now, just simulate rollback
        return {
            "status": "rolled_back",
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_canary_report(self, service_url: str):
        """Generate canary deployment report."""
        slo_results = self.slo_monitor.check_all_slos()
        
        report = {
            "service_url": service_url,
            "timestamp": datetime.now().isoformat(),
            "slo_status": slo_results,
            "canary_config": self.canary_config
        }
        
        report_file = f"canary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Canary report generated: {report_file}")
        return report

if __name__ == "__main__":
    canary = CanarySLOIntegration()
    
    # Simulate canary deployment
    result = canary.run_canary_with_slo_check(
        service_url="http://localhost:8501",
        new_image="coolbits-ai:v1.2.3"
    )
    
    print(f"🎯 Canary result: {result}")
'''

        with open("canary_slo_integration.py", "w", encoding="utf-8") as f:
            f.write(canary_slo_script)

        print("✅ Canary SLO integration created")
        return True

    def create_audit_logging(self):
        """Create JSONL audit logging for sensitive endpoints."""
        print("\n📝 CREATING AUDIT LOGGING")
        print("=" * 30)

        audit_logging_script = '''
import json
import time
import hashlib
from datetime import datetime
from flask import Flask, request, g
from functools import wraps

app = Flask(__name__)

class AuditLogger:
    """JSONL audit logging for CoolBits.ai."""
    
    def __init__(self, log_file="audit_log.jsonl"):
        self.log_file = log_file
        self.sensitive_endpoints = [
            "/api/open-cursor",
            "/api/connect-gcloud",
            "/api/admin/users",
            "/api/admin/keys",
            "/api/admin/deploy"
        ]
    
    def log_audit_event(self, event_data):
        """Log audit event to JSONL file."""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_id": self._generate_event_id(),
            **event_data
        }
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(audit_entry) + "\\n")
    
    def _generate_event_id(self):
        """Generate unique event ID."""
        timestamp = datetime.now().isoformat()
        return hashlib.sha256(timestamp.encode()).hexdigest()[:16]
    
    def _get_client_ip(self):
        """Get client IP address."""
        return request.headers.get('X-Forwarded-For', request.remote_addr)
    
    def _get_signature_prefix(self, signature):
        """Get signature prefix for logging."""
        if signature and len(signature) > 8:
            return signature[:8] + "..."
        return "none"
    
    def audit_sensitive_endpoint(self, endpoint_name):
        """Decorator for auditing sensitive endpoints."""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                start_time = time.time()
                
                # Extract request information
                request_data = {
                    "who": getattr(g, 'user_id', 'anonymous'),
                    "action": endpoint_name,
                    "resource": request.path,
                    "ip": self._get_client_ip(),
                    "method": request.method,
                    "user_agent": request.headers.get('User-Agent', 'unknown'),
                    "signature_prefix": self._get_signature_prefix(
                        request.headers.get('Authorization', '')
                    )
                }
                
                try:
                    # Execute the endpoint
                    result = f(*args, **kwargs)
                    
                    # Log successful access
                    request_data.update({
                        "status": "success",
                        "took_ms": round((time.time() - start_time) * 1000, 2),
                        "response_code": 200
                    })
                    
                    self.log_audit_event(request_data)
                    return result
                    
                except Exception as e:
                    # Log failed access
                    request_data.update({
                        "status": "error",
                        "took_ms": round((time.time() - start_time) * 1000, 2),
                        "error": str(e),
                        "response_code": 500
                    })
                    
                    self.log_audit_event(request_data)
                    raise
            
            return decorated_function
        return decorator

# Initialize audit logger
audit_logger = AuditLogger()

@app.route("/api/open-cursor", methods=["POST"])
@audit_logger.audit_sensitive_endpoint("open_cursor")
def open_cursor():
    """Open Cursor IDE - sensitive endpoint."""
    return {"status": "success", "message": "Cursor opened"}

@app.route("/api/connect-gcloud", methods=["POST"])
@audit_logger.audit_sensitive_endpoint("connect_gcloud")
def connect_gcloud():
    """Connect to Google Cloud - sensitive endpoint."""
    return {"status": "success", "message": "GCloud connected"}

@app.route("/api/admin/users", methods=["GET", "POST", "PUT", "DELETE"])
@audit_logger.audit_sensitive_endpoint("admin_users")
def admin_users():
    """Admin user management - sensitive endpoint."""
    return {"status": "success", "message": "User management accessed"}

@app.route("/api/admin/keys", methods=["GET", "POST", "DELETE"])
@audit_logger.audit_sensitive_endpoint("admin_keys")
def admin_keys():
    """Admin key management - sensitive endpoint."""
    return {"status": "success", "message": "Key management accessed"}

@app.route("/api/admin/deploy", methods=["POST"])
@audit_logger.audit_sensitive_endpoint("admin_deploy")
def admin_deploy():
    """Admin deployment - sensitive endpoint."""
    return {"status": "success", "message": "Deployment triggered"}

if __name__ == "__main__":
    print("📝 Starting CoolBits.ai audit logging server...")
    app.run(host="0.0.0.0", port=8502, debug=False)
'''

        with open("audit_logging.py", "w", encoding="utf-8") as f:
            f.write(audit_logging_script)

        print("✅ Audit logging system created")
        return True

    def run_standardization(self):
        """Run health standardization and SLO definition."""
        print("🏥 COOLBITS.AI HEALTH STANDARDIZATION & SLO DEFINITION")
        print("=" * 60)
        print(f"🕐 Started: {datetime.now().isoformat()}")

        # 1. Create standardized health endpoint
        health_created = self.create_standardized_health_endpoint()

        # 2. Create SLO monitoring
        slo_created = self.create_slo_monitoring()

        # 3. Create canary SLO integration
        canary_created = self.create_canary_slo_integration()

        # 4. Create audit logging
        audit_created = self.create_audit_logging()

        # Summary
        print("\n🎯 STANDARDIZATION SUMMARY")
        print("=" * 35)
        print(f"✅ Standardized health endpoint: {health_created}")
        print(f"✅ SLO monitoring system: {slo_created}")
        print(f"✅ Canary SLO integration: {canary_created}")
        print(f"✅ Audit logging system: {audit_created}")

        if all([health_created, slo_created, canary_created, audit_created]):
            print("\n🎉 STANDARDIZATION COMPLETE!")
            print("🚀 CoolBits.ai now has enterprise-grade health & SLO monitoring")
            return True
        else:
            print("\n❌ STANDARDIZATION INCOMPLETE")
            print("🚨 Some components failed")
            return False


if __name__ == "__main__":
    standardization = HealthStandardization()
    standardization.run_standardization()
