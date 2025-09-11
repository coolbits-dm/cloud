# CoolBits.ai NHA Registry - Artifact Generator
# Generates JSON, Markdown, and other artifacts from agents.yaml

import sys
import os
from pathlib import Path
from registry import load_yaml, dump_json, dump_markdown, dump_by_category

def main():
    """Generate all NHA registry artifacts"""
    try:
        # Load registry
        print("📋 Loading NHA registry...")
        reg = load_yaml("cblm/opipe/nha/agents.yaml")
        
        # Ensure output directory exists
        os.makedirs("cblm/opipe/nha/out", exist_ok=True)
        
        # Generate artifacts
        print("📄 Generating JSON artifact...")
        dump_json(reg, "cblm/opipe/nha/out/registry.json")
        
        print("📝 Generating Markdown artifact...")
        dump_markdown(reg, "cblm/opipe/nha/out/registry.md")
        
        print("📊 Generating category breakdown...")
        dump_by_category(reg, "cblm/opipe/nha/out/by-category.md")
        
        # Generate summary
        print("\n✅ NHA Registry Artifacts Generated Successfully!")
        print(f"📊 Total Agents: {len(reg.nhas)}")
        print(f"📁 Output Directory: cblm/opipe/nha/out/")
        print(f"📄 Files Generated:")
        print(f"   - registry.json")
        print(f"   - registry.md")
        print(f"   - by-category.md")
        
        # Show category breakdown
        categories = {}
        for nha in reg.nhas:
            if nha.category not in categories:
                categories[nha.category] = 0
            categories[nha.category] += 1
        
        print(f"\n📈 Category Breakdown:")
        for category, count in sorted(categories.items()):
            print(f"   - {category.replace('_', ' ').title()}: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating artifacts: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
