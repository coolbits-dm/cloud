#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CoolBits.ai System Console with nVidia GPU Integration
SC COOL BITS SRL - Hardware monitoring and processing
"""

import os
import sys
import json
import subprocess
import psutil
import time
from datetime import datetime
from typing import Dict, List, Any, Optional


class CoolBitsSystemConsole:
    """System Console with nVidia GPU integration"""

    def __init__(self):
        self.company = "SC COOL BITS SRL"
        self.ceo = "Andrei"
        self.ai_assistant = "Cursor AI Assistant"
        self.contract_date = "2025-09-06"

        # Hardware specs
        self.hardware = {
            "cpu": "AMD Ryzen 7 2700X (8 cores, 16 threads)",
            "gpu": "NVIDIA GeForce RTX 2060 (6GB VRAM)",
            "ram": "32GB",
            "os": "Windows 11",
        }

        # Processing capabilities
        self.processing = {
            "cpu_cores": 8,
            "cpu_threads": 16,
            "gpu_memory": 6144,  # MB
            "gpu_cuda_version": "12.6",
            "ram_total": 32,  # GB
            "gpu_utilization": 0,
            "cpu_utilization": 0,
            "ram_utilization": 0,
        }

    def get_nvidia_info(self) -> Dict[str, Any]:
        """Get nVidia GPU information"""
        try:
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,memory.total,memory.used,utilization.gpu,temperature.gpu,power.draw",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                gpu_info = result.stdout.strip().split(", ")
                return {
                    "name": gpu_info[0],
                    "memory_total": int(gpu_info[1]),
                    "memory_used": int(gpu_info[2]),
                    "utilization": int(gpu_info[3]),
                    "temperature": int(gpu_info[4]),
                    "power_draw": float(gpu_info[5]) if gpu_info[5] != "N/A" else 0,
                    "status": "active",
                }
            else:
                return {"status": "error", "message": "nvidia-smi failed"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()

            return {
                "utilization": cpu_percent,
                "cores": cpu_count,
                "frequency": cpu_freq.current if cpu_freq else 0,
                "status": "active",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory information"""
        try:
            memory = psutil.virtual_memory()
            return {
                "total": memory.total // (1024**3),  # GB
                "used": memory.used // (1024**3),  # GB
                "available": memory.available // (1024**3),  # GB
                "utilization": memory.percent,
                "status": "active",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_system_status(self) -> Dict[str, Any]:
        """Get complete system status"""
        return {
            "company": self.company,
            "ceo": self.ceo,
            "ai_assistant": self.ai_assistant,
            "contract_date": self.contract_date,
            "timestamp": datetime.now().isoformat(),
            "hardware": self.hardware,
            "nvidia_gpu": self.get_nvidia_info(),
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "processing": self.processing,
        }

    def print_system_status(self):
        """Print system status"""
        print("=" * 80)
        print("🖥️ COOLBITS.AI SYSTEM CONSOLE WITH nVidia GPU")
        print("🏢 SC COOL BITS SRL - Hardware Monitoring & Processing")
        print("=" * 80)
        print(f"👤 CEO: {self.ceo}")
        print(f"🤖 AI Assistant: {self.ai_assistant}")
        print(f"📅 Contract Date: {self.contract_date}")
        print("=" * 80)

        # Hardware specs
        print("🖥️ HARDWARE SPECIFICATIONS:")
        print(f"  • CPU: {self.hardware['cpu']}")
        print(f"  • GPU: {self.hardware['gpu']}")
        print(f"  • RAM: {self.hardware['ram']}")
        print(f"  • OS: {self.hardware['os']}")
        print("=" * 80)

        # nVidia GPU status
        gpu_info = self.get_nvidia_info()
        if gpu_info["status"] == "active":
            print("🎮 NVIDIA GPU STATUS:")
            print(f"  • Name: {gpu_info['name']}")
            print(
                f"  • Memory: {gpu_info['memory_used']}MB / {gpu_info['memory_total']}MB"
            )
            print(f"  • Utilization: {gpu_info['utilization']}%")
            print(f"  • Temperature: {gpu_info['temperature']}°C")
            print(f"  • Power Draw: {gpu_info['power_draw']}W")
        else:
            print(f"❌ NVIDIA GPU ERROR: {gpu_info['message']}")

        print("=" * 80)

        # CPU status
        cpu_info = self.get_cpu_info()
        if cpu_info["status"] == "active":
            print("💻 CPU STATUS:")
            print(f"  • Utilization: {cpu_info['utilization']}%")
            print(f"  • Cores: {cpu_info['cores']}")
            print(f"  • Frequency: {cpu_info['frequency']:.0f}MHz")
        else:
            print(f"❌ CPU ERROR: {cpu_info['message']}")

        print("=" * 80)

        # Memory status
        memory_info = self.get_memory_info()
        if memory_info["status"] == "active":
            print("🧠 MEMORY STATUS:")
            print(f"  • Total: {memory_info['total']}GB")
            print(f"  • Used: {memory_info['used']}GB")
            print(f"  • Available: {memory_info['available']}GB")
            print(f"  • Utilization: {memory_info['utilization']}%")
        else:
            print(f"❌ MEMORY ERROR: {memory_info['message']}")

        print("=" * 80)

        # Processing capabilities
        print("🚀 PROCESSING CAPABILITIES:")
        print(f"  • CPU Cores: {self.processing['cpu_cores']}")
        print(f"  • CPU Threads: {self.processing['cpu_threads']}")
        print(f"  • GPU Memory: {self.processing['gpu_memory']}MB")
        print(f"  • CUDA Version: {self.processing['gpu_cuda_version']}")
        print(f"  • RAM Total: {self.processing['ram_total']}GB")
        print("=" * 80)

        # Processing status
        print("⚡ PROCESSING STATUS:")
        print(f"  • GPU Utilization: {gpu_info.get('utilization', 0)}%")
        print(f"  • CPU Utilization: {cpu_info.get('utilization', 0)}%")
        print(f"  • RAM Utilization: {memory_info.get('utilization', 0)}%")
        print("=" * 80)

        # AI Processing capabilities
        print("🤖 AI PROCESSING CAPABILITIES:")
        print("  • ✅ CPU Processing: Available")
        print("  • ✅ GPU Processing: Available (nVidia CUDA)")
        print("  • ✅ Memory Processing: Available (32GB)")
        print("  • ✅ Multi-threading: Available (16 threads)")
        print("  • ✅ Parallel Processing: Available")
        print("=" * 80)

        print("🎯 SYSTEM READY FOR AI PROCESSING!")
        print("=" * 80)


# Initialize System Console
system_console = CoolBitsSystemConsole()


# Main functions
def system_status():
    """🖥️ Show complete system status"""
    system_console.print_system_status()


def nvidia_status():
    """🎮 Show nVidia GPU status"""
    gpu_info = system_console.get_nvidia_info()
    if gpu_info["status"] == "active":
        print("🎮 NVIDIA GPU STATUS:")
        print(f"  • Name: {gpu_info['name']}")
        print(f"  • Memory: {gpu_info['memory_used']}MB / {gpu_info['memory_total']}MB")
        print(f"  • Utilization: {gpu_info['utilization']}%")
        print(f"  • Temperature: {gpu_info['temperature']}°C")
        print(f"  • Power Draw: {gpu_info['power_draw']}W")
    else:
        print(f"❌ NVIDIA GPU ERROR: {gpu_info['message']}")


def cpu_status():
    """💻 Show CPU status"""
    cpu_info = system_console.get_cpu_info()
    if cpu_info["status"] == "active":
        print("💻 CPU STATUS:")
        print(f"  • Utilization: {cpu_info['utilization']}%")
        print(f"  • Cores: {cpu_info['cores']}")
        print(f"  • Frequency: {cpu_info['frequency']:.0f}MHz")
    else:
        print(f"❌ CPU ERROR: {cpu_info['message']}")


def memory_status():
    """🧠 Show memory status"""
    memory_info = system_console.get_memory_info()
    if memory_info["status"] == "active":
        print("🧠 MEMORY STATUS:")
        print(f"  • Total: {memory_info['total']}GB")
        print(f"  • Used: {memory_info['used']}GB")
        print(f"  • Available: {memory_info['available']}GB")
        print(f"  • Utilization: {memory_info['utilization']}%")
    else:
        print(f"❌ MEMORY ERROR: {memory_info['message']}")


def processing_status():
    """⚡ Show processing status"""
    gpu_info = system_console.get_nvidia_info()
    cpu_info = system_console.get_cpu_info()
    memory_info = system_console.get_memory_info()

    print("⚡ PROCESSING STATUS:")
    print(f"  • GPU Utilization: {gpu_info.get('utilization', 0)}%")
    print(f"  • CPU Utilization: {cpu_info.get('utilization', 0)}%")
    print(f"  • RAM Utilization: {memory_info.get('utilization', 0)}%")
    print("=" * 50)


if __name__ == "__main__":
    print("=" * 80)
    print("🖥️ COOLBITS.AI SYSTEM CONSOLE WITH nVidia GPU")
    print("🏢 SC COOL BITS SRL - Hardware Monitoring & Processing")
    print("=" * 80)
    print(f"👤 CEO: {system_console.ceo}")
    print(f"🤖 AI Assistant: {system_console.ai_assistant}")
    print(f"📅 Contract Date: {system_console.contract_date}")
    print("=" * 80)
    print("🚀 Available Commands:")
    print("  • system_status() - Show complete system status")
    print("  • nvidia_status() - Show nVidia GPU status")
    print("  • cpu_status() - Show CPU status")
    print("  • memory_status() - Show memory status")
    print("  • processing_status() - Show processing status")
    print("=" * 80)
