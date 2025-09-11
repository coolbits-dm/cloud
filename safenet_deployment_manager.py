#!/usr/bin/env python3
"""
SafeNet Integration Deployment Script - COOL BITS SRL
Automated deployment script for SafeNet Authentication Client integration
"""

import os
import sys
import json
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SafeNetDeploymentManager:
    """SafeNet Deployment Manager for COOL BITS SRL"""

    def __init__(self):
        self.company_name = "COOL BITS S.R.L."
        self.company_cui = "42331573"
        self.company_registration = "ROONRC.J22/676/2020"
        self.workspace_path = Path.cwd()

        # Deployment configuration
        self.deployment_config = {
            "safenet_version": "12.0.0",
            "installation_path": self.workspace_path / "safenet",
            "certificates_path": self.workspace_path / "safenet" / "certificates",
            "logs_path": self.workspace_path / "safenet" / "logs",
            "backup_path": self.workspace_path / "safenet" / "backup",
            "api_port": 5001,
            "api_host": "0.0.0.0",
        }

        logger.info(f"SafeNet Deployment Manager initialized for {self.company_name}")

    def check_prerequisites(self) -> bool:
        """Check system prerequisites for SafeNet deployment"""
        logger.info("🔍 Checking system prerequisites...")

        prerequisites = {
            "python_version": sys.version_info >= (3, 8),
            "workspace_writable": os.access(self.workspace_path, os.W_OK),
            "company_config_exists": (
                self.workspace_path / "coolbits_srl_complete_details.json"
            ).exists(),
            "required_modules": self._check_required_modules(),
        }

        all_prerequisites_met = all(prerequisites.values())

        logger.info("Prerequisites check results:")
        for check, result in prerequisites.items():
            status = "✅" if result else "❌"
            logger.info(f"  {status} {check}: {result}")

        if not all_prerequisites_met:
            logger.error("❌ Prerequisites not met. Please fix the issues above.")
            return False

        logger.info("✅ All prerequisites met!")
        return True

    def _check_required_modules(self) -> bool:
        """Check if required Python modules are available"""
        required_modules = [
            "flask",
            "flask_cors",
            "json",
            "datetime",
            "hashlib",
            "hmac",
        ]

        missing_modules = []
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)

        if missing_modules:
            logger.error(f"Missing modules: {', '.join(missing_modules)}")
            return False

        return True

    def create_directory_structure(self) -> bool:
        """Create SafeNet directory structure"""
        logger.info("📁 Creating directory structure...")

        directories = [
            self.deployment_config["installation_path"],
            self.deployment_config["certificates_path"],
            self.deployment_config["logs_path"],
            self.deployment_config["backup_path"],
            self.workspace_path / "safenet" / "temp",
            self.workspace_path / "safenet" / "config",
        ]

        try:
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"  ✅ Created: {directory}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to create directories: {e}")
            return False

    def install_python_dependencies(self) -> bool:
        """Install Python dependencies"""
        logger.info("📦 Installing Python dependencies...")

        dependencies = ["flask>=2.0.0", "flask-cors>=3.0.0", "requests>=2.25.0"]

        try:
            for dependency in dependencies:
                logger.info(f"  Installing {dependency}...")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", dependency],
                    capture_output=True,
                    text=True,
                )

                if result.returncode != 0:
                    logger.error(f"❌ Failed to install {dependency}: {result.stderr}")
                    return False

                logger.info(f"  ✅ Installed {dependency}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to install dependencies: {e}")
            return False

    def create_configuration_files(self) -> bool:
        """Create configuration files"""
        logger.info("⚙️ Creating configuration files...")

        try:
            # Create SafeNet configuration
            safenet_config = {
                "company_info": {
                    "name": self.company_name,
                    "cui": self.company_cui,
                    "registration": self.company_registration,
                    "address": "str. Columnei, nr.14, bl.K4, et.4, ap.19, Iași, România",
                },
                "safenet_settings": {
                    "version": self.deployment_config["safenet_version"],
                    "installation_path": str(
                        self.deployment_config["installation_path"]
                    ),
                    "certificates_path": str(
                        self.deployment_config["certificates_path"]
                    ),
                    "logs_path": str(self.deployment_config["logs_path"]),
                    "backup_path": str(self.deployment_config["backup_path"]),
                },
                "api_settings": {
                    "host": self.deployment_config["api_host"],
                    "port": self.deployment_config["api_port"],
                    "debug": False,
                    "ssl_enabled": True,
                },
                "security_settings": {
                    "default_security_level": "L3",
                    "certificate_expiry_days": 365,
                    "audit_retention_days": 2555,  # 7 years
                    "password_min_length": 12,
                },
                "deployment_info": {
                    "deployed_at": datetime.now().isoformat(),
                    "deployed_by": "SafeNet Deployment Manager",
                    "environment": "production",
                },
            }

            config_file = (
                self.deployment_config["installation_path"] / "safenet_config.json"
            )
            with open(config_file, "w") as f:
                json.dump(safenet_config, f, indent=2)

            logger.info(f"  ✅ Created: {config_file}")

            # Create environment file
            env_content = f"""# SafeNet Environment Configuration - COOL BITS S.R.L.
# Generated on: {datetime.now().isoformat()}

# Company Information
COMPANY_NAME={self.company_name}
COMPANY_CUI={self.company_cui}
COMPANY_REGISTRATION={self.company_registration}

# SafeNet Paths
SAFENET_INSTALLATION_PATH={self.deployment_config["installation_path"]}
SAFENET_CERTIFICATES_PATH={self.deployment_config["certificates_path"]}
SAFENET_LOGS_PATH={self.deployment_config["logs_path"]}
SAFENET_BACKUP_PATH={self.deployment_config["backup_path"]}

# API Configuration
SAFENET_API_HOST={self.deployment_config["api_host"]}
SAFENET_API_PORT={self.deployment_config["api_port"]}

# Security Settings
SAFENET_DEFAULT_SECURITY_LEVEL=L3
SAFENET_CERTIFICATE_EXPIRY_DAYS=365
SAFENET_AUDIT_RETENTION_DAYS=2555
SAFENET_PASSWORD_MIN_LENGTH=12

# Logging
SAFENET_LOG_LEVEL=INFO
SAFENET_LOG_FILE=safenet.log
"""

            env_file = self.deployment_config["installation_path"] / ".env"
            with open(env_file, "w") as f:
                f.write(env_content)

            logger.info(f"  ✅ Created: {env_file}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to create configuration files: {e}")
            return False

    def create_startup_scripts(self) -> bool:
        """Create startup scripts"""
        logger.info("🚀 Creating startup scripts...")

        try:
            # Create Windows batch script
            windows_script = f"""@echo off
echo Starting SafeNet Authentication Client API Server - COOL BITS S.R.L.
echo Company CUI: {self.company_cui}
echo Company Registration: {self.company_registration}
echo.

cd /d "{self.workspace_path}"

echo Starting SafeNet API server on port {self.deployment_config["api_port"]}...
python safenet_api_integration.py

pause
"""

            windows_file = self.workspace_path / "start_safenet_api.bat"
            with open(windows_file, "w") as f:
                f.write(windows_script)

            logger.info(f"  ✅ Created: {windows_file}")

            # Create Linux/Mac shell script
            linux_script = f"""#!/bin/bash
echo "Starting SafeNet Authentication Client API Server - COOL BITS S.R.L."
echo "Company CUI: {self.company_cui}"
echo "Company Registration: {self.company_registration}"
echo ""

cd "{self.workspace_path}"

echo "Starting SafeNet API server on port {self.deployment_config["api_port"]}..."
python3 safenet_api_integration.py
"""

            linux_file = self.workspace_path / "start_safenet_api.sh"
            with open(linux_file, "w") as f:
                f.write(linux_script)

            # Make Linux script executable
            os.chmod(linux_file, 0o755)

            logger.info(f"  ✅ Created: {linux_file}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to create startup scripts: {e}")
            return False

    def create_service_scripts(self) -> bool:
        """Create service management scripts"""
        logger.info("🔧 Creating service management scripts...")

        try:
            # Create service installation script
            service_script = f"""@echo off
echo Installing SafeNet Authentication Client as Windows Service - COOL BITS S.R.L.
echo Company CUI: {self.company_cui}
echo.

REM Install Python service dependencies
pip install pywin32

REM Create service installation script
echo Creating service installation script...
(
echo import win32serviceutil
echo import win32service
echo import win32event
echo import servicemanager
echo import socket
echo import time
echo import sys
echo import os
echo.
echo class SafeNetService^(win32serviceutil.ServiceFramework^):
echo     _svc_name_ = "SafeNetAPIService"
echo     _svc_display_name_ = "SafeNet Authentication Client API - COOL BITS S.R.L."
echo     _svc_description_ = "SafeNet Authentication Client API Service for COOL BITS S.R.L."
echo.
echo     def __init__^(self, args^):
echo         win32serviceutil.ServiceFramework.__init__^(self, args^)
echo         self.hWaitStop = win32event.CreateEvent^(None, 0, 0, None^)
echo         socket.setdefaulttimeout^(60^)
echo.
echo     def SvcStop^(self^):
echo         self.ReportServiceStatus^(win32service.SERVICE_STOP_PENDING^)
echo         win32event.SetEvent^(self.hWaitStop^)
echo.
echo     def SvcDoRun^(self^):
echo         servicemanager.LogMsg^(servicemanager.EVENTLOG_INFORMATION_TYPE,
echo                               servicemanager.PYS_SERVICE_STARTED,
echo                               ^(self._svc_name_, ''^)^)
echo         self.main^(^)
echo.
echo     def main^(self^):
echo         os.chdir^('{self.workspace_path}'^)
echo         os.system^('python safenet_api_integration.py'^)
echo.
echo if __name__ == '__main__':
echo     win32serviceutil.HandleCommandLine^(SafeNetService^)
) > install_safenet_service.py

echo Service installation script created.
echo To install the service, run: python install_safenet_service.py install
echo To start the service, run: python install_safenet_service.py start
echo To stop the service, run: python install_safenet_service.py stop
echo To remove the service, run: python install_safenet_service.py remove

pause
"""

            service_file = self.workspace_path / "install_safenet_service.bat"
            with open(service_file, "w") as f:
                f.write(service_script)

            logger.info(f"  ✅ Created: {service_file}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to create service scripts: {e}")
            return False

    def run_tests(self) -> bool:
        """Run SafeNet integration tests"""
        logger.info("🧪 Running SafeNet integration tests...")

        try:
            result = subprocess.run(
                [sys.executable, "safenet_testing_suite.py"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                logger.info("✅ All tests passed!")
                return True
            else:
                logger.error(f"❌ Tests failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to run tests: {e}")
            return False

    def create_deployment_report(self) -> bool:
        """Create deployment report"""
        logger.info("📊 Creating deployment report...")

        try:
            report = {
                "deployment_info": {
                    "company_name": self.company_name,
                    "company_cui": self.company_cui,
                    "company_registration": self.company_registration,
                    "deployment_date": datetime.now().isoformat(),
                    "deployment_version": self.deployment_config["safenet_version"],
                    "workspace_path": str(self.workspace_path),
                },
                "deployment_config": self.deployment_config,
                "installed_components": [
                    "SafeNet Integration Architecture",
                    "SafeNet API Integration Layer",
                    "SafeNet Security Policies",
                    "SafeNet Testing Suite",
                    "SafeNet Deployment Scripts",
                ],
                "api_endpoints": [
                    "GET /api/safenet/status",
                    "GET /api/safenet/certificates",
                    "POST /api/safenet/certificates",
                    "GET /api/safenet/certificates/<id>/status",
                    "POST /api/safenet/sign",
                    "POST /api/safenet/verify",
                    "GET /api/safenet/signing-history",
                    "GET /api/safenet/compliance-report",
                    "GET /api/safenet/audit-trail",
                    "POST /api/safenet/install",
                ],
                "security_features": [
                    "Multi-level certificate management",
                    "Digital document signing",
                    "Signature verification",
                    "Comprehensive audit trails",
                    "Security policy enforcement",
                    "Compliance reporting",
                ],
                "next_steps": [
                    "Install THALES SafeNet Authentication Client",
                    "Configure certificate authorities",
                    "Set up SSL/TLS certificates",
                    "Configure firewall rules",
                    "Train users on digital signing procedures",
                    "Schedule regular security reviews",
                ],
            }

            report_file = self.workspace_path / "safenet_deployment_report.json"
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)

            logger.info(f"  ✅ Created: {report_file}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to create deployment report: {e}")
            return False

    def deploy(self) -> bool:
        """Deploy SafeNet integration"""
        logger.info("🚀 Starting SafeNet deployment for COOL BITS S.R.L.")
        logger.info("=" * 60)

        deployment_steps = [
            ("Check Prerequisites", self.check_prerequisites),
            ("Create Directory Structure", self.create_directory_structure),
            ("Install Python Dependencies", self.install_python_dependencies),
            ("Create Configuration Files", self.create_configuration_files),
            ("Create Startup Scripts", self.create_startup_scripts),
            ("Create Service Scripts", self.create_service_scripts),
            ("Run Integration Tests", self.run_tests),
            ("Create Deployment Report", self.create_deployment_report),
        ]

        for step_name, step_function in deployment_steps:
            logger.info(f"\n📋 {step_name}...")

            if not step_function():
                logger.error(f"❌ Deployment failed at step: {step_name}")
                return False

            logger.info(f"✅ {step_name} completed successfully")

        logger.info("\n" + "=" * 60)
        logger.info("🎉 SafeNet deployment completed successfully!")
        logger.info(f"Company: {self.company_name}")
        logger.info(f"CUI: {self.company_cui}")
        logger.info(f"Registration: {self.company_registration}")
        logger.info(
            f"API Server: http://{self.deployment_config['api_host']}:{self.deployment_config['api_port']}"
        )

        return True


def main():
    """Main deployment function"""
    print("🔐 SafeNet Authentication Client Deployment")
    print("=" * 60)
    print("Company: COOL BITS S.R.L.")
    print("CUI: 42331573")
    print("Registration: ROONRC.J22/676/2020")
    print("=" * 60)

    deployment_manager = SafeNetDeploymentManager()

    if deployment_manager.deploy():
        print("\n✅ Deployment completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Install THALES SafeNet Authentication Client")
        print("2. Configure certificate authorities")
        print("3. Start the API server using start_safenet_api.bat")
        print("4. Test the integration using the API endpoints")
        print("5. Train users on digital signing procedures")

        return 0
    else:
        print("\n❌ Deployment failed!")
        print("Please check the logs above for error details.")

        return 1


if __name__ == "__main__":
    sys.exit(main())
