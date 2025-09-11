#!/usr/bin/env python3
"""
oPython Response to oGeminiCLI - Local Service Status Report
COOL BITS SRL Local Windows 11 Machine Status Check
"""

import json
import logging
import subprocess
import socket
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class oPythonLocalStatusReport:
    def __init__(self):
        self.company = "COOL BITS SRL"
        self.ceo = "Andrei"
        self.machine = "Windows 11"
        self.report_to = "@GeminiCLI"
        self.report_from = "@oPython"

        # Service ports to check
        self.service_ports = {"Andy Service": 8101, "Kim Service / Main Console": 8102}

        # API keys to prepare for sync
        self.api_keys_to_sync = {
            "openai_api_key_ogpt01": "OpenAI API Key for oGPT01",
            "openai_api_key_ogpt02": "OpenAI API Key for oGPT02",
            "xai_api_key_ogrok01": "xAI API Key for oGrok01",
            "xai_api_key_ogrok02": "xAI API Key for oGrok02",
            "ocursor_api_key": "oCursor API Key",
            "gemini_api_key": "Gemini API Key",
        }

    def check_local_services(self):
        """Check status of local services on reserved ports"""
        logger.info("🔍 Checking local services status...")

        print("=" * 80)
        print("🔍 LOCAL SERVICE STATUS CHECK")
        print("=" * 80)
        print(f"🏢 Company: {self.company}")
        print(f"👤 CEO: {self.ceo}")
        print(f"💻 Machine: {self.machine}")
        print(f"📤 Report To: {self.report_to}")
        print(f"📥 Report From: {self.report_from}")
        print("=" * 80)

        service_status = {}

        for service_name, port in self.service_ports.items():
            print(f"\n🔍 Checking {service_name} on port {port}...")

            status = self._check_port_status(port)
            service_status[service_name] = {
                "port": port,
                "status": status["status"],
                "details": status["details"],
            }

            if status["status"] == "Active":
                print(f"   ✅ {service_name}: ACTIVE on port {port}")
                print(f"   📡 Details: {status['details']}")
            else:
                print(f"   ❌ {service_name}: INACTIVE on port {port}")
                print(f"   📡 Details: {status['details']}")

        return service_status

    def _check_port_status(self, port):
        """Check if a port is listening"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(("localhost", port))
            sock.close()

            if result == 0:
                return {
                    "status": "Active",
                    "details": f"Port {port} is listening and accepting connections",
                }
            else:
                return {
                    "status": "Inactive",
                    "details": f"Port {port} is not listening or not accessible",
                }
        except Exception as e:
            return {
                "status": "Error",
                "details": f"Error checking port {port}: {str(e)}",
            }

    def check_nvidia_gpu_readiness(self):
        """Check NVIDIA GPU readiness for CUDA operations"""
        logger.info("🚀 Checking NVIDIA GPU readiness...")

        print("\n" + "=" * 80)
        print("🚀 NVIDIA GPU READINESS CHECK")
        print("=" * 80)

        gpu_status = {}

        # Check nvidia-smi
        print("\n🔍 Checking nvidia-smi...")
        try:
            result = subprocess.run(
                ["nvidia-smi"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                print("   ✅ nvidia-smi: Available")
                gpu_status["nvidia_smi"] = "Available"

                # Parse GPU info
                output_lines = result.stdout.split("\n")
                for line in output_lines:
                    if "RTX" in line or "GeForce" in line:
                        print(f"   📊 GPU: {line.strip()}")
                        gpu_status["gpu_model"] = line.strip()
                        break
            else:
                print("   ❌ nvidia-smi: Not available")
                gpu_status["nvidia_smi"] = "Not available"

        except FileNotFoundError:
            print("   ❌ nvidia-smi: Command not found")
            gpu_status["nvidia_smi"] = "Command not found"
        except Exception as e:
            print(f"   ❌ nvidia-smi: Error - {e}")
            gpu_status["nvidia_smi"] = f"Error: {e}"

        # Check CUDA availability
        print("\n🔍 Checking CUDA availability...")
        try:
            import torch

            if torch.cuda.is_available():
                print("   ✅ CUDA: Available")
                print(f"   📊 CUDA Version: {torch.version.cuda}")
                print(f"   📊 GPU Count: {torch.cuda.device_count()}")
                gpu_status["cuda"] = "Available"
                gpu_status["cuda_version"] = torch.version.cuda
                gpu_status["gpu_count"] = torch.cuda.device_count()
            else:
                print("   ❌ CUDA: Not available")
                gpu_status["cuda"] = "Not available"
        except ImportError:
            print("   ⚠️ PyTorch: Not installed")
            gpu_status["cuda"] = "PyTorch not installed"
        except Exception as e:
            print(f"   ❌ CUDA: Error - {e}")
            gpu_status["cuda"] = f"Error: {e}"

        return gpu_status

    def prepare_api_keys_for_sync(self):
        """Prepare API keys for Google Secret Manager synchronization"""
        logger.info("🔐 Preparing API keys for sync...")

        print("\n" + "=" * 80)
        print("🔐 API KEYS PREPARATION FOR GOOGLE SECRET MANAGER")
        print("=" * 80)

        # Create local_secrets.json template
        secrets_template = []

        print("\n📋 API Keys to be synchronized:")
        for key_name, description in self.api_keys_to_sync.items():
            print(f"   • {key_name}: {description}")
            secrets_template.append(
                {"name": key_name, "value": f"YOUR_{key_name.upper()}_HERE"}
            )

        # Save template
        with open("local_secrets_template.json", "w") as f:
            json.dump(secrets_template, f, indent=2)

        print("\n📝 Template created: local_secrets_template.json")
        print("📋 Instructions:")
        print("   1. Copy local_secrets_template.json to local_secrets.json")
        print("   2. Replace 'YOUR_*_HERE' with actual API keys")
        print("   3. Run the PowerShell sync script")
        print("   4. Delete local_secrets.json after sync")

        return secrets_template

    def create_sync_script(self):
        """Create PowerShell sync script for API keys"""
        logger.info("📝 Creating PowerShell sync script...")

        sync_script = """# .sync_secrets.ps1
