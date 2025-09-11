#!/usr/bin/env python3
"""
🚀 CoolBits.ai Local RAG System with GPU Processing
Simulates Vertex AI Search and Vector Search locally using RTX 2060

Author: oCopilot (oCursor)
Date: September 5, 2025
"""

import os
import json
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import asyncio
from dataclasses import dataclass
from datetime import datetime

# GPU Processing
import torch
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import chromadb
from chromadb.config import Settings

# Document Processing
import PyPDF2
import docx
import markdown
from bs4 import BeautifulSoup
import requests

# API Framework
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn


# Configuration
@dataclass
class RAGConfig:
    """Configuration for Local RAG System"""

    # GPU Settings
    gpu_enabled: bool = True
    cuda_device: int = 0
    memory_fraction: float = 0.8

    # Model Settings
    embedding_model: str = "all-MiniLM-L6-v2"  # Lightweight for RTX 2060
    embedding_dimension: int = 384
    batch_size: int = 32

    # Vector Database
    vector_db_type: str = "faiss"  # or "chromadb"
    index_path: str = "./rag_indexes"

    # Search Settings
    top_k: int = 10
    similarity_threshold: float = 0.7

    # API Settings
    api_port: int = 8087
    api_host: str = "localhost"


class GPUMonitor:
    """GPU Memory and Performance Monitor"""

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.gpu_available = torch.cuda.is_available()

    def get_gpu_info(self) -> Dict[str, Any]:
        """Get GPU information and status"""
        if not self.gpu_available:
            return {"available": False, "error": "CUDA not available"}

        try:
            gpu_name = torch.cuda.get_device_name(0)
            total_memory = torch.cuda.get_device_properties(0).total_memory
            allocated_memory = torch.cuda.memory_allocated(0)
            cached_memory = torch.cuda.memory_reserved(0)

            return {
                "available": True,
                "device_name": gpu_name,
                "total_memory_gb": total_memory / (1024**3),
                "allocated_memory_mb": allocated_memory / (1024**2),
                "cached_memory_mb": cached_memory / (1024**2),
                "memory_usage_percent": (allocated_memory / total_memory) * 100,
                "cuda_version": torch.version.cuda,
            }
        except Exception as e:
            return {"available": False, "error": str(e)}

    def clear_cache(self):
        """Clear GPU memory cache"""
        if self.gpu_available:
            torch.cuda.empty_cache()


