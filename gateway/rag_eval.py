# RAG Connect & Eval harness for M20.4
import os
import json
import logging
import hashlib
import yaml
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
import numpy as np
from sklearn.metrics import ndcg_score
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Environment variables
RAG_VARIANT = os.getenv("RAG_VARIANT", "A")  # A or B for canary
EVAL_THRESHOLD_NDCG = float(os.getenv("EVAL_THRESHOLD_NDCG", "0.70"))
EVAL_THRESHOLD_RECALL = float(os.getenv("EVAL_THRESHOLD_RECALL", "0.85"))
EVAL_THRESHOLD_P95 = float(os.getenv("EVAL_THRESHOLD_P95", "300"))

class RAGConnector:
    """Base class for RAG connectors"""
    
    def __init__(self, name: str):
        self.name = name
    
    def connect(self, config: Dict[str, Any]) -> bool:
        """Test connection to source"""
        raise NotImplementedError
    
    def ingest(self, config: Dict[str, Any], org_id: str, space: str) -> List[Dict[str, Any]]:
        """Ingest content from source"""
        raise NotImplementedError

class FSLocalConnector(RAGConnector):
    """Local filesystem connector"""
    
    def __init__(self):
        super().__init__("fs_local")
    
    def connect(self, config: Dict[str, Any]) -> bool:
        """Test filesystem access"""
        try:
            path = Path(config.get("path", ""))
            return path.exists() and path.is_dir()
        except:
            return False
    
    def ingest(self, config: Dict[str, Any], org_id: str, space: str) -> List[Dict[str, Any]]:
        """Ingest files from local directory"""
        chunks = []
        path = Path(config.get("path", ""))
        
        if not path.exists():
            return chunks
        
        for file_path in path.rglob("*"):
            if file_path.is_file() and file_path.suffix in ['.txt', '.md', '.json']:
                try:
                    content = file_path.read_text(encoding='utf-8')
                    
                    # Split into chunks
                    chunk_size = config.get("chunk_size", 1000)
                    chunk_overlap = config.get("chunk_overlap", 200)
                    
                    for i in range(0, len(content), chunk_size - chunk_overlap):
                        chunk_text = content[i:i + chunk_size]
                        if chunk_text.strip():
                            chunks.append({
                                "content": chunk_text,
                                "source_uri": f"file://{file_path}",
                                "chunk_id": f"{file_path.stem}_{i}",
                                "metadata": {
                                    "file_path": str(file_path),
                                    "chunk_index": i // (chunk_size - chunk_overlap),
                                    "org_id": org_id,
                                    "space": space
                                }
                            })
                except Exception as e:
                    logger.warning(f"Failed to read {file_path}: {e}")
        
        return chunks

class HTTPSitemapConnector(RAGConnector):
    """HTTP sitemap connector"""
    
    def __init__(self):
        super().__init__("http_sitemap")
    
    def connect(self, config: Dict[str, Any]) -> bool:
        """Test HTTP access"""
        try:
            url = config.get("base_url", "")
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def ingest(self, config: Dict[str, Any], org_id: str, space: str) -> List[Dict[str, Any]]:
        """Ingest content from sitemap"""
        chunks = []
        base_url = config.get("base_url", "")
        sitemap_url = config.get("sitemap_url", f"{base_url}/sitemap.xml")
        
        try:
            # Parse sitemap
            response = requests.get(sitemap_url, timeout=30)
            if response.status_code != 200:
                return chunks
            
            soup = BeautifulSoup(response.content, 'xml')
            urls = soup.find_all('url')
            
            for url_elem in urls[:config.get("max_pages", 50)]:  # Limit for dev
                loc = url_elem.find('loc')
                if loc:
                    page_url = loc.text
                    
                    try:
                        page_response = requests.get(page_url, timeout=10)
                        if page_response.status_code == 200:
                            page_soup = BeautifulSoup(page_response.content, 'html.parser')
                            
                            # Extract text content
                            text_content = page_soup.get_text(separator=' ', strip=True)
                            
                            # Split into chunks
                            chunk_size = config.get("chunk_size", 1000)
                            for i in range(0, len(text_content), chunk_size):
                                chunk_text = text_content[i:i + chunk_size]
                                if chunk_text.strip():
                                    chunks.append({
                                        "content": chunk_text,
                                        "source_uri": page_url,
                                        "chunk_id": f"{hashlib.md5(page_url.encode()).hexdigest()[:8]}_{i}",
                                        "metadata": {
                                            "page_url": page_url,
                                            "chunk_index": i // chunk_size,
                                            "org_id": org_id,
                                            "space": space
                                        }
                                    })
                    except Exception as e:
                        logger.warning(f"Failed to fetch {page_url}: {e}")
                        
        except Exception as e:
            logger.error(f"Failed to parse sitemap: {e}")
        
        return chunks

