#!/usr/bin/env python3
"""
🤖 CoolBits.ai Advanced RAG Admin Panel Server
Unified RAG system with hierarchical categories and admin interface

Author: oCopilot (oCursor)
Date: September 6, 2025
"""

import os
import json
import logging
import asyncio
import sqlite3
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
import re

from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configuration
class RAGConfig(BaseModel):
    base_port: int = 8098
    max_documents: int = 1000

    # Main categories with display names and subcategories - Agent-specific RAG structure
    categories: Dict[str, Dict[str, Any]] = {
        # Agent-specific RAG categories
        "ceo-rag": {
            "display_name": "CEO Agent RAG",
            "description": "Strategic leadership, business development, and executive decision-making knowledge",
            "subcategories": {
                "strategy": {
                    "display_name": "Strategic Planning",
                    "description": "Business strategy and strategic planning",
                    "items": {
                        "market_analysis": "Market Analysis",
                        "competitive_strategy": "Competitive Strategy",
                        "business_development": "Business Development",
                        "partnerships": "Partnerships & Alliances",
                    },
                },
                "leadership": {
                    "display_name": "Leadership & Management",
                    "description": "Leadership principles and management practices",
                    "items": {
                        "team_leadership": "Team Leadership",
                        "organizational_culture": "Organizational Culture",
                        "decision_making": "Decision Making",
                        "crisis_management": "Crisis Management",
                    },
                },
                "finance": {
                    "display_name": "Financial Strategy",
                    "description": "Financial planning and investment decisions",
                    "items": {
                        "fundraising": "Fundraising",
                        "investment_strategy": "Investment Strategy",
                        "financial_planning": "Financial Planning",
                        "risk_management": "Risk Management",
                    },
                },
            },
        },
        "cto-rag": {
            "display_name": "CTO Agent RAG",
            "description": "Technical leadership, architecture, and technology strategy",
            "subcategories": {
                "architecture": {
                    "display_name": "System Architecture",
                    "description": "Technical architecture and system design",
                    "items": {
                        "microservices": "Microservices Architecture",
                        "cloud_strategy": "Cloud Strategy",
                        "scalability": "Scalability Planning",
                        "security_architecture": "Security Architecture",
                    },
                },
                "technology": {
                    "display_name": "Technology Stack",
                    "description": "Technology selection and implementation",
                    "items": {
                        "ai_ml": "AI/ML Technologies",
                        "databases": "Database Technologies",
                        "frontend": "Frontend Technologies",
                        "backend": "Backend Technologies",
                    },
                },
                "innovation": {
                    "display_name": "Innovation & R&D",
                    "description": "Research and development initiatives",
                    "items": {
                        "emerging_tech": "Emerging Technologies",
                        "research_projects": "Research Projects",
                        "patent_strategy": "Patent Strategy",
                        "tech_trends": "Technology Trends",
                    },
                },
            },
        },
        "cmo-rag": {
            "display_name": "CMO Agent RAG",
            "description": "Marketing strategy, brand management, and customer acquisition",
            "subcategories": {
                "digital_marketing": {
                    "display_name": "Digital Marketing",
                    "description": "Digital marketing strategies and tactics",
                    "items": {
                        "seo_sem": "SEO & SEM",
                        "social_media": "Social Media Marketing",
                        "content_marketing": "Content Marketing",
                        "email_marketing": "Email Marketing",
                    },
                },
                "brand": {
                    "display_name": "Brand Management",
                    "description": "Brand strategy and brand management",
                    "items": {
                        "brand_strategy": "Brand Strategy",
                        "brand_identity": "Brand Identity",
                        "brand_positioning": "Brand Positioning",
                        "brand_awareness": "Brand Awareness",
                    },
                },
                "analytics": {
                    "display_name": "Marketing Analytics",
                    "description": "Marketing performance and analytics",
                    "items": {
                        "campaign_analytics": "Campaign Analytics",
                        "customer_analytics": "Customer Analytics",
                        "roi_measurement": "ROI Measurement",
                        "attribution": "Attribution Modeling",
                    },
                },
            },
        },
        "cfo-rag": {
            "display_name": "CFO Agent RAG",
            "description": "Financial management, accounting, and financial strategy",
            "subcategories": {
                "accounting": {
                    "display_name": "Accounting & Finance",
                    "description": "Accounting principles and financial management",
                    "items": {
                        "financial_reporting": "Financial Reporting",
                        "budgeting": "Budgeting & Forecasting",
                        "cost_management": "Cost Management",
                        "tax_strategy": "Tax Strategy",
                    },
                },
                "investment": {
                    "display_name": "Investment & Capital",
                    "description": "Investment decisions and capital management",
                    "items": {
                        "capital_allocation": "Capital Allocation",
                        "investment_analysis": "Investment Analysis",
                        "mergers_acquisitions": "M&A Strategy",
                        "financial_modeling": "Financial Modeling",
                    },
                },
                "compliance": {
                    "display_name": "Compliance & Risk",
                    "description": "Financial compliance and risk management",
                    "items": {
                        "regulatory_compliance": "Regulatory Compliance",
                        "audit_management": "Audit Management",
                        "financial_controls": "Financial Controls",
                        "risk_assessment": "Risk Assessment",
                    },
                },
            },
        },
        "coo-rag": {
            "display_name": "COO Agent RAG",
            "description": "Operations management, process optimization, and operational excellence",
            "subcategories": {
                "operations": {
                    "display_name": "Operations Management",
                    "description": "Operational processes and management",
                    "items": {
                        "process_optimization": "Process Optimization",
                        "supply_chain": "Supply Chain Management",
                        "quality_management": "Quality Management",
                        "operational_efficiency": "Operational Efficiency",
                    },
                },
                "infrastructure": {
                    "display_name": "Infrastructure & Systems",
                    "description": "Infrastructure and system management",
                    "items": {
                        "it_infrastructure": "IT Infrastructure",
                        "facilities_management": "Facilities Management",
                        "system_integration": "System Integration",
                        "automation": "Process Automation",
                    },
                },
                "performance": {
                    "display_name": "Performance Management",
                    "description": "Performance measurement and improvement",
                    "items": {
                        "kpi_management": "KPI Management",
                        "performance_metrics": "Performance Metrics",
                        "continuous_improvement": "Continuous Improvement",
                        "operational_reporting": "Operational Reporting",
                    },
                },
            },
        },
        "vp_engineering-rag": {
            "display_name": "VP Engineering Agent RAG",
            "description": "Engineering management, development processes, and technical leadership",
            "subcategories": {
                "development": {
                    "display_name": "Development Processes",
                    "description": "Software development methodologies and processes",
                    "items": {
                        "agile_methodology": "Agile Methodology",
                        "devops": "DevOps Practices",
                        "code_quality": "Code Quality",
                        "testing_strategy": "Testing Strategy",
                    },
                },
                "team_management": {
                    "display_name": "Engineering Team Management",
                    "description": "Managing engineering teams and resources",
                    "items": {
                        "team_structure": "Team Structure",
                        "hiring": "Hiring & Recruitment",
                        "performance_reviews": "Performance Reviews",
                        "career_development": "Career Development",
                    },
                },
                "technical_debt": {
                    "display_name": "Technical Debt & Architecture",
                    "description": "Managing technical debt and architectural decisions",
                    "items": {
                        "technical_debt": "Technical Debt Management",
                        "architecture_decisions": "Architecture Decisions",
                        "refactoring": "Refactoring Strategies",
                        "legacy_systems": "Legacy System Management",
                    },
                },
            },
        },
        "head_ai-rag": {
            "display_name": "Head of AI Agent RAG",
            "description": "AI strategy, machine learning, and artificial intelligence initiatives",
            "subcategories": {
                "ai_strategy": {
                    "display_name": "AI Strategy",
                    "description": "AI strategy and implementation planning",
                    "items": {
                        "ai_roadmap": "AI Roadmap",
                        "ai_ethics": "AI Ethics",
                        "ai_governance": "AI Governance",
                        "ai_roi": "AI ROI Measurement",
                    },
                },
                "machine_learning": {
                    "display_name": "Machine Learning",
                    "description": "Machine learning models and algorithms",
                    "items": {
                        "ml_models": "ML Models",
                        "deep_learning": "Deep Learning",
                        "nlp": "Natural Language Processing",
                        "computer_vision": "Computer Vision",
                    },
                },
                "ai_infrastructure": {
                    "display_name": "AI Infrastructure",
                    "description": "AI infrastructure and platform management",
                    "items": {
                        "ml_platforms": "ML Platforms",
                        "data_pipelines": "Data Pipelines",
                        "model_deployment": "Model Deployment",
                        "ai_tools": "AI Tools & Frameworks",
                    },
                },
            },
        },
        "head_data-rag": {
            "display_name": "Head of Data Agent RAG",
            "description": "Data strategy, data management, and data analytics",
            "subcategories": {
                "data_strategy": {
                    "display_name": "Data Strategy",
                    "description": "Data strategy and governance",
                    "items": {
                        "data_governance": "Data Governance",
                        "data_quality": "Data Quality",
                        "data_privacy": "Data Privacy",
                        "data_security": "Data Security",
                    },
                },
                "data_engineering": {
                    "display_name": "Data Engineering",
                    "description": "Data engineering and infrastructure",
                    "items": {
                        "data_pipelines": "Data Pipelines",
                        "etl_processes": "ETL Processes",
                        "data_warehousing": "Data Warehousing",
                        "real_time_data": "Real-time Data",
                    },
                },
                "analytics": {
                    "display_name": "Data Analytics",
                    "description": "Data analytics and business intelligence",
                    "items": {
                        "business_intelligence": "Business Intelligence",
                        "data_visualization": "Data Visualization",
                        "predictive_analytics": "Predictive Analytics",
                        "reporting": "Reporting & Dashboards",
                    },
                },
            },
        },
        "head_hr-rag": {
            "display_name": "Head of HR Agent RAG",
            "description": "Human resources, talent management, and organizational development",
            "subcategories": {
                "talent_management": {
                    "display_name": "Talent Management",
                    "description": "Talent acquisition and management",
                    "items": {
                        "recruitment": "Recruitment",
                        "onboarding": "Onboarding",
                        "performance_management": "Performance Management",
                        "succession_planning": "Succession Planning",
                    },
                },
                "employee_development": {
                    "display_name": "Employee Development",
                    "description": "Employee training and development",
                    "items": {
                        "training_programs": "Training Programs",
                        "career_development": "Career Development",
                        "mentoring": "Mentoring",
                        "skills_assessment": "Skills Assessment",
                    },
                },
                "culture": {
                    "display_name": "Culture & Engagement",
                    "description": "Organizational culture and employee engagement",
                    "items": {
                        "company_culture": "Company Culture",
                        "employee_engagement": "Employee Engagement",
                        "diversity_inclusion": "Diversity & Inclusion",
                        "employee_wellness": "Employee Wellness",
                    },
                },
            },
        },
        "research_director-rag": {
            "display_name": "Research Director Agent RAG",
            "description": "Research strategy, innovation, and R&D management",
            "subcategories": {
                "research_strategy": {
                    "display_name": "Research Strategy",
                    "description": "Research planning and strategy",
                    "items": {
                        "research_planning": "Research Planning",
                        "innovation_strategy": "Innovation Strategy",
                        "research_budgeting": "Research Budgeting",
                        "research_metrics": "Research Metrics",
                    },
                },
                "innovation": {
                    "display_name": "Innovation Management",
                    "description": "Innovation processes and management",
                    "items": {
                        "innovation_processes": "Innovation Processes",
                        "patent_management": "Patent Management",
                        "technology_transfer": "Technology Transfer",
                        "innovation_culture": "Innovation Culture",
                    },
                },
                "collaboration": {
                    "display_name": "Research Collaboration",
                    "description": "External research partnerships and collaboration",
                    "items": {
                        "academic_partnerships": "Academic Partnerships",
                        "industry_collaboration": "Industry Collaboration",
                        "research_networks": "Research Networks",
                        "open_innovation": "Open Innovation",
                    },
                },
            },
        },
        "finance_manager-rag": {
            "display_name": "Finance Manager Agent RAG",
            "description": "Financial management, accounting, and financial operations",
            "subcategories": {
                "financial_management": {
                    "display_name": "Financial Management",
                    "description": "Financial planning and management",
                    "items": {
                        "budgeting": "Budgeting",
                        "forecasting": "Forecasting",
                        "financial_analysis": "Financial Analysis",
                        "cost_control": "Cost Control",
                    },
                },
                "accounting": {
                    "display_name": "Accounting Operations",
                    "description": "Accounting processes and operations",
                    "items": {
                        "bookkeeping": "Bookkeeping",
                        "financial_reporting": "Financial Reporting",
                        "accounts_payable": "Accounts Payable",
                        "accounts_receivable": "Accounts Receivable",
                    },
                },
                "financial_controls": {
                    "display_name": "Financial Controls",
                    "description": "Financial controls and procedures",
                    "items": {
                        "internal_controls": "Internal Controls",
                        "financial_policies": "Financial Policies",
                        "audit_preparation": "Audit Preparation",
                        "financial_reviews": "Financial Reviews",
                    },
                },
            },
        },
        "operations_manager-rag": {
            "display_name": "Operations Manager Agent RAG",
            "description": "Operations management, process optimization, and operational efficiency",
            "subcategories": {
                "operations": {
                    "display_name": "Operations Management",
                    "description": "Operational processes and management",
                    "items": {
                        "process_management": "Process Management",
                        "operational_planning": "Operational Planning",
                        "resource_management": "Resource Management",
                        "operational_metrics": "Operational Metrics",
                    },
                },
                "optimization": {
                    "display_name": "Process Optimization",
                    "description": "Process improvement and optimization",
                    "items": {
                        "lean_methodology": "Lean Methodology",
                        "six_sigma": "Six Sigma",
                        "process_improvement": "Process Improvement",
                        "automation": "Process Automation",
                    },
                },
                "supply_chain": {
                    "display_name": "Supply Chain",
                    "description": "Supply chain management and logistics",
                    "items": {
                        "supplier_management": "Supplier Management",
                        "inventory_management": "Inventory Management",
                        "logistics": "Logistics",
                        "procurement": "Procurement",
                    },
                },
            },
        },
        "sales_specialist-rag": {
            "display_name": "Sales Specialist Agent RAG",
            "description": "Sales execution, customer relationship management, and sales performance",
            "subcategories": {
                "sales_execution": {
                    "display_name": "Sales Execution",
                    "description": "Sales process execution and management",
                    "items": {
                        "lead_qualification": "Lead Qualification",
                        "sales_presentations": "Sales Presentations",
                        "negotiation": "Negotiation",
                        "closing": "Closing Techniques",
                    },
                },
                "customer_management": {
                    "display_name": "Customer Management",
                    "description": "Customer relationship and account management",
                    "items": {
                        "account_management": "Account Management",
                        "customer_retention": "Customer Retention",
                        "upselling": "Upselling",
                        "cross_selling": "Cross-selling",
                    },
                },
                "sales_analytics": {
                    "display_name": "Sales Analytics",
                    "description": "Sales performance analysis and reporting",
                    "items": {
                        "sales_reporting": "Sales Reporting",
                        "performance_analysis": "Performance Analysis",
                        "sales_forecasting": "Sales Forecasting",
                        "pipeline_management": "Pipeline Management",
                    },
                },
            },
        },
        "hr_specialist-rag": {
            "display_name": "HR Specialist Agent RAG",
            "description": "Human resources operations, employee relations, and HR administration",
            "subcategories": {
                "hr_operations": {
                    "display_name": "HR Operations",
                    "description": "HR administrative operations and processes",
                    "items": {
                        "payroll": "Payroll Management",
                        "benefits": "Benefits Administration",
                        "employee_records": "Employee Records",
                        "hr_policies": "HR Policies",
                    },
                },
                "employee_relations": {
                    "display_name": "Employee Relations",
                    "description": "Employee relations and engagement",
                    "items": {
                        "employee_communication": "Employee Communication",
                        "conflict_resolution": "Conflict Resolution",
                        "employee_satisfaction": "Employee Satisfaction",
                        "workplace_culture": "Workplace Culture",
                    },
                },
                "recruitment": {
                    "display_name": "Recruitment & Selection",
                    "description": "Recruitment and selection processes",
                    "items": {
                        "job_posting": "Job Posting",
                        "candidate_screening": "Candidate Screening",
                        "interviews": "Interview Process",
                        "onboarding": "Onboarding Process",
                    },
                },
            },
        },
        "product_specialist-rag": {
            "display_name": "Product Specialist Agent RAG",
            "description": "Product management, product development, and product analytics",
            "subcategories": {
                "product_management": {
                    "display_name": "Product Management",
                    "description": "Product management processes and practices",
                    "items": {
                        "product_planning": "Product Planning",
                        "feature_management": "Feature Management",
                        "product_backlog": "Product Backlog",
                        "release_management": "Release Management",
                    },
                },
                "user_research": {
                    "display_name": "User Research",
                    "description": "User research and user experience",
                    "items": {
                        "user_interviews": "User Interviews",
                        "usability_testing": "Usability Testing",
                        "user_personas": "User Personas",
                        "user_journey": "User Journey Mapping",
                    },
                },
                "product_analytics": {
                    "display_name": "Product Analytics",
                    "description": "Product performance and analytics",
                    "items": {
                        "product_metrics": "Product Metrics",
                        "feature_analytics": "Feature Analytics",
                        "user_behavior": "User Behavior Analysis",
                        "product_insights": "Product Insights",
                    },
                },
            },
        },
    }


