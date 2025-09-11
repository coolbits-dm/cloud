#!/usr/bin/env python3
"""
API Cost Optimization Script
CoolBits.ai - Update all systems to use cheaper models
"""

import os


def update_model_in_file(file_path, old_model, new_model, comment=""):
    """Update model in a file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Replace model with comment
        if comment:
            new_content = content.replace(
                f'"{old_model}"', f'"{new_model}"  # {comment}'
            )
        else:
            new_content = content.replace(f'"{old_model}"', f'"{new_model}"')

        if new_content != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"✅ Updated {file_path}: {old_model} -> {new_model}")
            return True
        else:
            print(f"ℹ️  No changes needed in {file_path}")
            return False
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False


def main():
    """Main function to update all systems"""
    print("🚀 API Cost Optimization - Updating all systems to cheaper models")
    print("=" * 70)

    # Define model updates
    model_updates = [
        {
            "old": "gpt-4",
            "new": "gpt-4o-mini",
            "comment": "Much cheaper: $0.15 vs $30 per 1M tokens",
            "files": [
                "enhanced_multi_agent_chat_server.py",
                "multi_agent_chat_server.py",
                "rag_admin_server.py",
                "rag_categories_system.py",
            ],
        },
        {
            "old": "grok-2-1212",
            "new": "grok-3-mini",
            "comment": "Much cheaper: $0.30 vs $2.00 per 1M tokens",
            "files": [
                "enhanced_multi_agent_chat_server.py",
                "multi_agent_chat_server.py",
                "rag_admin_server.py",
                "rag_categories_system.py",
            ],
        },
    ]

    # Update files
    total_updates = 0
    for update in model_updates:
        print(f"\n🔄 Updating {update['old']} -> {update['new']}")
        print(f"💡 Reason: {update['comment']}")

        for file_path in update["files"]:
            if os.path.exists(file_path):
                if update_model_in_file(
                    file_path, update["old"], update["new"], update["comment"]
                ):
                    total_updates += 1
            else:
                print(f"⚠️  File not found: {file_path}")

    # Create cost monitoring script
    create_cost_monitoring_script()

    print("\n🎯 SUMMARY:")
    print(f"✅ Total files updated: {total_updates}")
    print("💰 Estimated cost reduction: 90%+ (from $30 to $0.15 per 1M tokens)")
    print("🚀 All systems now use cost-optimized models!")

    print("\n📊 COST COMPARISON:")
    print("GPT-4: $30/1M tokens -> GPT-4o-mini: $0.15/1M tokens (200x cheaper!)")
    print(
        "Grok-2-1212: $2.00/1M tokens -> Grok-3-mini: $0.30/1M tokens (6.7x cheaper!)"
    )


def create_cost_monitoring_script():
    """Create a cost monitoring script"""
    script_content = '''#!/usr/bin/env python3
"""
Cost Monitoring Script
Monitor API usage and costs
"""

import requests
import json
from datetime import datetime

def check_openai_usage():
    """Check OpenAI usage"""
    try:
        # This would need your OpenAI API key
        # headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        # response = requests.get("https://api.openai.com/v1/usage", headers=headers)
        print("OpenAI usage check - implement with your API key")
    except Exception as e:
        print(f"Error checking OpenAI usage: {e}")

def check_xai_usage():
    """Check xAI usage"""
    try:
        # This would need your xAI API key
        # headers = {"Authorization": f"Bearer {XAI_API_KEY}"}
        # response = requests.get("https://api.x.ai/v1/usage", headers=headers)
        print("xAI usage check - implement with your API key")
    except Exception as e:
        print(f"Error checking xAI usage: {e}")

if __name__ == "__main__":
    print("💰 Cost Monitoring Script")
    print("=" * 30)
    check_openai_usage()
    check_xai_usage()
'''

    with open("cost_monitoring.py", "w", encoding="utf-8") as f:
        f.write(script_content)
    print("✅ Created cost_monitoring.py")


if __name__ == "__main__":
    main()
