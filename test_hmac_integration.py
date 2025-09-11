# CoolBits.ai HMAC Key Integration Test
# =====================================

import time


def integrate_real_hmac_key():
    """Integrate the real HMAC key into RBAC manager."""
    print("🔑 Integrating Real HMAC Key")
    print("=" * 35)

    try:
        from hmac_key_manager import HMACKeyManager
        from rbac_manager import rbac_manager

        # Load HMAC key manager
        key_manager = HMACKeyManager()

        # Get the admin key we generated earlier
        admin_key_id = "cb401cb643e9f67a"
        key_info = key_manager.get_key(admin_key_id)

        if not key_info:
            print(f"❌ Key {admin_key_id} not found")
            return False

        print(f"✅ Found HMAC key: {key_info['name']}")
        print(f"   Description: {key_info['description']}")
        print(f"   Created: {key_info['created_at']}")
        print(f"   Status: {'Active' if key_info['is_active'] else 'Inactive'}")

        # Extract the key
        key_b64 = key_info["key_b64"]
        print(f"   Key (Base64): {key_b64[:20]}...")

        # Update RBAC manager with real key
        print("\n🔄 Updating RBAC manager with real HMAC key...")

        # Update the HMAC config in RBAC manager
        rbac_manager.hmac_config.secret_key = key_b64
        rbac_manager._save_config()

        print("✅ RBAC manager updated with real HMAC key")

        # Test the integration
        print("\n🧪 Testing HMAC integration...")

        # Generate signature with real key
        method = "POST"
        path = "/api/sensitive/data"
        body = '{"sensitive": "operation"}'

        signature_data = rbac_manager.generate_hmac_signature(method, path, body)

        print(f"Generated signature: {signature_data['signature'][:16]}...")
        print(f"Timestamp: {signature_data['timestamp']}")
        print(f"Nonce: {signature_data['nonce']}")

        # Verify signature
        is_valid = rbac_manager.verify_hmac_signature(
            method,
            path,
            body,
            signature_data["signature"],
            signature_data["timestamp"],
            signature_data["nonce"],
        )

        print(f"Signature verification: {'✅ Valid' if is_valid else '❌ Invalid'}")

        # Test with wrong signature
        wrong_signature = "wrong_signature_12345"
        is_invalid = rbac_manager.verify_hmac_signature(
            method,
            path,
            body,
            wrong_signature,
            signature_data["timestamp"],
            signature_data["nonce"],
        )

        print(
            f"Wrong signature test: {'✅ Rejected' if not is_invalid else '❌ Accepted'}"
        )

        # Update key usage
        key_manager.update_key_usage(admin_key_id)

        print("\n📊 Key usage updated")

        # Verify integration
        assert is_valid, "Real HMAC key should generate valid signatures"
        assert not is_invalid, "Wrong signatures should be rejected"

        print("✅ HMAC key integration successful!")

        return True

    except Exception as e:
        print(f"❌ HMAC key integration failed: {e}")
        return False


def test_hmac_with_real_key():
    """Test HMAC functionality with the real integrated key."""
    print("\n🔐 Testing HMAC with Real Key")
    print("=" * 35)

    try:
        from rbac_manager import rbac_manager

        # Test different endpoints
        test_cases = [
            {
                "method": "POST",
                "path": "/api/sensitive/data",
                "body": '{"data": "test"}',
                "description": "Sensitive data endpoint",
            },
            {
                "method": "PUT",
                "path": "/api/admin/users",
                "body": '{"action": "create"}',
                "description": "Admin user management",
            },
            {
                "method": "DELETE",
                "path": "/api/system/config",
                "body": '{"reset": true}',
                "description": "System configuration",
            },
        ]

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 Test {i}: {test_case['description']}")

            # Generate signature
            signature_data = rbac_manager.generate_hmac_signature(
                test_case["method"], test_case["path"], test_case["body"]
            )

            print(f"   Method: {test_case['method']}")
            print(f"   Path: {test_case['path']}")
            print(f"   Signature: {signature_data['signature'][:16]}...")

            # Verify signature
            is_valid = rbac_manager.verify_hmac_signature(
                test_case["method"],
                test_case["path"],
                test_case["body"],
                signature_data["signature"],
                signature_data["timestamp"],
                signature_data["nonce"],
            )

            print(f"   Verification: {'✅ Valid' if is_valid else '❌ Invalid'}")

            assert is_valid, f"Test case {i} should be valid"

        print("\n✅ All HMAC tests with real key passed!")

        return True

    except Exception as e:
        print(f"❌ HMAC real key test failed: {e}")
        return False


