#!/usr/bin/env python3
"""
🤖 CoolBits.ai Training Discussion Processor
Process training discussions and save them to RAG categories

Author: oCopilot (oCursor)
Date: September 6, 2025
"""

import requests
import os


def process_training_file(
    file_path: str,
    category: str = "b-rag",
    subcategory: str = "business_tools",
    item: str = "general",
):
    """Process a training file and save it to RAG system"""

    # Read the training file
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract session title from filename
    session_title = os.path.basename(file_path).replace(".txt", "")

    # Prepare the request
    url = "http://localhost:8097/api/process-training-discussion"
    data = {
        "discussion_content": content,
        "session_title": session_title,
        "category": category,
        "subcategory": subcategory,
        "item": item,
    }

    try:
        # Send request to RAG system
        response = requests.post(
            url, json=data, headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Successfully processed {session_title}")
            print(f"📚 Document ID: {result['document']['id']}")
            print(f"📁 Category: {result['document']['category']}")
            print(f"📊 Metadata: {result['metadata']}")
            return result
        else:
            print(f"❌ Error processing {session_title}: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to RAG system. Make sure it's running on port 8097")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def main():
    """Main function to process training files"""
    print("🤖 CoolBits.ai Training Discussion Processor")
    print("=" * 50)

    # Process training002.txt
    training_file = "train/training002.txt"

    if os.path.exists(training_file):
        print(f"📖 Processing {training_file}...")
        result = process_training_file(
            training_file, "b-rag", "business_tools", "general"
        )

        if result:
            print("\n✅ Training discussion successfully saved to RAG system!")
            print(f"📚 Title: {result['document']['title']}")
            print(f"📁 Category: {result['document']['category']}")
            print(f"📊 Participants: {len(result['metadata']['participants'])}")
            print(f"📝 Total Lines: {result['metadata']['total_lines']}")
        else:
            print("\n❌ Failed to process training discussion")
    else:
        print(f"❌ Training file not found: {training_file}")

    print("\n" + "=" * 50)
    print("🎯 Next steps:")
    print("1. Start RAG system: python rag_categories_system.py")
    print("2. Access RAG admin panel: http://localhost:8098")
    print("3. View categories and documents")
    print("4. Categories: User RAG, Business RAG, Agency RAG, Development RAG")
    print(
        "5. Subcategories: Social, Email, AI, Channels, Tools, SEO, Programming, DevOps, etc."
    )


if __name__ == "__main__":
    main()
