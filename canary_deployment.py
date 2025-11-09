# CoolBits.ai Staging Canary Deployment Script
# =============================================

import os
import sys
import time
import json
import requests
import subprocess
import argparse
from typing import Dict
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class DeploymentConfig:
    """Configuration for canary deployment."""

    staging_url: str
    production_url: str
    canary_percentage: int = 10
    health_check_endpoint: str = "/_stcore/health"
    metrics_endpoint: str = "/api/metrics"
    rollback_threshold: float = 0.95  # 95% success rate threshold
    monitoring_duration: int = 300  # 5 minutes
    max_rollback_time: int = 60  # 1 minute


class CanaryDeployment:
    """Handles canary deployment with automatic rollback."""

    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.deployment_id = f"canary-{int(time.time())}"
        self.start_time = None
        self.metrics = []
        self.rollback_triggered = False

    def deploy_to_staging(self) -> bool:
        """Deploy to staging environment."""
        print(f"🚀 Deploying to staging: {self.config.staging_url}")

        try:
            # Build and deploy to staging
            result = subprocess.run(
                [
                    "docker",
                    "build",
                    "-t",
                    f"coolbits-staging:{self.deployment_id}",
                    ".",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            # Start staging container
            subprocess.run(
                [
                    "docker",
                    "run",
                    "-d",
                    "--name",
                    f"coolbits-staging-{self.deployment_id}",
                    "-p",
                    "8502:8501",
                    f"coolbits-staging:{self.deployment_id}",
                ],
                check=True,
            )

            # Wait for staging to be ready
            self._wait_for_health(self.config.staging_url)
            print("✅ Staging deployment successful")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Staging deployment failed: {e}")
            return False

    def run_canary_deployment(self) -> bool:
        """Run canary deployment with monitoring."""
        print(f"🎯 Starting canary deployment: {self.deployment_id}")
        self.start_time = datetime.now()

        try:
            # Deploy canary version
            self._deploy_canary()

            # Monitor canary performance
            self._monitor_canary()

            # Decide on promotion or rollback
            if self.rollback_triggered:
                self._rollback_deployment()
                return False
            else:
                self._promote_to_production()
                return True

        except Exception as e:
            print(f"❌ Canary deployment failed: {e}")
            self._rollback_deployment()
            return False

    def _deploy_canary(self):
        """Deploy canary version."""
        print(f"📦 Deploying canary version ({self.config.canary_percentage}% traffic)")

        # Build canary image
        subprocess.run(
            ["docker", "build", "-t", f"coolbits-canary:{self.deployment_id}", "."],
            check=True,
        )

        # Start canary container
        subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "--name",
                f"coolbits-canary-{self.deployment_id}",
                "-p",
                "8503:8501",
                f"coolbits-canary:{self.deployment_id}",
            ],
            check=True,
        )

        # Wait for canary to be ready
        self._wait_for_health("http://localhost:8503")

        # Configure load balancer for canary traffic
        self._configure_load_balancer()

    def _monitor_canary(self):
        """Monitor canary performance."""
        print("📊 Monitoring canary performance...")

        end_time = datetime.now() + timedelta(seconds=self.config.monitoring_duration)

        while datetime.now() < end_time and not self.rollback_triggered:
            metrics = self._collect_metrics()
            self.metrics.append(metrics)

            # Check rollback conditions
            if self._should_rollback(metrics):
                print("⚠️ Rollback conditions met!")
                self.rollback_triggered = True
                break

            print(f"📈 Metrics: {metrics}")
            time.sleep(30)  # Check every 30 seconds

    def _collect_metrics(self) -> Dict:
        """Collect performance metrics."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "response_time": 0,
            "error_rate": 0,
            "success_rate": 0,
            "cpu_usage": 0,
            "memory_usage": 0,
        }

        try:
            # Test response time
            start_time = time.time()
            response = requests.get(
                f"http://localhost:8503{self.config.health_check_endpoint}", timeout=5
            )
            metrics["response_time"] = (time.time() - start_time) * 1000  # ms

            # Test success rate
            if response.status_code == 200:
                metrics["success_rate"] = 1.0
            else:
                metrics["success_rate"] = 0.0

            # Get container metrics
            result = subprocess.run(
                [
                    "docker",
                    "stats",
                    f"coolbits-canary-{self.deployment_id}",
                    "--no-stream",
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                stats = json.loads(result.stdout)
                metrics["cpu_usage"] = float(stats["CPUPerc"].replace("%", ""))
                metrics["memory_usage"] = float(stats["MemPerc"].replace("%", ""))

        except Exception as e:
            print(f"⚠️ Error collecting metrics: {e}")
            metrics["error_rate"] = 1.0

        return metrics

    def _should_rollback(self, metrics: Dict) -> bool:
        """Determine if rollback should be triggered."""
        # Check success rate threshold
        if metrics["success_rate"] < self.config.rollback_threshold:
            return True

        # Check response time (if > 5 seconds)
        if metrics["response_time"] > 5000:
            return True

        # Check error rate (if > 5%)
        if metrics["error_rate"] > 0.05:
            return True

        # Check resource usage (if CPU > 90% or Memory > 90%)
        if metrics["cpu_usage"] > 90 or metrics["memory_usage"] > 90:
            return True

        return False

    def _configure_load_balancer(self):
        """Configure load balancer for canary traffic."""
        print(
            f"⚖️ Configuring load balancer for {self.config.canary_percentage}% canary traffic"
        )

        # This would integrate with your load balancer (nginx, traefik, etc.)
        # For now, we'll simulate the configuration
        config = {
            "canary_percentage": self.config.canary_percentage,
            "canary_container": f"coolbits-canary-{self.deployment_id}",
            "production_container": "coolbits-production",
        }

        # Save load balancer config
        with open(f"canary-config-{self.deployment_id}.json", "w") as f:
            json.dump(config, f, indent=2)

    def _promote_to_production(self):
        """Promote canary to production."""
        print("🎉 Promoting canary to production")

        # Stop old production container
        subprocess.run(["docker", "stop", "coolbits-production"], check=False)
        subprocess.run(["docker", "rm", "coolbits-production"], check=False)

        # Rename canary to production
        subprocess.run(
            [
                "docker",
                "rename",
                f"coolbits-canary-{self.deployment_id}",
                "coolbits-production",
            ],
            check=True,
        )

        # Update load balancer to 100% production traffic
        self._update_load_balancer_production()

        print("✅ Canary promoted to production successfully")

    def _rollback_deployment(self):
        """Rollback to previous production version."""
        print("🔄 Rolling back deployment")

        start_rollback = time.time()

        try:
            # Stop canary container
            subprocess.run(
                ["docker", "stop", f"coolbits-canary-{self.deployment_id}"], check=True
            )
            subprocess.run(
                ["docker", "rm", f"coolbits-canary-{self.deployment_id}"], check=True
            )

            # Restore previous production version
            subprocess.run(
                [
                    "docker",
                    "run",
                    "-d",
                    "--name",
                    "coolbits-production-restored",
                    "-p",
                    "8501:8501",
                    "coolbits-production:previous",
                ],
                check=True,
            )

            # Update load balancer to 100% restored production
            self._update_load_balancer_production()

            rollback_time = time.time() - start_rollback
            print(f"✅ Rollback completed in {rollback_time:.2f} seconds")

        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            # Emergency procedures would go here

    def _update_load_balancer_production(self):
        """Update load balancer to 100% production traffic."""
        print("⚖️ Updating load balancer to 100% production traffic")

        config = {"canary_percentage": 0, "production_container": "coolbits-production"}

        with open(f"production-config-{self.deployment_id}.json", "w") as f:
            json.dump(config, f, indent=2)

    def _wait_for_health(self, url: str, timeout: int = 60):
        """Wait for service to be healthy."""
        print(f"⏳ Waiting for health check: {url}")

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(
                    f"{url}{self.config.health_check_endpoint}", timeout=5
                )
                if response.status_code == 200:
                    print("✅ Health check passed")
                    return
            except requests.RequestException:
                pass

            time.sleep(5)

        raise TimeoutError(f"Health check timeout after {timeout} seconds")

    def cleanup(self):
        """Cleanup deployment artifacts."""
        print("🧹 Cleaning up deployment artifacts")

        # Remove staging container
        subprocess.run(
            ["docker", "stop", f"coolbits-staging-{self.deployment_id}"], check=False
        )
        subprocess.run(
            ["docker", "rm", f"coolbits-staging-{self.deployment_id}"], check=False
        )

        # Remove config files
        for file in [
            f"canary-config-{self.deployment_id}.json",
            f"production-config-{self.deployment_id}.json",
        ]:
            if os.path.exists(file):
                os.remove(file)


def main():
    """Main deployment script."""
    parser = argparse.ArgumentParser(description="CoolBits.ai Canary Deployment")
    parser.add_argument(
        "--staging-url", default="http://localhost:8502", help="Staging URL"
    )
    parser.add_argument(
        "--production-url", default="http://localhost:8501", help="Production URL"
    )
    parser.add_argument(
        "--canary-percentage", type=int, default=10, help="Canary traffic percentage"
    )
    parser.add_argument(
        "--monitoring-duration",
        type=int,
        default=300,
        help="Monitoring duration in seconds",
    )

    args = parser.parse_args()

    config = DeploymentConfig(
        staging_url=args.staging_url,
        production_url=args.production_url,
        canary_percentage=args.canary_percentage,
        monitoring_duration=args.monitoring_duration,
    )

    deployment = CanaryDeployment(config)

    try:
        # Deploy to staging first
        if not deployment.deploy_to_staging():
            print("❌ Staging deployment failed, aborting")
            sys.exit(1)

        # Run canary deployment
        success = deployment.run_canary_deployment()

        if success:
            print("🎉 Canary deployment successful!")
            sys.exit(0)
        else:
            print("❌ Canary deployment failed and rolled back")
            sys.exit(1)

    finally:
        deployment.cleanup()


if __name__ == "__main__":
    main()
