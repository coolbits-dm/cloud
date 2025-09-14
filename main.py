from fastapi import FastAPI
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI()

class Msg(BaseModel):
    model: str | None = "default-model"
    messages: list[dict] = []

@app.post("/chat")
def chat(body: Msg):
    return {"ok": True, "echo_model": body.model, "messages": body.messages}

@app.get("/health", response_class=JSONResponse)
@app.get("/healthz", response_class=JSONResponse)
def health():
    """Standard health check endpoint."""
    return {"status": "ok"}

@app.get("/_ah/health", response_class=JSONResponse)
def gfe_health():
    """Health check for Google Front End (GFE)."""
    return {"status": "ok"}

@app.get("/")
async def root():
    """Root redirects to /health."""
    return RedirectResponse(url="/health", status_code=302)
