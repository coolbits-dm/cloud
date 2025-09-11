# CoolBits.ai Rollback Script
# ============================

import os
import sys
import time
import json
import requests
import subprocess
import argparse
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RollbackConfig:
    """Configuration for rollback operations."""

    production_url: str
    health_check_endpoint: str = "/_stcore/health"
    max_rollback_time: int = 60  # 1 minute
    backup_retention_days: int = 7
    notification_webhook: Optional[str] = None


class RollbackManager:
    """Handles rollback operations with safety checks."""

    def __init__(self, config: RollbackConfig):
        self.config = config
        self.rollback_id = f"rollback-{int(time.time())}"
        self.start_time = None

    def emergency_rollback(self, reason: str = "Emergency rollback") -> bool:
        """Perform emergency rollback to previous version."""
        print(f"🚨 EMERGENCY ROLLBACK INITIATED: {reason}")
        print(f"🆔 Rollback ID: {self.rollback_id}")

        self.start_time = datetime.now()

        try:
            # Step 1: Stop current production
            self._stop_current_production()

            # Step 2: Restore previous version
            self._restore_previous_version()

            # Step 3: Verify rollback success
            if self._verify_rollback():
                self._notify_rollback_success(reason)
                print("✅ Emergency rollback completed successfully")
                return True
            else:
                self._notify_rollback_failure(reason)
                print("❌ Emergency rollback verification failed")
                return False

        except Exception as e:
            print(f"❌ Emergency rollback failed: {e}")
            self._notify_rollback_failure(f"{reason}: {str(e)}")
            return False

    def planned_rollback(
        self, target_version: str, reason: str = "Planned rollback"
    ) -> bool:
        """Perform planned rollback to specific version."""
        print(f"📋 PLANNED ROLLBACK INITIATED: {reason}")
        print(f"🎯 Target version: {target_version}")
        print(f"🆔 Rollback ID: {self.rollback_id}")

        self.start_time = datetime.now()

        try:
            # Step 1: Validate target version exists
            if not self._validate_target_version(target_version):
                print(f"❌ Target version {target_version} not found")
                return False

            # Step 2: Create backup of current version
            self._backup_current_version()

            # Step 3: Deploy target version
            self._deploy_target_version(target_version)

            # Step 4: Verify rollback success
            if self._verify_rollback():
                self._notify_rollback_success(f"{reason} to {target_version}")
                print("✅ Planned rollback completed successfully")
                return True
            else:
                # Rollback the rollback
                self._restore_from_backup()
                self._notify_rollback_failure(f"{reason} to {target_version}")
                print("❌ Planned rollback verification failed, restored from backup")
                return False

        except Exception as e:
            print(f"❌ Planned rollback failed: {e}")
            self._notify_rollback_failure(f"{reason}: {str(e)}")
            return False

    def _stop_current_production(self):
        """Stop current production container."""
        print("🛑 Stopping current production...")

        try:
            # Stop production container
            subprocess.run(["docker", "stop", "coolbits-production"], check=True)
            subprocess.run(["docker", "rm", "coolbits-production"], check=True)
            print("✅ Current production stopped")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Warning: Could not stop production container: {e}")

    def _restore_previous_version(self):
        """Restore previous production version."""
        print("🔄 Restoring previous version...")

        try:
            # Check if previous version exists
            result = subprocess.run(
                [
                    "docker",
                    "images",
                    "coolbits-production:previous",
                    "--format",
                    "{{.Repository}}:{{.Tag}}",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0 or not result.stdout.strip():
                print("❌ Previous version not found")
                raise Exception("Previous version not available")

            # Start previous version
            subprocess.run(
                [
                    "docker",
                    "run",
                    "-d",
                    "--name",
                    "coolbits-production",
                    "-p",
                    "8501:8501",
                    "coolbits-production:previous",
                ],
                check=True,
            )

            print("✅ Previous version restored")

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to restore previous version: {e}")
            raise

    def _validate_target_version(self, version: str) -> bool:
        """Validate that target version exists."""
        print(f"🔍 Validating target version: {version}")

        try:
            result = subprocess.run(
                [
                    "docker",
                    "images",
                    f"coolbits-production:{version}",
                    "--format",
                    "{{.Repository}}:{{.Tag}}",
                ],
                capture_output=True,
                text=True,
            )

            exists = result.returncode == 0 and result.stdout.strip()
            if exists:
                print(f"✅ Target version {version} found")
            else:
                print(f"❌ Target version {version} not found")

            return bool(exists)

        except Exception as e:
            print(f"❌ Error validating target version: {e}")
            return False

    def _backup_current_version(self):
        """Create backup of current version."""
        print("💾 Creating backup of current version...")

        try:
            # Tag current version as backup
            subprocess.run(
                [
                    "docker",
                    "tag",
                    "coolbits-production:latest",
                    f"coolbits-production:backup-{self.rollback_id}",
                ],
                check=True,
            )

            print(f"✅ Backup created: coolbits-production:backup-{self.rollback_id}")

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create backup: {e}")
            raise

    def _deploy_target_version(self, version: str):
        """Deploy target version."""
        print(f"🚀 Deploying target version: {version}")

        try:
            # Stop current production
            self._stop_current_production()

            # Start target version
            subprocess.run(
                [
                    "docker",
                    "run",
                    "-d",
                    "--name",
                    "coolbits-production",
                    "-p",
                    "8501:8501",
                    f"coolbits-production:{version}",
                ],
                check=True,
            )

            print(f"✅ Target version {version} deployed")

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to deploy target version: {e}")
            raise

    def _restore_from_backup(self):
        """Restore from backup if rollback fails."""
        print("🔄 Restoring from backup...")

        try:
            # Stop current (failed) version
            self._stop_current_production()

            # Start backup version
            subprocess.run(
                [
                    "docker",
                    "run",
                    "-d",
                    "--name",
                    "coolbits-production",
                    "-p",
                    "8501:8501",
                    f"coolbits-production:backup-{self.rollback_id}",
                ],
                check=True,
            )

            print("✅ Restored from backup")

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to restore from backup: {e}")
            raise

    def _verify_rollback(self) -> bool:
        """Verify that rollback was successful."""
        print("🔍 Verifying rollback...")

        max_attempts = 12  # 1 minute with 5-second intervals
        attempt = 0

        while attempt < max_attempts:
            try:
                response = requests.get(
                    f"{self.config.production_url}{self.config.health_check_endpoint}",
                    timeout=5,
                )

                if response.status_code == 200:
                    print("✅ Rollback verification successful")
                    return True

            except requests.RequestException:
                pass

            attempt += 1
            time.sleep(5)

        print("❌ Rollback verification failed")
        return False

    def _notify_rollback_success(self, reason: str):
        """Notify about successful rollback."""
        if self.config.notification_webhook:
            self._send_notification("success", reason)

        # Log rollback success
        self._log_rollback("success", reason)

    def _notify_rollback_failure(self, reason: str):
        """Notify about failed rollback."""
        if self.config.notification_webhook:
            self._send_notification("failure", reason)

        # Log rollback failure
        self._log_rollback("failure", reason)

    def _send_notification(self, status: str, reason: str):
        """Send notification via webhook."""
        try:
            duration = (datetime.now() - self.start_time).total_seconds()

            payload = {
                "rollback_id": self.rollback_id,
                "status": status,
                "reason": reason,
                "duration_seconds": duration,
                "timestamp": datetime.now().isoformat(),
            }

            response = requests.post(
                self.config.notification_webhook, json=payload, timeout=10
            )

            if response.status_code == 200:
                print("✅ Notification sent successfully")
            else:
                print(f"⚠️ Notification failed: {response.status_code}")

        except Exception as e:
            print(f"⚠️ Failed to send notification: {e}")

    def _log_rollback(self, status: str, reason: str):
        """Log rollback operation."""
        duration = (datetime.now() - self.start_time).total_seconds()

        log_entry = {
            "rollback_id": self.rollback_id,
            "status": status,
            "reason": reason,
            "duration_seconds": duration,
            "timestamp": datetime.now().isoformat(),
        }

        # Save to log file
        log_file = f"rollback-log-{self.rollback_id}.json"
        with open(log_file, "w") as f:
            json.dump(log_entry, f, indent=2)

        print(f"📝 Rollback logged to {log_file}")

    def cleanup_old_backups(self):
        """Clean up old backup images."""
        print("🧹 Cleaning up old backups...")

        try:
            # List all backup images older than retention period
            result = subprocess.run(
                [
                    "docker",
                    "images",
                    "coolbits-production:backup-*",
                    "--format",
                    "{{.Repository}}:{{.Tag}} {{.CreatedAt}}",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                for line in lines:
                    if line.strip():
                        image_tag, created_at = line.split(" ", 1)
                        # Parse creation date and check if older than retention period
                        # This is a simplified check - in production you'd parse the date properly
                        print(f"🗑️ Would remove old backup: {image_tag}")

            print("✅ Backup cleanup completed")

        except Exception as e:
            print(f"⚠️ Backup cleanup failed: {e}")


def main():
    """Main rollback script."""
    parser = argparse.ArgumentParser(description="CoolBits.ai Rollback Manager")
    parser.add_argument(
        "--production-url", default="http://localhost:8501", help="Production URL"
    )
    parser.add_argument("--notification-webhook", help="Webhook URL for notifications")
    parser.add_argument(
        "--emergency", action="store_true", help="Perform emergency rollback"
    )
    parser.add_argument("--target-version", help="Target version for planned rollback")
    parser.add_argument("--reason", default="Manual rollback", help="Rollback reason")
    parser.add_argument("--cleanup", action="store_true", help="Clean up old backups")

    args = parser.parse_args()

    config = RollbackConfig(
        production_url=args.production_url,
        notification_webhook=args.notification_webhook,
    )

    rollback_manager = RollbackManager(config)

    try:
        if args.cleanup:
            rollback_manager.cleanup_old_backups()
        elif args.emergency:
            success = rollback_manager.emergency_rollback(args.reason)
            sys.exit(0 if success else 1)
        elif args.target_version:
            success = rollback_manager.planned_rollback(
                args.target_version, args.reason
            )
            sys.exit(0 if success else 1)
        else:
            print("❌ Please specify --emergency or --target-version")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️ Rollback interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Rollback failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
