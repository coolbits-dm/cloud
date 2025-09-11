#!/usr/bin/env python3
"""
CoolBits.ai SLO Check Script
============================

Checks SLO compliance for canary deployments and promotion gates.
"""

import sys
import argparse
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class SLOChecker:
    """SLO compliance checker for CoolBits.ai services"""
    
    def __init__(self, project_id: str = "coolbits-og-bridge"):
        self.project_id = project_id
        self.monitoring_api_base = f"https://monitoring.googleapis.com/v3/projects/{project_id}"
        self.access_token = self._get_access_token()
    
    def _get_access_token(self) -> str:
        """Get Google Cloud access token"""
        try:
            import subprocess
            result = subprocess.run([
                'gcloud', 'auth', 'application-default', 'print-access-token'
            ], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except Exception as e:
            print(f"❌ Error getting access token: {e}")
            sys.exit(1)
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make authenticated request to Monitoring API"""
        url = f"{self.monitoring_api_base}/{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ API request failed: {e}")
            sys.exit(1)
    
    def check_p95_latency(self, service: str, window_minutes: int = 30, threshold_ms: float = 400) -> Tuple[bool, float]:
        """Check P95 latency SLO"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=window_minutes)
        
        # Convert to RFC3339 format
        start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # Query P95 latency
        params = {
            'filter': f'metric.type="run.googleapis.com/request_latencies" AND resource.label."service_name"="{service}"',
            'interval.endTime': end_time_str,
            'interval.startTime': start_time_str,
            'aggregation.alignmentPeriod': '60s',
            'aggregation.perSeriesAligner': 'ALIGN_DELTA',
            'aggregation.crossSeriesReducer': 'REDUCE_PERCENTILE_95',
            'aggregation.groupByFields': 'resource.label.service_name'
        }
        
        data = self._make_request('timeSeries', params)
        
        if not data.get('timeSeries'):
            print(f"⚠️  No latency data found for {service}")
            return True, 0.0
        
        # Get latest P95 value
        latest_value = 0.0
        for series in data['timeSeries']:
            if series['points']:
                latest_value = float(series['points'][-1]['value']['doubleValue'])
                break
        
        threshold_seconds = threshold_ms / 1000.0
        is_compliant = latest_value <= threshold_seconds
        
        print(f"📊 {service} P95 Latency: {latest_value:.3f}s (threshold: {threshold_seconds:.3f}s)")
        
        return is_compliant, latest_value
    
    def check_error_rate(self, service: str, window_minutes: int = 30, threshold_percent: float = 1.0) -> Tuple[bool, float]:
        """Check 5xx error rate SLO"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=window_minutes)
        
        start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # Query total requests
        total_params = {
            'filter': f'metric.type="run.googleapis.com/request_count" AND resource.label."service_name"="{service}"',
            'interval.endTime': end_time_str,
            'interval.startTime': start_time_str,
            'aggregation.alignmentPeriod': '60s',
            'aggregation.perSeriesAligner': 'ALIGN_RATE',
            'aggregation.crossSeriesReducer': 'REDUCE_SUM',
            'aggregation.groupByFields': 'resource.label.service_name'
        }
        
        total_data = self._make_request('timeSeries', total_params)
        
        # Query 5xx requests
        error_params = {
            'filter': f'metric.type="run.googleapis.com/request_count" AND metric.label."response_code_class"="5xx" AND resource.label."service_name"="{service}"',
            'interval.endTime': end_time_str,
            'interval.startTime': start_time_str,
            'aggregation.alignmentPeriod': '60s',
            'aggregation.perSeriesAligner': 'ALIGN_RATE',
            'aggregation.crossSeriesReducer': 'REDUCE_SUM',
            'aggregation.groupByFields': 'resource.label.service_name'
        }
        
        error_data = self._make_request('timeSeries', error_params)
        
        # Calculate error rate
        total_requests = 0.0
        error_requests = 0.0
        
        if total_data.get('timeSeries'):
            for series in total_data['timeSeries']:
                if series['points']:
                    total_requests = float(series['points'][-1]['value']['doubleValue'])
                    break
        
        if error_data.get('timeSeries'):
            for series in error_data['timeSeries']:
                if series['points']:
                    error_requests = float(series['points'][-1]['value']['doubleValue'])
                    break
        
        error_rate_percent = (error_requests / total_requests * 100) if total_requests > 0 else 0.0
        is_compliant = error_rate_percent <= threshold_percent
        
        print(f"📊 {service} Error Rate: {error_rate_percent:.2f}% (threshold: {threshold_percent:.2f}%)")
        
        return is_compliant, error_rate_percent
    
    def check_uptime(self, service: str, window_minutes: int = 30) -> Tuple[bool, float]:
        """Check uptime SLO"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=window_minutes)
        
        start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # Query uptime check
        params = {
            'filter': f'metric.type="monitoring.googleapis.com/uptime_check/check_passed" AND resource.label."check_id"=~".*{service}.*"',
            'interval.endTime': end_time_str,
            'interval.startTime': start_time_str,
            'aggregation.alignmentPeriod': '60s',
            'aggregation.perSeriesAligner': 'ALIGN_MEAN',
            'aggregation.crossSeriesReducer': 'REDUCE_MEAN'
        }
        
        data = self._make_request('timeSeries', params)
        
        if not data.get('timeSeries'):
            print(f"⚠️  No uptime data found for {service}")
            return True, 100.0
        
        # Calculate uptime percentage
        uptime_values = []
        for series in data['timeSeries']:
            for point in series['points']:
                uptime_values.append(float(point['value']['doubleValue']))
        
        uptime_percent = (sum(uptime_values) / len(uptime_values) * 100) if uptime_values else 100.0
        is_compliant = uptime_percent >= 99.9  # 99.9% uptime SLO
        
        print(f"📊 {service} Uptime: {uptime_percent:.2f}% (threshold: 99.9%)")
        
        return is_compliant, uptime_percent
    
    def check_all_slos(self, service: str, window_minutes: int = 30, 
                      p95_threshold_ms: float = 400, error_threshold_percent: float = 1.0) -> bool:
        """Check all SLOs for a service"""
        print(f"🔍 Checking SLOs for {service} (last {window_minutes} minutes)")
        print("=" * 60)
        
        # Check P95 latency
        latency_ok, latency_value = self.check_p95_latency(service, window_minutes, p95_threshold_ms)
        
        # Check error rate
        error_ok, error_rate = self.check_error_rate(service, window_minutes, error_threshold_percent)
        
        # Check uptime
        uptime_ok, uptime_percent = self.check_uptime(service, window_minutes)
        
        print("=" * 60)
        
        # Overall SLO compliance
        all_ok = latency_ok and error_ok and uptime_ok
        
        if all_ok:
            print(f"✅ {service} SLO compliance: PASSED")
        else:
            print(f"❌ {service} SLO compliance: FAILED")
            if not latency_ok:
                print(f"   - P95 latency exceeded threshold")
            if not error_ok:
                print(f"   - Error rate exceeded threshold")
            if not uptime_ok:
                print(f"   - Uptime below threshold")
        
        return all_ok

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Check CoolBits.ai SLO compliance')
    parser.add_argument('--service', required=True, help='Service name to check')
    parser.add_argument('--window', type=int, default=30, help='Time window in minutes (default: 30)')
    parser.add_argument('--p95', type=float, default=400, help='P95 latency threshold in ms (default: 400)')
    parser.add_argument('--error-rate', type=float, default=1.0, help='Error rate threshold in % (default: 1.0)')
    parser.add_argument('--project', default='coolbits-og-bridge', help='GCP project ID')
    
    args = parser.parse_args()
    
    checker = SLOChecker(args.project)
    
    # Check SLOs
    slo_ok = checker.check_all_slos(
        service=args.service,
        window_minutes=args.window,
        p95_threshold_ms=args.p95,
        error_threshold_percent=args.error_rate
    )
    
    # Exit with appropriate code
    sys.exit(0 if slo_ok else 1)

if __name__ == "__main__":
    main()