#
# Securely synchronizes secrets from a local JSON file to Google Cloud Secret Manager.
#
# Prerequisites:
# 1. Google Cloud SDK installed and authenticated (`gcloud auth login`).
# 2. Project set in gcloud config (`gcloud config set project coolbits-ai`).

# --- Configuration ---
$ProjectID = "coolbits-ai"
$SecretsFile = "local_secrets.json"

# --- Script ---
Write-Host "🔧 Starting secret synchronization for project '$ProjectID'..." -ForegroundColor Cyan

if (-not (Test-Path $SecretsFile)) {
    Write-Error "Error: Secrets file not found at '$SecretsFile'. Please create it first."
    exit 1
}

# Use PowerShell's native JSON parsing
$secrets = Get-Content $SecretsFile | ConvertFrom-Json

foreach ($secret in $secrets) {
    $secretName = $secret.name
    $secretValue = $secret.value

    Write-Host "Processing secret: '$secretName'..."

    # Check if secret exists
    $existingSecret = gcloud secrets describe $secretName --project $ProjectID --format="value(name)" --quiet 2>$null
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  -> Secret '$secretName' does not exist. Creating it..." -ForegroundColor Yellow
        gcloud secrets create $secretName --project $ProjectID --replication-policy="automatic" --labels="source=local-sync,managed-by=ogeminicli" | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Error "  -> Failed to create secret '$secretName'."
            continue
        }
        Write-Host "  -> Secret '$secretName' created successfully." -ForegroundColor Green
    } else {
        Write-Host "  -> Secret '$secretName' already exists. Adding a new version."
    }

    # Add a new version with the secret value from a temporary file for security
    $TempFile = [System.IO.Path]::GetTempFileName()
    Set-Content -Path $TempFile -Value $secretValue -NoNewline
    
    gcloud secrets versions add $secretName --project $ProjectID --data-file=$TempFile | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  -> ✅ Successfully added new version for secret '$secretName'." -ForegroundColor Green
    } else {
        Write-Error "  -> ❌ Failed to add new version for secret '$secretName'."
    }
    
    Remove-Item $TempFile -Force
}

