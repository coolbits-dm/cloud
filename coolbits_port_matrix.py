#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CoolBits.ai Port Matrix Manager
SC COOL BITS SRL - Scalable Port Management System
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class CoolBitsPortMatrix:
    """Scalable port matrix management for CoolBits.ai ecosystem"""

    def __init__(self):
        self.company = "SC COOL BITS SRL"
        self.ceo = "Andrei"
        self.ai_assistant = "Cursor AI Assistant"
        self.contract_date = "2025-09-06"

        # Port Matrix Strategy - Starting from 8100+
        self.port_matrix = {
            # CORE SERVICES (8100-8149)
            "core_services": {
                "range": "8100-8149",
                "description": "Core CoolBits.ai services",
                "services": {
                    "main_bridge": {
                        "port": 8100,
                        "service": "Main CoolBits Bridge",
                        "status": "active",
                    },
                    "multi_agent_chat": {
                        "port": 8101,
                        "service": "Multi-Agent Chat System",
                        "status": "active",
                    },
                    "enhanced_multi_agent": {
                        "port": 8102,
                        "service": "Enhanced Multi-Agent Chat",
                        "status": "active",
                    },
                    "agent_portal": {
                        "port": 8103,
                        "service": "Individual Agent Portal",
                        "status": "active",
                    },
                    "cursor_root": {
                        "port": 8104,
                        "service": "Cursor AI Assistant Root Console",
                        "status": "active",
                    },
                    "complete_dashboard": {
                        "port": 8105,
                        "service": "Complete Dashboard",
                        "status": "active",
                    },
                    "google_cloud_agent": {
                        "port": 8106,
                        "service": "Google Cloud CLI Agent",
                        "status": "active",
                    },
                    "api_gateway": {
                        "port": 8107,
                        "service": "API Gateway",
                        "status": "reserved",
                    },
                    "websocket_server": {
                        "port": 8108,
                        "service": "WebSocket Server",
                        "status": "reserved",
                    },
                    "notification_service": {
                        "port": 8109,
                        "service": "Notification Service",
                        "status": "reserved",
                    },
                },
            },
            # RAG SERVICES (8150-8199)
            "rag_services": {
                "range": "8150-8199",
                "description": "Retrieval-Augmented Generation services",
                "services": {
                    "advanced_rag": {
                        "port": 8150,
                        "service": "Advanced RAG System",
                        "status": "active",
                    },
                    "multi_domain_rag": {
                        "port": 8151,
                        "service": "Multi-Domain RAG",
                        "status": "active",
                    },
                    "functional_rag": {
                        "port": 8152,
                        "service": "Functional RAG System",
                        "status": "active",
                    },
                    "vertex_rag": {
                        "port": 8153,
                        "service": "Vertex AI RAG",
                        "status": "active",
                    },
                    "rag_admin": {
                        "port": 8154,
                        "service": "RAG Admin Panel",
                        "status": "active",
                    },
                    "vector_search": {
                        "port": 8155,
                        "service": "Vector Search Engine",
                        "status": "reserved",
                    },
                    "embedding_service": {
                        "port": 8156,
                        "service": "Embedding Service",
                        "status": "reserved",
                    },
                    "knowledge_graph": {
                        "port": 8157,
                        "service": "Knowledge Graph",
                        "status": "reserved",
                    },
                    "document_processor": {
                        "port": 8158,
                        "service": "Document Processor",
                        "status": "reserved",
                    },
                    "semantic_search": {
                        "port": 8159,
                        "service": "Semantic Search",
                        "status": "reserved",
                    },
                },
            },
            # DEVELOPMENT AGENTS (8200-8249)
            "development_agents": {
                "range": "8200-8249",
                "description": "Specialized development agents with external API keys",
                "services": {
                    "frontend_agent": {
                        "port": 8200,
                        "service": "Frontend Development Agent",
                        "status": "ready",
                        "api_keys": ["ogpt01-frontend", "ogrok01-frontend"],
                    },
                    "backend_agent": {
                        "port": 8201,
                        "service": "Backend Development Agent",
                        "status": "ready",
                        "api_keys": ["ogpt02-backend", "ogrok02-backend"],
                    },
                    "devops_agent": {
                        "port": 8202,
                        "service": "DevOps Automation Agent",
                        "status": "ready",
                        "api_keys": ["ogpt03-devops", "ogrok03-devops"],
                    },
                    "testing_agent": {
                        "port": 8203,
                        "service": "Quality Assurance Agent",
                        "status": "ready",
                        "api_keys": ["ogpt04-testing", "ogrok04-testing"],
                    },
                    "security_agent": {
                        "port": 8204,
                        "service": "Security Agent",
                        "status": "reserved",
                        "api_keys": ["ogpt05-security", "ogrok05-security"],
                    },
                    "database_agent": {
                        "port": 8205,
                        "service": "Database Agent",
                        "status": "reserved",
                        "api_keys": ["ogpt06-database", "ogrok06-database"],
                    },
                    "mobile_agent": {
                        "port": 8206,
                        "service": "Mobile Development Agent",
                        "status": "reserved",
                        "api_keys": ["ogpt07-mobile", "ogrok07-mobile"],
                    },
                    "ai_ml_agent": {
                        "port": 8207,
                        "service": "AI/ML Development Agent",
                        "status": "reserved",
                        "api_keys": ["ogpt08-aiml", "ogrok08-aiml"],
                    },
                    "blockchain_agent": {
                        "port": 8208,
                        "service": "Blockchain Agent",
                        "status": "reserved",
                        "api_keys": ["ogpt09-blockchain", "ogrok09-blockchain"],
                    },
                    "iot_agent": {
                        "port": 8209,
                        "service": "IoT Development Agent",
                        "status": "reserved",
                        "api_keys": ["ogpt10-iot", "ogrok10-iot"],
                    },
                },
            },
            # CBLM.AI SERVICES (8250-8299)
            "cblm_services": {
                "range": "8250-8299",
                "description": "cbLM.ai Language Model Platform services",
                "services": {
                    "cblm_main": {
                        "port": 8250,
                        "service": "cbLM.ai Main Platform",
                        "status": "planning",
                    },
                    "cblm_inference": {
                        "port": 8251,
                        "service": "cbLM.ai Inference Engine",
                        "status": "planning",
                    },
                    "cblm_training": {
                        "port": 8252,
                        "service": "cbLM.ai Training Pipeline",
                        "status": "planning",
                    },
                    "cblm_evaluation": {
                        "port": 8253,
                        "service": "cbLM.ai Evaluation Metrics",
                        "status": "planning",
                    },
                    "model_serving": {
                        "port": 8254,
                        "service": "Model Serving",
                        "status": "reserved",
                    },
                    "fine_tuning": {
                        "port": 8255,
                        "service": "Fine-tuning Service",
                        "status": "reserved",
                    },
                    "model_registry": {
                        "port": 8256,
                        "service": "Model Registry",
                        "status": "reserved",
                    },
                    "experiment_tracking": {
                        "port": 8257,
                        "service": "Experiment Tracking",
                        "status": "reserved",
                    },
                    "data_pipeline": {
                        "port": 8258,
                        "service": "Data Pipeline",
                        "status": "reserved",
                    },
                    "model_monitoring": {
                        "port": 8259,
                        "service": "Model Monitoring",
                        "status": "reserved",
                    },
                },
            },
            # ADMIN & MONITORING (8300-8349)
            "admin_monitoring": {
                "range": "8300-8349",
                "description": "Administration and monitoring services",
                "services": {
                    "coolbits_admin": {
                        "port": 8300,
                        "service": "CoolBits Admin Panel",
                        "status": "active",
                    },
                    "vertex_admin": {
                        "port": 8301,
                        "service": "Vertex AI Admin",
                        "status": "active",
                    },
                    "system_monitor": {
                        "port": 8302,
                        "service": "System Monitor",
                        "status": "reserved",
                    },
                    "log_aggregator": {
                        "port": 8303,
                        "service": "Log Aggregator",
                        "status": "reserved",
                    },
                    "metrics_collector": {
                        "port": 8304,
                        "service": "Metrics Collector",
                        "status": "reserved",
                    },
                    "alert_manager": {
                        "port": 8305,
                        "service": "Alert Manager",
                        "status": "reserved",
                    },
                    "health_checker": {
                        "port": 8306,
                        "service": "Health Checker",
                        "status": "reserved",
                    },
                    "backup_service": {
                        "port": 8307,
                        "service": "Backup Service",
                        "status": "reserved",
                    },
                    "config_manager": {
                        "port": 8308,
                        "service": "Configuration Manager",
                        "status": "reserved",
                    },
                    "secret_manager": {
                        "port": 8309,
                        "service": "Secret Manager",
                        "status": "reserved",
                    },
                },
            },
            # GOOGLE CLOUD INTEGRATION (8350-8399)
            "google_cloud": {
                "range": "8350-8399",
                "description": "Google Cloud and Vertex AI integration services",
                "services": {
                    "vertex_ai_bridge": {
                        "port": 8350,
                        "service": "Vertex AI Bridge",
                        "status": "reserved",
                    },
                    "bigquery_connector": {
                        "port": 8351,
                        "service": "BigQuery Connector",
                        "status": "reserved",
                    },
                    "cloud_storage": {
                        "port": 8352,
                        "service": "Cloud Storage",
                        "status": "reserved",
                    },
                    "cloud_functions": {
                        "port": 8353,
                        "service": "Cloud Functions",
                        "status": "reserved",
                    },
                    "cloud_run": {
                        "port": 8354,
                        "service": "Cloud Run",
                        "status": "reserved",
                    },
                    "gke_connector": {
                        "port": 8355,
                        "service": "GKE Connector",
                        "status": "reserved",
                    },
                    "cloud_sql": {
                        "port": 8356,
                        "service": "Cloud SQL",
                        "status": "reserved",
                    },
                    "pub_sub": {
                        "port": 8357,
                        "service": "Pub/Sub",
                        "status": "reserved",
                    },
                    "cloud_logging": {
                        "port": 8358,
                        "service": "Cloud Logging",
                        "status": "reserved",
                    },
                    "cloud_monitoring": {
                        "port": 8359,
                        "service": "Cloud Monitoring",
                        "status": "reserved",
                    },
                },
            },
            # TESTING & DEVELOPMENT (8400-8449)
            "testing_development": {
                "range": "8400-8449",
                "description": "Testing and development services",
                "services": {
                    "test_runner": {
                        "port": 8400,
                        "service": "Test Runner",
                        "status": "reserved",
                    },
                    "mock_services": {
                        "port": 8401,
                        "service": "Mock Services",
                        "status": "reserved",
                    },
                    "dev_tools": {
                        "port": 8402,
                        "service": "Development Tools",
                        "status": "reserved",
                    },
                    "debug_server": {
                        "port": 8403,
                        "service": "Debug Server",
                        "status": "reserved",
                    },
                    "hot_reload": {
                        "port": 8404,
                        "service": "Hot Reload",
                        "status": "reserved",
                    },
                    "code_analyzer": {
                        "port": 8405,
                        "service": "Code Analyzer",
                        "status": "reserved",
                    },
                    "performance_test": {
                        "port": 8406,
                        "service": "Performance Testing",
                        "status": "reserved",
                    },
                    "load_testing": {
                        "port": 8407,
                        "service": "Load Testing",
                        "status": "reserved",
                    },
                    "security_scan": {
                        "port": 8408,
                        "service": "Security Scanning",
                        "status": "reserved",
                    },
                    "dependency_check": {
                        "port": 8409,
                        "service": "Dependency Check",
                        "status": "reserved",
                    },
                },
            },
            # FUTURE EXPANSION (8450-8999)
            "future_expansion": {
                "range": "8450-8999",
                "description": "Future expansion and custom services",
                "services": {
                    "custom_service_1": {
                        "port": 8450,
                        "service": "Custom Service 1",
                        "status": "available",
                    },
                    "custom_service_2": {
                        "port": 8451,
                        "service": "Custom Service 2",
                        "status": "available",
                    },
                    "custom_service_3": {
                        "port": 8452,
                        "service": "Custom Service 3",
                        "status": "available",
                    },
                    "expansion_slot_1": {
                        "port": 8453,
                        "service": "Expansion Slot 1",
                        "status": "available",
                    },
                    "expansion_slot_2": {
                        "port": 8454,
                        "service": "Expansion Slot 2",
                        "status": "available",
                    },
                    "expansion_slot_3": {
                        "port": 8455,
                        "service": "Expansion Slot 3",
                        "status": "available",
                    },
                    "expansion_slot_4": {
                        "port": 8456,
                        "service": "Expansion Slot 4",
                        "status": "available",
                    },
                    "expansion_slot_5": {
                        "port": 8457,
                        "service": "Expansion Slot 5",
                        "status": "available",
                    },
                    "expansion_slot_6": {
                        "port": 8458,
                        "service": "Expansion Slot 6",
                        "status": "available",
                    },
                    "expansion_slot_7": {
                        "port": 8459,
                        "service": "Expansion Slot 7",
                        "status": "available",
                    },
                },
            },
        }

        # Port allocation strategy
        self.allocation_strategy = {
            "core_services": {"start": 8100, "end": 8149, "count": 50},
            "rag_services": {"start": 8150, "end": 8199, "count": 50},
            "development_agents": {"start": 8200, "end": 8249, "count": 50},
            "cblm_services": {"start": 8250, "end": 8299, "count": 50},
            "admin_monitoring": {"start": 8300, "end": 8349, "count": 50},
            "google_cloud": {"start": 8350, "end": 8399, "count": 50},
            "testing_development": {"start": 8400, "end": 8449, "count": 50},
            "future_expansion": {"start": 8450, "end": 8999, "count": 550},
        }

    def get_port_matrix(self) -> Dict[str, Any]:
        """Get complete port matrix"""
        return {
            "company": self.company,
            "ceo": self.ceo,
            "ai_assistant": self.ai_assistant,
            "contract_date": self.contract_date,
            "port_matrix": self.port_matrix,
            "allocation_strategy": self.allocation_strategy,
            "total_ports": 900,  # 8100-8999
            "available_ports": 900,
            "timestamp": datetime.now().isoformat(),
        }

    def get_available_port(self, category: str) -> Optional[int]:
        """Get next available port in category"""
        if category not in self.port_matrix:
            return None

        category_services = self.port_matrix[category]["services"]
        for service_name, service_info in category_services.items():
            if service_info["status"] == "available":
                return service_info["port"]

        return None

    def allocate_port(self, category: str, service_name: str, port: int) -> bool:
        """Allocate a specific port for a service"""
        try:
            if category not in self.port_matrix:
                return False

            if service_name in self.port_matrix[category]["services"]:
                self.port_matrix[category]["services"][service_name]["port"] = port
                self.port_matrix[category]["services"][service_name][
                    "status"
                ] = "allocated"
                return True

            return False

        except Exception as e:
            print(f"Error allocating port: {e}")
            return False

    def check_port_conflicts(self) -> List[Dict[str, Any]]:
        """Check for port conflicts"""
        conflicts = []
        used_ports = {}

        for category_name, category_info in self.port_matrix.items():
            for service_name, service_info in category_info["services"].items():
                port = service_info["port"]
                if port in used_ports:
                    conflicts.append(
                        {
                            "port": port,
                            "conflict": f"{used_ports[port]} vs {service_name}",
                            "category": category_name,
                            "status": "conflict",
                        }
                    )
                else:
                    used_ports[port] = service_name

        return conflicts

    def get_services_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get all services with specific status"""
        services = []

        for category_name, category_info in self.port_matrix.items():
            for service_name, service_info in category_info["services"].items():
                if service_info["status"] == status:
                    services.append(
                        {
                            "service": service_name,
                            "port": service_info["port"],
                            "category": category_name,
                            "description": service_info["service"],
                            "status": service_info["status"],
                        }
                    )

        return services

    def print_port_matrix(self):
        """Print complete port matrix"""
        print("=" * 80)
        print("🚀 COOLBITS.AI PORT MATRIX - SCALABLE SYSTEM")
        print("🏢 SC COOL BITS SRL - Port Management Strategy")
        print("=" * 80)
        print(f"👤 CEO: {self.ceo}")
        print(f"🤖 AI Assistant: {self.ai_assistant}")
        print(f"📅 Contract Date: {self.contract_date}")
        print("=" * 80)

        for category_name, category_info in self.port_matrix.items():
            print(
                f"\n📋 {category_name.upper().replace('_', ' ')} ({category_info['range']})"
            )
            print(f"   Description: {category_info['description']}")
            print("   " + "-" * 60)

            for service_name, service_info in category_info["services"].items():
                status_icon = (
                    "🟢"
                    if service_info["status"] == "active"
                    else (
                        "🟡"
                        if service_info["status"] == "ready"
                        else "🔵" if service_info["status"] == "reserved" else "⚪"
                    )
                )
                print(
                    f"   {status_icon} Port {service_info['port']:4d} | {service_info['service']:<30} | {service_info['status']}"
                )

        print("=" * 80)
        print("🎯 PORT ALLOCATION STRATEGY:")
        for category, strategy in self.allocation_strategy.items():
            print(
                f"   {category}: {strategy['start']}-{strategy['end']} ({strategy['count']} ports)"
            )

        print("=" * 80)
        print("✅ TOTAL PORTS: 900 (8100-8999)")
        print("✅ SCALABLE: Incremental expansion possible")
        print("✅ COMPATIBLE: Google Cloud & Vertex AI ready")
        print("=" * 80)


# Initialize Port Matrix
port_matrix = CoolBitsPortMatrix()


# Main functions
def show_port_matrix():
    """🚀 Show complete port matrix"""
    port_matrix.print_port_matrix()


def get_port_matrix():
    """📋 Get port matrix data"""
    return port_matrix.get_port_matrix()


def check_port_conflicts():
    """⚠️ Check for port conflicts"""
    conflicts = port_matrix.check_port_conflicts()
    if conflicts:
        print("⚠️ PORT CONFLICTS DETECTED:")
        for conflict in conflicts:
            print(f"   Port {conflict['port']}: {conflict['conflict']}")
    else:
        print("✅ No port conflicts detected")
    return conflicts


def get_active_services():
    """🟢 Get all active services"""
    active_services = port_matrix.get_services_by_status("active")
    print("🟢 ACTIVE SERVICES:")
    for service in active_services:
        print(
            f"   Port {service['port']:4d} | {service['service']:<30} | {service['category']}"
        )
    return active_services


def get_ready_services():
    """🟡 Get all ready services"""
    ready_services = port_matrix.get_services_by_status("ready")
    print("🟡 READY SERVICES:")
    for service in ready_services:
        print(
            f"   Port {service['port']:4d} | {service['service']:<30} | {service['category']}"
        )
    return ready_services


if __name__ == "__main__":
    print("=" * 80)
    print("🚀 COOLBITS.AI PORT MATRIX MANAGER")
    print("🏢 SC COOL BITS SRL - Scalable Port Management")
    print("=" * 80)
    print(f"👤 CEO: {port_matrix.ceo}")
    print(f"🤖 AI Assistant: {port_matrix.ai_assistant}")
    print(f"📅 Contract Date: {port_matrix.contract_date}")
    print("=" * 80)
    print("🚀 Available Commands:")
    print("  • show_port_matrix() - Show complete port matrix")
    print("  • get_port_matrix() - Get port matrix data")
    print("  • check_port_conflicts() - Check for conflicts")
    print("  • get_active_services() - Get active services")
    print("  • get_ready_services() - Get ready services")
    print("=" * 80)
