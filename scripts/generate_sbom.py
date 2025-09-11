# CoolBits.ai SBOM Generation Script
# ==================================

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def generate_sbom():
    """Generate Software Bill of Materials (SBOM)"""

    print("🔍 Generating Software Bill of Materials (SBOM)...")

    # Create SBOM directory
    sbom_dir = Path("sbom")
    sbom_dir.mkdir(exist_ok=True)

    # Generate Python dependencies SBOM
    try:
        print("📦 Generating Python dependencies SBOM...")
        result = subprocess.run(
            ["pip", "list", "--format=json"], capture_output=True, text=True
        )

        if result.returncode == 0:
            python_deps = json.loads(result.stdout)

            # Create SPDX format SBOM
            spdx_sbom = {
                "spdxVersion": "SPDX-2.3",
                "dataLicense": "CC0-1.0",
                "SPDXID": "SPDXRef-DOCUMENT",
                "documentNamespace": f"https://coolbits.ai/spdx/coolbits-ai-{datetime.now().strftime('%Y%m%d')}",
                "name": "CoolBits.ai",
                "creationInfo": {
                    "created": datetime.now().isoformat() + "Z",
                    "creators": [
                        "Tool: CoolBits.ai SBOM Generator",
                        "Organization: COOL BITS SRL",
                    ],
                },
                "packages": [],
                "relationships": [],
            }

            # Add main package
            main_package = {
                "SPDXID": "SPDXRef-Package-coolbits-ai",
                "name": "coolbits-ai",
                "versionInfo": "1.0.0",
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": False,
                "licenseConcluded": "PROPRIETARY",
                "licenseDeclared": "PROPRIETARY",
                "copyrightText": "Copyright (c) 2025 COOL BITS SRL",
                "description": "CoolBits.ai AI Platform",
                "supplier": "Organization: COOL BITS SRL",
                "originator": "Organization: COOL BITS SRL",
            }
            spdx_sbom["packages"].append(main_package)

            # Add Python dependencies
            for dep in python_deps:
                if dep["name"] and dep["version"]:
                    package_id = f"SPDXRef-Package-{dep['name'].replace('-', '_').replace('.', '_')}"
                    package = {
                        "SPDXID": package_id,
                        "name": dep["name"],
                        "versionInfo": dep["version"],
                        "downloadLocation": "NOASSERTION",
                        "filesAnalyzed": False,
                        "licenseConcluded": "NOASSERTION",
                        "licenseDeclared": "NOASSERTION",
                        "copyrightText": "NOASSERTION",
                        "description": f"Python package: {dep['name']}",
                        "supplier": "NOASSERTION",
                        "originator": "NOASSERTION",
                    }
                    spdx_sbom["packages"].append(package)

                    # Add relationship
                    relationship = {
                        "spdxElementId": "SPDXRef-Package-coolbits-ai",
                        "relationshipType": "DEPENDS_ON",
                        "relatedSpdxElement": package_id,
                    }
                    spdx_sbom["relationships"].append(relationship)

            # Write SBOM
            sbom_file = (
                sbom_dir / f"coolbits-ai-sbom-{datetime.now().strftime('%Y%m%d')}.json"
            )
            with open(sbom_file, "w") as f:
                json.dump(spdx_sbom, f, indent=2)

            print(f"✅ Python SBOM generated: {sbom_file}")

        else:
            print("❌ Failed to generate Python dependencies SBOM")
            return False

    except Exception as e:
        print(f"❌ Error generating Python SBOM: {e}")
        return False

    # Generate Docker image SBOM (if Docker is available)
    try:
        print("🐳 Generating Docker image SBOM...")

        # Check if Docker is available
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker found, generating image SBOM...")

            # Build Docker image
            build_result = subprocess.run(
                ["docker", "build", "-t", "coolbits-ai:latest", "."],
                capture_output=True,
                text=True,
            )

            if build_result.returncode == 0:
                print("✅ Docker image built successfully")

                # Generate SBOM using syft (if available)
                syft_result = subprocess.run(
                    ["syft", "coolbits-ai:latest", "-o", "spdx-json"],
                    capture_output=True,
                    text=True,
                )

                if syft_result.returncode == 0:
                    docker_sbom_file = (
                        sbom_dir
                        / f"coolbits-ai-docker-sbom-{datetime.now().strftime('%Y%m%d')}.json"
                    )
                    with open(docker_sbom_file, "w") as f:
                        f.write(syft_result.stdout)
                    print(f"✅ Docker SBOM generated: {docker_sbom_file}")
                else:
                    print("⚠️  Syft not available, skipping Docker SBOM")
            else:
                print("❌ Failed to build Docker image")
        else:
            print("⚠️  Docker not available, skipping Docker SBOM")

    except Exception as e:
        print(f"⚠️  Docker SBOM generation skipped: {e}")

    return True


