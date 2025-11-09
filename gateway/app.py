from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime
import time

# Import local modules
from models import ChatRequest, ChatResponse, RAGQueryRequest, RAGQueryResponse, NHAInvokeRequest, NHAInvokeResponse, InvocationsResponse, LedgerBalance, FlowCreate, FlowResponse, FlowRunRequest, FlowRunResponse, RunEventResponse, FlowRunDetails, MetricsSnapshot
from deps import get_openai, get_anthropic, get_redis, get_db_session
from rag import search_rag_chunks
from nha import queue_nha_invocation, extract_nha_mentions, CB_TARIFF
from ledger import debit_cbt, get_balance
from orchestrator import queue_flow_run, process_flow_run, ORCH_ENABLED
from metrics import get_metrics_snapshot, export_prometheus_metrics, record_nha_invocation, record_rag_query, record_flow_run, record_flow_node, record_error
from rate_limiter import check_rate_limit
from circuit_breaker import call_with_breaker, is_circuit_open, CircuitBreakerOpenException
from auth import get_google_auth_url, exchange_code_for_token, get_user_info, generate_magic_link, verify_magic_link, create_session_token, verify_session_token, generate_csrf_token, verify_csrf_token, generate_pkce_pair
from orgs import get_org_manager
from billing import BillingManager
from sre import SREManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CoolBits Gateway API",
    description="M19 Gateway API for chat, RAG, and agent services",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://coolbits.ai", "https://dev.coolbits.ai"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    # Check rate limit
    allowed, retry_after = check_rate_limit(request)
    
    if not allowed:
        response = JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded", "retry_after": retry_after}
        )
        response.headers["Retry-After"] = str(int(retry_after))
        return response
    
    # Process request
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Add timing header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Environment variables
DB_DSN = os.getenv("DB_DSN", "postgresql://localhost/coolbits_dev")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CB_BILLING_MODE = os.getenv("CB_BILLING_MODE", "dev")