class DocumentProcessor:
    """GPU-accelerated document processing"""

    def __init__(self, config: RAGConfig):
        self.config = config
        self.gpu_monitor = GPUMonitor()

    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from various file formats"""
        file_path = Path(file_path)

        try:
            if file_path.suffix.lower() == ".pdf":
                return self._extract_pdf_text(file_path)
            elif file_path.suffix.lower() == ".docx":
                return self._extract_docx_text(file_path)
            elif file_path.suffix.lower() == ".md":
                return self._extract_markdown_text(file_path)
            elif file_path.suffix.lower() == ".html":
                return self._extract_html_text(file_path)
            elif file_path.suffix.lower() == ".txt":
                return self._extract_txt_text(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
        except Exception as e:
            logging.error(f"Error extracting text from {file_path}: {e}")
            return ""

    def _extract_pdf_text(self, file_path: Path) -> str:
        """Extract text from PDF"""
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text

    def _extract_docx_text(self, file_path: Path) -> str:
        """Extract text from DOCX"""
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

    def _extract_markdown_text(self, file_path: Path) -> str:
        """Extract text from Markdown"""
        with open(file_path, "r", encoding="utf-8") as file:
            md_content = file.read()
            html = markdown.markdown(md_content)
            soup = BeautifulSoup(html, "html.parser")
            return soup.get_text()

    def _extract_html_text(self, file_path: Path) -> str:
        """Extract text from HTML"""
        with open(file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file.read(), "html.parser")
            return soup.get_text()

    def _extract_txt_text(self, file_path: Path) -> str:
        """Extract text from TXT"""
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    def chunk_document(
        self, text: str, chunk_size: int = 1000, overlap: int = 200
    ) -> List[str]:
        """Split document into overlapping chunks"""
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk.strip())
            start = end - overlap

        return [chunk for chunk in chunks if chunk]


class EmbeddingGenerator:
    """GPU-accelerated embedding generation"""

    def __init__(self, config: RAGConfig):
        self.config = config
        self.gpu_monitor = GPUMonitor()
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load sentence transformer model on GPU"""
        try:
            logging.info(f"Loading embedding model: {self.config.embedding_model}")
            self.model = SentenceTransformer(self.config.embedding_model)

            if self.gpu_monitor.gpu_available and self.config.gpu_enabled:
                self.model = self.model.to(self.gpu_monitor.device)
                logging.info(f"✅ Model loaded on GPU: {self.gpu_monitor.device}")
            else:
                logging.warning("⚠️ Model loaded on CPU (GPU not available)")

        except Exception as e:
            logging.error(f"Error loading model: {e}")
            raise

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for texts using GPU"""
        try:
            if not self.model:
                raise ValueError("Model not loaded")

            # Process in batches to manage GPU memory
            embeddings = []
            batch_size = self.config.batch_size

            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i : i + batch_size]

                # Generate embeddings
                batch_embeddings = self.model.encode(
                    batch_texts, convert_to_numpy=True, show_progress_bar=False
                )

                embeddings.append(batch_embeddings)

                # Clear cache periodically
                if i % (batch_size * 4) == 0:
                    self.gpu_monitor.clear_cache()

            # Concatenate all embeddings
            all_embeddings = np.vstack(embeddings)

            logging.info(f"✅ Generated {len(all_embeddings)} embeddings")
            return all_embeddings

        except Exception as e:
            logging.error(f"Error generating embeddings: {e}")
            raise


class VectorDatabase:
    """Local vector database with FAISS and ChromaDB support"""

    def __init__(self, config: RAGConfig):
        self.config = config
        self.index_path = Path(config.index_path)
        self.index_path.mkdir(exist_ok=True)

        # Initialize based on type
        if config.vector_db_type == "faiss":
            self._init_faiss()
        elif config.vector_db_type == "chromadb":
            self._init_chromadb()
        else:
            raise ValueError(f"Unsupported vector DB type: {config.vector_db_type}")

    def _init_faiss(self):
        """Initialize FAISS index"""
        self.index = None
        self.documents = []
        self.metadata = []

    def _init_chromadb(self):
        """Initialize ChromaDB"""
        self.client = chromadb.Client(
            Settings(
                persist_directory=str(self.index_path / "chromadb"),
                anonymized_telemetry=False,
            )
        )

        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="coolbits_rag",
            metadata={"description": "CoolBits.ai Local RAG Collection"},
        )

    def add_documents(
        self, documents: List[str], embeddings: np.ndarray, metadata: List[Dict] = None
    ):
        """Add documents and embeddings to vector database"""
        if self.config.vector_db_type == "faiss":
            self._add_to_faiss(documents, embeddings, metadata)
        elif self.config.vector_db_type == "chromadb":
            self._add_to_chromadb(documents, embeddings, metadata)

    def _add_to_faiss(
        self, documents: List[str], embeddings: np.ndarray, metadata: List[Dict] = None
    ):
        """Add to FAISS index"""
        if self.index is None:
            # Create new index
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(
                dimension
            )  # Inner product for cosine similarity

        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)

        # Add to index
        self.index.add(embeddings.astype("float32"))

        # Store documents and metadata
        self.documents.extend(documents)
        if metadata:
            self.metadata.extend(metadata)
        else:
            self.metadata.extend([{}] * len(documents))

        logging.info(f"✅ Added {len(documents)} documents to FAISS index")

    def _add_to_chromadb(
        self, documents: List[str], embeddings: np.ndarray, metadata: List[Dict] = None
    ):
        """Add to ChromaDB"""
        # Convert embeddings to list format
        embeddings_list = embeddings.tolist()

        # Prepare metadata
        if metadata is None:
            metadata = [{"index": i} for i in range(len(documents))]

        # Add to collection
        self.collection.add(
            documents=documents,
            embeddings=embeddings_list,
            metadatas=metadata,
            ids=[f"doc_{i}" for i in range(len(documents))],
        )

        logging.info(f"✅ Added {len(documents)} documents to ChromaDB")

    def search(self, query_embedding: np.ndarray, top_k: int = None) -> List[Dict]:
        """Search for similar documents"""
        if top_k is None:
            top_k = self.config.top_k

        if self.config.vector_db_type == "faiss":
            return self._search_faiss(query_embedding, top_k)
        elif self.config.vector_db_type == "chromadb":
            return self._search_chromadb(query_embedding, top_k)

    def _search_faiss(self, query_embedding: np.ndarray, top_k: int) -> List[Dict]:
        """Search FAISS index"""
        if self.index is None:
            return []

        # Normalize query embedding
        query_embedding = query_embedding.reshape(1, -1)
        faiss.normalize_L2(query_embedding)

        # Search
        scores, indices = self.index.search(query_embedding.astype("float32"), top_k)

        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.documents):
                results.append(
                    {
                        "document": self.documents[idx],
                        "score": float(score),
                        "metadata": (
                            self.metadata[idx] if idx < len(self.metadata) else {}
                        ),
                    }
                )

        return results

    def _search_chromadb(self, query_embedding: np.ndarray, top_k: int) -> List[Dict]:
        """Search ChromaDB"""
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()], n_results=top_k
        )

        formatted_results = []
        for i in range(len(results["documents"][0])):
            formatted_results.append(
                {
                    "document": results["documents"][0][i],
                    "score": results["distances"][0][i],
                    "metadata": results["metadatas"][0][i],
                }
            )

        return formatted_results

    def save_index(self, name: str):
        """Save index to disk"""
        if self.config.vector_db_type == "faiss":
            faiss.write_index(self.index, str(self.index_path / f"{name}.faiss"))
            # Save documents and metadata
            with open(self.index_path / f"{name}_docs.json", "w") as f:
                json.dump({"documents": self.documents, "metadata": self.metadata}, f)
        elif self.config.vector_db_type == "chromadb":
            # ChromaDB auto-persists
            pass

    def load_index(self, name: str):
        """Load index from disk"""
        if self.config.vector_db_type == "faiss":
            self.index = faiss.read_index(str(self.index_path / f"{name}.faiss"))
            # Load documents and metadata
            with open(self.index_path / f"{name}_docs.json", "r") as f:
                data = json.load(f)
                self.documents = data["documents"]
                self.metadata = data["metadata"]


class LocalRAGSystem:
    """Main Local RAG System"""

    def __init__(self, config: RAGConfig):
        self.config = config
        self.gpu_monitor = GPUMonitor()
        self.document_processor = DocumentProcessor(config)
        self.embedding_generator = EmbeddingGenerator(config)
        self.vector_db = VectorDatabase(config)

        # Initialize FastAPI
        self.app = FastAPI(
            title="CoolBits.ai Local RAG System",
            description="Local RAG system with GPU processing",
            version="1.0.0",
        )

        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self._setup_routes()

    def _setup_routes(self):
        """Setup API routes"""

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            gpu_info = self.gpu_monitor.get_gpu_info()
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "gpu": gpu_info,
                "config": {
                    "embedding_model": self.config.embedding_model,
                    "vector_db_type": self.config.vector_db_type,
                    "gpu_enabled": self.config.gpu_enabled,
                },
            }

        @self.app.post("/documents/upload")
        async def upload_document(file: UploadFile = File(...)):
            """Upload and process document"""
            try:
                # Save uploaded file
                file_path = f"./temp_{file.filename}"
                with open(file_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)

                # Process document
                text = self.document_processor.extract_text_from_file(file_path)
                chunks = self.document_processor.chunk_document(text)

                # Generate embeddings
                embeddings = self.embedding_generator.generate_embeddings(chunks)

                # Add to vector database
                metadata = [
                    {"filename": file.filename, "chunk_id": i}
                    for i in range(len(chunks))
                ]
                self.vector_db.add_documents(chunks, embeddings, metadata)

                # Cleanup
                os.remove(file_path)

                return {
                    "status": "success",
                    "filename": file.filename,
                    "chunks_processed": len(chunks),
                    "embeddings_generated": len(embeddings),
                }

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/search")
        async def search_documents(query: Dict[str, str]):
            """Search documents"""
            try:
                query_text = query.get("query", "")
                top_k = query.get("top_k", self.config.top_k)

                # Generate query embedding
                query_embedding = self.embedding_generator.generate_embeddings(
                    [query_text]
                )[0]

                # Search vector database
                results = self.vector_db.search(query_embedding, top_k)

                # Filter by similarity threshold
                filtered_results = [
                    r for r in results if r["score"] >= self.config.similarity_threshold
                ]

                return {
                    "query": query_text,
                    "results": filtered_results,
                    "total_found": len(filtered_results),
                    "gpu_used": self.gpu_monitor.gpu_available,
                }

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/gpu/status")
        async def gpu_status():
            """Get GPU status and performance"""
            return self.gpu_monitor.get_gpu_info()

        @self.app.post("/gpu/clear-cache")
        async def clear_gpu_cache():
            """Clear GPU memory cache"""
            self.gpu_monitor.clear_cache()
            return {"status": "cache_cleared"}

    def run(self):
        """Run the RAG system"""
        logging.info("🚀 Starting CoolBits.ai Local RAG System")
        logging.info(f"GPU Available: {self.gpu_monitor.gpu_available}")

        if self.gpu_monitor.gpu_available:
            gpu_info = self.gpu_monitor.get_gpu_info()
            logging.info(f"GPU: {gpu_info['device_name']}")
            logging.info(f"Memory: {gpu_info['total_memory_gb']:.1f} GB")

        uvicorn.run(
            self.app,
            host=self.config.api_host,
            port=self.config.api_port,
            log_level="info",
        )


def main():
    """Main function"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Configuration
    config = RAGConfig()

    # Create and run RAG system
    rag_system = LocalRAGSystem(config)
    rag_system.run()


if __name__ == "__main__":
    main()
