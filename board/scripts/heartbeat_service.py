#!/usr/bin/env python3
"""
Heartbeat Service
Periodic status checks & feed for oCopilot Board Orchestrator
"""

import argparse
import json
import logging
import psutil
import subprocess
import time
import yaml
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class HeartbeatService:
    def __init__(self, config_path="config/board.agents.yaml"):
        self.config_path = config_path
        self.running = False
        self.interval = 15  # seconds

    def probe_cpu(self):
        """Probe CPU information"""
        try:
            cpu_info = {
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                "load_avg": (
                    psutil.getloadavg() if hasattr(psutil, "getloadavg") else None
                ),
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"🖥️ CPU Probe: {cpu_info['cpu_count']} cores, {cpu_info['cpu_percent']}% usage"
            )
            return cpu_info

        except Exception as e:
            logger.error(f"CPU probe error: {e}")
            return None

    def probe_gpu(self):
        """Probe GPU information"""
        try:
            gpu_info = {
                "cuda_available": False,
                "gpu_count": 0,
                "gpu_memory": None,
                "timestamp": datetime.now().isoformat(),
            }

            # Try to detect NVIDIA GPU
            try:
                result = subprocess.run(
                    [
                        "nvidia-smi",
                        "--query-gpu=name,memory.total,memory.used",
                        "--format=csv,noheader,nounits",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split("\n")
                    gpu_info["gpu_count"] = len(lines)
                    gpu_info["gpu_memory"] = []

                    for line in lines:
                        parts = line.split(", ")
                        if len(parts) >= 3:
                            gpu_info["gpu_memory"].append(
                                {
                                    "name": parts[0],
                                    "total_memory": int(parts[1]),
                                    "used_memory": int(parts[2]),
                                }
                            )

                    gpu_info["cuda_available"] = True
                    logger.info(f"🎮 GPU Probe: {gpu_info['gpu_count']} GPUs detected")

            except (subprocess.TimeoutExpired, FileNotFoundError):
                logger.info("🎮 GPU Probe: No NVIDIA GPU detected")

            # Try to detect CUDA availability
            try:
                import torch

                if torch.cuda.is_available():
                    gpu_info["cuda_available"] = True
                    gpu_info["gpu_count"] = torch.cuda.device_count()
                    logger.info(
                        f"🎮 GPU Probe: CUDA available, {gpu_info['gpu_count']} devices"
                    )
            except ImportError:
                logger.info("🎮 GPU Probe: PyTorch not available")

            return gpu_info

        except Exception as e:
            logger.error(f"GPU probe error: {e}")
            return None

    def probe_memory(self):
        """Probe memory information"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()

            memory_info = {
                "total_memory": memory.total,
                "available_memory": memory.available,
                "used_memory": memory.used,
                "memory_percent": memory.percent,
                "swap_total": swap.total,
                "swap_used": swap.used,
                "swap_percent": swap.percent,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"💾 Memory Probe: {memory_info['memory_percent']:.1f}% used, {memory_info['available_memory'] // (1024**3)}GB available"
            )
            return memory_info

        except Exception as e:
            logger.error(f"Memory probe error: {e}")
            return None

    def probe_disk(self):
        """Probe disk information"""
        try:
            disk_info = []

            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info.append(
                        {
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "fstype": partition.fstype,
                            "total_space": usage.total,
                            "used_space": usage.used,
                            "free_space": usage.free,
                            "percent_used": (usage.used / usage.total) * 100,
                        }
                    )
                except PermissionError:
                    continue

            logger.info(f"💿 Disk Probe: {len(disk_info)} partitions")
            return disk_info

        except Exception as e:
            logger.error(f"Disk probe error: {e}")
            return None

    def check_agent_health(self, agent):
        """Check health of a specific agent"""
        try:
            import requests

            # Try to ping the agent
            if agent.get("heartbeat_url"):
                url = agent["heartbeat_url"]

                # Convert ws:// to http:// for health check
                if url.startswith("ws://"):
                    url = url.replace("ws://", "http://")
                elif url.startswith("wss://"):
                    url = url.replace("wss://", "https://")

                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    return "healthy"
                else:
                    return "unhealthy"
            else:
                return "unknown"

        except Exception as e:
            logger.debug(f"Health check error for {agent['id']}: {e}")
            return "unhealthy"

    def update_agent_status(self):
        """Update status of all agents"""
        try:
            if not Path(self.config_path).exists():
                return

            with open(self.config_path, "r") as f:
                agents_data = yaml.safe_load(f)

            agents = agents_data.get("agents", [])
            updated_count = 0

            for agent in agents:
                old_status = agent.get("status", "unknown")
                new_status = self.check_agent_health(agent)

                if old_status != new_status:
                    agent["status"] = new_status
                    agent["last_seen"] = datetime.now().isoformat()
                    updated_count += 1

                    logger.info(f"📊 Agent {agent['id']}: {old_status} -> {new_status}")

            if updated_count > 0:
                # Write updated status
                with open(self.config_path, "w") as f:
                    yaml.dump(agents_data, f, default_flow_style=False)

                logger.info(f"📝 Updated {updated_count} agent statuses")

        except Exception as e:
            logger.error(f"Error updating agent status: {e}")

    def start_heartbeat(self, interval=15):
        """Start periodic heartbeat service"""
        self.interval = interval
        self.running = True

        logger.info(f"💓 Starting heartbeat service (interval: {interval}s)")

        while self.running:
            try:
                # Update agent status
                self.update_agent_status()

                # Log system metrics
                cpu_info = self.probe_cpu()
                memory_info = self.probe_memory()

                logger.info(
                    f"📊 System: CPU {cpu_info['cpu_percent']:.1f}%, Memory {memory_info['memory_percent']:.1f}%"
                )

                # Wait for next cycle
                time.sleep(self.interval)

            except KeyboardInterrupt:
                logger.info("🛑 Heartbeat service stopped")
                self.running = False
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
                time.sleep(self.interval)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Heartbeat Service")
    parser.add_argument("--start", action="store_true", help="Start heartbeat service")
    parser.add_argument(
        "--interval", type=int, default=15, help="Heartbeat interval in seconds"
    )
    parser.add_argument(
        "--probe", choices=["cpu", "gpu", "memory", "disk"], help="Run specific probe"
    )

    args = parser.parse_args()

    service = HeartbeatService()

    if args.probe:
        if args.probe == "cpu":
            service.probe_cpu()
        elif args.probe == "gpu":
            service.probe_gpu()
        elif args.probe == "memory":
            service.probe_memory()
        elif args.probe == "disk":
            service.probe_disk()
    elif args.start:
        service.start_heartbeat(args.interval)
    else:
        # Run all probes
        logger.info("🔍 Running system probes...")
        service.probe_cpu()
        service.probe_gpu()
        service.probe_memory()
        service.probe_disk()
        logger.info("✅ System probes completed")


if __name__ == "__main__":
    main()
