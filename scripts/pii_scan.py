#!/usr/bin/env python3
"""
CoolBits.ai PII Scan Script
==========================

Scans codebase for personally identifiable information (PII) and sensitive data.
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import List, Dict


class PIIScanner:
    """PII and sensitive data scanner"""

    def __init__(self):
        self.pii_patterns = {
            # Email addresses
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            # Phone numbers (various formats)
            "phone": r"(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})",
            # Social Security Numbers
            "ssn": r"\b\d{3}-?\d{2}-?\d{4}\b",
            # Credit Card Numbers
            "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
            # IP Addresses
            "ip_address": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
            # Passwords (common patterns)
            "password": r'(password|passwd|pwd)\s*[:=]\s*["\']?[^"\'\s]+["\']?',
            # API Keys (common patterns)
            "api_key": r'(api[_-]?key|apikey|access[_-]?token|secret[_-]?key)\s*[:=]\s*["\']?[A-Za-z0-9+/=]{20,}["\']?',
            # Database connection strings
            "db_connection": r"(mongodb|mysql|postgresql|sqlite)://[^\s]+",
            # AWS credentials
            "aws_credentials": r'(aws[_-]?access[_-]?key[_-]?id|aws[_-]?secret[_-]?access[_-]?key)\s*[:=]\s*["\']?[A-Za-z0-9+/=]{20,}["\']?',
            # Google Cloud credentials
            "gcp_credentials": r'(google[_-]?application[_-]?credentials|gcp[_-]?key)\s*[:=]\s*["\']?[A-Za-z0-9+/=]{20,}["\']?',
            # JWT tokens
            "jwt_token": r"eyJ[A-Za-z0-9+/=]+\.[A-Za-z0-9+/=]+\.[A-Za-z0-9+/=]+",
            # Personal names (basic pattern)
            "personal_name": r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b",
        }

        self.excluded_dirs = {
            ".git",
            ".venv",
            "node_modules",
            "__pycache__",
            ".pytest_cache",
            "venv",
            "env",
            ".env",
            "dist",
            "build",
            "target",
            "bin",
            "obj",
        }

        self.excluded_files = {
            ".gitignore",
            ".gitattributes",
            "package-lock.json",
            "yarn.lock",
            "requirements.txt",
            "Pipfile.lock",
            "poetry.lock",
        }

        self.sensitive_extensions = {".env", ".key", ".pem", ".p12", ".pfx", ".jks"}

    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single file for PII and sensitive data"""
        findings = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                for pii_type, pattern in self.pii_patterns.items():
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        findings.append(
                            {
                                "file": str(file_path),
                                "line": line_num,
                                "type": pii_type,
                                "match": match.group(),
                                "context": line.strip(),
                                "severity": self._get_severity(pii_type),
                            }
                        )

            # Check for sensitive file extensions
            if file_path.suffix.lower() in self.sensitive_extensions:
                findings.append(
                    {
                        "file": str(file_path),
                        "line": 0,
                        "type": "sensitive_file",
                        "match": f"Sensitive file extension: {file_path.suffix}",
                        "context": "File with sensitive extension detected",
                        "severity": "high",
                    }
                )

        except Exception as e:
            findings.append(
                {
                    "file": str(file_path),
                    "line": 0,
                    "type": "scan_error",
                    "match": f"Error scanning file: {e}",
                    "context": "Failed to scan file",
                    "severity": "medium",
                }
            )

        return findings

    def _get_severity(self, pii_type: str) -> str:
        """Get severity level for PII type"""
        high_severity = {
            "email",
            "phone",
            "ssn",
            "credit_card",
            "password",
            "api_key",
            "aws_credentials",
            "gcp_credentials",
        }
        medium_severity = {"ip_address", "db_connection", "jwt_token"}
        low_severity = {"personal_name"}

        if pii_type in high_severity:
            return "high"
        elif pii_type in medium_severity:
            return "medium"
        else:
            return "low"

    def scan_directory(self, directory: Path) -> List[Dict]:
        """Scan directory recursively for PII and sensitive data"""
        all_findings = []

        for root, dirs, files in os.walk(directory):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in self.excluded_dirs]

            for file in files:
                file_path = Path(root) / file

                # Skip excluded files
                if file in self.excluded_files:
                    continue

                # Skip binary files
                if self._is_binary_file(file_path):
                    continue

                # Scan file
                findings = self.scan_file(file_path)
                all_findings.extend(findings)

        return all_findings

    def _is_binary_file(self, file_path: Path) -> bool:
        """Check if file is binary"""
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(1024)
                return b"\0" in chunk
        except:
            return True

    def generate_report(self, findings: List[Dict]) -> str:
        """Generate scan report"""
        if not findings:
            return "✅ No PII or sensitive data found in scan."

        # Group findings by severity
        high_findings = [f for f in findings if f["severity"] == "high"]
        medium_findings = [f for f in findings if f["severity"] == "medium"]
        low_findings = [f for f in findings if f["severity"] == "low"]

        report = []
        report.append("🔍 CoolBits.ai PII Scan Report")
        report.append("=" * 50)
        report.append(f"Total findings: {len(findings)}")
        report.append(f"High severity: {len(high_findings)}")
        report.append(f"Medium severity: {len(medium_findings)}")
        report.append(f"Low severity: {len(low_findings)}")
        report.append("")

        # High severity findings
        if high_findings:
            report.append("🚨 HIGH SEVERITY FINDINGS:")
            report.append("-" * 30)
            for finding in high_findings:
                report.append(f"File: {finding['file']}:{finding['line']}")
                report.append(f"Type: {finding['type']}")
                report.append(f"Match: {finding['match']}")
                report.append(f"Context: {finding['context']}")
                report.append("")

        # Medium severity findings
        if medium_findings:
            report.append("⚠️  MEDIUM SEVERITY FINDINGS:")
            report.append("-" * 30)
            for finding in medium_findings:
                report.append(f"File: {finding['file']}:{finding['line']}")
                report.append(f"Type: {finding['type']}")
                report.append(f"Match: {finding['match']}")
                report.append("")

        # Low severity findings
        if low_findings:
            report.append("ℹ️  LOW SEVERITY FINDINGS:")
            report.append("-" * 30)
            for finding in low_findings:
                report.append(f"File: {finding['file']}:{finding['line']}")
                report.append(f"Type: {finding['type']}")
                report.append("")

        return "\n".join(report)

    def save_report(self, findings: List[Dict], output_file: str):
        """Save scan report to file"""
        report = self.generate_report(findings)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report)

        # Also save JSON format
        json_file = output_file.replace(".txt", ".json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(findings, f, indent=2)


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Scan codebase for PII and sensitive data"
    )
    parser.add_argument(
        "--path", default=".", help="Path to scan (default: current directory)"
    )
    parser.add_argument(
        "--output", default="pii_scan_report.txt", help="Output file for report"
    )
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument(
        "--fail-on-high",
        action="store_true",
        help="Exit with error if high severity findings",
    )

    args = parser.parse_args()

    scanner = PIIScanner()
    scan_path = Path(args.path)

    print("🔍 Scanning for PII and sensitive data...")
    print(f"📁 Path: {scan_path}")
    print("")

    # Scan directory
    findings = scanner.scan_directory(scan_path)

    # Generate report
    report = scanner.generate_report(findings)
    print(report)

    # Save report
    scanner.save_report(findings, args.output)
    print(f"📄 Report saved to: {args.output}")

    # Check for high severity findings
    high_findings = [f for f in findings if f["severity"] == "high"]
    if high_findings and args.fail_on_high:
        print(f"\n❌ Found {len(high_findings)} high severity findings!")
        sys.exit(1)

    # Exit with appropriate code
    if findings:
        print(f"\n⚠️  Found {len(findings)} total findings")
        sys.exit(1)
    else:
        print("\n✅ No PII or sensitive data found!")
        sys.exit(0)


if __name__ == "__main__":
    main()