def sign_artifacts():
    """Sign artifacts using cosign"""

    print("🔐 Signing artifacts with cosign...")

    try:
        # Check if cosign is available
        result = subprocess.run(["cosign", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Cosign found")

            # Generate key pair if not exists
            key_file = Path("cosign.key")
            if not key_file.exists():
                print("🔑 Generating cosign key pair...")
                subprocess.run(["cosign", "generate-key-pair"], check=True)
                print("✅ Cosign key pair generated")

            # Sign Docker image
            try:
                subprocess.run(
                    ["cosign", "sign", "--key", "cosign.key", "coolbits-ai:latest"],
                    check=True,
                )
                print("✅ Docker image signed")
            except subprocess.CalledProcessError:
                print("⚠️  Failed to sign Docker image")

            # Sign SBOM files
            sbom_dir = Path("sbom")
            if sbom_dir.exists():
                for sbom_file in sbom_dir.glob("*.json"):
                    try:
                        subprocess.run(
                            [
                                "cosign",
                                "sign-blob",
                                "--key",
                                "cosign.key",
                                str(sbom_file),
                            ],
                            check=True,
                        )
                        print(f"✅ Signed SBOM: {sbom_file}")
                    except subprocess.CalledProcessError:
                        print(f"⚠️  Failed to sign SBOM: {sbom_file}")

        else:
            print("⚠️  Cosign not available, skipping signing")

    except Exception as e:
        print(f"⚠️  Signing skipped: {e}")


def verify_sbom():
    """Verify SBOM integrity"""

    print("🔍 Verifying SBOM integrity...")

    sbom_dir = Path("sbom")
    if not sbom_dir.exists():
        print("❌ SBOM directory not found")
        return False

    sbom_files = list(sbom_dir.glob("*.json"))
    if not sbom_files:
        print("❌ No SBOM files found")
        return False

    for sbom_file in sbom_files:
        try:
            with open(sbom_file, "r") as f:
                sbom_data = json.load(f)

            # Verify SPDX format
            required_fields = ["spdxVersion", "SPDXID", "name", "packages"]
            if all(field in sbom_data for field in required_fields):
                print(f"✅ SBOM format valid: {sbom_file}")
            else:
                print(f"❌ SBOM format invalid: {sbom_file}")
                return False

        except Exception as e:
            print(f"❌ Error verifying SBOM {sbom_file}: {e}")
            return False

    return True


def main():
    """Main SBOM generation function"""

    print("🚀 CoolBits.ai SBOM Generation")
    print("===============================")

    # Generate SBOM
    if not generate_sbom():
        sys.exit(1)

    # Sign artifacts
    sign_artifacts()

    # Verify SBOM
    if not verify_sbom():
        sys.exit(1)

    print("✅ SBOM generation completed successfully!")
    print("📁 SBOM files saved in: sbom/")
    print("🔐 Artifacts signed with cosign (if available)")


if __name__ == "__main__":
    main()
