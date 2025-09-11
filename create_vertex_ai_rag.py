#!/usr/bin/env python3
"""
Vertex AI RAG Engine Script for CoolBits.ai
Based on official Google Cloud documentation
"""

import os
from vertexai import rag
import vertexai

# Configuration
PROJECT_ID = "coolbits-ai"
LOCATION = "us-central1"  # RAG Engine uses us-central1


def create_rag_corpus():
    """Create a RAG corpus using Vertex AI RAG Engine"""

    print("🚀 Starting RAG corpus creation with Vertex AI RAG Engine...")
    print(f"Project: {PROJECT_ID}")
    print(f"Location: {LOCATION}")

    # Initialize Vertex AI
    try:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        print("✅ Vertex AI initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Vertex AI: {e}")
        return False

    # Create RAG corpus
    try:
        print("📝 Creating RAG corpus: ai-board-corpus")

        response = rag.create_corpus(
            display_name="ai-board-corpus",
            description="RAG corpus for AI Board management and coordination",
        )

        corpus_name = response.name
        print(f"✅ Created RAG corpus: {corpus_name}")

        # Import sample files
        print("📄 Importing sample files...")

        # Create a sample document
        sample_content = """
# AI Board Management Best Practices

## Overview
The AI Board is responsible for overseeing artificial intelligence initiatives and ensuring ethical AI deployment.

## Key Responsibilities
- Strategic AI planning
- Risk assessment and mitigation
- Compliance with AI regulations
- Resource allocation for AI projects

## Best Practices
1. Regular board meetings
2. Clear communication channels
3. Transparent decision making
4. Continuous learning and adaptation

## Governance Framework
- Ethical AI principles
- Data privacy protection
- Algorithmic transparency
- Human oversight requirements
"""

        # Save sample content to a file
        with open("ai_board_sample.txt", "w") as f:
            f.write(sample_content)

        # Import the file
        import_response = rag.import_files(
            corpus_name=corpus_name,
            paths=["ai_board_sample.txt"],
            transformation_config=rag.TransformationConfig(
                rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)
            ),
        )

        print(f"✅ Imported {import_response.imported_rag_files_count} files")

        # Test retrieval
        print("🔍 Testing retrieval...")

        retrieval_response = rag.retrieval_query(
            rag_resources=[rag.RagResource(rag_corpus=corpus_name)],
            text="What are the key responsibilities of the AI Board?",
            rag_retrieval_config=rag.RagRetrievalConfig(
                top_k=3,
                filter=rag.utils.resources.Filter(vector_distance_threshold=0.5),
            ),
        )

        print("✅ Retrieval test successful!")
        print(f"Found {len(retrieval_response.contexts)} relevant contexts")

        # Clean up
        os.remove("ai_board_sample.txt")

        print("🎉 RAG corpus creation completed successfully!")
        print(f"Corpus name: {corpus_name}")

        return True

    except Exception as e:
        print(f"❌ Failed to create RAG corpus: {e}")
        return False


def main():
    """Main execution function"""
    print("=" * 60)
    print("Vertex AI RAG Engine - CoolBits.ai")
    print("=" * 60)

    if create_rag_corpus():
        print("\n✅ Success! RAG corpus created and tested.")
        print("\nNext steps:")
        print("1. Create more RAG corpora for other industries")
        print("2. Upload industry-specific documents")
        print("3. Integrate with Business Panel")
    else:
        print("\n❌ Failed to create RAG corpus.")
        print("Please check your permissions and try again.")


if __name__ == "__main__":
    main()
