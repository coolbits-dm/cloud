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
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True
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
                ["git", "log", "-1", "--format=%ci"], capture_output=True, text=True
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
            "timestamp": datetime.now().isoformat(),
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
