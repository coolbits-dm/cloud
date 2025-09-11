# CoolBits.ai FastAPI Integration Example
# Exemplu de integrare a NHA Enforcement Middleware în FastAPI

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from cblm.opipe.nha.middleware import NhaEnforcementMiddleware, create_action_resolver
from cblm.opipe.nha.enforcer import health as policy_health, get_agent_info

# Create FastAPI app
app = FastAPI(title="CoolBits.ai NHA Enforced API", version="1.0.0")

# Add NHA enforcement middleware
action_resolver = create_action_resolver("headers")  # Use header-based resolution
app.add_middleware(NhaEnforcementMiddleware, action_resolver=action_resolver)

# Policy health endpoint
@app.get("/policy/health")
def policy_healthcheck():
    """Get policy enforcement health status"""
    return policy_health()

# Agent info endpoint
@app.get("/policy/agent/{nha_id}")
def get_agent_policy_info(nha_id: str):
    """Get agent policy information"""
    info = get_agent_info(nha_id)
    if not info:
        raise HTTPException(status_code=404, detail="Agent not found")
    return info

# Example protected endpoints
@app.get("/api/rag/search")
def rag_search(request: Request):
    """RAG search endpoint - requires read:rag scope"""
    return {"message": "RAG search successful", "agent": request.headers.get("X-NHA-ID")}

@app.post("/api/rag/ingest")
def rag_ingest(request: Request):
    """RAG ingest endpoint - requires write:rag scope"""
    return {"message": "RAG ingest successful", "agent": request.headers.get("X-NHA-ID")}

@app.get("/api/agents")
def list_agents(request: Request):
    """List agents endpoint - requires agents:read scope"""
    return {"message": "Agents list retrieved", "agent": request.headers.get("X-NHA-ID")}

@app.post("/api/export")
def export_data(request: Request):
    """Export data endpoint - requires export:data scope"""
    return {"message": "Data export successful", "agent": request.headers.get("X-NHA-ID")}

# Error handler for policy violations
@app.exception_handler(HTTPException)
async def policy_violation_handler(request: Request, exc: HTTPException):
    """Handle policy violation errors"""
    if exc.status_code == 403:
        return JSONResponse(
            status_code=403,
            content={
                "error": "Policy Violation",
                "message": "Access denied by NHA enforcement policy",
                "details": exc.detail
            }
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