# Routes
@app.get("/")
async def root():
    return {
        "service": "CoolBits Gateway API",
        "version": "0.1.0",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "billing_mode": CB_BILLING_MODE,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    trace_id = str(uuid.uuid4())
    logger.info(f"Chat request {trace_id}: model={request.model}, messages={len(request.messages)}")
    
    try:
        if request.model == "dummy":
            # Dummy response for testing
            reply = f"Dummy response for {len(request.messages)} messages. Trace: {trace_id}"
            usage = {"tokens_in": 10, "tokens_out": 5}
        else:
            # TODO: Implement real AI calls
            reply = f"AI response placeholder for {request.model}. Trace: {trace_id}"
            usage = {"tokens_in": 20, "tokens_out": 10}
        
        return ChatResponse(
            reply=reply,
            usage=usage,
            trace_id=trace_id
        )
    except Exception as e:
        logger.error(f"Chat error {trace_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/rag/query", response_model=RAGQueryResponse)
async def rag_query(request: RAGQueryRequest):
    trace_id = str(uuid.uuid4())
    logger.info(f"RAG query {trace_id}: panel={request.panel}, q='{request.q}', k={request.k}")
    
    try:
        db = get_db_session()
        openai_client = get_openai()
        
        answers = search_rag_chunks(
            db=db,
            panel=request.panel,
            query=request.q,
            k=request.k,
            min_score=0.15,  # Default min score
            openai_client=openai_client
        )
        
        return RAGQueryResponse(
            answers=answers,
            trace_id=trace_id
        )
    except Exception as e:
        logger.error(f"RAG query error {trace_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/nha/invoke", response_model=NHAInvokeResponse)
async def nha_invoke(request: NHAInvokeRequest):
    trace_id = str(uuid.uuid4())
    logger.info(f"NHA invoke {trace_id}: {request.post}")
    
    start_time = time.time()
    
    try:
        # Check circuit breaker for NHA agents
        mentions = extract_nha_mentions(request.post.get("text", ""))
        if not mentions:
            raise HTTPException(status_code=400, detail="No valid NHA mentions found")
        
        # Check circuit breakers for each agent
        for mention in mentions:
            if is_circuit_open(f"nha_{mention}"):
                raise HTTPException(status_code=503, detail=f"Circuit breaker open for agent {mention}")
        
        db = get_db_session()
        
        # Create post
        from .db import Post
        post = Post(
            panel=request.post.get("panel", "user"),
            author=request.post.get("author", "unknown"),
            text=request.post.get("text", ""),
            attachments=request.post.get("attachments", {})
        )
        db.add(post)
        db.flush()  # Get the ID
        
        # Calculate total cost
        total_cost = sum(CB_TARIFF.get(mention, -2) for mention in mentions)
        
        # Create invocations and debit ledger
        invocations = []
        for mention in mentions:
            invocation_id = queue_nha_invocation(
                post_id=post.id,
                agent_id=mention,
                trace_id=trace_id,
                cost_cbT=CB_TARIFF.get(mention, -2)
            )
            invocations.append({
                "id": invocation_id,
                "agent_id": mention,
                "status": "queued"
            })
        
        # Debit ledger
        ledger_entry_id = debit_cbt(
            ref=post.id,
            amount=abs(total_cost),
            reason=f"NHA_INVOCATION: {', '.join(mentions)}",
            meta={"trace_id": trace_id, "mentions": mentions}
        )
        
        db.commit()
        
        # Record metrics
        latency_ms = int((time.time() - start_time) * 1000)
        for mention in mentions:
            record_nha_invocation(mention, "queued", latency_ms)
        
        logger.info(f"NHA invoke {trace_id}: created {len(mentions)} invocations, debited {total_cost} cbT")
        
        return NHAInvokeResponse(
            post_id=post.id,
            invocations=invocations,
            ledger_delta=total_cost,
            trace_id=trace_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Record error metrics
        latency_ms = int((time.time() - start_time) * 1000)
        for mention in mentions:
            record_nha_invocation(mention, "error", latency_ms)
        record_error("/v1/nha/invoke")
        
        logger.error(f"NHA invoke error {trace_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/v1/invocations", response_model=InvocationsResponse)
async def get_invocations(post_id: str):
    """Get invocation status for a post"""
    try:
        db = get_db_session()
        
        from .db import Invocation
        invocations = db.query(Invocation).filter(Invocation.post_id == post_id).all()
        
        result = []
        for inv in invocations:
            result.append({
                "id": inv.id,
                "agent_id": inv.agent_id,
                "status": inv.status,
                "result": inv.result_ref,
                "error": inv.error,
                "cost_cbT": float(inv.cost_cbT),
                "trace_id": inv.trace_id
            })
        
        return InvocationsResponse(invocations=result)
        
    except Exception as e:
        logger.error(f"Get invocations error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/v1/ledger/balance", response_model=LedgerBalance)
async def get_ledger_balance(ref: str):
    """Get cbT balance for reference"""
    try:
        balance = get_balance(ref)
        
        # Get last activity
        db = get_db_session()
        from .db import LedgerEntry
        last_entry = db.query(LedgerEntry).filter(LedgerEntry.ref == ref).order_by(LedgerEntry.ts.desc()).first()
        
        return LedgerBalance(
            balance=balance,
            last_activity=last_entry.ts if last_entry else None
        )
        
    except Exception as e:
        logger.error(f"Get balance error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/v1/metrics/snapshot")
async def metrics_snapshot():
    """Observability V3 metrics endpoint"""
    try:
        return get_metrics_snapshot()
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    try:
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(export_prometheus_metrics())
    except Exception as e:
        logger.error(f"Prometheus metrics error: {e}")
        return PlainTextResponse(f"# Error: {e}")

# Authentication endpoints
@app.get("/v1/auth/google")
async def google_auth():
    """Initiate Google OAuth flow"""
    try:
        state = str(uuid.uuid4())
        code_verifier, code_challenge = generate_pkce_pair()
        
        auth_url = get_google_auth_url(state, code_challenge)
        
        return {
            "auth_url": auth_url,
            "state": state,
            "code_challenge": code_challenge
        }
    except Exception as e:
        logger.error(f"Google auth error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/auth/callback")
async def auth_callback(code: str, state: str, code_verifier: str):
    """Handle OAuth callback"""
    try:
        # Exchange code for tokens
        tokens = exchange_code_for_token(code, code_verifier)
        access_token = tokens["access_token"]
        
        # Get user info
        user_info = get_user_info(access_token)
        
        # Create or get user
        user_id = user_info["sub"]
        email = user_info["email"]
        name = user_info.get("name", email)
        
        # Create session token
        session_token = create_session_token(user_id, "default", "admin")
        
        return {
            "user_id": user_id,
            "email": email,
            "name": name,
            "session_token": session_token
        }
    except Exception as e:
        logger.error(f"Auth callback error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/auth/magic-link")
async def create_magic_link(email: str, org_id: str = None):
    """Create magic link for email authentication"""
    try:
        magic_link = generate_magic_link(email, org_id)
        
        # TODO: Send email with magic link
        logger.info(f"Magic link generated for {email}: {magic_link}")
        
        return {
            "magic_link": magic_link,
            "expires_in": 3600
        }
    except Exception as e:
        logger.error(f"Magic link error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/auth/verify-magic")
async def verify_magic_link(token: str):
    """Verify magic link token"""
    try:
        payload = verify_magic_link(token)
        
        # Create session token
        session_token = create_session_token(
            payload["email"], 
            payload.get("org_id", "default"), 
            "viewer"
        )
        
        return {
            "email": payload["email"],
            "org_id": payload.get("org_id"),
            "session_token": session_token
        }
    except Exception as e:
        logger.error(f"Magic link verification error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Organization endpoints
@app.post("/v1/orgs")
async def create_org(name: str, owner_id: str, owner_email: str):
    """Create new organization"""
    try:
        db = get_db_session()
        org_manager = get_org_manager(db)
        
        org = org_manager.create_org(name, owner_id, owner_email)
        
        return org
    except Exception as e:
        logger.error(f"Create org error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/v1/orgs")
async def get_user_orgs(user_id: str):
    """Get organizations for user"""
    try:
        db = get_db_session()
        org_manager = get_org_manager(db)
        
        orgs = org_manager.get_user_orgs(user_id)
        
        return {"organizations": orgs}
    except Exception as e:
        logger.error(f"Get user orgs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/v1/orgs/{org_id}")
async def get_org(org_id: str):
    """Get organization details"""
    try:
        db = get_db_session()
        org_manager = get_org_manager(db)
        
        org = org_manager.get_org(org_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        return org
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get org error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/v1/orgs/{org_id}/invite")
async def invite_user(org_id: str, email: str, role: str, invited_by: str):
    """Invite user to organization"""
    try:
        db = get_db_session()
        org_manager = get_org_manager(db)
        
        invite = org_manager.invite_user(org_id, email, role, invited_by)
        
        return invite
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Invite user error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/v1/orgs/accept-invite")
async def accept_invite(token: str, user_id: str):
    """Accept organization invitation"""
    try:
        db = get_db_session()
        org_manager = get_org_manager(db)
        
        result = org_manager.accept_invite(token, user_id)
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Accept invite error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/v1/orgs/{org_id}/members")
async def get_org_members(org_id: str, user_id: str):
    """Get organization members"""
    try:
        db = get_db_session()
        org_manager = get_org_manager(db)
        
        members = org_manager.get_org_members(org_id, user_id)
        
        return {"members": members}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Get org members error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# Orchestrator endpoints
@app.post("/v1/flows", response_model=FlowResponse)
async def create_flow(request: FlowCreate):
    """Create a new flow"""
    if not ORCH_ENABLED:
        raise HTTPException(status_code=503, detail="Orchestrator not enabled")
    
    flow_id = str(uuid.uuid4())
    
    try:
        db = get_db_session()
        
        from .db import Flow
        flow = Flow(
            id=flow_id,
            name=request.name,
            panel=request.panel,
            version=request.spec.version,
            spec=request.spec.dict()
        )
        db.add(flow)
        db.commit()
        
        return FlowResponse(
            id=flow.id,
            name=flow.name,
            panel=flow.panel,
            version=flow.version,
            is_active=flow.is_active,
            created_at=flow.created_at,
            updated_at=flow.updated_at,
            spec=request.spec
        )
        
    except Exception as e:
        logger.error(f"Failed to create flow: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/v1/flows", response_model=List[FlowResponse])
async def list_flows(panel: Optional[str] = None):
    """List flows"""
    if not ORCH_ENABLED:
        raise HTTPException(status_code=503, detail="Orchestrator not enabled")
    
    try:
        db = get_db_session()
        
        from .db import Flow
        query = db.query(Flow)
        if panel:
            query = query.filter(Flow.panel == panel)
        
        flows = query.all()
        
        result = []
        for flow in flows:
            result.append(FlowResponse(
                id=flow.id,
                name=flow.name,
                panel=flow.panel,
                version=flow.version,
                is_active=flow.is_active,
                created_at=flow.created_at,
                updated_at=flow.updated_at,
                spec=flow.spec
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to list flows: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/v1/flows/{flow_id}", response_model=FlowResponse)
async def get_flow(flow_id: str):
    """Get flow by ID"""
    if not ORCH_ENABLED:
        raise HTTPException(status_code=503, detail="Orchestrator not enabled")
    
    try:
        db = get_db_session()
        
        from .db import Flow
        flow = db.query(Flow).filter(Flow.id == flow_id).first()
        if not flow:
            raise HTTPException(status_code=404, detail="Flow not found")
        
        return FlowResponse(
            id=flow.id,
            name=flow.name,
            panel=flow.panel,
            version=flow.version,
            is_active=flow.is_active,
            created_at=flow.created_at,
            updated_at=flow.updated_at,
            spec=flow.spec
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get flow: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/v1/flows/{flow_id}/activate")
async def activate_flow(flow_id: str):
    """Activate flow"""
    if not ORCH_ENABLED:
        raise HTTPException(status_code=503, detail="Orchestrator not enabled")
    
    try:
        db = get_db_session()
        
        from .db import Flow
        flow = db.query(Flow).filter(Flow.id == flow_id).first()
        if not flow:
            raise HTTPException(status_code=404, detail="Flow not found")
        
        flow.is_active = True
        flow.updated_at = datetime.utcnow()
        db.commit()
        
        return {"status": "activated"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to activate flow: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/v1/flows/{flow_id}/deactivate")
async def deactivate_flow(flow_id: str):
    """Deactivate flow"""
    if not ORCH_ENABLED:
        raise HTTPException(status_code=503, detail="Orchestrator not enabled")
    
    try:
        db = get_db_session()
        
        from .db import Flow
        flow = db.query(Flow).filter(Flow.id == flow_id).first()
        if not flow:
            raise HTTPException(status_code=404, detail="Flow not found")
        
        flow.is_active = False
        flow.updated_at = datetime.utcnow()
        db.commit()
        
        return {"status": "deactivated"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to deactivate flow: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/v1/flows/{flow_id}/run", response_model=FlowRunResponse)
async def run_flow(flow_id: str, request: FlowRunRequest):
    """Run flow manually"""
    if not ORCH_ENABLED:
        raise HTTPException(status_code=503, detail="Orchestrator not enabled")
    
    try:
        db = get_db_session()
        
        from .db import Flow
        flow = db.query(Flow).filter(Flow.id == flow_id).first()
        if not flow:
            raise HTTPException(status_code=404, detail="Flow not found")
        
        # Queue flow run
        run_id = queue_flow_run(
            flow_id=flow_id,
            version=flow.version,
            mode=request.mode,
            trigger_ref=request.input or {}
        )
        
        return FlowRunResponse(
            run_id=run_id,
            flow_id=flow_id,
            status="queued",
            trace_id=str(uuid.uuid4())
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to run flow: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/v1/flows/{flow_id}/runs")
async def list_flow_runs(flow_id: str, limit: int = 10):
    """List flow runs"""
    if not ORCH_ENABLED:
        raise HTTPException(status_code=503, detail="Orchestrator not enabled")
    
    try:
        db = get_db_session()
        
        from .db import FlowRun
        runs = db.query(FlowRun).filter(FlowRun.flow_id == flow_id).order_by(FlowRun.started_at.desc()).limit(limit).all()
        
        result = []
        for run in runs:
            result.append({
                "id": run.id,
                "flow_id": run.flow_id,
                "status": run.status,
                "started_at": run.started_at,
                "finished_at": run.finished_at,
                "trace_id": run.trace_id
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to list flow runs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/v1/flow-runs/{run_id}", response_model=FlowRunDetails)
async def get_flow_run(run_id: str):
    """Get flow run details"""
    if not ORCH_ENABLED:
        raise HTTPException(status_code=503, detail="Orchestrator not enabled")
    
    try:
        db = get_db_session()
        
        from .db import FlowRun, NodeCache
        flow_run = db.query(FlowRun).filter(FlowRun.id == run_id).first()
        if not flow_run:
            raise HTTPException(status_code=404, detail="Flow run not found")
        
        # Get node statuses
        nodes = db.query(NodeCache).filter(NodeCache.run_id == run_id).all()
        node_statuses = []
        for node in nodes:
            node_statuses.append({
                "node_id": node.node_id,
                "status": node.status,
                "output": node.output,
                "started_at": node.started_at,
                "finished_at": node.finished_at,
                "took_ms": node.took_ms
            })
        
        return FlowRunDetails(
            id=flow_run.id,
            flow_id=flow_run.flow_id,
            status=flow_run.status,
            started_at=flow_run.started_at,
            finished_at=flow_run.finished_at,
            trigger_ref=flow_run.trigger_ref,
            trace_id=flow_run.trace_id,
            nodes=node_statuses
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get flow run: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/v1/flow-runs/{run_id}/events")
async def get_flow_run_events(run_id: str, limit: int = 100):
    """Get flow run events"""
    if not ORCH_ENABLED:
        raise HTTPException(status_code=503, detail="Orchestrator not enabled")
    
    try:
        db = get_db_session()
        
        from .db import RunEvent
        events = db.query(RunEvent).filter(RunEvent.run_id == run_id).order_by(RunEvent.ts.desc()).limit(limit).all()
        
        result = []
        for event in events:
            result.append(RunEventResponse(
                id=event.id,
                ts=event.ts,
                level=event.level,
                node_id=event.node_id,
                message=event.message,
                data=event.data
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get flow run events: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# M20.2 Billing endpoints
@app.get("/v1/billing/balance/{org_id}")
async def get_billing_balance(org_id: str):
    """Get organization billing balance and quotas"""
    try:
        db = get_db_session()
        billing_manager = BillingManager(db)
        
        balance_info = billing_manager.get_org_balance(org_id)
        return balance_info
        
    except Exception as e:
        logger.error(f"Failed to get billing balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/v1/billing/usage/{org_id}")
async def get_usage_stats(org_id: str, days: int = 30):
    """Get organization usage statistics"""
    try:
        db = get_db_session()
        billing_manager = BillingManager(db)
        
        usage_stats = billing_manager.get_usage_stats(org_id, days)
        return usage_stats
        
    except Exception as e:
        logger.error(f"Failed to get usage stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/v1/billing/credit")
async def credit_cbt(request: Dict[str, Any]):
    """Credit cbT to organization"""
    try:
        db = get_db_session()
        billing_manager = BillingManager(db)
        
        org_id = request.get("org_id")
        amount = request.get("amount", 0)
        reason = request.get("reason", "manual_credit")
        ref_id = request.get("ref_id")
        metadata = request.get("metadata", {})
        
        if not org_id or amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid org_id or amount")
        
        success = billing_manager.credit_cbt(org_id, amount, reason, ref_id, metadata)
        
        if success:
            return {"status": "success", "message": f"Credited {amount} cbT to org {org_id}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to credit cbT")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to credit cbT: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/v1/billing/payment-intent")
async def create_payment_intent(request: Dict[str, Any]):
    """Create Stripe payment intent"""
    try:
        db = get_db_session()
        billing_manager = BillingManager(db)
        
        org_id = request.get("org_id")
        amount_cents = request.get("amount_cents", 0)
        description = request.get("description", "cbT Top-up")
        
        if not org_id or amount_cents <= 0:
            raise HTTPException(status_code=400, detail="Invalid org_id or amount")
        
        payment_intent = billing_manager.create_payment_intent(org_id, amount_cents, description)
        
        if payment_intent:
            return payment_intent
        else:
            raise HTTPException(status_code=500, detail="Failed to create payment intent")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create payment intent: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/v1/billing/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    try:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        
        if not sig_header:
            raise HTTPException(status_code=400, detail="Missing stripe-signature header")
        
        # TODO: Verify webhook signature in production
        # For M20.2, we'll just log the event
        logger.info(f"Received Stripe webhook: {payload.decode()}")
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Failed to process Stripe webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# M20.5 SRE endpoints
@app.get("/v1/sre/slo")
async def get_slo_status():
    """Get SLO status and error budgets"""
    try:
        sre_manager = SREManager()
        return sre_manager.get_slo_status()
    except Exception as e:
        logger.error(f"Failed to get SLO status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/sre/alerts")
async def get_active_alerts():
    """Get active alerts"""
    try:
        sre_manager = SREManager()
        return sre_manager.get_active_alerts()
    except Exception as e:
        logger.error(f"Failed to get active alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/sre/synthetics")
async def run_synthetic_tests():
    """Run synthetic monitoring tests"""
    try:
        sre_manager = SREManager()
        return sre_manager.run_synthetic_tests()
    except Exception as e:
        logger.error(f"Failed to run synthetic tests: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/sre/drill")
async def run_sre_drill(request: Dict[str, Any]):
    """Run SRE drill scenarios"""
    try:
        sre_manager = SREManager()
        scenario = request.get("scenario", "all")
        return sre_manager.run_drill(scenario)
    except Exception as e:
        logger.error(f"Failed to run SRE drill: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/sre/rollback")
async def execute_rollback(request: Dict[str, Any]):
    """Execute rollback to previous revision"""
    try:
        sre_manager = SREManager()
        target_revision = request.get("target_revision")
        reason = request.get("reason", "SRE rollback")
        return sre_manager.execute_rollback(target_revision, reason)
    except Exception as e:
        logger.error(f"Failed to execute rollback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