# Initialize configuration
config = RAGConfig()

# Database setup
DB_PATH = "rag_system.db"


def init_database():
    """Initialize the SQLite database with categories and documents tables"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create categories table (matching existing structure)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                name TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                description TEXT,
                document_count INTEGER DEFAULT 0,
                last_updated TEXT,
                subcategories TEXT
            )
        """
        )

        # Create documents table (matching existing structure)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT,
                item TEXT,
                source TEXT DEFAULT 'manual',
                created_at TEXT,
                metadata TEXT
            )
        """
        )

        # Insert default categories if they don't exist
        for category_id, category_data in config.categories.items():
            cursor.execute(
                """
                SELECT name FROM categories WHERE name = ?
            """,
                (category_id,),
            )

            if not cursor.fetchone():
                cursor.execute(
                    """
                    INSERT INTO categories (name, display_name, description, document_count, last_updated, subcategories)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        category_id,
                        category_data["display_name"],
                        category_data["description"],
                        0,
                        datetime.now().isoformat(),
                        json.dumps(category_data["subcategories"]),
                    ),
                )

        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")

    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


# Initialize database
init_database()

app = FastAPI(title="CoolBits.ai Advanced RAG Admin Panel")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Serve the advanced admin panel HTML
@app.get("/")
async def serve_admin_panel():
    """Serve the advanced RAG admin panel"""
    return FileResponse("advanced_rag_admin_panel.html")


