# Orchestrator - DAG runner with connectors
import logging
import time
import json
import uuid
from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime
import re
import os
from .deps import get_openai, get_anthropic, get_redis, get_db_session
from .nha import get_nha_adapter, CB_TARIFF
from .rag import search_rag_chunks
from .metrics import record_flow_run, record_flow_node

logger = logging.getLogger(__name__)

# Environment variables
ORCH_ENABLED = os.getenv("ORCH_ENABLED", "0") == "1"
WORKER_TIMEOUT = int(os.getenv("WORKER_TIMEOUT", "15"))
WORKER_RETRY_COUNT = int(os.getenv("WORKER_RETRY_COUNT", "2"))

class RunContext(TypedDict):
    run_id: str
    flow_id: str
    trace_id: str
    mode: str  # live|dry
    trigger_ref: Dict[str, Any]

class ConnectorResult(TypedDict):
    ok: bool
    output: Dict[str, Any]
    logs: List[str]

class Connector:
    """Base connector class"""
    
    def __init__(self, node_id: str, node_type: str, params: Dict[str, Any]):
        self.node_id = node_id
        self.node_type = node_type
        self.params = params
    
    def run(self, input: Dict[str, Any], context: RunContext) -> ConnectorResult:
        """Execute connector logic"""
        raise NotImplementedError

class TriggerNewPostConnector(Connector):
    """Trigger connector for new posts"""
    
    def run(self, input: Dict[str, Any], context: RunContext) -> ConnectorResult:
        # This is handled by the orchestrator, not by individual nodes
        return {
            "ok": True,
            "output": context["trigger_ref"],
            "logs": ["Trigger.NewPost activated"]
        }

class ActionNHAInvokeConnector(Connector):
    """NHA invocation connector"""
    
    def run(self, input: Dict[str, Any], context: RunContext) -> ConnectorResult:
        agent = self.params.get("agent", "sentiment")
        text = self.params.get("text", "")
        
        # Resolve template variables
        text = self._resolve_template(text, input)
        
        logs = [f"Invoking NHA {agent} on text: {text[:100]}..."]
        
        try:
            adapter = get_nha_adapter(agent)
            if not adapter:
                return {
                    "ok": False,
                    "output": {"error": f"No adapter for agent {agent}"},
                    "logs": logs + [f"ERROR: No adapter for agent {agent}"]
                }
            
            # Process with adapter
            result = adapter.process({"text": text})
            
            logs.append(f"NHA {agent} completed successfully")
            
            return {
                "ok": True,
                "output": result,
                "logs": logs
            }
            
        except Exception as e:
            logs.append(f"ERROR: NHA {agent} failed: {str(e)}")
            return {
                "ok": False,
                "output": {"error": str(e)},
                "logs": logs
            }
    
    def _resolve_template(self, text: str, input: Dict[str, Any]) -> str:
        """Simple template resolution"""
        # Replace {{variable}} with values from input
        def replace_var(match):
            var_path = match.group(1).strip()
            try:
                # Simple path resolution (e.g., "trigger.post.text")
                parts = var_path.split('.')
                value = input
                for part in parts:
                    value = value[part]
                return str(value)
            except (KeyError, TypeError):
                return f"{{{{ {var_path} }}}}"
        
        return re.sub(r'\{\{([^}]+)\}\}', replace_var, text)

class ActionRAGQueryConnector(Connector):
    """RAG query connector"""
    
    def run(self, input: Dict[str, Any], context: RunContext) -> ConnectorResult:
        panel = self.params.get("panel", "user")
        q = self.params.get("q", "")
        k = self.params.get("k", 5)
        
        # Resolve template variables
        q = self._resolve_template(q, input)
        
        logs = [f"RAG query on panel {panel}: {q[:100]}..."]
        
        try:
            db = get_db_session()
            openai_client = get_openai()
            
            # Search RAG chunks
            results = search_rag_chunks(
                db=db,
                panel=panel,
                query=q,
                k=k,
                openai_client=openai_client
            )
            
            logs.append(f"RAG query returned {len(results)} results")
            
            return {
                "ok": True,
                "output": {"results": results, "query": q, "k": k},
                "logs": logs
            }
            
        except Exception as e:
            logs.append(f"ERROR: RAG query failed: {str(e)}")
            return {
                "ok": False,
                "output": {"error": str(e)},
                "logs": logs
            }
        finally:
            db.close()
    
    def _resolve_template(self, text: str, input: Dict[str, Any]) -> str:
        """Simple template resolution"""
        def replace_var(match):
            var_path = match.group(1).strip()
            try:
                parts = var_path.split('.')
                value = input
                for part in parts:
                    value = value[part]
                return str(value)
            except (KeyError, TypeError):
                return f"{{{{ {var_path} }}}}"
        
        return re.sub(r'\{\{([^}]+)\}\}', replace_var, text)

