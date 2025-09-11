# CoolBits.ai Operational Checklist
# =================================

"""
🎯 COOLBITS.AI OPERATIONAL CHECKLIST
====================================

This checklist ensures CoolBits.ai infrastructure remains healthy and operational.
Run this weekly or whenever you need to verify system health.

📋 DAILY CHECKS (Automated)
- [ ] CI pipeline runs on every commit
- [ ] Health endpoints respond (8501, 8502)
- [ ] Log files are rotated and cleaned
- [ ] Uptime monitoring is active

📋 WEEKLY CHECKS (Manual + Automated)
- [ ] Run weekly validation: python weekly_validator.py --run
- [ ] Test canary deployment: python test_canary_deployment.py
- [ ] Test RBAC/HMAC security: python test_rbac_hmac.py
- [ ] Test dashboard API connectivity: python test_dashboard_real_api.py
- [ ] Review security audit logs
- [ ] Check HMAC key expiration dates

📋 MONTHLY CHECKS (Manual)
- [ ] Rotate HMAC keys: python hmac_key_manager.py generate
- [ ] Review and update security policies
- [ ] Test disaster recovery procedures
- [ ] Update dependencies and security patches
- [ ] Review monitoring dashboards and alerts

📋 QUARTERLY CHECKS (Manual)
- [ ] Full infrastructure audit
- [ ] Performance benchmarking
- [ ] Security penetration testing
- [ ] Backup and recovery testing
- [ ] Documentation review and updates

🚨 EMERGENCY PROCEDURES
- [ ] Rollback deployment: python rollback_manager.py emergency
- [ ] Revoke compromised HMAC keys: python hmac_key_manager.py revoke
- [ ] Activate maintenance mode
- [ ] Notify stakeholders of issues

📊 HEALTH INDICATORS
- [ ] CI pipeline: Green status
- [ ] Uptime: >99.5%
- [ ] Response time: <500ms P95
- [ ] Error rate: <1%
- [ ] Security alerts: 0 critical

🔧 MAINTENANCE COMMANDS
- [ ] Start automated maintenance: python automated_maintenance.py --setup
- [ ] Run validation now: python weekly_validator.py --run
- [ ] Check system status: python roadmap.py list
- [ ] View logs: tail -f maintenance_log_*.txt

📞 ESCALATION CONTACTS
- [ ] Primary: Andrei (CEO)
- [ ] Technical: oPyGPT03
- [ ] Security: oGrok08 (CISO)
- [ ] AI/ML: oGrok09 (CAIO)

🎯 SUCCESS CRITERIA
- [ ] All automated tests pass
- [ ] No critical security vulnerabilities
- [ ] System performance within SLA
- [ ] Documentation up to date
- [ ] Team trained on procedures
"""

import os
import sys
from datetime import datetime