class RAGIngestionManager:
    """RAG ingestion manager for M20.4"""
    
    def __init__(self, db: Session):
        self.db = db
        self.connectors = {
            "fs_local": FSLocalConnector(),
            "http_sitemap": HTTPSitemapConnector()
        }
    
    def ingest_from_source(self, source: str, config: Dict[str, Any], 
                          org_id: str, space: str) -> Dict[str, Any]:
        """Ingest content from specified source"""
        if source not in self.connectors:
            raise ValueError(f"Unknown connector: {source}")
        
        connector = self.connectors[source]
        
        # Test connection
        if not connector.connect(config):
            raise ConnectionError(f"Failed to connect to {source}")
        
        # Ingest content
        chunks = connector.ingest(config, org_id, space)
        
        # Store chunks in database
        stored_count = 0
        for chunk in chunks:
            try:
                from .db import RAGChunk
                
                # Check for duplicates
                existing = self.db.query(RAGChunk).filter(
                    and_(
                        RAGChunk.org_id == org_id,
                        RAGChunk.source_uri == chunk["source_uri"],
                        RAGChunk.chunk_id == chunk["chunk_id"]
                    )
                ).first()
                
                if not existing:
                    rag_chunk = RAGChunk(
                        org_id=org_id,
                        space=space,
                        content=chunk["content"],
                        source_uri=chunk["source_uri"],
                        chunk_id=chunk["chunk_id"],
                        metadata=chunk["metadata"],
                        created_at=datetime.utcnow()
                    )
                    
                    self.db.add(rag_chunk)
                    stored_count += 1
                    
            except Exception as e:
                logger.warning(f"Failed to store chunk: {e}")
        
        self.db.commit()
        
        return {
            "source": source,
            "chunks_ingested": len(chunks),
            "chunks_stored": stored_count,
            "org_id": org_id,
            "space": space
        }