class ActionPostCommentConnector(Connector):
    """Post comment connector"""
    
    def run(self, input: Dict[str, Any], context: RunContext) -> ConnectorResult:
        post_id = self.params.get("post_id", "")
        text = self.params.get("text", "")
        author = self.params.get("author", "@orchestrator")
        
        # Resolve template variables
        post_id = self._resolve_template(post_id, input)
        text = self._resolve_template(text, input)
        
        logs = [f"Posting comment to {post_id}: {text[:100]}..."]
        
        if context["mode"] == "dry":
            logs.append("DRY RUN: Comment not posted")
            return {
                "ok": True,
                "output": {"dry_run": True, "post_id": post_id, "text": text},
                "logs": logs
            }
        
        try:
            db = get_db_session()
            
            # Create comment
            from .db import Comment
            comment = Comment(
                post_id=post_id,
                author=author,
                text=text,
                meta={
                    "orchestrator": True,
                    "run_id": context["run_id"],
                    "trace_id": context["trace_id"],
                    "node_id": self.node_id
                }
            )
            db.add(comment)
            db.commit()
            
            logs.append(f"Comment posted successfully: {comment.id}")
            
            return {
                "ok": True,
                "output": {"comment_id": str(comment.id), "post_id": post_id},
                "logs": logs
            }
            
        except Exception as e:
            logs.append(f"ERROR: Failed to post comment: {str(e)}")
            return {
                "ok": False,
                "output": {"error": str(e)},
                "logs": logs
            }
        finally:
            db.close()
    
    def _resolve_template(self, text: str, input: Dict[str, Any]) -> str:
        """Simple template resolution"""
        def replace_var(match):
            var_path = match.group(1).strip()
            try:
                parts = var_path.split('.')
                value = input
                for part in parts:
                    value = value[part]
                return str(value)
            except (KeyError, TypeError):
                return f"{{{{ {var_path} }}}}"
        
        return re.sub(r'\{\{([^}]+)\}\}', replace_var, text)

class FilterExpressionConnector(Connector):
    """Expression filter connector"""
    
    def run(self, input: Dict[str, Any], context: RunContext) -> ConnectorResult:
        expr = self.params.get("expr", "true")
        
        logs = [f"Evaluating expression: {expr}"]
        
        try:
            # Simple expression evaluation (safe subset)
            result = self._evaluate_expression(expr, input)
            
            logs.append(f"Expression result: {result}")
            
            return {
                "ok": True,
                "output": {"passed": result, "expression": expr},
                "logs": logs
            }
            
        except Exception as e:
            logs.append(f"ERROR: Expression evaluation failed: {str(e)}")
            return {
                "ok": False,
                "output": {"error": str(e), "passed": False},
                "logs": logs
            }
    
    def _evaluate_expression(self, expr: str, input: Dict[str, Any]) -> bool:
        """Safe expression evaluation"""
        # Replace variables with values
        def replace_var(match):
            var_path = match.group(1).strip()
            try:
                parts = var_path.split('.')
                value = input
                for part in parts:
                    value = value[part]
                return repr(value)
            except (KeyError, TypeError):
                return "None"
        
        # Replace {{variable}} with repr(value)
        safe_expr = re.sub(r'\{\{([^}]+)\}\}', replace_var, expr)
        
        # Only allow safe operations
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._()[]'\"=<>! ")
        if not all(c in allowed_chars for c in safe_expr):
            raise ValueError("Expression contains unsafe characters")
        
        # Evaluate safely
        try:
            return bool(eval(safe_expr))
        except:
            return False

class EnrichMapConnector(Connector):
    """Map enrichment connector"""
    
    def run(self, input: Dict[str, Any], context: RunContext) -> ConnectorResult:
        mapping = self.params.get("mapping", {})
        
        logs = [f"Applying mapping: {mapping}"]
        
        try:
            output = {}
            for key, value in mapping.items():
                if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                    # Template variable
                    var_path = value[2:-2].strip()
                    try:
                        parts = var_path.split('.')
                        val = input
                        for part in parts:
                            val = val[part]
                        output[key] = val
                    except (KeyError, TypeError):
                        output[key] = None
                else:
                    output[key] = value
            
            logs.append(f"Mapping completed: {output}")
            
            return {
                "ok": True,
                "output": output,
                "logs": logs
            }
            
        except Exception as e:
            logs.append(f"ERROR: Mapping failed: {str(e)}")
            return {
                "ok": False,
                "output": {"error": str(e)},
                "logs": logs
            }

