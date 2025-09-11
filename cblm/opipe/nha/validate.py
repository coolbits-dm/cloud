# CoolBits.ai NHA Registry - Validation Engine
# Validates schema, business rules, and consistency

import sys
import yaml
from registry import load_yaml, validate_registry
import jsonschema


def validate_schema():
    """Validate YAML against JSONSchema"""
    try:
        # Load schema
        with open("cblm/opipe/nha/schema.yaml", "r", encoding="utf-8") as f:
            schema = yaml.safe_load(f)

        # Load agents
        with open("cblm/opipe/nha/agents.yaml", "r", encoding="utf-8") as f:
            agents_data = yaml.safe_load(f)

        # Validate
        jsonschema.validate(agents_data, schema)
        print("[SUCCESS] Schema validation passed")
        return True

    except jsonschema.ValidationError as e:
        print(f"[ERROR] Schema validation failed: {e.message}")
        print(f"   Path: {' -> '.join(str(p) for p in e.absolute_path)}")
        return False
    except Exception as e:
        print(f"[ERROR] Schema validation error: {e}")
        return False


def validate_business_rules():
    """Validate business rules and consistency"""
    try:
        reg = load_yaml("cblm/opipe/nha/agents.yaml")
        errors = validate_registry(reg)

        if errors:
            print("[ERROR] Business rule validation failed:")
            for error in errors:
                print(f"   - {error}")
            return False

        print("[SUCCESS] Business rule validation passed")
        return True

    except Exception as e:
        print(f"[ERROR] Business rule validation error: {e}")
        return False


def validate_required_tags():
    """Validate required tags are present"""
    try:
        reg = load_yaml("cblm/opipe/nha/agents.yaml")
        errors = []

        required_tags = ["env", "service"]

        for nha in reg.nhas:
            nha_tags = [tag.split(":")[0] for tag in nha.tags]

            for required_tag in required_tags:
                if required_tag not in nha_tags:
                    errors.append(
                        f"NHA {nha.name} missing required tag: {required_tag}"
                    )

        if errors:
            print("[ERROR] Required tags validation failed:")
            for error in errors:
                print(f"   - {error}")
            return False

        print("[SUCCESS] Required tags validation passed")
        return True

    except Exception as e:
        print(f"[ERROR] Required tags validation error: {e}")
        return False


def validate_unique_constraints():
    """Validate uniqueness constraints"""
    try:
        reg = load_yaml("cblm/opipe/nha/agents.yaml")

        # Check for duplicate IDs
        ids = [nha.id for nha in reg.nhas]
        if len(ids) != len(set(ids)):
            duplicates = [id for id in ids if ids.count(id) > 1]
            print(f"[ERROR] Duplicate IDs found: {duplicates}")
            return False

        # Check for duplicate names
        names = [nha.name for nha in reg.nhas]
        if len(names) != len(set(names)):
            duplicates = [name for name in names if names.count(name) > 1]
            print(f"[ERROR] Duplicate names found: {duplicates}")
            return False

        print("[SUCCESS] Uniqueness validation passed")
        return True

    except Exception as e:
        print(f"[ERROR] Uniqueness validation error: {e}")
        return False


def validate_secrets_format():
    """Validate secret references format"""
    try:
        reg = load_yaml("cblm/opipe/nha/agents.yaml")
        errors = []

        for nha in reg.nhas:
            for secret in nha.secrets:
                if not secret.startswith("nha/"):
                    errors.append(f"NHA {nha.name} has invalid secret format: {secret}")
                elif len(secret.split("/")) != 3:
                    errors.append(f"NHA {nha.name} has invalid secret format: {secret}")

        if errors:
            print("[ERROR] Secret format validation failed:")
            for error in errors:
                print(f"   - {error}")
            return False

        print("[SUCCESS] Secret format validation passed")
        return True

    except Exception as e:
        print(f"[ERROR] Secret format validation error: {e}")
        return False


def validate_permissions_format():
    """Validate permission format"""
    try:
        reg = load_yaml("cblm/opipe/nha/agents.yaml")
        errors = []

        for nha in reg.nhas:
            for permission in nha.permissions:
                if "." not in permission and "/" not in permission:
                    errors.append(
                        f"NHA {nha.name} has invalid permission format: {permission}"
                    )

        if errors:
            print("[ERROR] Permission format validation failed:")
            for error in errors:
                print(f"   - {error}")
            return False

        print("[SUCCESS] Permission format validation passed")
        return True

    except Exception as e:
        print(f"[ERROR] Permission format validation error: {e}")
        return False


def validate_channels_required():
    """Validate all NHAs have at least one channel"""
    try:
        reg = load_yaml("cblm/opipe/nha/agents.yaml")
        errors = []

        for nha in reg.nhas:
            if not nha.channels:
                errors.append(f"NHA {nha.name} has no channels defined")

        if errors:
            print("[ERROR] Channels validation failed:")
            for error in errors:
                print(f"   - {error}")
            return False

        print("[SUCCESS] Channels validation passed")
        return True

    except Exception as e:
        print(f"[ERROR] Channels validation error: {e}")
        return False


def main():
    """Run all validation checks"""
    print("[VALIDATE] NHA Registry Validation")
    print("=" * 50)

    validations = [
        ("Schema", validate_schema),
        ("Business Rules", validate_business_rules),
        ("Required Tags", validate_required_tags),
        ("Uniqueness", validate_unique_constraints),
        ("Secret Format", validate_secrets_format),
        ("Permission Format", validate_permissions_format),
        ("Channels Required", validate_channels_required),
    ]

    all_passed = True

    for name, validation_func in validations:
        print(f"\n[CHECK] {name} Validation:")
        if not validation_func():
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("[SUCCESS] All validations passed! Registry is valid.")
        return True
    else:
        print("[ERROR] Some validations failed. Please fix the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
