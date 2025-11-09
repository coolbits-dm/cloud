#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cbLM Reference Updater
COOL BITS SRL - Internal Secret

Updates all cbLM references to point to the new cblm directory structure
and prepares for future DNS integration (cblm.ai)
"""

import os
import re
import json
from datetime import datetime
from typing import List, Dict, Any


class CBLMReferenceUpdater:
    """Updates all cbLM references in the project"""

    def __init__(self):
        self.project_root = os.getcwd()
        self.cblm_path = os.path.join(self.project_root, "cblm")
        self.cblm_ai_domain = "cblm.ai"  # Future DNS
        self.coolbits_ai_domain = "coolbits.ai"

        # Files to update
        self.files_to_update = [
            "str.py",
            "policy_names_audit.py",
            "cblm_economy_cbt_policy_update.py",
            "ogemini_cli_cblm_ai_deployment_prompt.py",
            "ogemini_cli_complete_cblm_policies.py",
            "cblm_ai_official_registration.py",
            "cblm_ai_organization_policies.py",
        ]

        # Reference patterns to update
        self.reference_patterns = {
            # Directory references
            r"cblm/": "cblm/",
            r"cbLM/": "cblm/",
            r"CBLM/": "cblm/",
            # Domain references (for future DNS)
            r"cblm\.ai": "cblm.ai",
            r"cbLM\.ai": "cblm.ai",
            r"CBLM\.ai": "cblm.ai",
            # Path references
            r"coolbits\.ai/cblm": "coolbits.ai/cblm",
            r"coolbits\.ai/cbLM": "coolbits.ai/cblm",
            r"coolbits\.ai/CBLM": "coolbits.ai/cblm",
            # Policy references
            r"cblm\.ai/policy": "cblm.ai/policy",
            r"cblm\.ai/policy-manager": "cblm.ai/policy-manager",
            r"cbLM\.ai/policy": "cblm.ai/policy",
            r"cbLM\.ai/policy-manager": "cblm.ai/policy-manager",
        }

    def find_cblm_references(self, file_path: str) -> List[Dict[str, Any]]:
        """Find all cbLM references in a file"""
        references = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

                for line_num, line in enumerate(lines, 1):
                    # Check for various cbLM patterns
                    patterns = [r"cbLM", r"CBLM", r"cblm\.ai", r"cbLM\.ai", r"CBLM\.ai"]

                    for pattern in patterns:
                        matches = re.finditer(pattern, line, re.IGNORECASE)
                        for match in matches:
                            references.append(
                                {
                                    "file": file_path,
                                    "line": line_num,
                                    "content": line.strip(),
                                    "match": match.group(),
                                    "position": match.span(),
                                }
                            )

        except Exception as e:
            print(f"Error reading {file_path}: {e}")

        return references

    def update_file_references(self, file_path: str) -> Dict[str, Any]:
        """Update cbLM references in a file"""
        result = {"file": file_path, "updated": False, "changes": [], "error": None}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Apply reference patterns
            for pattern, replacement in self.reference_patterns.items():
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    result["changes"].append(
                        {
                            "pattern": pattern,
                            "replacement": replacement,
                            "matches": len(re.findall(pattern, content)),
                        }
                    )
                    content = new_content

            # Write updated content if changes were made
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                result["updated"] = True

        except Exception as e:
            result["error"] = str(e)

        return result

    def scan_all_files(self) -> Dict[str, Any]:
        """Scan all files for cbLM references"""
        scan_results = {
            "timestamp": datetime.now().isoformat(),
            "project_root": self.project_root,
            "cblm_path": self.cblm_path,
            "files_scanned": 0,
            "total_references": 0,
            "files_with_references": [],
            "references_by_file": {},
        }

        # Scan specified files
        for file_name in self.files_to_update:
            file_path = os.path.join(self.project_root, file_name)
            if os.path.exists(file_path):
                references = self.find_cblm_references(file_path)
                scan_results["files_scanned"] += 1
                scan_results["total_references"] += len(references)

                if references:
                    scan_results["files_with_references"].append(file_name)
                    scan_results["references_by_file"][file_name] = references

        return scan_results

    def update_all_files(self) -> Dict[str, Any]:
        """Update all files with cbLM references"""
        update_results = {
            "timestamp": datetime.now().isoformat(),
            "files_processed": 0,
            "files_updated": 0,
            "total_changes": 0,
            "results": [],
        }

        for file_name in self.files_to_update:
            file_path = os.path.join(self.project_root, file_name)
            if os.path.exists(file_path):
                result = self.update_file_references(file_path)
                update_results["files_processed"] += 1
                update_results["results"].append(result)

                if result["updated"]:
                    update_results["files_updated"] += 1
                    update_results["total_changes"] += len(result["changes"])

        return update_results

    def create_update_report(self) -> str:
        """Create comprehensive update report"""
        scan_results = self.scan_all_files()
        update_results = self.update_all_files()

        report = {
            "cblm_reference_update_report": {
                "timestamp": datetime.now().isoformat(),
                "company": "COOL BITS SRL",
                "ceo": "Andrei",
                "ai_assistant": "oCursor",
                "classification": "Internal Secret - CoolBits.ai Members Only",
            },
            "scan_results": scan_results,
            "update_results": update_results,
            "summary": {
                "files_scanned": scan_results["files_scanned"],
                "total_references_found": scan_results["total_references"],
                "files_updated": update_results["files_updated"],
                "total_changes_made": update_results["total_changes"],
            },
        }

        report_file = os.path.join(self.cblm_path, "cblm_reference_update_report.json")
        try:
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            return report_file
        except Exception as e:
            print(f"Error saving report: {e}")
            return ""

    def print_status(self):
        """Print update status to console"""
        print("=" * 80)
        print("🔄 CBLM REFERENCE UPDATE STATUS")
        print("=" * 80)
        print(f"Project Root: {self.project_root}")
        print(f"cbLM Path: {self.cblm_path}")
        print(f"Future Domain: {self.cblm_ai_domain}")
        print(f"Current Domain: {self.coolbits_ai_domain}")
        print("=" * 80)

        scan_results = self.scan_all_files()
        print(f"Files Scanned: {scan_results['files_scanned']}")
        print(f"Total References Found: {scan_results['total_references']}")
        print(f"Files with References: {len(scan_results['files_with_references'])}")

        if scan_results["files_with_references"]:
            print("\n📋 Files with cbLM References:")
            for file_name in scan_results["files_with_references"]:
                ref_count = len(scan_results["references_by_file"][file_name])
                print(f"  • {file_name}: {ref_count} references")

        print("\n🔒 Classification: Internal Secret - CoolBits.ai Members Only")
        print("=" * 80)


def main():
    """Main function to run cbLM reference update"""
    print("🔄 Starting cbLM Reference Update...")

    updater = CBLMReferenceUpdater()

    # Print current status
    updater.print_status()

    # Update all files
    print("\n📝 Updating files...")
    update_results = updater.update_all_files()

    print(f"✅ Processed {update_results['files_processed']} files")
    print(f"✅ Updated {update_results['files_updated']} files")
    print(f"✅ Made {update_results['total_changes']} total changes")

    # Create report
    report_file = updater.create_update_report()
    if report_file:
        print(f"📊 Update report saved: {report_file}")

    print("\n🎯 cbLM Reference Update Complete!")
    print("🔒 Classification: Internal Secret - CoolBits.ai Members Only")


if __name__ == "__main__":
    main()
