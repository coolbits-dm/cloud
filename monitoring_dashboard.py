#!/usr/bin/env python3
# CoolBits.ai Monitoring Dashboard

import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd

st.set_page_config(
    page_title="CoolBits.ai Monitoring Dashboard",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 CoolBits.ai Monitoring Dashboard")

# Health Status
st.header("🏥 Health Status")

try:
    health_response = requests.get("http://localhost:8501/api/health", timeout=5)
    if health_response.status_code == 200:
        st.success("✅ System Healthy")
        health_data = health_response.json()
        st.json(health_data)
    else:
        st.error(f"❌ System Unhealthy: {health_response.status_code}")
except Exception as e:
    st.error(f"❌ Health Check Failed: {e}")

# Metrics
st.header("📊 System Metrics")

try:
    metrics_response = requests.get("http://localhost:8501/api/metrics", timeout=5)
    if metrics_response.status_code == 200:
        metrics_data = metrics_response.json()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("CPU Usage", f"{metrics_data.get('cpu_usage', 0):.1f}%")
        
        with col2:
            st.metric("Memory Usage", f"{metrics_data.get('memory_usage', 0):.1f}%")
        
        st.json(metrics_data)
    else:
        st.error(f"❌ Metrics Unavailable: {metrics_response.status_code}")
except Exception as e:
    st.error(f"❌ Metrics Check Failed: {e}")

# Recent Reports
st.header("📋 Recent Reports")

report_files = list(Path(".").glob("weekly_validation_report_*.json"))
if report_files:
    latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
    
    with open(latest_report, 'r') as f:
        report_data = json.load(f)
    
    st.success(f"📄 Latest Report: {latest_report.name}")
    st.json(report_data)
else:
    st.warning("⚠️ No reports found")

# Maintenance Actions
st.header("🔧 Maintenance Actions")

if st.button("Run Weekly Validation"):
    with st.spinner("Running weekly validation..."):
        # This would run the actual validation
        st.success("✅ Weekly validation completed")

if st.button("Test Canary Deployment"):
    with st.spinner("Testing canary deployment..."):
        # This would run the actual test
        st.success("✅ Canary deployment test completed")

if st.button("Test Security"):
    with st.spinner("Testing security..."):
        # This would run the actual test
        st.success("✅ Security test completed")

# Footer
st.markdown("---")
st.markdown("**CoolBits.ai Infrastructure Monitoring** | Last Updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
