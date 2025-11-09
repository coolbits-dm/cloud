#!/usr/bin/env python3
# cblm/rag/build_index.py - Build RAG local index

import json
import os
from pathlib import Path
from str import s_read_text, s_write_text_atomic, stable_uuid
import andrei

def build_fake_embedding(text: str) -> list:
    """Create fake embedding for M18 (deterministic hash-based)."""
    # Simple hash-based fake embedding for M18
    hash_val = hash(text) % 1000000
    embedding = []
    for i in range(128):  # 128-dim embedding
        val = (hash_val + i * 7919) % 1000 / 1000.0  # Normalize to 0-1
        embedding.append(val)
    return embedding

def chunk_text(text: str, chunk_size: int = 500) -> list:
    """Split text into chunks."""
    words = text.split()
    chunks = []
    current_chunk = []
    
    for word in words:
        current_chunk.append(word)
        if len(' '.join(current_chunk)) > chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def build_panel_index(panel: str):
    """Build RAG index for a specific panel."""
    print(f"Building RAG index for {panel}...")
    
    # Collect content sources
    content_sources = []
    
    # 1. Panel state
    if os.path.exists("panel/state.json"):
        state_text = s_read_text("panel/state.json")
        content_sources.append(f"Panel State: {state_text}")
    
    # 2. Wall content
    wall_path = andrei.get_wall_path(panel)
    if os.path.exists(wall_path):
        wall_data = json.loads(s_read_text(wall_path))
        for post in wall_data.get("posts", []):
            content_sources.append(f"Wall Post: {post.get('text', '')}")
    
    # 3. Board content
    board_path = andrei.get_board_path(panel)
    if os.path.exists(board_path):
        board_data = json.loads(s_read_text(board_path))
        content_sources.append(f"Board Charter: {board_data.get('charter', '')}")
    
    # 4. Documentation (if exists)
    docs_path = f"sites/{panel}/docs"
    if os.path.exists(docs_path):
        for doc_file in Path(docs_path).glob("*.md"):
            content_sources.append(f"Documentation: {s_read_text(str(doc_file))}")
    
    # Build index
    index_data = {
        "panel": panel,
        "chunks": [],
        "metadata": {
            "total_chunks": 0,
            "total_sources": len(content_sources),
            "build_timestamp": andrei.ts_now_iso() if hasattr(andrei, 'ts_now_iso') else "2025-01-01T00:00:00Z"
        }
    }
    
    # Process each content source
    for source_text in content_sources:
        chunks = chunk_text(source_text)
        for chunk in chunks:
            chunk_data = {
                "id": stable_uuid("chunk", panel, chunk[:50]),
                "text": chunk,
                "embedding": build_fake_embedding(chunk),
                "source": "local",
                "metadata": {"panel": panel}
            }
            index_data["chunks"].append(chunk_data)
    
    index_data["metadata"]["total_chunks"] = len(index_data["chunks"])
    
    # Save index
    rag_path = andrei.get_rag_path(panel)
    s_write_text_atomic(rag_path, json.dumps(index_data, indent=2))
    print(f"✓ Built RAG index for {panel}: {len(index_data['chunks'])} chunks")

def main():
    """Main RAG build function."""
    print("RAG Build: Starting local index construction...")
    
    # Build index for each panel
    for panel in andrei.PANELS:
        build_panel_index(panel)
    
    print("RAG Build: Local index construction completed!")

if __name__ == "__main__":
    main()
