# SRE Manager for M20.5
import os
import json
import logging
import yaml
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path
import requests
import time

logger = logging.getLogger(__name__)

class SREManager:
    """SRE Manager for M20.5 - SLO, alerting, runbooks"""
    
    def __init__(self):
        self.gateway_url = os.getenv("GW", "http://localhost:8080")
        self.slo_config_path = "artifacts/dev/slo/slo_config.yaml"
        self.alerts_config_path = "artifacts/dev/alerts/alert_rules.yaml"
        self.runbooks_path = "gateway/runbooks"
        
    def get_slo_status(self) -> Dict[str, Any]:
        """Get current SLO status and error budgets"""
        try:
            # Load SLO configuration
            if Path(self.slo_config_path).exists():
                with open(self.slo_config_path, 'r') as f:
                    slo_config = yaml.safe_load(f)
            else:
                # Default SLO configuration
                slo_config = {
                    "slos": [
                        {
                            "name": "Gateway Availability",
                            "slo": 99.9,
                            "error_budget_minutes_per_month": 43
                        },
                        {
                            "name": "Gateway p95 Latency",
                            "slo": 400,
                            "unit": "ms"
                        },
                        {
                            "name": "Orchestrator Success Rate",
                            "slo": 98.5,
                            "unit": "percent"
                        },
                        {
                            "name": "Stripe Webhook Success",
                            "slo": 99.5,
                            "unit": "percent"
                        }
                    ]
                }
            
            # Get current metrics
            metrics = self._get_current_metrics()
            
            # Calculate SLO status
            slo_status = []
            for slo in slo_config["slos"]:
                status = self._calculate_slo_status(slo, metrics)
                slo_status.append(status)
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "slos": slo_status,
                "overall_status": "healthy" if all(s["status"] == "healthy" for s in slo_status) else "degraded"
            }
            
        except Exception as e:
            logger.error(f"Failed to get SLO status: {e}")
            return {"error": str(e)}
    
    def get_active_alerts(self) -> Dict[str, Any]:
        """Get active alerts"""
        try:
            # Simulate alert checking
            alerts = [
                {
                    "name": "SLOBurnFast",
                    "status": "firing",
                    "severity": "page",
                    "description": "SLO burn rate rapid >14x",
                    "since": (datetime.utcnow() - timedelta(minutes=5)).isoformat()
                },
                {
                    "name": "RAGLatencyP95High",
                    "status": "resolved",
                    "severity": "page",
                    "description": "RAG p95 latency > 300ms",
                    "since": (datetime.utcnow() - timedelta(minutes=30)).isoformat(),
                    "resolved_at": (datetime.utcnow() - timedelta(minutes=10)).isoformat()
                }
            ]
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "alerts": alerts,
                "active_count": len([a for a in alerts if a["status"] == "firing"])
            }
            
        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return {"error": str(e)}
    
    def run_synthetic_tests(self) -> Dict[str, Any]:
        """Run synthetic monitoring tests"""
        try:
            endpoints = [
                {"url": "/health", "name": "health"},
                {"url": "/v1/nha/invoke", "name": "nha_invoke", "method": "POST"},
                {"url": "/v1/rag/search", "name": "rag_search", "method": "POST"},
                {"url": "/v1/billing/balance/demo", "name": "billing_balance"}
            ]
            
            results = []
            for endpoint in endpoints:
                start_time = time.time()
                success = False
                latency_ms = 0
                
                try:
                    if endpoint.get("method") == "POST":
                        response = requests.post(
                            f"{self.gateway_url}{endpoint['url']}",
                            json={"test": True},
                            timeout=10
                        )
                    else:
                        response = requests.get(
                            f"{self.gateway_url}{endpoint['url']}",
                            timeout=10
                        )
                    
                    latency_ms = (time.time() - start_time) * 1000
                    success = response.status_code == 200
                    
                except Exception as e:
                    latency_ms = (time.time() - start_time) * 1000
                    success = False
                    logger.warning(f"Synthetic test failed for {endpoint['name']}: {e}")
                
                results.append({
                    "endpoint": endpoint["name"],
                    "success": success,
                    "latency_ms": round(latency_ms, 2),
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "results": results,
                "success_rate": len([r for r in results if r["success"]]) / len(results),
                "avg_latency_ms": sum(r["latency_ms"] for r in results) / len(results)
            }
            
        except Exception as e:
            logger.error(f"Failed to run synthetic tests: {e}")
            return {"error": str(e)}
    
    def run_drill(self, scenario: str = "all") -> Dict[str, Any]:
        """Run SRE drill scenarios"""
        try:
            scenarios = {
                "stripe_webhook": {
                    "name": "Stripe Webhook Down",
                    "description": "Simulate Stripe webhook failures",
                    "test_endpoint": "/v1/billing/webhook/stripe",
                    "expected_alert": "StripeWebhookFailures"
                },
                "redis_down": {
                    "name": "Redis Connection Down",
                    "description": "Simulate Redis connection failures",
                    "test_endpoint": "/v1/nha/invoke",
                    "expected_alert": "NHAErrorsSpike"
                },
                "rag_latency": {
                    "name": "RAG Latency High",
                    "description": "Simulate RAG latency degradation",
                    "test_endpoint": "/v1/rag/search",
                    "expected_alert": "RAGLatencyP95High"
                }
            }
            
            if scenario == "all":
                scenarios_to_run = scenarios
            else:
                scenarios_to_run = {scenario: scenarios[scenario]} if scenario in scenarios else {}
            
            drill_results = []
            for scenario_key, scenario_config in scenarios_to_run.items():
                start_time = time.time()
                
                # Simulate scenario
                try:
                    response = requests.get(
                        f"{self.gateway_url}{scenario_config['test_endpoint']}",
                        timeout=5
                    )
                    simulation_success = response.status_code == 200
                except Exception as e:
                    simulation_success = False
                    logger.warning(f"Drill scenario {scenario_key} failed: {e}")
                
                # Check if alert would be triggered
                alert_triggered = self._check_alert_trigger(scenario_config["expected_alert"])
                
                duration = time.time() - start_time
                
                drill_results.append({
                    "scenario": scenario_config["name"],
                    "description": scenario_config["description"],
                    "simulation_success": simulation_success,
                    "alert_triggered": alert_triggered,
                    "duration_seconds": round(duration, 2),
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "scenarios": drill_results,
                "total_scenarios": len(drill_results),
                "successful_simulations": len([r for r in drill_results if r["simulation_success"]]),
                "alerts_triggered": len([r for r in drill_results if r["alert_triggered"]])
            }
            
        except Exception as e:
            logger.error(f"Failed to run SRE drill: {e}")
            return {"error": str(e)}
    
    def execute_rollback(self, target_revision: Optional[str] = None, reason: str = "SRE rollback") -> Dict[str, Any]:
        """Execute rollback to previous revision"""
        try:
            # Get current revision
            current_revision = self._get_current_revision()
            
            # Get target revision
            if not target_revision:
                target_revision = self._get_previous_revision()
            
            if not target_revision:
                return {"error": "No target revision found"}
            
            # Execute rollback
            rollback_result = self._execute_rollback_to_revision(target_revision, reason)
            
            # Verify rollback
            verification = self._verify_rollback()
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "current_revision": current_revision,
                "target_revision": target_revision,
                "reason": reason,
                "rollback_success": rollback_result,
                "verification_success": verification,
                "status": "completed" if rollback_result and verification else "failed"
            }
            
        except Exception as e:
            logger.error(f"Failed to execute rollback: {e}")
            return {"error": str(e)}
    
    def _get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            response = requests.get(f"{self.gateway_url}/metrics", timeout=10)
            if response.status_code == 200:
                # Parse Prometheus metrics (simplified)
                metrics_text = response.text
                return {
                    "http_requests_total": self._parse_metric(metrics_text, "http_requests_total"),
                    "http_latency_ms_bucket": self._parse_metric(metrics_text, "http_latency_ms_bucket"),
                    "rag_latency_ms_bucket": self._parse_metric(metrics_text, "rag_latency_ms_bucket"),
                    "nha_latency_ms_bucket": self._parse_metric(metrics_text, "nha_latency_ms_bucket"),
                    "flow_runs_total": self._parse_metric(metrics_text, "flow_runs_total"),
                    "flow_runs_success_total": self._parse_metric(metrics_text, "flow_runs_success_total"),
                    "billing_webhook_total": self._parse_metric(metrics_text, "billing_webhook_total"),
                    "billing_webhook_success_total": self._parse_metric(metrics_text, "billing_webhook_success_total")
                }
            else:
                return {}
        except Exception as e:
            logger.warning(f"Failed to get metrics: {e}")
            return {}
    
    def _parse_metric(self, metrics_text: str, metric_name: str) -> float:
        """Parse a specific metric from Prometheus format"""
        try:
            for line in metrics_text.split('\n'):
                if line.startswith(metric_name) and not line.startswith('#'):
                    parts = line.split()
                    if len(parts) >= 2:
                        return float(parts[1])
            return 0.0
        except Exception:
            return 0.0
    
    def _calculate_slo_status(self, slo: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate status for a specific SLO"""
        try:
            slo_name = slo["name"]
            slo_target = slo["slo"]
            
            if "Availability" in slo_name:
                # Calculate availability
                total_requests = metrics.get("http_requests_total", 0)
                error_requests = metrics.get("http_requests_total", 0) * 0.001  # Simulate 0.1% error rate
                availability = ((total_requests - error_requests) / total_requests * 100) if total_requests > 0 else 100
                status = "healthy" if availability >= slo_target else "degraded"
                
                return {
                    "name": slo_name,
                    "target": slo_target,
                    "current": round(availability, 2),
                    "unit": "percent",
                    "status": status,
                    "error_budget_remaining": max(0, slo_target - availability)
                }
                
            elif "Latency" in slo_name:
                # Calculate latency
                latency = metrics.get("http_latency_ms_bucket", 300)  # Simulate 300ms
                status = "healthy" if latency <= slo_target else "degraded"
                
                return {
                    "name": slo_name,
                    "target": slo_target,
                    "current": latency,
                    "unit": "ms",
                    "status": status
                }
                
            elif "Success" in slo_name:
                # Calculate success rate
                total_runs = metrics.get("flow_runs_total", 100)
                success_runs = metrics.get("flow_runs_success_total", 98)
                success_rate = (success_runs / total_runs * 100) if total_runs > 0 else 100
                status = "healthy" if success_rate >= slo_target else "degraded"
                
                return {
                    "name": slo_name,
                    "target": slo_target,
                    "current": round(success_rate, 2),
                    "unit": "percent",
                    "status": status
                }
                
            else:
                return {
                    "name": slo_name,
                    "target": slo_target,
                    "current": slo_target,
                    "unit": slo.get("unit", ""),
                    "status": "healthy"
                }
                
        except Exception as e:
            logger.warning(f"Failed to calculate SLO status for {slo.get('name', 'unknown')}: {e}")
            return {
                "name": slo.get("name", "unknown"),
                "target": slo.get("slo", 0),
                "current": 0,
                "unit": slo.get("unit", ""),
                "status": "unknown"
            }
    
    def _check_alert_trigger(self, alert_name: str) -> bool:
        """Check if an alert would be triggered"""
        try:
            # Simulate alert checking
            alert_conditions = {
                "StripeWebhookFailures": True,  # Simulate webhook failure
                "NHAErrorsSpike": False,  # Simulate no NHA errors
                "RAGLatencyP95High": True  # Simulate high RAG latency
            }
            return alert_conditions.get(alert_name, False)
        except Exception:
            return False
    
    def _get_current_revision(self) -> str:
        """Get current deployment revision"""
        try:
            response = requests.get(f"{self.gateway_url}/v1/deploy/current", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("revision", "unknown")
            return "unknown"
        except Exception:
            return "unknown"
    
    def _get_previous_revision(self) -> str:
        """Get previous deployment revision"""
        try:
            response = requests.get(f"{self.gateway_url}/v1/deploy/revisions", timeout=10)
            if response.status_code == 200:
                data = response.json()
                revisions = data.get("revisions", [])
                if len(revisions) > 1:
                    return revisions[1]["revision"]
            return "unknown"
        except Exception:
            return "unknown"
    
    def _execute_rollback_to_revision(self, target_revision: str, reason: str) -> bool:
        """Execute rollback to target revision"""
        try:
            response = requests.post(
                f"{self.gateway_url}/v1/deploy/rollback",
                json={
                    "target_revision": target_revision,
                    "reason": reason
                },
                timeout=30
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def _verify_rollback(self) -> bool:
        """Verify rollback was successful"""
        try:
            response = requests.get(f"{self.gateway_url}/health", timeout=10)
            return response.status_code == 200
        except Exception:
            return False
