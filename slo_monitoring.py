
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