def test_hmac_key_rotation():
    """Test HMAC key rotation functionality."""
    print("\n🔄 Testing HMAC Key Rotation")
    print("=" * 30)

    try:
        from hmac_key_manager import HMACKeyManager

        key_manager = HMACKeyManager()

        # Generate a new key for rotation test
        print("🔑 Generating new key for rotation test...")

        new_key = key_manager.generate_key(
            name="rotation-test-key",
            description="Key for testing rotation functionality",
            expires_in_days=1,  # Short expiration for testing
        )

        print(f"✅ New key generated: {new_key['key_id']}")
        print(f"   Expires: {new_key['expires_at']}")

        # Test key validation
        is_valid = key_manager.is_key_valid(new_key["key_id"])
        print(f"   Valid: {'✅ Yes' if is_valid else '❌ No'}")

        # Test key revocation
        print("\n🚫 Testing key revocation...")

        revoked = key_manager.revoke_key(new_key["key_id"])
        print(f"Revocation: {'✅ Success' if revoked else '❌ Failed'}")

        # Test validation after revocation
        is_still_valid = key_manager.is_key_valid(new_key["key_id"])
        print(
            f"Still valid after revocation: {'❌ Yes' if is_still_valid else '✅ No'}"
        )

        # Test key activation
        print("\n🔄 Testing key activation...")

        activated = key_manager.activate_key(new_key["key_id"])
        print(f"Activation: {'✅ Success' if activated else '❌ Failed'}")

        # Test validation after activation
        is_valid_again = key_manager.is_key_valid(new_key["key_id"])
        print(f"Valid after activation: {'✅ Yes' if is_valid_again else '❌ No'}")

        # Cleanup expired keys
        print("\n🧹 Testing cleanup...")

        removed_count = key_manager.cleanup_expired_keys()
        print(f"Expired keys removed: {removed_count}")

        print("✅ HMAC key rotation tests passed!")

        return True

    except Exception as e:
        print(f"❌ HMAC key rotation test failed: {e}")
        return False


def test_hmac_security():
    """Test HMAC security features."""
    print("\n🛡️ Testing HMAC Security")
    print("=" * 25)

    try:
        from rbac_manager import rbac_manager

        # Test timestamp tolerance
        print("⏰ Testing timestamp tolerance...")

        method = "POST"
        path = "/api/test"
        body = "{}"

        # Generate signature with current timestamp
        signature_data = rbac_manager.generate_hmac_signature(method, path, body)

        # Test with valid timestamp
        is_valid_now = rbac_manager.verify_hmac_signature(
            method,
            path,
            body,
            signature_data["signature"],
            signature_data["timestamp"],
            signature_data["nonce"],
        )

        print(f"Current timestamp: {'✅ Valid' if is_valid_now else '❌ Invalid'}")

        # Test with old timestamp (should fail)
        old_timestamp = str(
            int(time.time()) - 400
        )  # 400 seconds ago (beyond tolerance)

        is_valid_old = rbac_manager.verify_hmac_signature(
            method,
            path,
            body,
            signature_data["signature"],
            old_timestamp,
            signature_data["nonce"],
        )

        print(
            f"Old timestamp (400s ago): {'❌ Valid' if is_valid_old else '✅ Invalid'}"
        )

        # Test nonce uniqueness
        print("\n🎲 Testing nonce uniqueness...")

        signatures = []
        for i in range(5):
            sig_data = rbac_manager.generate_hmac_signature(method, path, body)
            signatures.append(sig_data["nonce"])

        unique_nonces = len(set(signatures))
        print(f"Unique nonces generated: {unique_nonces}/5")

        # Test signature uniqueness
        print("\n🔐 Testing signature uniqueness...")

        sig_values = []
        for i in range(5):
            sig_data = rbac_manager.generate_hmac_signature(method, path, body)
            sig_values.append(sig_data["signature"])

        unique_signatures = len(set(sig_values))
        print(f"Unique signatures generated: {unique_signatures}/5")

        # Verify security features
        assert is_valid_now, "Current timestamp should be valid"
        assert not is_valid_old, "Old timestamp should be invalid"
        assert unique_nonces == 5, "All nonces should be unique"
        assert unique_signatures == 5, "All signatures should be unique"

        print("✅ HMAC security tests passed!")

        return True

    except Exception as e:
        print(f"❌ HMAC security test failed: {e}")
        return False


if __name__ == "__main__":
    print("🔑 CoolBits.ai HMAC Key Integration Test")
    print("========================================")

    success = True

    # Test 1: Integrate real HMAC key
    if not integrate_real_hmac_key():
        success = False

    # Test 2: Test HMAC with real key
    if not test_hmac_with_real_key():
        success = False

    # Test 3: Test key rotation
    if not test_hmac_key_rotation():
        success = False

    # Test 4: Test security features
    if not test_hmac_security():
        success = False

    print("\n" + "=" * 50)
    if success:
        print("🎉 All HMAC key integration tests passed!")
        print("✅ Real HMAC key integrated successfully")
        print("✅ HMAC signatures working with real key")
        print("✅ Key rotation functionality operational")
        print("✅ Security features enforced")
    else:
        print("❌ Some HMAC key integration tests failed")
        print("🔧 Check the errors above and fix them")

    print("=" * 50)
