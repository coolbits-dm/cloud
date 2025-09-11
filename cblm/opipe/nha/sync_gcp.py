# CoolBits.ai NHA Registry - Google Cloud IAM Synchronization
# Syncs NHA registry with Google Cloud IAM permissions

import sys
import json
import yaml
import subprocess
import argparse
from pathlib import Path
from registry import load_yaml

def run_gcloud_command(cmd, dry_run=False):
    """Run gcloud command with error handling"""
    if dry_run:
        print(f"[DRY RUN] Would execute: {' '.join(cmd)}")
        return True, "Dry run - no actual changes"
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def create_service_account(nha_id, project_id, dry_run=False):
    """Create service account for NHA"""
    sa_name = nha_id.replace("nha:", "").replace("-", "")
    sa_email = f"{sa_name}@{project_id}.iam.gserviceaccount.com"
    
    cmd = [
        "gcloud", "iam", "service-accounts", "create", sa_name,
        "--project", project_id,
        "--display-name", f"NHA Agent: {nha_id}",
        "--description", f"Service account for NHA agent {nha_id}"
    ]
    
    success, output = run_gcloud_command(cmd, dry_run)
    if success:
        print(f"✅ Service account created: {sa_email}")
        return sa_email
    else:
        if "already exists" in output:
            print(f"ℹ️  Service account already exists: {sa_email}")
            return sa_email
        else:
            print(f"❌ Failed to create service account: {output}")
            return None

def apply_iam_permissions(sa_email, permissions, project_id, dry_run=False):
    """Apply IAM permissions to service account"""
    applied_permissions = []
    failed_permissions = []
    
    for permission in permissions:
        cmd = [
            "gcloud", "projects", "add-iam-policy-binding", project_id,
            "--member", f"serviceAccount:{sa_email}",
            "--role", permission
        ]
        
        success, output = run_gcloud_command(cmd, dry_run)
        if success:
            applied_permissions.append(permission)
            print(f"✅ Applied permission: {permission}")
        else:
            failed_permissions.append(permission)
            print(f"❌ Failed to apply permission {permission}: {output}")
    
    return applied_permissions, failed_permissions

def sync_nha_with_gcp(nha, project_id, dry_run=False):
    """Sync individual NHA with Google Cloud"""
    print(f"\n🔄 Syncing NHA: {nha.name} ({nha.id})")
    
    # Create service account
    sa_email = create_service_account(nha.id, project_id, dry_run)
    if not sa_email:
        return False
    
    # Apply permissions
    if nha.permissions:
        applied, failed = apply_iam_permissions(sa_email, nha.permissions, project_id, dry_run)
        
        if failed:
            print(f"⚠️  Some permissions failed for {nha.name}: {failed}")
            return False
        else:
            print(f"✅ All permissions applied for {nha.name}")
    
    return True

def validate_iam_policies():
    """Validate IAM policies against minimum requirements"""
    try:
        # Load IAM minimum policies
        with open("cblm/opipe/nha/policies/iam_minimum.yaml", "r", encoding="utf-8") as f:
            iam_policies = yaml.safe_load(f)
        
        reg = load_yaml("cblm/opipe/nha/agents.yaml")
        
        errors = []
        
        for nha in reg.nhas:
            category = nha.category
            if category in iam_policies:
                allowed_permissions = iam_policies[category]
                
                for permission in nha.permissions:
                    if permission not in allowed_permissions:
                        errors.append(f"NHA {nha.name} has unauthorized permission {permission} for category {category}")
        
        if errors:
            print("❌ IAM policy validation failed:")
            for error in errors:
                print(f"   - {error}")
            return False
        
        print("✅ IAM policy validation passed")
        return True
        
    except FileNotFoundError:
        print("⚠️  IAM minimum policies file not found - skipping validation")
        return True
    except Exception as e:
        print(f"❌ IAM policy validation error: {e}")
        return False

def generate_sync_report(sync_results, dry_run=False):
    """Generate synchronization report"""
    report = {
        "timestamp": str(Path(__file__).stat().st_mtime),
        "dry_run": dry_run,
        "total_nhas": len(sync_results),
        "successful": sum(1 for result in sync_results.values() if result),
        "failed": sum(1 for result in sync_results.values() if not result),
        "results": sync_results
    }
    
    report_file = "cblm/opipe/nha/out/sync_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"📊 Sync report saved to: {report_file}")
    return report

def main():
    """Main synchronization function"""
    parser = argparse.ArgumentParser(description="Sync NHA registry with Google Cloud IAM")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run without making changes")
    parser.add_argument("--apply", action="store_true", help="Apply changes to Google Cloud")
    parser.add_argument("--project", default="coolbits-ai", help="Google Cloud project ID")
    parser.add_argument("--validate-only", action="store_true", help="Only validate IAM policies")
    
    args = parser.parse_args()
    
    if args.validate_only:
        print("🔍 Validating IAM policies...")
        success = validate_iam_policies()
        sys.exit(0 if success else 1)
    
    if not args.dry_run and not args.apply:
        print("❌ Please specify either --dry-run or --apply")
        sys.exit(1)
    
    print("🔄 NHA Registry Google Cloud Synchronization")
    print("=" * 60)
    print(f"Project: {args.project}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'APPLY'}")
    print("=" * 60)
    
    try:
        # Load registry
        reg = load_yaml("cblm/opipe/nha/agents.yaml")
        
        # Validate IAM policies first
        if not validate_iam_policies():
            print("❌ IAM policy validation failed - aborting sync")
            sys.exit(1)
        
        # Sync each NHA
        sync_results = {}
        
        for nha in reg.nhas:
            if nha.status == "active":  # Only sync active NHAs
                success = sync_nha_with_gcp(nha, args.project, args.dry_run)
                sync_results[nha.id] = success
        
        # Generate report
        report = generate_sync_report(sync_results, args.dry_run)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Synchronization Summary:")
        print(f"   Total NHAs: {report['total_nhas']}")
        print(f"   Successful: {report['successful']}")
        print(f"   Failed: {report['failed']}")
        
        if report['failed'] > 0:
            print("\n❌ Some synchronizations failed:")
            for nha_id, success in sync_results.items():
                if not success:
                    print(f"   - {nha_id}")
        
        if args.dry_run:
            print("\n💡 This was a dry run. Use --apply to make actual changes.")
        
        success = report['failed'] == 0
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"❌ Synchronization error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