class DelayConnector(Connector):
    """Delay connector"""
    
    def run(self, input: Dict[str, Any], context: RunContext) -> ConnectorResult:
        delay_ms = self.params.get("delay_ms", 1000)
        
        # Limit delay in dev
        if delay_ms > 5000:
            delay_ms = 5000
        
        logs = [f"Delaying for {delay_ms}ms"]
        
        try:
            time.sleep(delay_ms / 1000.0)
            logs.append("Delay completed")
            
            return {
                "ok": True,
                "output": {"delay_ms": delay_ms},
                "logs": logs
            }
            
        except Exception as e:
            logs.append(f"ERROR: Delay failed: {str(e)}")
            return {
                "ok": False,
                "output": {"error": str(e)},
                "logs": logs
            }

class EmitEventConnector(Connector):
    """Emit event connector"""
    
    def run(self, input: Dict[str, Any], context: RunContext) -> ConnectorResult:
        event_type = self.params.get("event_type", "info")
        message = self.params.get("message", "")
        data = self.params.get("data", {})
        
        logs = [f"Emitting event {event_type}: {message}"]
        
        try:
            # Log event
            db = get_db_session()
            
            from .db import RunEvent
            event = RunEvent(
                run_id=context["run_id"],
                level=event_type,
                node_id=self.node_id,
                message=message,
                data=data
            )
            db.add(event)
            db.commit()
            
            logs.append("Event emitted successfully")
            
            return {
                "ok": True,
                "output": {"event_type": event_type, "message": message},
                "logs": logs
            }
            
        except Exception as e:
            logs.append(f"ERROR: Failed to emit event: {str(e)}")
            return {
                "ok": False,
                "output": {"error": str(e)},
                "logs": logs
            }
        finally:
            db.close()

# Connector registry
CONNECTOR_REGISTRY = {
    "Trigger.NewPost": TriggerNewPostConnector,
    "Action.NHA.Invoke": ActionNHAInvokeConnector,
    "Action.RAG.Query": ActionRAGQueryConnector,
    "Action.PostComment": ActionPostCommentConnector,
    "Filter.Expression": FilterExpressionConnector,
    "Enrich.Map": EnrichMapConnector,
    "Delay": DelayConnector,
    "Emit.Event": EmitEventConnector
}

def get_connector(node_type: str, node_id: str, params: Dict[str, Any]) -> Connector:
    """Get connector instance"""
    connector_class = CONNECTOR_REGISTRY.get(node_type)
    if not connector_class:
        raise ValueError(f"Unknown connector type: {node_type}")
    
    return connector_class(node_id, node_type, params)