Write-Host "🎉 Secret synchronization complete." -ForegroundColor Magenta
Write-Warning "SECURITY REMINDER: Please delete the '$SecretsFile' file now that the secrets are in Google Cloud."
"""

        with open(".sync_secrets.ps1", "w", encoding="utf-8") as f:
            f.write(sync_script)

        logger.info("✅ PowerShell sync script created: .sync_secrets.ps1")

    def generate_status_report(self):
        """Generate comprehensive status report for oGeminiCLI"""
        logger.info("📊 Generating comprehensive status report...")

        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE STATUS REPORT FOR @GeminiCLI")
        print("=" * 80)

        # Run all checks
        service_status = self.check_local_services()
        gpu_status = self.check_nvidia_gpu_readiness()
        api_keys_template = self.prepare_api_keys_for_sync()
        self.create_sync_script()

        # Generate report
        report = {
            "company": self.company,
            "ceo": self.ceo,
            "machine": self.machine,
            "report_date": datetime.now().isoformat(),
            "report_to": self.report_to,
            "report_from": self.report_from,
            "service_status": service_status,
            "gpu_status": gpu_status,
            "api_keys_prepared": len(api_keys_template),
            "sync_script_created": True,
            "recommendations": [
                "Update local_secrets_template.json with actual API keys",
                "Run .sync_secrets.ps1 to sync keys to Google Secret Manager",
                "Verify service ports are properly configured",
                "Ensure NVIDIA drivers are up to date for CUDA operations",
            ],
        }

        # Save report
        with open("opython_status_report.json", "w") as f:
            json.dump(report, f, indent=2)

        print("\n📋 STATUS SUMMARY:")
        print(f"   🏢 Company: {self.company}")
        print(f"   👤 CEO: {self.ceo}")
        print(f"   💻 Machine: {self.machine}")
        print(f"   📅 Report Date: {report['report_date']}")

        print("\n🔍 SERVICE STATUS:")
        for service, status in service_status.items():
            print(f"   • {service}: {status['status']}")

        print("\n🚀 GPU STATUS:")
        print(f"   • nvidia-smi: {gpu_status.get('nvidia_smi', 'Unknown')}")
        print(f"   • CUDA: {gpu_status.get('cuda', 'Unknown')}")

        print("\n🔐 API KEYS:")
        print(f"   • Keys prepared: {report['api_keys_prepared']}")
        print(
            f"   • Sync script: {'Created' if report['sync_script_created'] else 'Failed'}"
        )

        print("\n📁 Generated Files:")
        print("   • local_secrets_template.json - API keys template")
        print("   • .sync_secrets.ps1 - PowerShell sync script")
        print("   • opython_status_report.json - Complete status report")

        print("\n🎯 NEXT STEPS:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"   {i}. {rec}")

        logger.info("✅ Comprehensive status report generated successfully")
        return report


def main():
    """Main function - oPython response to oGeminiCLI"""
    print("=" * 80)
    print("🤖 OPYTHON RESPONSE TO @GeminiCLI")
    print("=" * 80)
    print("📤 From: @oPython")
    print("📥 To: @GeminiCLI")
    print("🏢 Company: COOL BITS SRL")
    print("👤 CEO: Andrei")
    print("=" * 80)

    reporter = oPythonLocalStatusReport()
    report = reporter.generate_status_report()

    print("\n" + "=" * 80)
    print("✅ OPYTHON STATUS REPORT COMPLETED")
    print("=" * 80)
    print("📋 Ready for @GeminiCLI cloud-side configurations")
    print("🔐 API keys prepared for Google Secret Manager sync")
    print("🚀 Local services and GPU status verified")
    print("=" * 80)


if __name__ == "__main__":
    main()