# API Endpoints for RAG functionality
@app.get("/api/status")
async def get_status():
    """Get RAG system status"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Get document count
        cursor.execute("SELECT COUNT(*) FROM documents")
        total_documents = cursor.fetchone()[0]

        # Get category count
        cursor.execute("SELECT COUNT(*) FROM categories")
        total_categories = cursor.fetchone()[0]

        conn.close()

        return {
            "service": "CoolBits.ai Advanced RAG Admin Panel",
            "version": "2.0.0",
            "status": "healthy",
            "total_documents": total_documents,
            "total_categories": total_categories,
            "categories": {
                cat_id: cat_data["display_name"]
                for cat_id, cat_data in config.categories.items()
            },
        }
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/categories")
async def get_categories():
    """Get all categories with their structure"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM categories ORDER BY display_name")
        categories = cursor.fetchall()

        result = {}
        for cat in categories:
            (
                name,
                display_name,
                description,
                doc_count,
                last_updated,
                subcategories_json,
            ) = cat
            result[name] = {
                "display_name": display_name,
                "description": description,
                "document_count": doc_count,
                "last_updated": last_updated,
                "subcategories": (
                    json.loads(subcategories_json) if subcategories_json else {}
                ),
            }

        conn.close()
        return result
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents")
async def get_documents(
    category: Optional[str] = None, subcategory: Optional[str] = None
):
    """Get documents with optional filtering"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        query = "SELECT * FROM documents"
        params = []

        if category:
            query += " WHERE category = ?"
            params.append(category)

            if subcategory:
                query += " AND subcategory = ?"
                params.append(subcategory)

        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)
        documents = cursor.fetchall()

        result = []
        for doc in documents:
            doc_id, title, content, cat, subcat, item, source, created_at, metadata = (
                doc
            )
            result.append(
                {
                    "id": doc_id,
                    "title": title,
                    "content": content,
                    "category": cat,
                    "subcategory": subcat,
                    "item": item,
                    "source": source,
                    "created_at": created_at,
                    "metadata": json.loads(metadata) if metadata else {},
                }
            )

        conn.close()
        return result
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/documents/create")
async def create_document_json(request: dict):
    """Create a document from JSON data"""
    try:
        title = request.get("filename", request.get("title", "untitled"))
        content = request.get("content", "")
        category = request.get("category", "u-rag")
        subcategory = request.get("subcategory", "social")
        item = request.get("item", "general")
        source = request.get("source", "manual")

        if not content.strip():
            raise HTTPException(status_code=400, detail="Content cannot be empty")

        doc_id = str(uuid.uuid4())

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO documents (id, title, content, category, subcategory, item, source, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                doc_id,
                title,
                content,
                category,
                subcategory,
                item,
                source,
                datetime.now().isoformat(),
                json.dumps({"created_by": "api"}),
            ),
        )

        # Update category document count
        cursor.execute(
            """
            UPDATE categories SET document_count = document_count + 1 WHERE name = ?
        """,
            (category,),
        )

        conn.commit()
        conn.close()

        logger.info(f"Document created: {doc_id}")
        return {
            "id": doc_id,
            "status": "created",
            "message": "Document created successfully",
        }

    except Exception as e:
        logger.error(f"Error creating document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("🤖 Starting CoolBits.ai Advanced RAG Admin Panel Server")
    print("📚 Serving unified RAG system with hierarchical categories")
    print("🌐 Available at: http://localhost:8098")

    uvicorn.run(app, host="0.0.0.0", port=8098)
