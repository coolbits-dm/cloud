#!/usr/bin/env python3
"""
oVertex Agent - Windows 11 Infrastructure Analysis & Best Practices
COOL BITS S.R.L. Local Development Environment Optimization
"""

import json
import subprocess
import platform
import psutil
import os
from datetime import datetime


class Windows11InfrastructureAnalysis:
    def __init__(self):
        self.company_details = {
            "company": "COOL BITS S.R.L.",
            "cui": "42331573",
            "euid": "ROONRC.J22/676/2020",
            "project_id": "coolbits-ai",
        }

    def analyze_system_resources(self):
        """Analyze current system resources"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "os": platform.system(),
                "os_version": platform.version(),
                "architecture": platform.architecture(),
                "processor": platform.processor(),
                "hostname": platform.node(),
            },
            "cpu": {
                "cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            },
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "used": psutil.virtual_memory().used,
                "percentage": psutil.virtual_memory().percent,
            },
            "storage": self.analyze_storage(),
            "gpu": self.analyze_gpu(),
            "network": self.analyze_network(),
        }

        return analysis

    def analyze_storage(self):
        """Analyze storage devices"""
        storage_info = []
        for partition in psutil.disk_partitions():
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                storage_info.append(
                    {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": partition_usage.total,
                        "used": partition_usage.used,
                        "free": partition_usage.free,
                        "percentage": (partition_usage.used / partition_usage.total)
                        * 100,
                    }
                )
            except PermissionError:
                continue
        return storage_info

    def analyze_gpu(self):
        """Analyze GPU resources"""
        try:
            # Try to get NVIDIA GPU info
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                gpu_info = result.stdout.strip().split(",")
                return {
                    "name": gpu_info[0].strip(),
                    "memory_total": int(gpu_info[1].strip()),
                    "memory_used": int(gpu_info[2].strip()),
                    "memory_free": int(gpu_info[3].strip()),
                    "utilization": int(gpu_info[4].strip()),
                }
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return {"status": "NVIDIA GPU not detected or nvidia-smi not available"}

    def analyze_network(self):
        """Analyze network interfaces"""
        network_info = []
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == 2:  # AF_INET
                    network_info.append(
                        {
                            "interface": interface,
                            "ip": addr.address,
                            "netmask": addr.netmask,
                            "broadcast": addr.broadcast,
                        }
                    )
        return network_info

    def generate_best_practices(self):
        """Generate best practices for Windows 11 development environment"""
        best_practices = {
            "cpu_optimization": {
                "recommendations": [
                    "Enable CPU virtualization features (VT-x/AMD-V)",
                    "Set CPU power plan to 'High Performance' for development",
                    "Disable CPU throttling during intensive operations",
                    "Use CPU affinity for critical processes",
                    "Monitor CPU temperature and implement cooling solutions",
                ],
                "windows_specific": [
                    "Disable Windows Defender real-time scanning for dev folders",
                    "Exclude development directories from Windows Search indexing",
                    "Disable Windows Update automatic restarts during work hours",
                    "Configure Windows Power Management for consistent performance",
                ],
            },
            "gpu_optimization": {
                "nvidia_specific": [
                    "Install latest NVIDIA drivers (RTX 2060 compatible)",
                    "Configure CUDA 12.6 environment variables",
                    "Set GPU power management to 'Prefer Maximum Performance'",
                    "Enable GPU Boost for AI/ML workloads",
                    "Configure NVIDIA Control Panel for development applications",
                ],
                "cuda_optimization": [
                    "Set CUDA_VISIBLE_DEVICES environment variable",
                    "Configure CUDA memory allocation strategies",
                    "Enable CUDA unified memory for large datasets",
                    "Optimize CUDA kernel launch configurations",
                ],
            },
            "storage_optimization": {
                "nvme_optimization": [
                    "Enable TRIM support for SSD longevity",
                    "Configure Windows Storage Spaces for redundancy",
                    "Use NVMe-specific drivers for maximum performance",
                    "Implement SSD wear leveling monitoring",
                    "Configure page file on fastest storage device",
                ],
                "development_storage": [
                    "Separate OS, applications, and data on different drives",
                    "Use symbolic links for large dependency directories",
                    "Implement automated backup strategies",
                    "Configure Windows File History for critical projects",
                ],
            },
            "certificate_management": {
                "company_certificates": [
                    "Register SSL certificates under COOL BITS S.R.L.",
                    "Configure code signing certificates for applications",
                    "Set up client certificates for API authentication",
                    "Implement certificate auto-renewal mechanisms",
                    "Configure Windows Certificate Store for development",
                ],
                "development_certificates": [
                    "Generate self-signed certificates for local development",
                    "Configure HTTPS for local development servers",
                    "Set up certificate trust chains for testing",
                    "Implement certificate pinning for security",
                ],
            },
            "vertex_ai_integration": {
                "local_setup": [
                    "Configure Google Cloud CLI with COOL BITS S.R.L. credentials",
                    "Set up Application Default Credentials (ADC)",
                    "Configure local development environment variables",
                    "Implement secure credential storage using Windows Credential Manager",
                    "Set up local proxy for Google Cloud API calls",
                ],
                "document_ai_setup": [
                    "Enable Document AI API in Google Cloud Console",
                    "Configure Layout Parser processor for COOL BITS S.R.L.",
                    "Set up local document processing pipeline",
                    "Implement batch processing for large document sets",
                    "Configure error handling and retry mechanisms",
                ],
            },
        }

        return best_practices

    def generate_gemini_cli_plan(self):
        """Generate comprehensive plan for Gemini CLI implementation"""
        plan = {
            "phase_1": {
                "title": "Infrastructure Assessment & Setup",
                "tasks": [
                    "Analyze current Windows 11 system resources",
                    "Configure CPU/GPU optimization settings",
                    "Set up storage optimization for NVMe SSD",
                    "Register COOL BITS S.R.L. certificates",
                    "Configure Google Cloud CLI authentication",
                ],
                "deliverables": [
                    "System resource analysis report",
                    "Optimized Windows 11 configuration",
                    "Certificate registration documentation",
                    "Google Cloud CLI setup guide",
                ],
            },
            "phase_2": {
                "title": "Vertex AI Integration Setup",
                "tasks": [
                    "Enable Document AI API in Google Cloud Console",
                    "Create Layout Parser processor for COOL BITS S.R.L.",
                    "Configure RAG corpus with Layout Parser integration",
                    "Set up local development environment",
                    "Implement real-time sync pipeline",
                ],
                "deliverables": [
                    "Document AI API configuration",
                    "Layout Parser processor setup",
                    "RAG corpus with Layout Parser integration",
                    "Local development environment",
                    "Sync pipeline implementation",
                ],
            },
            "phase_3": {
                "title": "Production Deployment & Monitoring",
                "tasks": [
                    "Deploy Vertex AI services to production",
                    "Configure monitoring and alerting",
                    "Implement cost optimization strategies",
                    "Set up automated backup and recovery",
                    "Configure security and compliance",
                ],
                "deliverables": [
                    "Production deployment",
                    "Monitoring dashboard",
                    "Cost optimization report",
                    "Backup and recovery procedures",
                    "Security compliance documentation",
                ],
            },
        }

        return plan


if __name__ == "__main__":
    analyzer = Windows11InfrastructureAnalysis()

    print("🚀 oVertex Agent - Windows 11 Infrastructure Analysis")
    print("=" * 60)
    print(f"Company: {analyzer.company_details['company']}")
    print(f"CUI: {analyzer.company_details['cui']}")
    print(f"Project: {analyzer.company_details['project_id']}")
    print("=" * 60)

    # Analyze system resources
    print("📊 Analyzing system resources...")
    system_analysis = analyzer.analyze_system_resources()

    # Generate best practices
    print("🔧 Generating best practices...")
    best_practices = analyzer.generate_best_practices()

    # Generate Gemini CLI plan
    print("📋 Generating Gemini CLI implementation plan...")
    gemini_plan = analyzer.generate_gemini_cli_plan()

    # Save results
    results = {
        "company_details": analyzer.company_details,
        "system_analysis": system_analysis,
        "best_practices": best_practices,
        "gemini_cli_plan": gemini_plan,
        "generated_at": datetime.now().isoformat(),
    }

    with open("windows11_infrastructure_analysis.json", "w") as f:
        json.dump(results, f, indent=2)

    print("✅ Analysis complete!")
    print("📄 Results saved to: windows11_infrastructure_analysis.json")

    # Display key findings
    print("\n🔍 Key Findings:")
    print(
        f"CPU Cores: {system_analysis['cpu']['cores']} physical, {system_analysis['cpu']['logical_cores']} logical"
    )
    print(f"Memory: {system_analysis['memory']['total'] // (1024**3)} GB total")
    print(f"Storage Devices: {len(system_analysis['storage'])}")
    print(f"GPU Status: {system_analysis['gpu'].get('name', 'Not detected')}")

    print("\n📋 Gemini CLI Plan Summary:")
    for phase, details in gemini_plan.items():
        print(f"{phase.upper()}: {details['title']}")
        print(f"  Tasks: {len(details['tasks'])}")
        print(f"  Deliverables: {len(details['deliverables'])}")
