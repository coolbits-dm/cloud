# Metrics and SLO tracking for M19.4
import time
import logging
from typing import Dict, Any, Optional
from collections import defaultdict, deque
from datetime import datetime, timedelta
import threading
import json
import os

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Metrics collector with SLO tracking"""
    
    def __init__(self):
        self.lock = threading.Lock()
        
        # Counters
        self.nha_invocations_total = defaultdict(int)  # {agent: {status: count}}
        self.rag_queries_total = defaultdict(int)  # {panel: count}
        self.flows_runs_total = defaultdict(int)  # {status: count}
        self.flows_nodes_total = defaultdict(int)  # {type: {status: count}}
        
        # Histograms (latency buckets)
        self.nha_latency_ms = defaultdict(lambda: deque(maxlen=1000))  # {agent: [latencies]}
        self.rag_latency_ms = defaultdict(lambda: deque(maxlen=1000))  # {panel: [latencies]}
        self.flows_run_latency_ms = deque(maxlen=1000)
        self.flows_node_latency_ms = defaultdict(lambda: deque(maxlen=1000))  # {type: [latencies]}
        
        # Gauges
        self.queue_depth = defaultdict(int)  # {stream: depth}
        self.active_connections = 0
        self.active_runs = 0
        
        # Error tracking
        self.errors_by_agent = defaultdict(lambda: deque(maxlen=100))  # {agent: [timestamps]}
        self.errors_by_endpoint = defaultdict(lambda: deque(maxlen=100))  # {endpoint: [timestamps]}
        
        # SLO thresholds
        self.SLO_NODE_P95_MS = 800
        self.SLO_RAG_P95_MS = 300
        self.SLO_ERROR_RATE_PERCENT = 2.0
        self.SLO_CIRCUIT_BREAKER_PERCENT = 5.0
        
    def record_nha_invocation(self, agent: str, status: str, latency_ms: int):
        """Record NHA invocation metric"""
        with self.lock:
            self.nha_invocations_total[agent][status] += 1
            self.nha_latency_ms[agent].append(latency_ms)
            
            if status == "error":
                self.errors_by_agent[agent].append(time.time())
    
    def record_rag_query(self, panel: str, latency_ms: int):
        """Record RAG query metric"""
        with self.lock:
            self.rag_queries_total[panel] += 1
            self.rag_latency_ms[panel].append(latency_ms)
    
    def record_flow_run(self, status: str, latency_ms: int):
        """Record flow run metric"""
        with self.lock:
            self.flows_runs_total[status] += 1
            self.flows_run_latency_ms.append(latency_ms)
    
    def record_flow_node(self, node_type: str, status: str, latency_ms: int):
        """Record flow node metric"""
        with self.lock:
            self.flows_nodes_total[node_type][status] += 1
            self.flows_node_latency_ms[node_type].append(latency_ms)
    
    def update_queue_depth(self, stream: str, depth: int):
        """Update queue depth gauge"""
        with self.lock:
            self.queue_depth[stream] = depth
    
    def update_active_connections(self, count: int):
        """Update active connections gauge"""
        with self.lock:
            self.active_connections = count
    
    def update_active_runs(self, count: int):
        """Update active runs gauge"""
        with self.lock:
            self.active_runs = count
    
    def record_error(self, endpoint: str):
        """Record error for endpoint"""
        with self.lock:
            self.errors_by_endpoint[endpoint].append(time.time())
    
    def get_p95(self, latencies: deque) -> float:
        """Calculate P95 latency"""
        if not latencies:
            return 0.0
        
        sorted_latencies = sorted(latencies)
        index = int(len(sorted_latencies) * 0.95)
        return float(sorted_latencies[min(index, len(sorted_latencies) - 1)])
    
    def get_error_rate(self, agent: str, window_minutes: int = 3) -> float:
        """Calculate error rate for agent in time window"""
        with self.lock:
            now = time.time()
            window_start = now - (window_minutes * 60)
            
            # Count errors in window
            errors = [ts for ts in self.errors_by_agent[agent] if ts >= window_start]
            total_invocations = sum(self.nha_invocations_total[agent].values())
            
            if total_invocations == 0:
                return 0.0
            
            return (len(errors) / total_invocations) * 100.0
    
    def is_circuit_breaker_open(self, agent: str) -> bool:
        """Check if circuit breaker is open for agent"""
        error_rate = self.get_error_rate(agent)
        return error_rate > self.SLO_CIRCUIT_BREAKER_PERCENT
    
    def get_snapshot(self) -> Dict[str, Any]:
        """Get metrics snapshot"""
        with self.lock:
            # Calculate P95 latencies
            nha_p95_ms = {}
            for agent, latencies in self.nha_latency_ms.items():
                nha_p95_ms[agent] = self.get_p95(latencies)
            
            rag_p95_ms = {}
            for panel, latencies in self.rag_latency_ms.items():
                rag_p95_ms[panel] = self.get_p95(latencies)
            
            flows_p95_ms = self.get_p95(self.flows_run_latency_ms)
            
            orchestrator_p95_ms = {}
            for node_type, latencies in self.flows_node_latency_ms.items():
                orchestrator_p95_ms[node_type] = self.get_p95(latencies)
            
            # Calculate error rates
            error_rates = {}
            for agent in self.nha_invocations_total.keys():
                error_rates[agent] = self.get_error_rate(agent)
            
            # Calculate success rates
            invocations_success_rate = 0.0
            total_invocations = sum(sum(agent_counts.values()) for agent_counts in self.nha_invocations_total.values())
            total_errors = sum(len(errors) for errors in self.errors_by_agent.values())
            if total_invocations > 0:
                invocations_success_rate = ((total_invocations - total_errors) / total_invocations) * 100.0
            
            return {
                "chat_p50_ms": 150,  # Placeholder
                "chat_p95_ms": 300,  # Placeholder
                "rag_p50_ms": 200,  # Placeholder
                "rag_p95_ms": rag_p95_ms,
                "ws_connects_per_min": 5,  # Placeholder
                "invocations_success_rate": invocations_success_rate,
                "ledger_delta_session": 0,  # Placeholder
                "nha_queue_pending": self.queue_depth.get("nha:jobs", 0),
                "nha_p95_ms": nha_p95_ms,
                "orchestrator_active_runs": self.active_runs,
                "orchestrator_queue_pending": self.queue_depth.get("flows:jobs", 0),
                "orchestrator_p95_ms": orchestrator_p95_ms,
                "flows_run_p95_ms": flows_p95_ms,
                "error_rates": error_rates,
                "circuit_breakers": {agent: self.is_circuit_breaker_open(agent) for agent in self.nha_invocations_total.keys()},
                "slo_status": {
                    "node_p95_ok": all(p95 <= self.SLO_NODE_P95_MS for p95 in orchestrator_p95_ms.values()),
                    "rag_p95_ok": all(p95 <= self.SLO_RAG_P95_MS for p95 in rag_p95_ms.values()),
                    "error_rate_ok": all(rate <= self.SLO_ERROR_RATE_PERCENT for rate in error_rates.values())
                },
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        with self.lock:
            lines = []
            
            # NHA invocations counter
            for agent, status_counts in self.nha_invocations_total.items():
                for status, count in status_counts.items():
                    lines.append(f'nha_invocations_total{{agent="{agent}",status="{status}"}} {count}')
            
            # NHA latency histogram
            for agent, latencies in self.nha_latency_ms.items():
                if latencies:
                    p95 = self.get_p95(latencies)
                    lines.append(f'nha_latency_ms_bucket{{agent="{agent}",le="800"}} {p95}')
            
            # RAG latency histogram
            for panel, latencies in self.rag_latency_ms.items():
                if latencies:
                    p95 = self.get_p95(latencies)
                    lines.append(f'rag_latency_ms_bucket{{panel="{panel}",le="300"}} {p95}')
            
            # Flow runs counter
            for status, count in self.flows_runs_total.items():
                lines.append(f'flows_runs_total{{status="{status}"}} {count}')
            
            # Flow nodes counter
            for node_type, status_counts in self.flows_nodes_total.items():
                for status, count in status_counts.items():
                    lines.append(f'flows_nodes_total{{type="{node_type}",status="{status}"}} {count}')
            
            # Queue depth gauges
            for stream, depth in self.queue_depth.items():
                lines.append(f'queue_depth{{stream="{stream}"}} {depth}')
            
            # Active runs gauge
            lines.append(f'flows_active_runs {self.active_runs}')
            
            # Circuit breaker status
            for agent in self.nha_invocations_total.keys():
                is_open = self.is_circuit_breaker_open(agent)
                lines.append(f'circuit_breaker_open{{agent="{agent}"}} {1 if is_open else 0}')
            
            return '\n'.join(lines)

# Global metrics collector
metrics = MetricsCollector()

def record_nha_invocation(agent: str, status: str, latency_ms: int):
    """Record NHA invocation metric"""
    metrics.record_nha_invocation(agent, status, latency_ms)

def record_rag_query(panel: str, latency_ms: int):
    """Record RAG query metric"""
    metrics.record_rag_query(panel, latency_ms)

def record_flow_run(status: str, latency_ms: int):
    """Record flow run metric"""
    metrics.record_flow_run(status, latency_ms)

def record_flow_node(node_type: str, status: str, latency_ms: int):
    """Record flow node metric"""
    metrics.record_flow_node(node_type, status, latency_ms)

def update_queue_depth(stream: str, depth: int):
    """Update queue depth gauge"""
    metrics.update_queue_depth(stream, depth)

def update_active_connections(count: int):
    """Update active connections gauge"""
    metrics.update_active_connections(count)

def update_active_runs(count: int):
    """Update active runs gauge"""
    metrics.update_active_runs(count)

def record_error(endpoint: str):
    """Record error for endpoint"""
    metrics.record_error(endpoint)

def get_metrics_snapshot() -> Dict[str, Any]:
    """Get metrics snapshot"""
    return metrics.get_snapshot()

def export_prometheus_metrics() -> str:
    """Export metrics in Prometheus format"""
    return metrics.export_prometheus()

def is_circuit_breaker_open(agent: str) -> bool:
    """Check if circuit breaker is open for agent"""
    return metrics.is_circuit_breaker_open(agent)
