"""
data_generator.py — Synthetic Data Generator
=============================================
Generates highly realistic IT project portfolio data
that closely mirrors real-world Indian IT company scenarios.

What's realistic here:
- Project names, codes, types match real IT delivery models
- Budget figures in real INR ranges for Indian IT SMEs
- Schedule delays match industry averages (30-40% of projects delayed)
- Team sizes, resignation rates match Indian IT attrition (18-22% annually)
- Client satisfaction scores follow normal distribution
- Market signals mirror actual NASSCOM, RBI, SEBI reports (2025-26)
- Payment delays match real MSME payment cycle issues in India
- Technology stacks are current (2024-2026) real-world choices
- Vendor dependencies, compliance flags, sprint data are all realistic

How to add REAL market data later:
  1. pip install newsapi-python
  2. Get free key at https://newsapi.org
  3. Replace MARKET_SIGNALS list with:
       from newsapi import NewsApiClient
       api = NewsApiClient(api_key="your_key")
       articles = api.get_everything(q="Indian IT sector", language="en")
  4. Map articles to our MarketSignal format — same pipeline, zero other changes

Run this file directly to regenerate all data:
    python -m backend.data.data_generator
"""

import json
import os
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "generated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 15 REALISTIC IT PROJECTS
# Based on real Indian IT delivery scenarios (2025-26)
# Covers: BFSI, Retail, Healthcare, Manufacturing, EdTech,
#         Logistics, Fintech, Government sectors
# ============================================================

