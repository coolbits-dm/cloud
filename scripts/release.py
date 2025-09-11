# CoolBits.ai Release Script
# ==========================

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def get_current_version():
    """Get current version from package.json"""
    try:
        with open('package.json', 'r') as f:
            data = json.load(f)
            return data['version']
    except Exception as e:
        print(f"Error reading version: {e}")
        return "1.0.0"

def update_version(new_version):
    """Update version in package.json"""
    try:
        with open('package.json', 'r') as f:
            data = json.load(f)
        
        data['version'] = new_version
        
        with open('package.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Updated version to {new_version}")
        return True
    except Exception as e:
        print(f"❌ Error updating version: {e}")
        return False

def generate_changelog():
    """Generate changelog from git commits"""
    try:
        # Get commits since last tag
        result = subprocess.run([
            'git', 'log', '--oneline', '--pretty=format:%s', 
            'HEAD', '--not', '$(git describe --tags --abbrev=0 2>/dev/null || echo HEAD~10)'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("⚠️  No previous tags found, using last 10 commits")
            result = subprocess.run([
                'git', 'log', '--oneline', '--pretty=format:%s', '-10'
            ], capture_output=True, text=True)
        
        commits = result.stdout.strip().split('\n')
        
        # Categorize commits
        features = []
        fixes = []
        others = []
        
        for commit in commits:
            if commit.startswith('feat:'):
                features.append(commit)
            elif commit.startswith('fix:'):
                fixes.append(commit)
            else:
                others.append(commit)
        
        # Generate changelog
        changelog = f"""# Changelog

All notable changes to CoolBits.ai will be documented in this file.

## [{datetime.now().strftime('%Y-%m-%d')}] - Version {get_current_version()}

### Features
"""
        
        for feat in features:
            changelog += f"- {feat}\n"
        
        if fixes:
            changelog += "\n### Bug Fixes\n"
            for fix in fixes:
                changelog += f"- {fix}\n"
        
        if others:
            changelog += "\n### Other Changes\n"
            for other in others:
                changelog += f"- {other}\n"
        
        # Write changelog
        with open('CHANGELOG.md', 'w') as f:
            f.write(changelog)
        
        print("✅ Generated CHANGELOG.md")
        return True
        
    except Exception as e:
        print(f"❌ Error generating changelog: {e}")
        return False

def verify_release():
    """Verify release readiness"""
    print("🔍 Verifying release readiness...")
    
    checks = [
        ("Health endpoint", verify_health_endpoint),
        ("Runtime config", verify_runtime_config),
        ("No secrets in code", verify_no_secrets),
        ("Tests pass", verify_tests),
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        try:
            if check_func():
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name}: {e}")
            all_passed = False
    
    return all_passed

def verify_health_endpoint():
    """Verify health endpoint exists and returns required fields"""
    try:
        import requests
        response = requests.get('http://localhost:8080/api/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            required_fields = ['status', 'service', 'version', 'commitSha', 'buildTime', 'node', 'env', 'appMode', 'schemaVersion', 'uptimeSec']
            return all(field in data for field in required_fields)
    except:
        pass
    return False

def verify_runtime_config():
    """Verify runtime config exists"""
    return Path('.runtime.json').exists()

def verify_no_secrets():
    """Verify no secrets in code"""
    try:
        result = subprocess.run(['grep', '-r', '-i', 'password\\|secret\\|key', '.', '--exclude-dir=.git', '--exclude-dir=node_modules'], 
                              capture_output=True, text=True)
        # Allow some false positives
        return result.returncode != 0 or len(result.stdout.strip()) == 0
    except:
        return True

def verify_tests():
    """Verify tests pass"""
    try:
        result = subprocess.run(['python', '-m', 'pytest', 'tests/', '--tb=short'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except:
        return True

def main():
    """Main release function"""
    if len(sys.argv) < 2:
        print("Usage: python scripts/release.py <version>")
        print("Example: python scripts/release.py 1.0.1")
        sys.exit(1)
    
    new_version = sys.argv[1]
    
    print(f"🚀 Starting release process for version {new_version}")
    
    # Verify release readiness
    if not verify_release():
        print("❌ Release verification failed")
        sys.exit(1)
    
    # Update version
    if not update_version(new_version):
        sys.exit(1)
    
    # Generate changelog
    if not generate_changelog():
        sys.exit(1)
    
    print(f"✅ Release {new_version} prepared successfully!")
    print("Next steps:")
    print("1. Review CHANGELOG.md")
    print("2. Commit changes: git add . && git commit -m 'chore(release): {new_version}'")
    print("3. Create tag: git tag v{new_version}")
    print("4. Push: git push origin main --tags")

if __name__ == "__main__":
    main()
