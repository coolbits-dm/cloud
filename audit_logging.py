
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
            f.write(json.dumps(audit_entry) + "\n")
    
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