PROJECTS = [

    # ── CRITICAL / HIGH RISK ─────────────────────────────────

    {
        "id": "PRJ-001",
        "name": "Project Atlas",
        "type": "Enterprise ERP Implementation",
        "client": "Tata Steel Ltd",
        "client_industry": "Manufacturing",
        "client_location": "Mumbai, Maharashtra",
        "description": (
            "Full SAP S/4HANA implementation across 12 plant locations "
            "covering finance, supply chain, and HR modules. "
            "Phase 2 of a 3-phase digital transformation roadmap."
        ),
        "technology_stack": ["SAP S/4HANA", "SAP BTP", "Azure", "Python", "Power BI"],
        "infrastructure": "Hybrid Cloud (Azure + On-premise SAP)",
        "delivery_model": "Fixed Price",
        "team_location": "Hybrid (Pune + Client Site)",

        # Financial
        "budget_inr": 4200000,
        "amount_spent_inr": 2890000,
        "projected_overrun_inr": 748359,
        "pending_invoices_inr": 538085,
        "payment_overdue_days": 60,
        "billing_frequency": "Monthly",

        # Schedule
        "start_date": "2025-03-01",
        "planned_end_date": "2026-09-04",
        "actual_completion_pct": 45,
        "planned_completion_pct": 58,
        "days_behind_schedule": 25,
        "total_sprints": 24,
        "completed_sprints": 11,
        "delayed_sprints": 4,

        # Team
        "team_size": 18,
        "onsite_count": 4,
        "offshore_count": 14,
        "resignations_last_30_days": 2,
        "open_vacancies": 1,
        "avg_experience_years": 5.2,
        "team_utilization_pct": 88,
        "contractor_count": 3,
        "key_person_dependency": True,

        # Client
        "client_satisfaction_score": 6.5,
        "client_escalations_count": 1,
        "days_since_last_client_contact": 8,
        "nps_score": 32,
        "change_requests_pending": 3,
        "sla_breaches_count": 1,

        # Risk
        "risk_tags": [
            "payment_delay", "resource_attrition",
            "scope_creep", "schedule_delay", "key_person_dependency"
        ],
        "compliance_flags": ["DPDP Act compliance pending", "ISO 27001 renewal due"],
        "vendor_dependencies": [
            "SAP License renewal due Q3 2026",
            "Azure contract expiry Jul 2026"
        ],
        "previous_risk_scores": [38, 42, 47, 51, 53],
        "risk_trend": "INCREASING"
    },

    {
        "id": "PRJ-002",
        "name": "Project Helix",
        "type": "Cloud Migration & Modernization",
        "client": "HDFC Bank",
        "client_industry": "Banking & Financial Services",
        "client_location": "Mumbai, Maharashtra",
        "description": (
            "Migration of legacy on-premise banking applications to AWS cloud. "
            "Includes re-architecting 14 microservices, data lake setup, "
            "and DevSecOps pipeline implementation."
        ),
        "technology_stack": ["AWS", "Kubernetes", "Docker", "Terraform", "Python", "PostgreSQL"],
        "infrastructure": "AWS Cloud (Multi-AZ)",
        "delivery_model": "Time & Material",
        "team_location": "Offshore (Bengaluru)",

        "budget_inr": 3800000,
        "amount_spent_inr": 2470000,
        "projected_overrun_inr": 41158,
        "pending_invoices_inr": 85000,
        "payment_overdue_days": 12,
        "billing_frequency": "Bi-weekly",

        "start_date": "2025-06-01",
        "planned_end_date": "2026-08-05",
        "actual_completion_pct": 65,
        "planned_completion_pct": 66,
        "days_behind_schedule": 0,
        "total_sprints": 20,
        "completed_sprints": 13,
        "delayed_sprints": 1,

        "team_size": 14,
        "onsite_count": 2,
        "offshore_count": 12,
        "resignations_last_30_days": 0,
        "open_vacancies": 0,
        "avg_experience_years": 6.8,
        "team_utilization_pct": 82,
        "contractor_count": 2,
        "key_person_dependency": False,

        "client_satisfaction_score": 8.6,
        "client_escalations_count": 0,
        "days_since_last_client_contact": 3,
        "nps_score": 68,
        "change_requests_pending": 1,
        "sla_breaches_count": 0,

        "risk_tags": ["market_risk", "technical_complexity"],
        "compliance_flags": ["RBI Cloud Guidelines compliance", "PCI DSS audit due Q4 2026"],
        "vendor_dependencies": ["AWS Enterprise support contract renewal"],
        "previous_risk_scores": [22, 20, 18, 20, 19],
        "risk_trend": "STABLE"
    },

    {
        "id": "PRJ-003",
        "name": "Project Nova",
        "type": "AI/ML Platform Development",
        "client": "Bajaj Finserv",
        "client_industry": "Financial Services",
        "client_location": "Pune, Maharashtra",
        "description": (
            "Building an end-to-end AI/ML platform for credit risk scoring, "
            "fraud detection, and customer churn prediction. "
            "Includes MLOps pipeline, model registry, and real-time inference API."
        ),
        "technology_stack": ["Python", "TensorFlow", "MLflow", "FastAPI", "Azure ML", "Spark", "Kafka"],
        "infrastructure": "Azure Cloud (AI-optimized)",
        "delivery_model": "Fixed Price",
        "team_location": "Hybrid (Hyderabad + Remote)",

        "budget_inr": 5600000,
        "amount_spent_inr": 1680000,
        "projected_overrun_inr": 273286,
        "pending_invoices_inr": 193434,
        "payment_overdue_days": 45,
        "billing_frequency": "Monthly",

        "start_date": "2025-09-01",
        "planned_end_date": "2026-09-04",
        "actual_completion_pct": 30,
        "planned_completion_pct": 48,
        "days_behind_schedule": 40,
        "total_sprints": 26,
        "completed_sprints": 7,
        "delayed_sprints": 6,

        "team_size": 16,
        "onsite_count": 3,
        "offshore_count": 13,
        "resignations_last_30_days": 3,
        "open_vacancies": 3,
        "avg_experience_years": 4.1,
        "team_utilization_pct": 95,
        "contractor_count": 0,
        "key_person_dependency": True,

        "client_satisfaction_score": 5.5,
        "client_escalations_count": 2,
        "days_since_last_client_contact": 18,
        "nps_score": 12,
        "change_requests_pending": 5,
        "sla_breaches_count": 3,

        "risk_tags": [
            "resource_attrition", "schedule_delay", "client_dissatisfaction",
            "technical_complexity", "payment_delay", "key_person_dependency"
        ],
        "compliance_flags": [
            "RBI AI/ML model explainability guidelines",
            "DPDP Act data handling compliance"
        ],
        "vendor_dependencies": [
            "Azure GPU quota approval pending",
            "Kafka Enterprise license negotiation"
        ],
        "previous_risk_scores": [35, 44, 52, 57, 60],
        "risk_trend": "RAPIDLY_INCREASING"
    },

    {
        "id": "PRJ-004",
        "name": "Project Orion",
        "type": "Mobile Banking Application",
        "client": "Kotak Mahindra Bank",
        "client_industry": "Banking & Financial Services",
        "client_location": "Mumbai, Maharashtra",
        "description": (
            "Next-gen mobile banking app for retail and corporate banking customers. "
            "UPI 2.0 integration, biometric authentication, AI-powered spend analytics, "
            "and multi-currency support for 8M+ users."
        ),
        "technology_stack": ["Flutter", "Node.js", "PostgreSQL", "Redis", "AWS", "Firebase"],
        "infrastructure": "AWS (Mumbai Region)",
        "delivery_model": "Fixed Price",
        "team_location": "Offshore (Chennai)",

        "budget_inr": 2800000,
        "amount_spent_inr": 2464000,
        "projected_overrun_inr": 39905,
        "pending_invoices_inr": 292666,
        "payment_overdue_days": 22,
        "billing_frequency": "Monthly",

        "start_date": "2025-01-15",
        "planned_end_date": "2026-04-07",
        "actual_completion_pct": 88,
        "planned_completion_pct": 90,
        "days_behind_schedule": 5,
        "total_sprints": 18,
        "completed_sprints": 16,
        "delayed_sprints": 1,

        "team_size": 11,
        "onsite_count": 2,
        "offshore_count": 9,
        "resignations_last_30_days": 0,
        "open_vacancies": 0,
        "avg_experience_years": 5.9,
        "team_utilization_pct": 78,
        "contractor_count": 1,
        "key_person_dependency": False,

        "client_satisfaction_score": 9.0,
        "client_escalations_count": 0,
        "days_since_last_client_contact": 2,
        "nps_score": 74,
        "change_requests_pending": 1,
        "sla_breaches_count": 0,

        "risk_tags": ["near_completion", "minor_delay"],
        "compliance_flags": ["RBI Mobile Banking Guidelines v2", "PCI DSS Level 1 audit"],
        "vendor_dependencies": ["Apple App Store review", "Google Play Store certification"],
        "previous_risk_scores": [28, 22, 18, 16, 16],
        "risk_trend": "STABLE_LOW"
    },

    {
        "id": "PRJ-005",
        "name": "Project Zenith",
        "type": "Digital Transformation Program",
        "client": "Reliance Retail",
        "client_industry": "Retail & E-commerce",
        "client_location": "Mumbai, Maharashtra",
        "description": (
            "End-to-end digital transformation of retail operations including "
            "omnichannel commerce platform, inventory management AI, customer data "
            "platform (CDP), and loyalty program modernization across 2,500+ stores."
        ),
        "technology_stack": ["Salesforce", "MuleSoft", "React", "Python", "GCP", "BigQuery", "Vertex AI"],
        "infrastructure": "GCP (Multi-region India)",
        "delivery_model": "Fixed Price",
        "team_location": "Hybrid (Bengaluru + Mumbai)",

        "budget_inr": 8500000,
        "amount_spent_inr": 1700000,
        "projected_overrun_inr": 264759,
        "pending_invoices_inr": 522518,
        "payment_overdue_days": 75,
        "billing_frequency": "Monthly",

        "start_date": "2025-11-01",
        "planned_end_date": "2026-12-03",
        "actual_completion_pct": 20,
        "planned_completion_pct": 32,
        "days_behind_schedule": 55,
        "total_sprints": 30,
        "completed_sprints": 5,
        "delayed_sprints": 5,

        "team_size": 24,
        "onsite_count": 6,
        "offshore_count": 18,
        "resignations_last_30_days": 2,
        "open_vacancies": 2,
        "avg_experience_years": 4.8,
        "team_utilization_pct": 92,
        "contractor_count": 4,
        "key_person_dependency": True,

        "client_satisfaction_score": 5.0,
        "client_escalations_count": 3,
        "days_since_last_client_contact": 12,
        "nps_score": 8,
        "change_requests_pending": 7,
        "sla_breaches_count": 4,

        "risk_tags": [
            "payment_delay", "schedule_delay", "resource_attrition",
            "client_dissatisfaction", "scope_creep",
            "key_person_dependency", "multiple_escalations"
        ],
        "compliance_flags": [
            "DPDP Act customer data compliance",
            "GST integration audit pending"
        ],
        "vendor_dependencies": [
            "Salesforce license negotiation in progress",
            "MuleSoft Anypoint Platform quota approval",
            "GCP committed use discount pending"
        ],
        "previous_risk_scores": [40, 48, 55, 59, 61],
        "risk_trend": "RAPIDLY_INCREASING"
    },

    # ── MEDIUM RISK ───────────────────────────────────────────

    {
        "id": "PRJ-006",
        "name": "Project Titan",
        "type": "Data Warehouse & Analytics Platform",
        "client": "Wipro Technologies (Internal)",
        "client_industry": "IT Services",
        "client_location": "Bengaluru, Karnataka",
        "description": (
            "Enterprise data warehouse on Snowflake with real-time ETL pipelines "
            "from 18 source systems. Self-service BI dashboards for C-suite and "
            "operational reporting covering 6,000+ business users."
        ),
        "technology_stack": ["Snowflake", "dbt", "Airflow", "Power BI", "Python", "Azure Data Factory"],
        "infrastructure": "Azure + Snowflake Cloud",
        "delivery_model": "Time & Material",
        "team_location": "Offshore (Bengaluru)",

        "budget_inr": 3200000,
        "amount_spent_inr": 1920000,
        "projected_overrun_inr": 180000,
        "pending_invoices_inr": 145000,
        "payment_overdue_days": 28,
        "billing_frequency": "Monthly",

        "start_date": "2025-05-01",
        "planned_end_date": "2026-11-30",
        "actual_completion_pct": 52,
        "planned_completion_pct": 58,
        "days_behind_schedule": 18,
        "total_sprints": 22,
        "completed_sprints": 11,
        "delayed_sprints": 2,

        "team_size": 13,
        "onsite_count": 1,
        "offshore_count": 12,
        "resignations_last_30_days": 1,
        "open_vacancies": 1,
        "avg_experience_years": 5.5,
        "team_utilization_pct": 85,
        "contractor_count": 2,
        "key_person_dependency": True,

        "client_satisfaction_score": 7.2,
        "client_escalations_count": 0,
        "days_since_last_client_contact": 5,
        "nps_score": 45,
        "change_requests_pending": 2,
        "sla_breaches_count": 1,

        "risk_tags": ["schedule_delay", "resource_attrition", "key_person_dependency"],
        "compliance_flags": ["ISO 27001 data security review", "GDPR data residency check"],
        "vendor_dependencies": [
            "Snowflake credits consumption monitoring",
            "Power BI Premium license renewal"
        ],
        "previous_risk_scores": [30, 35, 38, 40, 43],
        "risk_trend": "SLOWLY_INCREASING"
    },

    {
        "id": "PRJ-007",
        "name": "Project Apex",
        "type": "Cybersecurity & SOC Implementation",
        "client": "Yes Bank",
        "client_industry": "Banking & Financial Services",
        "client_location": "Mumbai, Maharashtra",
        "description": (
            "Setting up Security Operations Center (SOC), implementing SIEM solution, "
            "endpoint detection & response (EDR), and zero-trust network architecture "
            "across 45 branch locations and 3,200 endpoints."
        ),
        "technology_stack": ["Splunk", "CrowdStrike", "Palo Alto", "Azure Sentinel", "Python", "SOAR"],
        "infrastructure": "Hybrid (On-premise SOC + Azure Cloud)",
        "delivery_model": "Fixed Price",
        "team_location": "Hybrid (Mumbai + Remote)",

        "budget_inr": 6200000,
        "amount_spent_inr": 3100000,
        "projected_overrun_inr": 320000,
        "pending_invoices_inr": 410000,
        "payment_overdue_days": 35,
        "billing_frequency": "Quarterly",

        "start_date": "2025-04-01",
        "planned_end_date": "2026-10-31",
        "actual_completion_pct": 50,
        "planned_completion_pct": 52,
        "days_behind_schedule": 12,
        "total_sprints": 20,
        "completed_sprints": 10,
        "delayed_sprints": 2,

        "team_size": 15,
        "onsite_count": 6,
        "offshore_count": 9,
        "resignations_last_30_days": 1,
        "open_vacancies": 1,
        "avg_experience_years": 7.2,
        "team_utilization_pct": 90,
        "contractor_count": 3,
        "key_person_dependency": True,

        "client_satisfaction_score": 7.8,
        "client_escalations_count": 0,
        "days_since_last_client_contact": 4,
        "nps_score": 52,
        "change_requests_pending": 2,
        "sla_breaches_count": 0,

        "risk_tags": ["technical_complexity", "regulatory_compliance", "payment_delay"],
        "compliance_flags": [
            "RBI Cybersecurity Framework compliance",
            "SEBI CSCRF audit Q2 2026"
        ],
        "vendor_dependencies": [
            "Splunk Enterprise license renewal",
            "CrowdStrike Falcon deployment approval"
        ],
        "previous_risk_scores": [28, 32, 38, 40, 42],
        "risk_trend": "SLOWLY_INCREASING"
    },

    {
        "id": "PRJ-008",
        "name": "Project Sigma",
        "type": "Healthcare Information System",
        "client": "Apollo Hospitals Group",
        "client_industry": "Healthcare",
        "client_location": "Hyderabad, Telangana",
        "description": (
            "Integrated Hospital Information System (HIS) covering OPD, IPD, pharmacy, "
            "lab, radiology, and billing modules across 12 hospital locations. "
            "Integration with insurance TPA systems and ABDM health stack."
        ),
        "technology_stack": ["Java Spring Boot", "React", "PostgreSQL", "HL7 FHIR", "AWS", "Kafka"],
        "infrastructure": "AWS (ap-south-1 Mumbai)",
        "delivery_model": "Fixed Price",
        "team_location": "Hybrid (Hyderabad + Client Site)",

        "budget_inr": 7800000,
        "amount_spent_inr": 3510000,
        "projected_overrun_inr": 425000,
        "pending_invoices_inr": 680000,
        "payment_overdue_days": 42,
        "billing_frequency": "Monthly",

        "start_date": "2025-02-01",
        "planned_end_date": "2026-12-31",
        "actual_completion_pct": 45,
        "planned_completion_pct": 50,
        "days_behind_schedule": 22,
        "total_sprints": 28,
        "completed_sprints": 12,
        "delayed_sprints": 3,

        "team_size": 20,
        "onsite_count": 5,
        "offshore_count": 15,
        "resignations_last_30_days": 1,
        "open_vacancies": 2,
        "avg_experience_years": 5.8,
        "team_utilization_pct": 87,
        "contractor_count": 3,
        "key_person_dependency": False,

        "client_satisfaction_score": 7.0,
        "client_escalations_count": 1,
        "days_since_last_client_contact": 6,
        "nps_score": 38,
        "change_requests_pending": 4,
        "sla_breaches_count": 1,

        "risk_tags": ["regulatory_compliance", "payment_delay", "scope_creep", "schedule_delay"],
        "compliance_flags": [
            "ABDM integration certification pending",
            "NABH accreditation compliance",
            "DPDP Act patient data handling"
        ],
        "vendor_dependencies": [
            "HL7 FHIR certification body approval",
            "Insurance TPA API documentation delay"
        ],
        "previous_risk_scores": [32, 36, 40, 44, 46],
        "risk_trend": "SLOWLY_INCREASING"
    },

    {
        "id": "PRJ-009",
        "name": "Project Nexus",
        "type": "Supply Chain Management System",
        "client": "Mahindra Logistics",
        "client_industry": "Logistics & Supply Chain",
        "client_location": "Pune, Maharashtra",
        "description": (
            "End-to-end supply chain visibility platform with real-time GPS tracking "
            "for 8,000+ vehicles, AI-based demand forecasting, warehouse management "
            "system (WMS), and last-mile delivery optimization engine."
        ),
        "technology_stack": ["Python", "Django", "React Native", "PostgreSQL", "Redis", "GCP", "TensorFlow"],
        "infrastructure": "GCP (Mumbai Region)",
        "delivery_model": "Time & Material",
        "team_location": "Offshore (Pune)",

        "budget_inr": 4500000,
        "amount_spent_inr": 2700000,
        "projected_overrun_inr": 95000,
        "pending_invoices_inr": 220000,
        "payment_overdue_days": 18,
        "billing_frequency": "Monthly",

        "start_date": "2025-07-01",
        "planned_end_date": "2026-12-15",
        "actual_completion_pct": 55,
        "planned_completion_pct": 58,
        "days_behind_schedule": 10,
        "total_sprints": 22,
        "completed_sprints": 12,
        "delayed_sprints": 1,

        "team_size": 16,
        "onsite_count": 2,
        "offshore_count": 14,
        "resignations_last_30_days": 1,
        "open_vacancies": 0,
        "avg_experience_years": 4.9,
        "team_utilization_pct": 84,
        "contractor_count": 2,
        "key_person_dependency": False,

        "client_satisfaction_score": 7.8,
        "client_escalations_count": 0,
        "days_since_last_client_contact": 4,
        "nps_score": 55,
        "change_requests_pending": 2,
        "sla_breaches_count": 0,

        "risk_tags": ["minor_delay", "resource_attrition"],
        "compliance_flags": ["GST e-way bill integration", "Customs EDI compliance"],
        "vendor_dependencies": [
            "GPS hardware vendor — 4 week delivery lead time",
            "GCP Maps API enterprise quota"
        ],
        "previous_risk_scores": [25, 28, 32, 35, 36],
        "risk_trend": "SLOWLY_INCREASING"
    },

    {
        "id": "PRJ-010",
        "name": "Project Vega",
        "type": "DevOps & Internal Developer Platform",
        "client": "Infosys BPM (Internal)",
        "client_industry": "IT Services / BPO",
        "client_location": "Bengaluru, Karnataka",
        "description": (
            "Internal Developer Platform (IDP) with self-service infrastructure "
            "provisioning, CI/CD pipeline standardization, observability stack, "
            "and developer portal using Backstage for 4,500+ internal developers."
        ),
        "technology_stack": ["Backstage", "ArgoCD", "Kubernetes", "Terraform", "Prometheus", "Grafana", "AWS"],
        "infrastructure": "AWS Multi-Account Landing Zone",
        "delivery_model": "Time & Material",
        "team_location": "Offshore (Bengaluru)",

        "budget_inr": 2900000,
        "amount_spent_inr": 1392000,
        "projected_overrun_inr": 58000,
        "pending_invoices_inr": 95000,
        "payment_overdue_days": 15,
        "billing_frequency": "Monthly",

        "start_date": "2025-08-01",
        "planned_end_date": "2026-07-31",
        "actual_completion_pct": 48,
        "planned_completion_pct": 50,
        "days_behind_schedule": 8,
        "total_sprints": 18,
        "completed_sprints": 8,
        "delayed_sprints": 1,

        "team_size": 10,
        "onsite_count": 0,
        "offshore_count": 10,
        "resignations_last_30_days": 0,
        "open_vacancies": 1,
        "avg_experience_years": 6.1,
        "team_utilization_pct": 80,
        "contractor_count": 2,
        "key_person_dependency": False,

        "client_satisfaction_score": 8.0,
        "client_escalations_count": 0,
        "days_since_last_client_contact": 3,
        "nps_score": 60,
        "change_requests_pending": 1,
        "sla_breaches_count": 0,

        "risk_tags": ["minor_delay", "technical_complexity"],
        "compliance_flags": ["SOC 2 Type II audit readiness"],
        "vendor_dependencies": ["AWS Partner Network tier review"],
        "previous_risk_scores": [22, 26, 28, 30, 31],
        "risk_trend": "STABLE"
    },

    # ── LOW RISK ──────────────────────────────────────────────

    {
        "id": "PRJ-011",
        "name": "Project Aurora",
        "type": "E-commerce Platform Revamp",
        "client": "Nykaa Fashion",
        "client_industry": "Retail & E-commerce",
        "client_location": "Mumbai, Maharashtra",
        "description": (
            "Complete frontend revamp of fashion e-commerce platform using Next.js, "
            "headless CMS architecture, AI-powered product recommendations, and "
            "performance optimization targeting sub-2s page load for 15M+ monthly users."
        ),
        "technology_stack": ["Next.js", "Contentful", "GraphQL", "Node.js", "Elasticsearch", "AWS CloudFront"],
        "infrastructure": "AWS (CloudFront + ECS Fargate)",
        "delivery_model": "Fixed Price",
        "team_location": "Offshore (Bengaluru)",

        "budget_inr": 1800000,
        "amount_spent_inr": 1296000,
        "projected_overrun_inr": 22000,
        "pending_invoices_inr": 180000,
        "payment_overdue_days": 8,
        "billing_frequency": "Monthly",

        "start_date": "2025-10-01",
        "planned_end_date": "2026-06-30",
        "actual_completion_pct": 72,
        "planned_completion_pct": 72,
        "days_behind_schedule": 0,
        "total_sprints": 14,
        "completed_sprints": 10,
        "delayed_sprints": 0,

        "team_size": 9,
        "onsite_count": 1,
        "offshore_count": 8,
        "resignations_last_30_days": 0,
        "open_vacancies": 0,
        "avg_experience_years": 4.5,
        "team_utilization_pct": 76,
        "contractor_count": 1,
        "key_person_dependency": False,

        "client_satisfaction_score": 8.8,
        "client_escalations_count": 0,
        "days_since_last_client_contact": 2,
        "nps_score": 70,
        "change_requests_pending": 1,
        "sla_breaches_count": 0,

        "risk_tags": ["on_track"],
        "compliance_flags": ["WCAG 2.1 accessibility compliance"],
        "vendor_dependencies": ["Contentful CMS license", "Algolia search tier"],
        "previous_risk_scores": [18, 16, 15, 14, 14],
        "risk_trend": "STABLE_LOW"
    },

    {
        "id": "PRJ-012",
        "name": "Project Cosmos",
        "type": "IoT & Smart Factory Implementation",
        "client": "Godrej Industries",
        "client_industry": "Manufacturing",
        "client_location": "Mumbai, Maharashtra",
        "description": (
            "Smart factory implementation with IoT sensors across 3 production lines, "
            "real-time OEE monitoring, predictive maintenance using ML models, "
            "and SCADA system integration for 850 connected machines."
        ),
        "technology_stack": ["Python", "MQTT", "InfluxDB", "Grafana", "TensorFlow Lite", "AWS IoT Core", "Node-RED"],
        "infrastructure": "AWS IoT + Edge Computing (Greengrass)",
        "delivery_model": "Fixed Price",
        "team_location": "Hybrid (Mumbai + Factory Site)",

        "budget_inr": 3600000,
        "amount_spent_inr": 1800000,
        "projected_overrun_inr": 45000,
        "pending_invoices_inr": 310000,
        "payment_overdue_days": 20,
        "billing_frequency": "Quarterly",

        "start_date": "2025-06-15",
        "planned_end_date": "2026-09-30",
        "actual_completion_pct": 50,
        "planned_completion_pct": 52,
        "days_behind_schedule": 7,
        "total_sprints": 18,
        "completed_sprints": 9,
        "delayed_sprints": 1,

        "team_size": 12,
        "onsite_count": 4,
        "offshore_count": 8,
        "resignations_last_30_days": 0,
        "open_vacancies": 0,
        "avg_experience_years": 5.3,
        "team_utilization_pct": 83,
        "contractor_count": 2,
        "key_person_dependency": False,

        "client_satisfaction_score": 8.2,
        "client_escalations_count": 0,
        "days_since_last_client_contact": 5,
        "nps_score": 62,
        "change_requests_pending": 1,
        "sla_breaches_count": 0,

        "risk_tags": ["minor_delay", "hardware_dependency"],
        "compliance_flags": [
            "IEC 62443 industrial cybersecurity standard",
            "Factory Acceptance Test (FAT) pending"
        ],
        "vendor_dependencies": [
            "IoT sensor hardware — 4 week lead time",
            "SCADA vendor API documentation pending"
        ],
        "previous_risk_scores": [20, 19, 18, 17, 17],
        "risk_trend": "STABLE_LOW"
    },

    {
        "id": "PRJ-013",
        "name": "Project Polaris",
        "type": "HR Tech & Gig Worker Platform",
        "client": "Zomato Ltd",
        "client_industry": "Food Tech / Gig Economy",
        "client_location": "Gurugram, Haryana",
        "description": (
            "Next-gen HR platform for managing 350,000+ delivery partners and 8,000 "
            "corporate employees. Onboarding automation, performance management, "
            "payroll integration, and gig worker compliance module."
        ),
        "technology_stack": ["React", "Node.js", "MongoDB", "Redis", "AWS", "Twilio", "Razorpay"],
        "infrastructure": "AWS (Multi-region India)",
        "delivery_model": "Time & Material",
        "team_location": "Offshore (Noida)",

        "budget_inr": 4100000,
        "amount_spent_inr": 2460000,
        "projected_overrun_inr": 120000,
        "pending_invoices_inr": 380000,
        "payment_overdue_days": 25,
        "billing_frequency": "Monthly",

        "start_date": "2025-04-15",
        "planned_end_date": "2026-10-15",
        "actual_completion_pct": 58,
        "planned_completion_pct": 60,
        "days_behind_schedule": 8,
        "total_sprints": 22,
        "completed_sprints": 13,
        "delayed_sprints": 1,

        "team_size": 14,
        "onsite_count": 2,
        "offshore_count": 12,
        "resignations_last_30_days": 0,
        "open_vacancies": 1,
        "avg_experience_years": 4.2,
        "team_utilization_pct": 81,
        "contractor_count": 2,
        "key_person_dependency": False,

        "client_satisfaction_score": 8.1,
        "client_escalations_count": 0,
        "days_since_last_client_contact": 4,
        "nps_score": 58,
        "change_requests_pending": 2,
        "sla_breaches_count": 0,

        "risk_tags": ["minor_delay", "scope_creep"],
        "compliance_flags": [
            "Gig Worker Code compliance (India 2026)",
            "PF/ESI integration audit"
        ],
        "vendor_dependencies": [
            "Razorpay payroll API approval",
            "Twilio WhatsApp Business API tier"
        ],
        "previous_risk_scores": [24, 22, 21, 20, 20],
        "risk_trend": "STABLE"
    },

    {
        "id": "PRJ-014",
        "name": "Project Quasar",
        "type": "EdTech Learning Management System",
        "client": "BYJU's (Think & Learn Pvt Ltd)",
        "client_industry": "Education Technology",
        "client_location": "Bengaluru, Karnataka",
        "description": (
            "Rebuilding core LMS with adaptive learning algorithms, live class "
            "infrastructure via WebRTC, offline sync capability for low-bandwidth "
            "users, and multilingual content support for 10M+ students across 12 languages."
        ),
        "technology_stack": ["React Native", "Python", "Django", "PostgreSQL", "WebRTC", "AWS", "Redis"],
        "infrastructure": "AWS (Multi-AZ Mumbai + CloudFront)",
        "delivery_model": "Fixed Price",
        "team_location": "Offshore (Bengaluru)",

        "budget_inr": 5200000,
        "amount_spent_inr": 2080000,
        "projected_overrun_inr": 180000,
        "pending_invoices_inr": 520000,
        "payment_overdue_days": 38,
        "billing_frequency": "Monthly",

        "start_date": "2025-08-01",
        "planned_end_date": "2027-01-31",
        "actual_completion_pct": 40,
        "planned_completion_pct": 42,
        "days_behind_schedule": 12,
        "total_sprints": 30,
        "completed_sprints": 12,
        "delayed_sprints": 2,

        "team_size": 18,
        "onsite_count": 2,
        "offshore_count": 16,
        "resignations_last_30_days": 1,
        "open_vacancies": 1,
        "avg_experience_years": 4.0,
        "team_utilization_pct": 85,
        "contractor_count": 3,
        "key_person_dependency": False,

        "client_satisfaction_score": 7.4,
        "client_escalations_count": 0,
        "days_since_last_client_contact": 5,
        "nps_score": 48,
        "change_requests_pending": 3,
        "sla_breaches_count": 0,

        "risk_tags": ["payment_delay", "minor_delay", "client_financial_stress"],
        "compliance_flags": [
            "COPPA compliance for minor users",
            "DPDP Act student data protection"
        ],
        "vendor_dependencies": [
            "WebRTC CDN infrastructure scaling",
            "AWS Reserved Instance 1-year commitment"
        ],
        "previous_risk_scores": [28, 30, 32, 33, 34],
        "risk_trend": "SLOWLY_INCREASING"
    },

    {
        "id": "PRJ-015",
        "name": "Project Meridian",
        "type": "Fintech Payment Gateway",
        "client": "PhonePe (Walmart Group)",
        "client_industry": "Fintech / Digital Payments",
        "client_location": "Bengaluru, Karnataka",
        "description": (
            "Next-gen payment gateway supporting UPI, cards, BNPL, and international "
            "payments with sub-100ms transaction processing, 99.99% uptime SLA, "
            "and PCI DSS Level 1 compliance for 500M+ registered users."
        ),
        "technology_stack": ["Java", "Spring Boot", "Kafka", "Cassandra", "Redis", "AWS", "Terraform"],
        "infrastructure": "AWS Multi-region Active-Active (Mumbai + Singapore)",
        "delivery_model": "Time & Material",
        "team_location": "Hybrid (Bengaluru + Remote)",

        "budget_inr": 9200000,
        "amount_spent_inr": 6900000,
        "projected_overrun_inr": 280000,
        "pending_invoices_inr": 850000,
        "payment_overdue_days": 30,
        "billing_frequency": "Monthly",

        "start_date": "2024-12-01",
        "planned_end_date": "2026-06-30",
        "actual_completion_pct": 75,
        "planned_completion_pct": 76,
        "days_behind_schedule": 5,
        "total_sprints": 26,
        "completed_sprints": 19,
        "delayed_sprints": 1,

        "team_size": 22,
        "onsite_count": 5,
        "offshore_count": 17,
        "resignations_last_30_days": 0,
        "open_vacancies": 0,
        "avg_experience_years": 7.5,
        "team_utilization_pct": 88,
        "contractor_count": 3,
        "key_person_dependency": False,

        "client_satisfaction_score": 8.5,
        "client_escalations_count": 0,
        "days_since_last_client_contact": 2,
        "nps_score": 66,
        "change_requests_pending": 2,
        "sla_breaches_count": 0,

        "risk_tags": ["technical_complexity", "compliance_heavy", "high_stakes"],
        "compliance_flags": [
            "PCI DSS Level 1 QSA audit",
            "RBI Payment Aggregator Guidelines compliance",
            "NPCI UPI 2.0 certification"
        ],
        "vendor_dependencies": [
            "NPCI infrastructure SLA dependency",
            "Visa/Mastercard network certification timeline"
        ],
        "previous_risk_scores": [30, 28, 26, 24, 22],
        "risk_trend": "IMPROVING"
    },
]


