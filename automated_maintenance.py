# CoolBits.ai Automated Maintenance Scripts
# ==========================================

import os
import sys
import time
import subprocess
import schedule
from datetime import datetime, timedelta
from pathlib import Path


class AutomatedMaintenance:
    """Automated maintenance routines for CoolBits.ai."""
    
    def __init__(self):
        self.log_file = f"maintenance_log_{datetime.now().strftime('%Y%m%d')}.txt"
        self.log("Automated maintenance started")
    
    def log(self, message: str):
        """Log maintenance activities."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    
    def daily_ci_check(self):
        """Daily CI pipeline check."""
        self.log("🔧 Running daily CI check...")
        
        try:
            # Check if there are any uncommitted changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                self.log("⚠️ Uncommitted changes detected - running CI")
                
                # Run basic CI checks
                subprocess.run(["python", "-m", "black", "--check", "."], check=False)
                subprocess.run(["python", "-m", "flake8", ".", "--count"], check=False)
                
                self.log("✅ Daily CI check completed")
            else:
                self.log("✅ No changes detected - CI check skipped")
                
        except Exception as e:
            self.log(f"❌ Daily CI check failed: {e}")
    
    def weekly_canary_test(self):
        """Weekly canary deployment test."""
        self.log("🚀 Running weekly canary test...")
        
        try:
            # Run canary deployment test
            result = subprocess.run(
                ["python", "test_canary_deployment.py"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                self.log("✅ Weekly canary test passed")
            else:
                self.log(f"❌ Weekly canary test failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.log("⏰ Weekly canary test timed out")
        except Exception as e:
            self.log(f"❌ Weekly canary test error: {e}")
    
    def monthly_hmac_rotation(self):
        """Monthly HMAC key rotation."""
        self.log("🔑 Running monthly HMAC key rotation...")
        
        try:
            from hmac_key_manager import HMACKeyManager
            
            key_manager = HMACKeyManager()
            
            # Generate new key
            new_key = key_manager.generate_key(
                name=f"monthly-rotation-{datetime.now().strftime('%Y%m')}",
                description="Monthly automated key rotation",
                expires_in_days=90
            )
            
            if new_key:
                self.log(f"✅ New HMAC key generated: {new_key['key_id']}")
                
                # Cleanup old keys
                removed_count = key_manager.cleanup_expired_keys()
                self.log(f"🧹 Cleaned up {removed_count} expired keys")
            else:
                self.log("❌ Failed to generate new HMAC key")
                
        except Exception as e:
            self.log(f"❌ Monthly HMAC rotation failed: {e}")
    
    def hourly_uptime_check(self):
        """Hourly uptime check."""
        self.log("📊 Running hourly uptime check...")
        
        try:
            import requests
            
            endpoints = [
                "http://localhost:8501/api/health",
                "http://localhost:8502/api/health"  # If you have multiple services
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, timeout=10)
                    if response.status_code == 200:
                        self.log(f"✅ {endpoint} - Healthy")
                    else:
                        self.log(f"⚠️ {endpoint} - Status: {response.status_code}")
                except Exception as e:
                    self.log(f"❌ {endpoint} - Error: {e}")
                    
        except Exception as e:
            self.log(f"❌ Hourly uptime check failed: {e}")
    
    def weekly_security_audit(self):
        """Weekly security audit."""
        self.log("🔐 Running weekly security audit...")
        
        try:
            # Test RBAC/HMAC
            result = subprocess.run(
                ["python", "test_rbac_hmac.py"],
                capture_output=True,
                text=True,
                timeout=180
            )
            
            if result.returncode == 0:
                self.log("✅ Weekly security audit passed")
            else:
                self.log(f"❌ Weekly security audit failed: {result.stderr}")
                
        except Exception as e:
            self.log(f"❌ Weekly security audit error: {e}")
    
    def daily_log_cleanup(self):
        """Daily log cleanup."""
        self.log("🧹 Running daily log cleanup...")
        
        try:
            # Clean up old log files (older than 30 days)
            log_dir = Path(".")
            cutoff_date = datetime.now() - timedelta(days=30)
            
            cleaned_count = 0
            for log_file in log_dir.glob("*.log"):
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    log_file.unlink()
                    cleaned_count += 1
            
            # Clean up old validation reports (older than 90 days)
            for report_file in log_dir.glob("weekly_validation_report_*.json"):
                if report_file.stat().st_mtime < cutoff_date.timestamp():
                    report_file.unlink()
                    cleaned_count += 1
            
            self.log(f"✅ Cleaned up {cleaned_count} old files")
            
        except Exception as e:
            self.log(f"❌ Daily log cleanup failed: {e}")
    
    def setup_scheduling(self):
        """Setup automated scheduling."""
        self.log("⏰ Setting up automated scheduling...")
        
        # Daily tasks
        schedule.every().day.at("06:00").do(self.daily_ci_check)
        schedule.every().day.at("23:00").do(self.daily_log_cleanup)
        
        # Hourly tasks
        schedule.every().hour.do(self.hourly_uptime_check)
        
        # Weekly tasks
        schedule.every().monday.at("09:00").do(self.weekly_canary_test)
        schedule.every().friday.at("14:00").do(self.weekly_security_audit)
        
        # Monthly tasks
        schedule.every().month.do(self.monthly_hmac_rotation)
        
        self.log("✅ Automated scheduling configured")
        self.log("📅 Daily CI check: 06:00")
        self.log("📅 Daily log cleanup: 23:00")
        self.log("📅 Hourly uptime check: Every hour")
        self.log("📅 Weekly canary test: Monday 09:00")
        self.log("📅 Weekly security audit: Friday 14:00")
        self.log("📅 Monthly HMAC rotation: First of month")
    
    def run_scheduler(self):
        """Run the maintenance scheduler."""
        self.log("🔄 Starting maintenance scheduler...")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                self.log("🛑 Maintenance scheduler stopped by user")
                break
            except Exception as e:
                self.log(f"❌ Scheduler error: {e}")
                time.sleep(60)


def create_windows_service():
    """Create Windows service for automated maintenance."""
    service_script = '''
import win32serviceutil
import win32service
import win32event
import servicemanager
import sys
import os
from automated_maintenance import AutomatedMaintenance

class CoolBitsMaintenanceService(win32serviceutil.ServiceFramework):
    _svc_name_ = "CoolBitsMaintenance"
    _svc_display_name_ = "CoolBits.ai Automated Maintenance"
    _svc_description_ = "Automated maintenance and validation for CoolBits.ai infrastructure"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.maintenance = AutomatedMaintenance()

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.maintenance.setup_scheduling()
        self.maintenance.run_scheduler()

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(CoolBitsMaintenanceService)
'''
    
    with open("coolbits_maintenance_service.py", "w") as f:
        f.write(service_script)
    
    print("✅ Windows service script created: coolbits_maintenance_service.py")
    print("📝 To install service: python coolbits_maintenance_service.py install")
    print("📝 To start service: python coolbits_maintenance_service.py start")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CoolBits.ai Automated Maintenance")
    parser.add_argument("--setup", action="store_true", help="Setup automated scheduling")
    parser.add_argument("--run", action="store_true", help="Run maintenance now")
    parser.add_argument("--service", action="store_true", help="Create Windows service")
    
    args = parser.parse_args()
    
    maintenance = AutomatedMaintenance()
    
    if args.setup:
        maintenance.setup_scheduling()
        print("🔄 Starting scheduler... (Press Ctrl+C to stop)")
        maintenance.run_scheduler()
    elif args.run:
        maintenance.daily_ci_check()
        maintenance.weekly_canary_test()
        maintenance.weekly_security_audit()
        maintenance.daily_log_cleanup()
    elif args.service:
        create_windows_service()
    else:
        print("Usage:")
        print("  python automated_maintenance.py --setup   # Setup automated scheduling")
        print("  python automated_maintenance.py --run     # Run maintenance now")
        print("  python automated_maintenance.py --service # Create Windows service")
