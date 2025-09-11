#!/bin/bash

# Cloud Shell Script to Create STREAM_UPDATE Index
# Run this in Google Cloud Shell to create the proper STREAM_UPDATE index

echo "🚀 Creating STREAM_UPDATE Index for RAG Engine in Cloud Shell..."
echo "Project: coolbits-ai"
echo "Location: europe-west3"
echo ""

# Install required packages
echo "📦 Installing required packages..."
pip install google-cloud-aiplatform

# Create Python script
cat > create_stream_update_index.py << 'EOF'
#!/usr/bin/env python3
"""
Create STREAM_UPDATE Index for Vertex AI RAG Engine
Run this in Cloud Shell
"""

from google.cloud import aiplatform
from google.cloud.aiplatform import matching_engine
from google.cloud.aiplatform.matching_engine import matching_engine_index_config

def create_stream_update_index():
    """Create a STREAM_UPDATE index for RAG Engine"""
    
    # Configuration
    PROJECT_ID = "coolbits-ai"
    LOCATION = "europe-west3"
    DISPLAY_NAME = "RAG Engine Stream Update Index"
    DESCRIPTION = "STREAM_UPDATE index for Vertex AI RAG Engine corpus creation"
    DIMENSIONS = 768  # text-embedding-004 dimensions
    
    print(f"🚀 Creating STREAM_UPDATE index for RAG Engine...")
    print(f"Project: {PROJECT_ID}")
    print(f"Location: {LOCATION}")
    print(f"Display Name: {DISPLAY_NAME}")
    print(f"Dimensions: {DIMENSIONS}")
    print()
    
    try:
        # Initialize Vertex AI
        aiplatform.init(project=PROJECT_ID, location=LOCATION)
        print("✅ Vertex AI initialized successfully")
        
        # Create STREAM_UPDATE index
        print("🔄 Creating STREAM_UPDATE index...")
        
        index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
            display_name=DISPLAY_NAME,
            description=DESCRIPTION,
            dimensions=DIMENSIONS,
            approximate_neighbors_count=150,
            leaf_node_embedding_count=500,
            leaf_nodes_to_search_percent=7,
            index_update_method="STREAM_UPDATE",  # This is the key!
            distance_measure_type=matching_engine_index_config.DistanceMeasureType.DOT_PRODUCT_DISTANCE,
        )
        
        print("✅ STREAM_UPDATE index created successfully!")
        print(f"Index Name: {index.name}")
        print(f"Index ID: {index.resource_name}")
        
        return index
        
    except Exception as e:
        print(f"❌ Error creating STREAM_UPDATE index: {e}")
        return None

def create_index_endpoint(index):
    """Create an index endpoint for the STREAM_UPDATE index"""
    
    PROJECT_ID = "coolbits-ai"
    LOCATION = "europe-west3"
    
    print()
    print("🔄 Creating Index Endpoint...")
    
    try:
        endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
            display_name="RAG Engine Stream Endpoint",
            description="Index endpoint for RAG Engine STREAM_UPDATE index",
            network="projects/271190369805/global/networks/default"
        )
        
        print("✅ Index Endpoint created successfully!")
        print(f"Endpoint Name: {endpoint.name}")
        print(f"Endpoint ID: {endpoint.resource_name}")
        
        return endpoint
        
    except Exception as e:
        print(f"❌ Error creating Index Endpoint: {e}")
        return None

def main():
    """Main function"""
    print("=" * 60)
    print("🎯 RAG Engine STREAM_UPDATE Index Creation")
    print("=" * 60)
    
    # Create STREAM_UPDATE index
    index = create_stream_update_index()
    
    if index:
        # Create index endpoint
        endpoint = create_index_endpoint(index)
        
        print()
        print("=" * 60)
        print("🎉 SUCCESS!")
        print("=" * 60)
        print("✅ STREAM_UPDATE index created successfully!")
        print("✅ Index Endpoint created successfully!")
        print()
        print("📋 NEXT STEPS:")
        print("1. Wait for index to be ready (5-10 minutes)")
        print("2. Go to Vertex AI RAG Engine > Create Corpus")
        print("3. Select the STREAM_UPDATE index")
        print("4. Create your corpus successfully!")
        print()
        print("🔗 Index Details:")
        print(f"   Name: {index.display_name}")
        print(f"   ID: {index.resource_name}")
        print(f"   Update Method: STREAM_UPDATE")
        print(f"   Dimensions: 768")
        print(f"   Distance Measure: DOT_PRODUCT_DISTANCE")
        
    else:
        print()
        print("❌ FAILED!")
        print("Could not create STREAM_UPDATE index")
        print()
        print("🔄 ALTERNATIVE SOLUTION:")
        print("Use Discovery Engine instead of RAG Engine:")
        print("1. Go to Discovery Engine > Data Stores")
        print("2. Create new Data Store")
        print("3. Connect to your Cloud Storage bucket")
        print("4. Use existing cblm-search app")

if __name__ == "__main__":
    main()
EOF

# Run the Python script
echo "🐍 Running Python script to create STREAM_UPDATE index..."
python create_stream_update_index.py

echo ""
echo "📋 INSTRUCTIONS:"
echo "1. If successful, wait 5-10 minutes for index to be ready"
echo "2. Go to Vertex AI RAG Engine > Create Corpus"
echo "3. Select the STREAM_UPDATE index"
echo "4. Create your corpus successfully!"
echo ""
echo "🔄 ALTERNATIVE:"
echo "If this fails, use Discovery Engine instead:"
echo "1. Go to Discovery Engine > Data Stores"
echo "2. Create new Data Store"
echo "3. Connect to your Cloud Storage bucket"
echo "4. Use existing cblm-search app"