# ============================================================
# 20 REALISTIC MARKET SIGNALS
# Based on actual NASSCOM, RBI, SEBI, Gartner reports (2025-26)
# Each signal includes: source, headline, sentiment,
# affected sectors, and real-world business impact
#
# HOW TO REPLACE WITH REAL DATA LATER:
#   pip install newsapi-python
#   from newsapi import NewsApiClient
#   api = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))
#   articles = api.get_everything(q="Indian IT sector NASSCOM", language="en")
#   Then map articles["articles"] to this same dict structure
# ============================================================

MARKET_SIGNALS = [
    {
        "id": "MKT-001",
        "source": "NASSCOM Strategic Review 2025-26",
        "headline": "Indian IT sector growth forecast revised down to 4.5% from 6.2% amid global headwinds",
        "description": (
            "NASSCOM revised its annual IT sector growth forecast downward citing global "
            "macroeconomic headwinds, reduced discretionary tech spending by BFSI clients, "
            "and pricing pressure from nearshore competition. Export revenues expected at "
            "$208B vs earlier estimate of $215B. Mid-tier IT companies most impacted."
        ),
        "sentiment": "negative",
        "impact_on_it": "Reduced new deal wins, margin pressure, potential workforce rightsizing",
        "affected_sectors": ["BFSI", "Retail", "Manufacturing"],
        "severity": "high",
        "date": "2026-01-15"
    },
    {
        "id": "MKT-002",
        "source": "RBI Monetary Policy Committee — February 2026",
        "headline": "RBI cuts repo rate by 25bps to 6.25% — first rate cut in 4 years signals easing cycle",
        "description": (
            "RBI reduced repo rate for first time in 4 years, signaling easing cycle begins. "
            "Banking sector IT budgets may see modest increase in H2 2026 as loan demand picks up. "
            "Digital transformation projects remain under budget scrutiny in H1 2026."
        ),
        "sentiment": "neutral",
        "impact_on_it": "Moderate positive for BFSI IT spending, cautious outlook for H1 2026",
        "affected_sectors": ["BFSI", "Fintech"],
        "severity": "medium",
        "date": "2026-02-08"
    },
    {
        "id": "MKT-003",
        "source": "Gartner IT Spending Forecast Q1 2026",
        "headline": "Global enterprise IT spending to grow 9.3% in 2026 driven by AI and cloud investments",
        "description": (
            "Gartner projects worldwide IT spending of $5.26 trillion in 2026, with GenAI, "
            "cloud, and cybersecurity as top investment areas. Indian IT services companies "
            "well-positioned to capture AI implementation work but face delivery skill gap challenges."
        ),
        "sentiment": "positive",
        "impact_on_it": "Strong demand for AI/ML, cloud migration, and cybersecurity services",
        "affected_sectors": ["All sectors"],
        "severity": "medium",
        "date": "2026-01-22"
    },
    {
        "id": "MKT-004",
        "source": "TeamLease Digital — IT Attrition Report Q4 2025",
        "headline": "IT sector attrition rises to 22.4% — highest in 3 years, GCC poaching accelerates",
        "description": (
            "Voluntary attrition in Indian IT sector reached 22.4% in Q4 2025, driven by "
            "AI-related role uncertainty, return-to-office mandates, and aggressive poaching by "
            "Global Capability Centers (GCCs). Mid-level engineers (3-7 years exp) most affected. "
            "Replacement cost per engineer averaging ₹8-12 lakh including training."
        ),
        "sentiment": "negative",
        "impact_on_it": "Project delivery risk from team instability, rising replacement and retention costs",
        "affected_sectors": ["All IT services"],
        "severity": "high",
        "date": "2026-01-10"
    },
    {
        "id": "MKT-005",
        "source": "SEBI Circular — Digital Infrastructure Requirements 2026",
        "headline": "SEBI mandates enhanced cybersecurity framework for all market institutions by June 2026",
        "description": (
            "SEBI issued circular requiring all stock exchanges, depositories, and clearing "
            "corporations to implement enhanced cybersecurity controls including 24x7 SOC, "
            "annual penetration testing, and third-party vendor risk assessment. "
            "Creates ₹2,200 crore+ IT project demand in capital markets sector."
        ),
        "sentiment": "positive",
        "impact_on_it": "Significant cybersecurity implementation project demand from BFSI clients",
        "affected_sectors": ["BFSI", "Capital Markets"],
        "severity": "medium",
        "date": "2026-02-01"
    },
    {
        "id": "MKT-006",
        "source": "ICICI Securities Research — INR Outlook 2026",
        "headline": "INR/USD at 87.2 — currency depreciation eroding IT export margins by 2-3%",
        "description": (
            "Indian Rupee depreciated 3.8% against USD in Q4 2025. While revenue in INR "
            "appears stronger, hedging costs increased significantly. Projects with high offshore "
            "content and USD billing see margin compression due to elevated hedging premiums. "
            "Fixed-price contracts with INR billing most severely impacted."
        ),
        "sentiment": "negative",
        "impact_on_it": "Margin compression on fixed-price contracts, hedging cost pressure",
        "affected_sectors": ["IT Exports", "BFSI", "Manufacturing"],
        "severity": "medium",
        "date": "2026-02-14"
    },
    {
        "id": "MKT-007",
        "source": "MeitY — Digital India 2026 Union Budget Allocation",
        "headline": "Government allocates ₹1.2 lakh crore for Digital India — massive public sector IT push",
        "description": (
            "Union Budget 2026 allocated ₹1.2 lakh crore for Digital India initiatives "
            "including health stack expansion, agriculture digitization, and digital infrastructure "
            "in tier 2/3 cities. Creates significant opportunities for IT services companies "
            "with government delivery experience, but payment cycles remain 90-120 days."
        ),
        "sentiment": "positive",
        "impact_on_it": "New large government IT project opportunities; complex procurement cycles",
        "affected_sectors": ["Government", "Healthcare", "Agriculture"],
        "severity": "medium",
        "date": "2026-02-01"
    },
    {
        "id": "MKT-008",
        "source": "MeitY — DPDP Act Implementation Update",
        "headline": "DPDP Act rules notified — 12-month compliance deadline creates IT compliance project wave",
        "description": (
            "MeitY notified Digital Personal Data Protection Act implementation rules with "
            "12-month compliance deadline. All companies handling Indian citizen data must "
            "implement data localization, consent management APIs, and data principal rights. "
            "Estimated ₹3,500 crore compliance project market across industries."
        ),
        "sentiment": "neutral",
        "impact_on_it": "Large compliance project demand wave; also adds compliance burden to ongoing projects",
        "affected_sectors": ["All sectors handling personal data"],
        "severity": "high",
        "date": "2026-01-28"
    },
    {
        "id": "MKT-009",
        "source": "Deloitte — India GCC Tracker Report 2026",
        "headline": "200+ new GCCs planned in India in 2026 — intensifying IT talent war dramatically",
        "description": (
            "Global Capability Centers of Fortune 500 companies planning 200+ new India centers "
            "in 2026, primarily in Bengaluru, Hyderabad, and Pune. GCCs offering 35-45% salary "
            "premium over IT service providers, aggressively targeting mid-senior talent. "
            "Expected to add 180,000 GCC jobs while poaching equivalent numbers from IT services."
        ),
        "sentiment": "negative",
        "impact_on_it": "Severe talent poaching, salary inflation, project delivery risk from attrition",
        "affected_sectors": ["IT Services", "Consulting"],
        "severity": "high",
        "date": "2026-01-18"
    },
    {
        "id": "MKT-010",
        "source": "McKinsey Global Institute — GenAI India Adoption 2026",
        "headline": "67% of Indian large enterprises piloting GenAI — creating premium for AI delivery capability",
        "description": (
            "McKinsey report shows 67% of Indian large enterprises actively piloting GenAI use cases, "
            "up from 31% in 2024. IT services companies with strong AI practices seeing 2x win rates "
            "on new deals. AI-augmented delivery models showing 25% productivity improvement. "
            "Creates clear premium pricing opportunity for AI-capable vendors."
        ),
        "sentiment": "positive",
        "impact_on_it": "Strong demand for AI implementation projects; premium pricing for AI-skilled teams",
        "affected_sectors": ["All sectors"],
        "severity": "medium",
        "date": "2026-02-10"
    },
    {
        "id": "MKT-011",
        "source": "FICCI — India MSME Payment Crisis Survey 2026",
        "headline": "Average payment delay to IT MSMEs reaches 98 days — cash flow crisis threatens delivery",
        "description": (
            "FICCI survey of 850 IT MSMEs shows average payment realization time of 98 days, "
            "up from 72 days in 2024. Large enterprise and PSU clients delaying payments due to "
            "internal budget freezes. 23% of IT MSMEs report cash flow crisis actively affecting "
            "project delivery — delayed salaries, deferred hiring, reduced training."
        ),
        "sentiment": "negative",
        "impact_on_it": "Cash flow crisis for IT vendors; delivery delays; resource retention breakdown",
        "affected_sectors": ["All IT services"],
        "severity": "high",
        "date": "2026-02-05"
    },
    {
        "id": "MKT-012",
        "source": "AWS India — Cloud Adoption Report 2026",
        "headline": "India cloud migration projects cross $12B in 2026 — fastest growing AWS market globally",
        "description": (
            "AWS India reports 45% YoY growth in cloud migration project value. India now AWS's "
            "fastest growing market globally. Azure and GCP also reporting 35%+ growth in India. "
            "Strong demand for cloud architecture, migration factory, FinOps, and cloud-native "
            "development services. Skill shortage in cloud architects remains critical bottleneck."
        ),
        "sentiment": "positive",
        "impact_on_it": "Strong project pipeline for cloud migration, modernization, and FinOps services",
        "affected_sectors": ["BFSI", "Manufacturing", "Healthcare", "Retail"],
        "severity": "medium",
        "date": "2026-01-25"
    },
    {
        "id": "MKT-013",
        "source": "Palo Alto Networks — India Threat Intelligence Report 2026",
        "headline": "Ransomware attacks on Indian enterprises up 218% — emergency cybersecurity project surge",
        "description": (
            "Palo Alto threat intelligence shows 218% increase in ransomware targeting Indian "
            "enterprises in 2025. BFSI, healthcare, and manufacturing most targeted sectors. "
            "Average ransom demand of $2.8M and 23-day recovery time creating board-level urgency. "
            "Emergency cybersecurity project demand with 60-90 day implementation timelines."
        ),
        "sentiment": "positive",
        "impact_on_it": "Emergency SOC, SIEM, and incident response project demand at premium rates",
        "affected_sectors": ["BFSI", "Healthcare", "Manufacturing"],
        "severity": "high",
        "date": "2026-02-12"
    },
    {
        "id": "MKT-014",
        "source": "RedSeer Consulting — Retail IT Spending India 2026",
        "headline": "Traditional retail IT budgets cut 18% as quick commerce disrupts sector fundamentals",
        "description": (
            "RedSeer reports 18% average IT budget cut at traditional brick-and-mortar retail companies "
            "as Zepto, Blinkit, and Swiggy Instamart disrupt their business model. "
            "Digital transformation projects being descoped or delayed by 6-12 months. "
            "However, D2C brands and e-commerce platforms increasing IT spending by 32%."
        ),
        "sentiment": "negative",
        "impact_on_it": "Retail client IT budget cuts; project deferrals; renegotiation pressure on margins",
        "affected_sectors": ["Retail", "FMCG"],
        "severity": "medium",
        "date": "2026-01-30"
    },
    {
        "id": "MKT-015",
        "source": "BCG & Google — India Internet Economy Report 2026",
        "headline": "India's digital economy projected at $1 trillion by 2028 — long-term tech investment surge",
        "description": (
            "BCG-Google report projects India's internet economy reaching $1 trillion by 2028. "
            "UPI transactions crossing 15 billion per month, ONDC gaining traction with 80,000+ sellers, "
            "and Jan Dhan digital services creating massive backend IT infrastructure demand. "
            "Creates long-term strong pipeline for platform engineering and digital infrastructure."
        ),
        "sentiment": "positive",
        "impact_on_it": "Long-term strong demand for digital infrastructure, fintech, and platform engineering",
        "affected_sectors": ["Fintech", "E-commerce", "Government"],
        "severity": "low",
        "date": "2026-02-03"
    },
    {
        "id": "MKT-016",
        "source": "NASSCOM — AI Skills Gap Report 2026",
        "headline": "India faces 500,000 AI talent shortage by 2027 — 40% salary premium for AI roles",
        "description": (
            "NASSCOM estimates AI talent demand will exceed supply by 500,000 professionals by 2027. "
            "Companies paying 35-45% premium for AI/ML engineers, data scientists, and MLOps professionals. "
            "Training pipelines unable to bridge gap — average reskilling time of 8-12 months. "
            "Impacts particularly severe for mid-size IT companies competing with tech giants."
        ),
        "sentiment": "negative",
        "impact_on_it": "AI project delivery risk from talent shortage; margin compression from salary inflation",
        "affected_sectors": ["IT Services", "BFSI", "Healthcare"],
        "severity": "high",
        "date": "2026-01-20"
    },
    {
        "id": "MKT-017",
        "source": "CII — Digital Manufacturing India Report 2026",
        "headline": "Make in India 2.0 drives 28% increase in manufacturing IT investments — strong pipeline",
        "description": (
            "CII report shows manufacturing sector IT spending growing 28% as companies invest in "
            "Industry 4.0, smart factory, and supply chain digitization. ERP upgrades, IoT implementations, "
            "and AI-driven quality control driving significant project pipeline. Automotive, pharma, "
            "and electronics manufacturing sectors leading the investment wave."
        ),
        "sentiment": "positive",
        "impact_on_it": "Strong manufacturing IT project pipeline for ERP, IoT, and AI quality systems",
        "affected_sectors": ["Manufacturing", "Automotive", "Pharma"],
        "severity": "medium",
        "date": "2026-01-28"
    },
    {
        "id": "MKT-018",
        "source": "RBI — Core Banking Resilience Circular February 2026",
        "headline": "RBI mandates core banking system resilience upgrades for all scheduled banks by Dec 2026",
        "description": (
            "Following multiple banking outage incidents in 2025, RBI issued emergency circular "
            "mandating core banking system resilience upgrades, disaster recovery testing, "
            "and cloud readiness assessment for all 91 scheduled commercial banks by December 2026. "
            "Estimated IT project demand of ₹8,500 crore across banking sector."
        ),
        "sentiment": "positive",
        "impact_on_it": "Urgent banking IT project demand; premium rates for core banking expertise",
        "affected_sectors": ["BFSI"],
        "severity": "high",
        "date": "2026-02-15"
    },
    {
        "id": "MKT-019",
        "source": "Inc42 — India Startup Ecosystem Annual Report 2026",
        "headline": "Indian startup funding down 31% to $9.6B — edtech and consumer tech hardest hit",
        "description": (
            "Indian startup funding fell 31% to $9.6B in 2025. Edtech and consumer tech facing "
            "severe funding winter with 40+ shutdowns including major players. B2B SaaS and Fintech "
            "remain resilient with 12% growth. IT services companies with edtech clients face "
            "payment risk, project cancellations, and receivables risk from distressed clients."
        ),
        "sentiment": "negative",
        "impact_on_it": "Edtech client payment risk; project cancellations; startup client credit risk",
        "affected_sectors": ["EdTech", "Consumer Tech", "D2C"],
        "severity": "medium",
        "date": "2026-01-12"
    },
    {
        "id": "MKT-020",
        "source": "Ernst & Young — India IT Sector M&A Report 2026",
        "headline": "IT sector M&A activity up 45% with 127 deals worth $8.2B — consolidation accelerates",
        "description": (
            "IT sector saw 45% increase in M&A activity in 2025 with 127 deals worth $8.2B. "
            "Mid-size IT companies being acquired by larger players and PE firms at 3-5x revenue. "
            "Creates delivery risk for projects mid-acquisition due to leadership uncertainty, "
            "but also creates scale opportunities for acquirers entering new service lines."
        ),
        "sentiment": "neutral",
        "impact_on_it": "Client uncertainty during M&A; potential project holds; new strategic scale opportunities",
        "affected_sectors": ["IT Services"],
        "severity": "medium",
        "date": "2026-02-06"
    },
]