class OperationalChecklist:
    """Operational checklist for CoolBits.ai."""
    
    def __init__(self):
        self.checklist_file = f"operational_checklist_{datetime.now().strftime('%Y%m%d')}.txt"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "overall_status": "unknown"
        }
    
    def log_check(self, category: str, check: str, status: str, notes: str = ""):
        """Log a checklist item."""
        if category not in self.results["checks"]:
            self.results["checks"][category] = {}
        
        self.results["checks"][category][check] = {
            "status": status,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {category}: {check} - {status}")
        if notes:
            print(f"   Notes: {notes}")
    
    def run_daily_checks(self):
        """Run daily operational checks."""
        print("\n📋 Running Daily Checks...")
        
        # Check CI pipeline
        try:
            result = subprocess.run(
                ["python", "-m", "black", "--check", "."],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self.log_check("DAILY", "CI Pipeline", "PASS", "Code formatting correct")
            else:
                self.log_check("DAILY", "CI Pipeline", "FAIL", "Formatting issues detected")
        except Exception as e:
            self.log_check("DAILY", "CI Pipeline", "ERROR", f"CI check failed: {e}")
        
        # Check health endpoints
        try:
            import requests
            response = requests.get("http://localhost:8501/api/health", timeout=5)
            if response.status_code == 200:
                self.log_check("DAILY", "Health Endpoints", "PASS", "Health endpoint responding")
            else:
                self.log_check("DAILY", "Health Endpoints", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_check("DAILY", "Health Endpoints", "ERROR", f"Health check failed: {e}")
        
        # Check log files
        log_files = list(Path(".").glob("*.log"))
        if len(log_files) > 0:
            self.log_check("DAILY", "Log Files", "PASS", f"{len(log_files)} log files found")
        else:
            self.log_check("DAILY", "Log Files", "WARNING", "No log files found")
    
    def run_weekly_checks(self):
        """Run weekly operational checks."""
        print("\n📋 Running Weekly Checks...")
        
        # Run weekly validation
        try:
            result = subprocess.run(
                ["python", "weekly_validator.py", "--run"],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                self.log_check("WEEKLY", "Weekly Validation", "PASS", "All weekly tests passed")
            else:
                self.log_check("WEEKLY", "Weekly Validation", "FAIL", "Some weekly tests failed")
        except Exception as e:
            self.log_check("WEEKLY", "Weekly Validation", "ERROR", f"Weekly validation failed: {e}")
        
        # Test canary deployment
        try:
            result = subprocess.run(
                ["python", "test_canary_deployment.py"],
                capture_output=True,
                text=True,
                timeout=180
            )
            if result.returncode == 0:
                self.log_check("WEEKLY", "Canary Deployment", "PASS", "Canary tests passed")
            else:
                self.log_check("WEEKLY", "Canary Deployment", "FAIL", "Canary tests failed")
        except Exception as e:
            self.log_check("WEEKLY", "Canary Deployment", "ERROR", f"Canary test failed: {e}")
        
        # Test security
        try:
            result = subprocess.run(
                ["python", "test_rbac_hmac.py"],
                capture_output=True,
                text=True,
                timeout=180
            )
            if result.returncode == 0:
                self.log_check("WEEKLY", "Security Tests", "PASS", "Security tests passed")
            else:
                self.log_check("WEEKLY", "Security Tests", "FAIL", "Security tests failed")
        except Exception as e:
            self.log_check("WEEKLY", "Security Tests", "ERROR", f"Security test failed: {e}")
    
    def run_monthly_checks(self):
        """Run monthly operational checks."""
        print("\n📋 Running Monthly Checks...")
        
        # Check HMAC key expiration
        try:
            from hmac_key_manager import HMACKeyManager
            key_manager = HMACKeyManager()
            keys = key_manager.list_keys()
            
            expired_keys = 0
            expiring_soon = 0
            
            for key in keys:
                if key.get('expires_at'):
                    from datetime import datetime
                    expires = datetime.fromisoformat(key['expires_at'])
                    days_until_expiry = (expires - datetime.now()).days
                    
                    if days_until_expiry < 0:
                        expired_keys += 1
                    elif days_until_expiry < 30:
                        expiring_soon += 1
            
            if expired_keys == 0 and expiring_soon == 0:
                self.log_check("MONTHLY", "HMAC Key Expiration", "PASS", "All keys valid")
            elif expiring_soon > 0:
                self.log_check("MONTHLY", "HMAC Key Expiration", "WARNING", f"{expiring_soon} keys expiring soon")
            else:
                self.log_check("MONTHLY", "HMAC Key Expiration", "FAIL", f"{expired_keys} keys expired")
                
        except Exception as e:
            self.log_check("MONTHLY", "HMAC Key Expiration", "ERROR", f"Key check failed: {e}")
        
        # Check system performance
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            
            if cpu_percent < 80 and memory_percent < 80:
                self.log_check("MONTHLY", "System Performance", "PASS", f"CPU: {cpu_percent:.1f}%, Memory: {memory_percent:.1f}%")
            else:
                self.log_check("MONTHLY", "System Performance", "WARNING", f"High usage - CPU: {cpu_percent:.1f}%, Memory: {memory_percent:.1f}%")
                
        except Exception as e:
            self.log_check("MONTHLY", "System Performance", "ERROR", f"Performance check failed: {e}")
    
    def generate_report(self):
        """Generate operational checklist report."""
        print("\n📊 Generating Operational Checklist Report...")
        
        # Calculate overall status
        all_checks = []
        for category in self.results["checks"].values():
            all_checks.extend(category.values())
        
        pass_count = sum(1 for check in all_checks if check["status"] == "PASS")
        total_count = len(all_checks)
        
        if pass_count == total_count:
            self.results["overall_status"] = "HEALTHY"
        elif pass_count >= total_count * 0.8:
            self.results["overall_status"] = "WARNING"
        else:
            self.results["overall_status"] = "CRITICAL"
        
        # Save report
        import json
        report_file = f"operational_report_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"📄 Report saved: {report_file}")
        
        # Print summary
        print(f"\n🎯 Operational Checklist Summary:")
        print(f"   Overall Status: {self.results['overall_status']}")
        print(f"   Checks Passed: {pass_count}/{total_count}")
        print(f"   Pass Rate: {(pass_count/total_count)*100:.1f}%")
        
        return self.results
    
    def run_all_checks(self):
        """Run all operational checks."""
        print("🎯 CoolBits.ai Operational Checklist")
        print("=" * 40)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
        print(f"🕐 Started: {datetime.now().strftime('%H:%M:%S')}")
        
        self.run_daily_checks()
        self.run_weekly_checks()
        self.run_monthly_checks()
        
        return self.generate_report()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CoolBits.ai Operational Checklist")
    parser.add_argument("--daily", action="store_true", help="Run daily checks only")
    parser.add_argument("--weekly", action="store_true", help="Run weekly checks only")
    parser.add_argument("--monthly", action="store_true", help="Run monthly checks only")
    parser.add_argument("--all", action="store_true", help="Run all checks")
    
    args = parser.parse_args()
    
    checklist = OperationalChecklist()
    
    if args.daily:
        checklist.run_daily_checks()
    elif args.weekly:
        checklist.run_weekly_checks()
    elif args.monthly:
        checklist.run_monthly_checks()
    elif args.all:
        checklist.run_all_checks()
    else:
        print("Usage:")
        print("  python operational_checklist.py --daily   # Run daily checks")
        print("  python operational_checklist.py --weekly   # Run weekly checks")
        print("  python operational_checklist.py --monthly  # Run monthly checks")
        print("  python operational_checklist.py --all      # Run all checks")