class RAGEvaluationManager:
    """RAG evaluation manager for M20.4"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def load_golden_set(self, org_id: str, space: str) -> List[Dict[str, Any]]:
        """Load golden evaluation set"""
        golden_set_path = Path(f"artifacts/dev/eval/{org_id}/{space}/golden_set.yaml")
        
        if not golden_set_path.exists():
            # Create default golden set
            golden_set_path.parent.mkdir(parents=True, exist_ok=True)
            default_set = [
                {
                    "qid": "u001",
                    "query": "politica de resetare parole",
                    "ideal": ["doc://policy/resetare_parole#h2", "doc://policy/resetare_parole#h3"]
                },
                {
                    "qid": "u002", 
                    "query": "cum se configureaza autentificarea",
                    "ideal": ["doc://auth/setup", "doc://auth/config"]
                }
            ]
            
            with open(golden_set_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_set, f, default_flow_style=False, allow_unicode=True)
        
        with open(golden_set_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def evaluate_rag(self, org_id: str, space: str, top_k: int = 5) -> Dict[str, Any]:
        """Evaluate RAG performance"""
        golden_set = self.load_golden_set(org_id, space)
        
        results = []
        total_latency = []
        
        for item in golden_set:
            qid = item["qid"]
            query = item["query"]
            ideal = item["ideal"]
            
            # Query RAG system
            start_time = datetime.utcnow()
            
            try:
                from .rag import search_rag_chunks
                chunks = search_rag_chunks(query, org_id, space, top_k)
                
                latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                total_latency.append(latency_ms)
                
                # Calculate metrics
                retrieved_ids = [chunk.get("chunk_id", "") for chunk in chunks]
                
                # Calculate relevance scores (simplified)
                relevance_scores = []
                for chunk_id in retrieved_ids:
                    if chunk_id in ideal:
                        relevance_scores.append(1.0)
                    else:
                        relevance_scores.append(0.0)
                
                # Calculate MRR
                mrr = 0.0
                for i, score in enumerate(relevance_scores):
                    if score > 0:
                        mrr = 1.0 / (i + 1)
                        break
                
                # Calculate nDCG
                ndcg = ndcg_score([ideal], [relevance_scores], k=top_k)
                
                # Calculate Recall
                recall = len(set(retrieved_ids) & set(ideal)) / len(ideal) if ideal else 0.0
                
                results.append({
                    "qid": qid,
                    "query": query,
                    "retrieved_ids": retrieved_ids,
                    "mrr": mrr,
                    "ndcg": ndcg,
                    "recall": recall,
                    "latency_ms": latency_ms
                })
                
            except Exception as e:
                logger.error(f"Failed to evaluate query {qid}: {e}")
                results.append({
                    "qid": qid,
                    "query": query,
                    "error": str(e),
                    "mrr": 0.0,
                    "ndcg": 0.0,
                    "recall": 0.0,
                    "latency_ms": 0.0
                })
        
        # Calculate aggregate metrics
        mrr_scores = [r["mrr"] for r in results if "error" not in r]
        ndcg_scores = [r["ndcg"] for r in results if "ndcg" in r]
        recall_scores = [r["recall"] for r in results if "recall" in r]
        
        avg_mrr = np.mean(mrr_scores) if mrr_scores else 0.0
        avg_ndcg = np.mean(ndcg_scores) if ndcg_scores else 0.0
        avg_recall = np.mean(recall_scores) if recall_scores else 0.0
        
        p50_latency = np.percentile(total_latency, 50) if total_latency else 0.0
        p95_latency = np.percentile(total_latency, 95) if total_latency else 0.0
        
        # Check SLO compliance
        slo_passed = (
            avg_ndcg >= EVAL_THRESHOLD_NDCG and
            avg_recall >= EVAL_THRESHOLD_RECALL and
            p95_latency <= EVAL_THRESHOLD_P95
        )
        
        evaluation_result = {
            "org_id": org_id,
            "space": space,
            "top_k": top_k,
            "timestamp": datetime.utcnow().isoformat(),
            "variant": RAG_VARIANT,
            "results": results,
            "aggregate_metrics": {
                "avg_mrr": float(avg_mrr),
                "avg_ndcg": float(avg_ndcg),
                "avg_recall": float(avg_recall),
                "p50_latency_ms": float(p50_latency),
                "p95_latency_ms": float(p95_latency)
            },
            "slo_compliance": {
                "ndcg_threshold": EVAL_THRESHOLD_NDCG,
                "recall_threshold": EVAL_THRESHOLD_RECALL,
                "p95_threshold_ms": EVAL_THRESHOLD_P95,
                "passed": slo_passed
            }
        }
        
        # Store evaluation result
        self._store_evaluation_result(evaluation_result)
        
        return evaluation_result
    
    def _store_evaluation_result(self, result: Dict[str, Any]):
        """Store evaluation result in database"""
        try:
            from .db import EvalRun
            
            eval_run = EvalRun(
                org_id=result["org_id"],
                space=result["space"],
                variant=result["variant"],
                metrics=result["aggregate_metrics"],
                slo_passed=result["slo_compliance"]["passed"],
                created_at=datetime.utcnow()
            )
            
            self.db.add(eval_run)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to store evaluation result: {e}")
    
    def generate_html_report(self, evaluation_result: Dict[str, Any]) -> str:
        """Generate HTML evaluation report"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>RAG Evaluation Report - {evaluation_result['org_id']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .metrics {{ display: flex; gap: 20px; margin: 20px 0; }}
                .metric {{ background: #e8f4fd; padding: 15px; border-radius: 5px; text-align: center; }}
                .metric.passed {{ background: #d4edda; }}
                .metric.failed {{ background: #f8d7da; }}
                .results {{ margin: 20px 0; }}
                .result {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
                .slo-status {{ font-weight: bold; font-size: 18px; }}
                .slo-passed {{ color: green; }}
                .slo-failed {{ color: red; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>RAG Evaluation Report</h1>
                <p><strong>Organization:</strong> {evaluation_result['org_id']}</p>
                <p><strong>Space:</strong> {evaluation_result['space']}</p>
                <p><strong>Variant:</strong> {evaluation_result['variant']}</p>
                <p><strong>Timestamp:</strong> {evaluation_result['timestamp']}</p>
            </div>
            
            <div class="metrics">
                <div class="metric {'passed' if evaluation_result['aggregate_metrics']['avg_ndcg'] >= EVAL_THRESHOLD_NDCG else 'failed'}">
                    <h3>nDCG@5</h3>
                    <p>{evaluation_result['aggregate_metrics']['avg_ndcg']:.3f}</p>
                    <p>Threshold: {EVAL_THRESHOLD_NDCG}</p>
                </div>
                <div class="metric {'passed' if evaluation_result['aggregate_metrics']['avg_recall'] >= EVAL_THRESHOLD_RECALL else 'failed'}">
                    <h3>Recall@5</h3>
                    <p>{evaluation_result['aggregate_metrics']['avg_recall']:.3f}</p>
                    <p>Threshold: {EVAL_THRESHOLD_RECALL}</p>
                </div>
                <div class="metric {'passed' if evaluation_result['aggregate_metrics']['p95_latency_ms'] <= EVAL_THRESHOLD_P95 else 'failed'}">
                    <h3>P95 Latency</h3>
                    <p>{evaluation_result['aggregate_metrics']['p95_latency_ms']:.1f}ms</p>
                    <p>Threshold: {EVAL_THRESHOLD_P95}ms</p>
                </div>
            </div>
            
            <div class="slo-status {'slo-passed' if evaluation_result['slo_compliance']['passed'] else 'slo-failed'}">
                SLO Status: {'PASSED' if evaluation_result['slo_compliance']['passed'] else 'FAILED'}
            </div>
            
            <div class="results">
                <h2>Query Results</h2>
                {self._generate_query_results_html(evaluation_result['results'])}
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_query_results_html(self, results: List[Dict[str, Any]]) -> str:
        """Generate HTML for query results"""
        html = ""
        for result in results:
            html += f"""
            <div class="result">
                <h3>Query: {result['query']}</h3>
                <p><strong>QID:</strong> {result['qid']}</p>
                <p><strong>MRR:</strong> {result['mrr']:.3f}</p>
                <p><strong>nDCG:</strong> {result['ndcg']:.3f}</p>
                <p><strong>Recall:</strong> {result['recall']:.3f}</p>
                <p><strong>Latency:</strong> {result['latency_ms']:.1f}ms</p>
                <p><strong>Retrieved IDs:</strong> {', '.join(result.get('retrieved_ids', []))}</p>
            </div>
            """
        return html