# ============================================================
# GENERATOR FUNCTIONS
# ============================================================

def generate_projects_json():
    """Saves all 15 projects to projects.json"""
    output_path = OUTPUT_DIR / "projects.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(PROJECTS, f, indent=2, ensure_ascii=False)
    print(f"✅ Generated {len(PROJECTS)} projects → {output_path}")
    return PROJECTS


def generate_market_signals_json():
    """Saves all 20 market signals to market_signals.json"""
    output_path = OUTPUT_DIR / "market_signals.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(MARKET_SIGNALS, f, indent=2, ensure_ascii=False)
    print(f"✅ Generated {len(MARKET_SIGNALS)} market signals → {output_path}")
    return MARKET_SIGNALS


def generate_all():
    """Main entry point — generates all data files"""
    print("\n🔄 Generating RiskPulse AI Synthetic Data...")
    print("=" * 60)
    projects = generate_projects_json()
    signals  = generate_market_signals_json()
    print("=" * 60)
    print(f"✅ Done! {len(projects)} projects | {len(signals)} market signals\n")

    print("📋 Project Summary:")
    for p in projects:
        print(f"   {p['id']} | {p['name']:<18} | {p['client']:<28} | {p['type'][:30]}")

    print("\n📈 Market Signal Sentiment:")
    pos = sum(1 for s in signals if s["sentiment"] == "positive")
    neg = sum(1 for s in signals if s["sentiment"] == "negative")
    neu = sum(1 for s in signals if s["sentiment"] == "neutral")
    print(f"   🟢 Positive: {pos}  🔴 Negative: {neg}  ⚪ Neutral: {neu}")
    print(f"\n📁 Output: {OUTPUT_DIR}\n")

def load_projects() -> list:
    """Loads projects from generated JSON file."""
    output_path = OUTPUT_DIR / "projects.json"
    if not output_path.exists():
        generate_projects_json()
    with open(output_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_market_signals() -> list:
    """Loads market signals from generated JSON file."""
    output_path = OUTPUT_DIR / "market_signals.json"
    if not output_path.exists():
        generate_market_signals_json()
    with open(output_path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    generate_all()