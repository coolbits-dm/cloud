# Industry-specific API endpoints for CoolBits.ai
# Each industry gets its own dedicated endpoint with RAG integration

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, List
import logging
from lib.industry_rag_manager import IndustryRAGManager
from lib.auth import get_current_user
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CoolBits.ai Industry API",
    description="Industry-specific AI endpoints with RAG integration",
    version="1.0.0",
)

# Initialize RAG manager
rag_manager = IndustryRAGManager(
    project_id=os.getenv("GOOGLE_CLOUD_PROJECT", "coolbits-ai"),
    region=os.getenv("GOOGLE_CLOUD_REGION", "europe-west3"),
)


# Pydantic models
class IndustryQuery(BaseModel):
    query: str
    provider: Optional[str] = "openai"  # "openai" or "xai"
    context: Optional[Dict] = None


class IndustryResponse(BaseModel):
    industry: str
    query: str
    response: str
    provider: str
    context_used: Optional[Dict] = None
    timestamp: str


class IndustryInfo(BaseModel):
    industry_id: str
    name: str
    description: str
    keywords: List[str]
    documents: List[str]
    rag_status: bool


# Industry endpoints
@app.get("/api/industries", response_model=List[IndustryInfo])
async def list_industries():
    """List all available industries"""
    industries = []
    for industry_id, info in rag_manager.industries.items():
        industries.append(
            IndustryInfo(
                industry_id=industry_id,
                name=info["name"],
                description=info["description"],
                keywords=info["keywords"],
                documents=info["documents"],
                rag_status=True,  # Assume RAG is set up
            )
        )
    return industries


@app.get("/api/industries/{industry_id}", response_model=IndustryInfo)
async def get_industry_info(industry_id: str):
    """Get information about a specific industry"""
    if industry_id not in rag_manager.industries:
        raise HTTPException(status_code=404, detail="Industry not found")

    info = rag_manager.industries[industry_id]
    return IndustryInfo(
        industry_id=industry_id,
        name=info["name"],
        description=info["description"],
        keywords=info["keywords"],
        documents=info["documents"],
        rag_status=True,
    )


@app.post("/api/industries/{industry_id}/query", response_model=IndustryResponse)
async def query_industry(
    industry_id: str,
    query_data: IndustryQuery,
    current_user: dict = Depends(get_current_user),
):
    """Query industry-specific AI with RAG integration"""
    if industry_id not in rag_manager.industries:
        raise HTTPException(status_code=404, detail="Industry not found")

    try:
        # Query the industry RAG
        response = rag_manager.query_industry_rag(
            industry_id=industry_id,
            query=query_data.query,
            provider=query_data.provider,
        )

        return IndustryResponse(
            industry=industry_id,
            query=query_data.query,
            response=response,
            provider=query_data.provider,
            context_used=query_data.context,
            timestamp=str(datetime.now()),
        )
    except Exception as e:
        logger.error(f"Error querying industry {industry_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Individual industry endpoints
def create_industry_endpoint(industry_id: str):
    """Create individual endpoint for each industry"""

    @app.post(f"/api/{industry_id}/query", response_model=IndustryResponse)
    async def query_specific_industry(
        query_data: IndustryQuery, current_user: dict = Depends(get_current_user)
    ):
        """Query {industry_id} industry AI with RAG integration"""
        try:
            response = rag_manager.query_industry_rag(
                industry_id=industry_id,
                query=query_data.query,
                provider=query_data.provider,
            )

            return IndustryResponse(
                industry=industry_id,
                query=query_data.query,
                response=response,
                provider=query_data.provider,
                context_used=query_data.context,
                timestamp=str(datetime.now()),
            )
        except Exception as e:
            logger.error(f"Error querying {industry_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))


# Create endpoints for all industries
for industry_id in rag_manager.industries.keys():
    create_industry_endpoint(industry_id)


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "industries": len(rag_manager.industries)}


# Setup endpoint
@app.post("/api/setup/industries")
async def setup_all_industries(current_user: dict = Depends(get_current_user)):
    """Set up RAG infrastructure for all industries"""
    try:
        results = rag_manager.setup_all_industry_rags()
        successful = sum(1 for success in results.values() if success)
        total = len(results)

        return {
            "message": f"RAG setup complete: {successful}/{total} industries configured",
            "results": results,
        }
    except Exception as e:
        logger.error(f"Error setting up industries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
