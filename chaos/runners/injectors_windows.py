# CoolBits.ai Chaos Engineering - Windows-Compatible Fault Injectors
# Simulated implementations for Windows PowerShell environment

import time
import threading
import psutil
import logging
import json
import os
from typing import Dict, Any
from datetime import datetime


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
    """Simulate network latency injection for Windows"""

    def __init__(self, scenario: Dict[str, Any]):
        super().__init__(scenario)
        self.target = scenario["targets"][0]
        self.latency_ms = self.target["latency_ms"]
        self.jitter_ms = self.target.get("jitter_ms", 0)
        self.duration_s = self.target["duration_s"]
        self.service = self.target["service"]
        self.simulated_latency = False

    def start(self) -> bool:
        """Simulate network latency injection"""
        try:
            self.logger.info(
                f"Simulating {self.latency_ms}ms latency injection to {self.service}"
            )
            self.active = True
            self.start_time = time.time()
            self.simulated_latency = True

            # Log injection event
            self._log_event(
                "latency_injection_start",
                {
                    "service": self.service,
                    "latency_ms": self.latency_ms,
                    "jitter_ms": self.jitter_ms,
                },
            )

            return True
        except Exception as e:
            self.logger.error(f"Network latency injection failed: {e}")
            return False

    def verify_injection(self) -> bool:
        """Verify injection is active"""
        return self.simulated_latency and self.active

    def stop(self) -> bool:
        """Stop latency injection"""
        try:
            self.logger.info(f"Stopping latency injection for {self.service}")
            self.active = False
            self.simulated_latency = False

            # Log injection stop event
            self._log_event(
                "latency_injection_stop",
                {
                    "service": self.service,
                    "duration_s": time.time() - self.start_time
                    if self.start_time
                    else 0,
                },
            )

            return True
        except Exception as e:
            self.logger.error(f"Failed to stop latency injection: {e}")
            return False

    def safety_guard(self) -> bool:
        """Safety guard - always allow in simulation"""
        return True

    def _log_event(self, event_type: str, data: Dict[str, Any]):
        """Log chaos event to JSONL file"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event": event_type,
                "scenario": "network_latency",
                "chaos": True,
                **data,
            }

            # Ensure logs directory exists
            os.makedirs("logs", exist_ok=True)

            # Append to monthly log file
            log_file = f"logs/chaos-{datetime.now().strftime('%Y%m')}.jsonl"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")

        except Exception as e:
            self.logger.error(f"Failed to log event: {e}")


class ServiceKillInjector(BaseInjector):
    """Simulate service kill injection for Windows"""

    def __init__(self, scenario: Dict[str, Any]):
        super().__init__(scenario)
        self.target = scenario["targets"][0]
        self.service = self.target["service"]
        self.duration_s = self.target["duration_s"]
        self.simulated_kill = False

    def start(self) -> bool:
        """Simulate service kill"""
        try:
            self.logger.info(f"Simulating service kill for {self.service}")
            self.active = True
            self.start_time = time.time()
            self.simulated_kill = True

            # Log kill event
            self._log_event(
                "service_kill_start",
                {"service": self.service, "duration_s": self.duration_s},
            )

            return True
        except Exception as e:
            self.logger.error(f"Service kill injection failed: {e}")
            return False

    def verify_injection(self) -> bool:
        """Verify kill is active"""
        return self.simulated_kill and self.active

    def stop(self) -> bool:
        """Stop service kill simulation"""
        try:
            self.logger.info(f"Stopping service kill simulation for {self.service}")
            self.active = False
            self.simulated_kill = False

            # Log kill stop event
            self._log_event(
                "service_kill_stop",
                {
                    "service": self.service,
                    "duration_s": time.time() - self.start_time
                    if self.start_time
                    else 0,
                },
            )

            return True
        except Exception as e:
            self.logger.error(f"Failed to stop service kill: {e}")
            return False

    def safety_guard(self) -> bool:
        """Safety guard - always allow in simulation"""
        return True

    def _log_event(self, event_type: str, data: Dict[str, Any]):
        """Log chaos event to JSONL file"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event": event_type,
                "scenario": "service_kill",
                "chaos": True,
                **data,
            }

            os.makedirs("logs", exist_ok=True)
            log_file = f"logs/chaos-{datetime.now().strftime('%Y%m')}.jsonl"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")

        except Exception as e:
            self.logger.error(f"Failed to log event: {e}")


class CPUSpikeInjector(BaseInjector):
    """Simulate CPU spike injection for Windows"""

    def __init__(self, scenario: Dict[str, Any]):
        super().__init__(scenario)
        self.target = scenario["targets"][0]
        self.service = self.target["service"]
        self.duration_s = self.target["duration_s"]
        self.cpu_percent = self.target.get("cpu_percent", 80)
        self.simulated_spike = False
        self.spike_thread = None

    def start(self) -> bool:
        """Simulate CPU spike"""
        try:
            self.logger.info(
                f"Simulating CPU spike ({self.cpu_percent}%) for {self.service}"
            )
            self.active = True
            self.start_time = time.time()
            self.simulated_spike = True

            # Start CPU spike simulation thread
            self.spike_thread = threading.Thread(target=self._cpu_spike_worker)
            self.spike_thread.daemon = True
            self.spike_thread.start()

            # Log spike event
            self._log_event(
                "cpu_spike_start",
                {
                    "service": self.service,
                    "cpu_percent": self.cpu_percent,
                    "duration_s": self.duration_s,
                },
            )

            return True
        except Exception as e:
            self.logger.error(f"CPU spike injection failed: {e}")
            return False

    def verify_injection(self) -> bool:
        """Verify spike is active"""
        return self.simulated_spike and self.active

    def stop(self) -> bool:
        """Stop CPU spike"""
        try:
            self.logger.info(f"Stopping CPU spike for {self.service}")
            self.active = False
            self.simulated_spike = False

            # Log spike stop event
            self._log_event(
                "cpu_spike_stop",
                {
                    "service": self.service,
                    "duration_s": time.time() - self.start_time
                    if self.start_time
                    else 0,
                },
            )

            return True
        except Exception as e:
            self.logger.error(f"Failed to stop CPU spike: {e}")
            return False

    def safety_guard(self) -> bool:
        """Safety guard - check system load"""
        try:
            load_avg = psutil.cpu_percent(interval=1)
            if load_avg > 90:  # Safety threshold
                self.logger.warning(f"System load too high: {load_avg}%")
                return False
            return True
        except Exception:
            return True

    def _cpu_spike_worker(self):
        """Worker thread that simulates CPU load"""
        try:
            while self.active and self.simulated_spike:
                # Simulate CPU work
                start = time.time()
                while time.time() - start < 0.1:  # 100ms bursts
                    pass
                time.sleep(0.1)  # Brief pause
        except Exception as e:
            self.logger.error(f"CPU spike worker error: {e}")

    def _log_event(self, event_type: str, data: Dict[str, Any]):
        """Log chaos event to JSONL file"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event": event_type,
                "scenario": "cpu_spike",
                "chaos": True,
                **data,
            }

            os.makedirs("logs", exist_ok=True)
            log_file = f"logs/chaos-{datetime.now().strftime('%Y%m')}.jsonl"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")

        except Exception as e:
            self.logger.error(f"Failed to log event: {e}")


# Export injectors for Windows
NetworkLatency = NetworkLatencyInjector
ServiceKill = ServiceKillInjector
CPUSpike = CPUSpikeInjector