def queue_flow_run(flow_id: str, version: int, mode: str, trigger_ref: Dict[str, Any]) -> str:
    """Queue flow run"""
    
    run_id = str(uuid.uuid4())
    trace_id = str(uuid.uuid4())
    
    # Create flow run record
    db = get_db_session()
    try:
        from .db import FlowRun
        flow_run = FlowRun(
            id=run_id,
            flow_id=flow_id,
            version=version,
            status="queued",
            trigger_ref=trigger_ref,
            trace_id=trace_id
        )
        db.add(flow_run)
        db.commit()
        
        # Queue in Redis (if available)
        redis_client = get_redis()
        if redis_client:
            job_data = {
                "run_id": run_id,
                "flow_id": flow_id,
                "version": str(version),
                "mode": mode,
                "trace_id": trace_id
            }
            redis_client.xadd("flows:jobs", job_data)
            logger.info(f"Queued flow run {run_id}")
        
        return run_id
        
    except Exception as e:
        logger.error(f"Failed to queue flow run: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def process_flow_run(run_id: str) -> Dict[str, Any]:
    """Process flow run"""
    
    db = get_db_session()
    try:
        from .db import FlowRun, Flow, NodeCache, RunEvent
        
        # Get flow run
        flow_run = db.query(FlowRun).filter(FlowRun.id == run_id).first()
        if not flow_run:
            raise Exception(f"Flow run {run_id} not found")
        
        # Get flow
        flow = db.query(Flow).filter(Flow.id == flow_run.flow_id).first()
        if not flow:
            raise Exception(f"Flow {flow_run.flow_id} not found")
        
        # Update status to running
        flow_run.status = "running"
        flow_run.started_at = datetime.utcnow()
        db.commit()
        
        # Build context
        context = {
            "run_id": run_id,
            "flow_id": flow_run.flow_id,
            "trace_id": flow_run.trace_id,
            "mode": "live",  # TODO: get from job data
            "trigger_ref": flow_run.trigger_ref or {}
        }
        
        # Process nodes in topological order
        spec = flow.spec
        nodes = {node["id"]: node for node in spec["nodes"]}
        edges = spec["edges"]
        
        # Build dependency graph
        dependencies = {}
        for edge in edges:
            from_node = edge["from"]
            to_node = edge["to"]
            if to_node not in dependencies:
                dependencies[to_node] = []
            dependencies[to_node].append(from_node)
        
        # Topological sort
        visited = set()
        completed = set()
        node_outputs = {}
        
        def process_node(node_id: str):
            if node_id in visited:
                return
            visited.add(node_id)
            
            # Check dependencies
            deps = dependencies.get(node_id, [])
            for dep in deps:
                if dep not in completed:
                    process_node(dep)
            
            # Process node
            node = nodes[node_id]
            node_type = node["type"]
            params = node.get("params", {})
            
            # Check if condition
            if "if" in node:
                condition = node["if"]
                if not _evaluate_condition(condition, node_outputs):
                    # Skip node
                    node_cache = NodeCache(
                        id=str(uuid.uuid4()),
                        run_id=run_id,
                        node_id=node_id,
                        status="skipped",
                        output={"skipped": True, "condition": condition}
                    )
                    db.add(node_cache)
                    completed.add(node_id)
                    return
            
            # Create connector
            connector = get_connector(node_type, node_id, params)
            
            # Execute node
            start_time = time.time()
            node_cache = NodeCache(
                id=str(uuid.uuid4()),
                run_id=run_id,
                node_id=node_id,
                status="running",
                started_at=datetime.utcnow()
            )
            db.add(node_cache)
            db.flush()
            
            try:
                result = connector.run(node_outputs, context)
                took_ms = int((time.time() - start_time) * 1000)
                
                # Update node cache
                node_cache.status = "success" if result["ok"] else "failed"
                node_cache.output = result["output"]
                node_cache.finished_at = datetime.utcnow()
                node_cache.took_ms = took_ms
                
                # Record metrics
                record_flow_node(node_type, "success" if result["ok"] else "failed", took_ms)
                
                # Log events
                for log_msg in result["logs"]:
                    event = RunEvent(
                        run_id=run_id,
                        level="info",
                        node_id=node_id,
                        message=log_msg
                    )
                    db.add(event)
                
                if result["ok"]:
                    node_outputs[node_id] = result["output"]
                    completed.add(node_id)
                else:
                    # Mark flow as failed
                    flow_run.status = "failed"
                    flow_run.finished_at = datetime.utcnow()
                    db.commit()
                    return {"status": "failed", "error": result["output"].get("error")}
                
            except Exception as e:
                node_cache.status = "failed"
                node_cache.output = {"error": str(e)}
                node_cache.finished_at = datetime.utcnow()
                node_cache.took_ms = int((time.time() - start_time) * 1000)
                
                # Log error event
                event = RunEvent(
                    run_id=run_id,
                    level="error",
                    node_id=node_id,
                    message=f"Node failed: {str(e)}"
                )
                db.add(event)
                
                flow_run.status = "failed"
                flow_run.finished_at = datetime.utcnow()
                db.commit()
                return {"status": "failed", "error": str(e)}
        
        # Process all nodes
        for node_id in nodes:
            if node_id not in completed:
                process_node(node_id)
        
        # Mark flow as successful
        flow_run.status = "success"
        flow_run.finished_at = datetime.utcnow()
        db.commit()
        
        # Record metrics
        total_latency_ms = int((datetime.utcnow() - flow_run.started_at).total_seconds() * 1000)
        record_flow_run("success", total_latency_ms)
        
        logger.info(f"Flow run {run_id} completed successfully")
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Failed to process flow run {run_id}: {e}")
        if 'flow_run' in locals():
            flow_run.status = "failed"
            flow_run.finished_at = datetime.utcnow()
            db.commit()
            
            # Record metrics
            total_latency_ms = int((datetime.utcnow() - flow_run.started_at).total_seconds() * 1000)
            record_flow_run("failed", total_latency_ms)
        raise
    finally:
        db.close()

def _evaluate_condition(condition: str, node_outputs: Dict[str, Any]) -> bool:
    """Evaluate node condition"""
    # Simple condition evaluation
    # e.g., "n1.passed" or "n2.output.score > 0.5"
    try:
        if condition in node_outputs:
            return bool(node_outputs[condition])
        
        # Parse condition like "n1.passed"
        parts = condition.split('.')
        if len(parts) == 2:
            node_id, field = parts
            if node_id in node_outputs:
                return bool(node_outputs[node_id].get(field, False))
        
        return False
    except:
        return False
