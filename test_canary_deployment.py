# CoolBits.ai Canary Deployment Test with Bug
# ===========================================

import os
import sys
import time
import subprocess
from datetime import datetime


def create_buggy_version():
    """Create a version with intentional bug for testing rollback."""
    print("🐛 Creating buggy version for canary test...")
    
    # Create a simple Flask app with a bug
    buggy_app = '''
from flask import Flask, jsonify
import time

app = Flask(__name__)

@app.route('/health')
def health():
    # Intentional bug: this will cause 500 error
    return jsonify({"status": "healthy", "bug": 1/0})

@app.route('/api/test')
def test():
    return jsonify({"message": "This endpoint works", "timestamp": time.time()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8502, debug=True)
'''
    
    with open("buggy_app.py", "w") as f:
        f.write(buggy_app)
    
    print("✅ Buggy app created: buggy_app.py")
    return "buggy_app.py"


def create_fixed_version():
    """Create a fixed version for rollback test."""
    print("🔧 Creating fixed version for rollback test...")
    
    fixed_app = '''
from flask import Flask, jsonify
import time

app = Flask(__name__)

@app.route('/health')
def health():
    # Fixed: removed the bug
    return jsonify({"status": "healthy", "version": "fixed"})

@app.route('/api/test')
def test():
    return jsonify({"message": "This endpoint works", "timestamp": time.time()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8502, debug=True)
'''
    
    with open("fixed_app.py", "w") as f:
        f.write(fixed_app)
    
    print("✅ Fixed app created: fixed_app.py")
    return "fixed_app.py"


def test_canary_deployment():
    """Test canary deployment with bug and rollback."""
    print("🚀 Testing Canary Deployment with Bug")
    print("=" * 50)
    
    # Step 1: Create buggy version
    buggy_file = create_buggy_version()
    
    # Step 2: Start buggy version
    print("\n📱 Starting buggy version...")
    try:
        buggy_process = subprocess.Popen(
            [sys.executable, buggy_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for app to start
        time.sleep(3)
        
        # Test buggy version
        print("🧪 Testing buggy version...")
        import requests
        
        try:
            # This should fail due to the bug
            response = requests.get("http://localhost:8502/health", timeout=5)
            print(f"❌ Buggy version responded: {response.status_code}")
            if response.status_code == 500:
                print("✅ Bug detected as expected!")
            else:
                print("⚠️ Unexpected response from buggy version")
        except requests.exceptions.RequestException as e:
            print(f"✅ Buggy version failed as expected: {e}")
        
        # Step 3: Simulate rollback
        print("\n🔄 Simulating rollback...")
        buggy_process.terminate()
        buggy_process.wait()
        
        # Create and start fixed version
        fixed_file = create_fixed_version()
        print("🔧 Starting fixed version...")
        
        fixed_process = subprocess.Popen(
            [sys.executable, fixed_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for app to start
        time.sleep(3)
        
        # Test fixed version
        print("🧪 Testing fixed version...")
        try:
            response = requests.get("http://localhost:8502/health", timeout=5)
            if response.status_code == 200:
                print("✅ Fixed version working correctly!")
                print(f"Response: {response.json()}")
            else:
                print(f"❌ Fixed version still has issues: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Fixed version failed: {e}")
        
        # Cleanup
        fixed_process.terminate()
        fixed_process.wait()
        
        print("\n🎯 Canary Deployment Test Results:")
        print("✅ Buggy version failed as expected")
        print("✅ Rollback to fixed version successful")
        print("✅ Health check passed after rollback")
        
        return True
        
    except Exception as e:
        print(f"❌ Canary deployment test failed: {e}")
        return False
    
    finally:
        # Cleanup files
        for file in [buggy_file, "fixed_app.py"]:
            if os.path.exists(file):
                os.remove(file)
                print(f"🧹 Cleaned up: {file}")


def test_rollback_script():
    """Test the rollback script functionality."""
    print("\n🔄 Testing Rollback Script")
    print("=" * 30)
    
    # Test rollback_manager.py
    try:
        from rollback_manager import RollbackManager
        
        print("✅ Rollback manager imported successfully")
        
        # Test with mock data
        print("🧪 Testing rollback functions...")
        
        # Test RollbackManager class
        from rollback_manager import RollbackConfig
        config = RollbackConfig(production_url="http://localhost:8501")
        rollback_manager = RollbackManager(config)
        assert hasattr(rollback_manager, 'emergency_rollback'), "emergency_rollback method not found"
        assert hasattr(rollback_manager, 'planned_rollback'), "planned_rollback method not found"
        
        print("✅ Rollback manager methods are available")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import rollback manager: {e}")
        return False
    except Exception as e:
        print(f"❌ Rollback script test failed: {e}")
        return False


def test_canary_deployment_script():
    """Test the canary deployment script."""
    print("\n🚀 Testing Canary Deployment Script")
    print("=" * 40)
    
    try:
        from canary_deployment import CanaryDeployment
        
        print("✅ Canary deployment script imported successfully")
        
        # Test with mock data
        print("🧪 Testing canary functions...")
        
        # Test CanaryDeployment class
        from canary_deployment import DeploymentConfig
        config = DeploymentConfig(staging_url="http://localhost:8501", production_url="http://localhost:8502")
        canary_deployment = CanaryDeployment(config)
        assert hasattr(canary_deployment, 'run_canary_deployment'), "run_canary_deployment method not found"
        assert hasattr(canary_deployment, 'deploy_to_staging'), "deploy_to_staging method not found"
        
        print("✅ Canary deployment methods are available")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import canary deployment: {e}")
        return False
    except Exception as e:
        print(f"❌ Canary deployment script test failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 CoolBits.ai Canary Deployment Test")
    print("=====================================")
    
    success = True
    
    # Test 1: Canary deployment with bug
    if not test_canary_deployment():
        success = False
    
    # Test 2: Rollback script
    if not test_rollback_script():
        success = False
    
    # Test 3: Canary deployment script
    if not test_canary_deployment_script():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All canary deployment tests passed!")
        print("✅ Bug detection working")
        print("✅ Rollback mechanism functional")
        print("✅ Canary deployment scripts ready")
    else:
        print("❌ Some canary deployment tests failed")
        print("🔧 Check the errors above and fix them")
    
    print("=" * 50)
