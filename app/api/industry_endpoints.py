# Individual industry endpoints for CoolBits.ai
# Each industry gets its own dedicated API endpoint

from fastapi import HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict
import logging
from lib.industry_rag_manager import IndustryRAGManager
from lib.auth import get_current_user
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


# Agriculture & Food Industry Endpoints
@app.post("/api/agritech/query", response_model=IndustryResponse)
async def query_agritech(
    query_data: IndustryQuery, current_user: dict = Depends(get_current_user)
):
    """Query AgTech industry AI with RAG integration"""
    try:
        response = rag_manager.query_industry_rag(
            industry_id="agritech", query=query_data.query, provider=query_data.provider
        )

        return IndustryResponse(
            industry="agritech",
            query=query_data.query,
            response=response,
            provider=query_data.provider,
            context_used=query_data.context,
            timestamp=str(datetime.now()),
        )
    except Exception as e:
        logger.error(f"Error querying agritech: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agri_inputs/query", response_model=IndustryResponse)
async def query_agri_inputs(
    query_data: IndustryQuery, current_user: dict = Depends(get_current_user)
):
    """Query Agricultural Inputs industry AI with RAG integration"""
    try:
        response = rag_manager.query_industry_rag(
            industry_id="agri_inputs",
            query=query_data.query,
            provider=query_data.provider,
        )

        return IndustryResponse(
            industry="agri_inputs",
            query=query_data.query,
            response=response,
            provider=query_data.provider,
            context_used=query_data.context,
            timestamp=str(datetime.now()),
        )
    except Exception as e:
        logger.error(f"Error querying agri_inputs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/food_bev_mfg/query", response_model=IndustryResponse)
async def query_food_bev_mfg(
    query_data: IndustryQuery, current_user: dict = Depends(get_current_user)
):
    """Query Food & Beverage Manufacturing industry AI with RAG integration"""
    try:
        response = rag_manager.query_industry_rag(
            industry_id="food_bev_mfg",
            query=query_data.query,
            provider=query_data.provider,
        )

        return IndustryResponse(
            industry="food_bev_mfg",
            query=query_data.query,
            response=response,
            provider=query_data.provider,
            context_used=query_data.context,
            timestamp=str(datetime.now()),
        )
    except Exception as e:
        logger.error(f"Error querying food_bev_mfg: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/foodservice/query", response_model=IndustryResponse)
async def query_foodservice(
    query_data: IndustryQuery, current_user: dict = Depends(get_current_user)
):
    """Query Food Service industry AI with RAG integration"""
    try:
        response = rag_manager.query_industry_rag(
            industry_id="foodservice",
            query=query_data.query,
            provider=query_data.provider,
        )

        return IndustryResponse(
            industry="foodservice",
            query=query_data.query,
            response=response,
            provider=query_data.provider,
            context_used=query_data.context,
            timestamp=str(datetime.now()),
        )
    except Exception as e:
        logger.error(f"Error querying foodservice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Energy & Utilities Industry Endpoints
@app.post("/api/oil_gas/query", response_model=IndustryResponse)
async def query_oil_gas(
    query_data: IndustryQuery, current_user: dict = Depends(get_current_user)
):
    """Query Oil & Gas industry AI with RAG integration"""
    try:
        response = rag_manager.query_industry_rag(
            industry_id="oil_gas", query=query_data.query, provider=query_data.provider
        )

        return IndustryResponse(
            industry="oil_gas",
            query=query_data.query,
            response=response,
            provider=query_data.provider,
            context_used=query_data.context,
            timestamp=str(datetime.now()),
        )
    except Exception as e:
        logger.error(f"Error querying oil_gas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/power_gen/query", response_model=IndustryResponse)
async def query_power_gen(
    query_data: IndustryQuery, current_user: dict = Depends(get_current_user)
):
    """Query Power Generation industry AI with RAG integration"""
    try:
        response = rag_manager.query_industry_rag(
            industry_id="power_gen",
            query=query_data.query,
            provider=query_data.provider,
        )

        return IndustryResponse(
            industry="power_gen",
            query=query_data.query,
            response=response,
            provider=query_data.provider,
            context_used=query_data.context,
            timestamp=str(datetime.now()),
        )
    except Exception as e:
        logger.error(f"Error querying power_gen: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/renewables/query", response_model=IndustryResponse)
async def query_renewables(
    query_data: IndustryQuery, current_user: dict = Depends(get_current_user)
):
    """Query Renewable Energy industry AI with RAG integration"""
    try:
        response = rag_manager.query_industry_rag(
            industry_id="renewables",
            query=query_data.query,
            provider=query_data.provider,
        )

        return IndustryResponse(
            industry="renewables",
            query=query_data.query,
            response=response,
            provider=query_data.provider,
            context_used=query_data.context,
            timestamp=str(datetime.now()),
        )
    except Exception as e:
        logger.error(f"Error querying renewables: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/water_wastewater/query", response_model=IndustryResponse)
async def query_water_wastewater(
    query_data: IndustryQuery, current_user: dict = Depends(get_current_user)
):
    """Query Water & Wastewater industry AI with RAG integration"""
    try:
        response = rag_manager.query_industry_rag(
            industry_id="water_wastewater",
            query=query_data.query,
            provider=query_data.provider,
        )

        return IndustryResponse(
            industry="water_wastewater",
            query=query_data.query,
            response=response,
            provider=query_data.provider,
            context_used=query_data.context,
            timestamp=str(datetime.now()),
        )
    except Exception as e:
        logger.error(f"Error querying water_wastewater: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Manufacturing Industry Endpoints
@app.post("/api/industrial_equipment/query", response_model=IndustryResponse)
async def query_industrial_equipment(
    query_data: IndustryQuery, current_user: dict = Depends(get_current_user)
):
    """Query Industrial Equipment industry AI with RAG integration"""
    try:
        response = rag_manager.query_industry_rag(
            industry_id="industrial_equipment",
            query=query_data.query,
            provider=query_data.provider,
        )

        return IndustryResponse(
            industry="industrial_equipment",
            query=query_data.query,
            response=response,
            provider=query_data.provider,
            context_used=query_data.context,
            timestamp=str(datetime.now()),
        )
    except Exception as e:
        logger.error(f"Error querying industrial_equipment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/electronics_mfg/query", response_model=IndustryResponse)
async def query_electronics_mfg(
    query_data: IndustryQuery, current_user: dict = Depends(get_current_user)
):
    """Query Electronics Manufacturing industry AI with RAG integration"""
    try:
        response = rag_manager.query_industry_rag(
            industry_id="electronics_mfg",
            query=query_data.query,
            provider=query_data.provider,
        )

        return IndustryResponse(
            industry="electronics_mfg",
            query=query_data.query,
            response=response,
            provider=query_data.provider,
            context_used=query_data.context,
            timestamp=str(datetime.now()),
        )
    except Exception as e:
        logger.error(f"Error querying electronics_mfg: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/automation_robotics/query", response_model=IndustryResponse)
async def query_automation_robotics(
    query_data: IndustryQuery, current_user: dict = Depends(get_current_user)
):
    """Query Automation & Robotics industry AI with RAG integration"""
    try:
        response = rag_manager.query_industry_rag(
            industry_id="automation_robotics",
            query=query_data.query,
            provider=query_data.provider,
        )

        return IndustryResponse(
            industry="automation_robotics",
            query=query_data.query,
            response=response,
            provider=query_data.provider,
            context_used=query_data.context,
            timestamp=str(datetime.now()),
        )
    except Exception as e:
        logger.error(f"Error querying automation_robotics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Financial Services Industry Endpoints
@app.post("/api/banking/query", response_model=IndustryResponse)
async def query_banking(
    query_data: IndustryQuery, current_user: dict = Depends(get_current_user)
):
    """Query Banking industry AI with RAG integration"""
    try:
        response = rag_manager.query_industry_rag(
            industry_id="banking", query=query_data.query, provider=query_data.provider
        )

        return IndustryResponse(
            industry="banking",
            query=query_data.query,
            response=response,
            provider=query_data.provider,
            context_used=query_data.context,
            timestamp=str(datetime.now()),
        )
    except Exception as e:
        logger.error(f"Error querying banking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/payments_fintech/query", response_model=IndustryResponse)
async def query_payments_fintech(
    query_data: IndustryQuery, current_user: dict = Depends(get_current_user)
):
    """Query Payments & FinTech industry AI with RAG integration"""
    try:
        response = rag_manager.query_industry_rag(
            industry_id="payments_fintech",
            query=query_data.query,
            provider=query_data.provider,
        )

        return IndustryResponse(
            industry="payments_fintech",
            query=query_data.query,
            response=response,
            provider=query_data.provider,
            context_used=query_data.context,
            timestamp=str(datetime.now()),
        )
    except Exception as e:
        logger.error(f"Error querying payments_fintech: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/wealth_asset/query", response_model=IndustryResponse)
async def query_wealth_asset(
    query_data: IndustryQuery, current_user: dict = Depends(get_current_user)
):
    """Query Wealth & Asset Management industry AI with RAG integration"""
    try:
        response = rag_manager.query_industry_rag(
            industry_id="wealth_asset",
            query=query_data.query,
            provider=query_data.provider,
        )

        return IndustryResponse(
            industry="wealth_asset",
            query=query_data.query,
            response=response,
            provider=query_data.provider,
            context_used=query_data.context,
            timestamp=str(datetime.now()),
        )
    except Exception as e:
        logger.error(f"Error querying wealth_asset: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/capital_markets/query", response_model=IndustryResponse)
async def query_capital_markets(
    query_data: IndustryQuery, current_user: dict = Depends(get_current_user)
):
    """Query Capital Markets industry AI with RAG integration"""
    try:
        response = rag_manager.query_industry_rag(
            industry_id="capital_markets",
            query=query_data.query,
            provider=query_data.provider,
        )

        return IndustryResponse(
            industry="capital_markets",
            query=query_data.query,
            response=response,
            provider=query_data.provider,
            context_used=query_data.context,
            timestamp=str(datetime.now()),
        )
    except Exception as e:
        logger.error(f"Error querying capital_markets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Healthcare Industry Endpoints
@app.post("/api/hospitals_clinics/query", response_model=IndustryResponse)
async def query_hospitals_clinics(
    query_data: IndustryQuery, current_user: dict = Depends(get_current_user)
):
    """Query Hospitals & Clinics industry AI with RAG integration"""
    try:
        response = rag_manager.query_industry_rag(
            industry_id="hospitals_clinics",
            query=query_data.query,
            provider=query_data.provider,
        )

        return IndustryResponse(
            industry="hospitals_clinics",
            query=query_data.query,
            response=response,
            provider=query_data.provider,
            context_used=query_data.context,
            timestamp=str(datetime.now()),
        )
    except Exception as e:
        logger.error(f"Error querying hospitals_clinics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/med_devices/query", response_model=IndustryResponse)
async def query_med_devices(
    query_data: IndustryQuery, current_user: dict = Depends(get_current_user)
):
    """Query Medical Devices industry AI with RAG integration"""
    try:
        response = rag_manager.query_industry_rag(
            industry_id="med_devices",
            query=query_data.query,
            provider=query_data.provider,
        )

        return IndustryResponse(
            industry="med_devices",
            query=query_data.query,
            response=response,
            provider=query_data.provider,
            context_used=query_data.context,
            timestamp=str(datetime.now()),
        )
    except Exception as e:
        logger.error(f"Error querying med_devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/digital_health/query", response_model=IndustryResponse)
async def query_digital_health(
    query_data: IndustryQuery, current_user: dict = Depends(get_current_user)
):
    """Query Digital Health industry AI with RAG integration"""
    try:
        response = rag_manager.query_industry_rag(
            industry_id="digital_health",
            query=query_data.query,
            provider=query_data.provider,
        )

        return IndustryResponse(
            industry="digital_health",
            query=query_data.query,
            response=response,
            provider=query_data.provider,
            context_used=query_data.context,
            timestamp=str(datetime.now()),
        )
    except Exception as e:
        logger.error(f"Error querying digital_health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Technology Industry Endpoints
@app.post("/api/saas_b2b/query", response_model=IndustryResponse)
async def query_saas_b2b(
    query_data: IndustryQuery, current_user: dict = Depends(get_current_user)
):
    """Query SaaS B2B industry AI with RAG integration"""
    try:
        response = rag_manager.query_industry_rag(
            industry_id="saas_b2b", query=query_data.query, provider=query_data.provider
        )

        return IndustryResponse(
            industry="saas_b2b",
            query=query_data.query,
            response=response,
            provider=query_data.provider,
            context_used=query_data.context,
            timestamp=str(datetime.now()),
        )
    except Exception as e:
        logger.error(f"Error querying saas_b2b: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/devtools_cloud/query", response_model=IndustryResponse)
async def query_devtools_cloud(
    query_data: IndustryQuery, current_user: dict = Depends(get_current_user)
):
    """Query DevTools & Cloud industry AI with RAG integration"""
    try:
        response = rag_manager.query_industry_rag(
            industry_id="devtools_cloud",
            query=query_data.query,
            provider=query_data.provider,
        )

        return IndustryResponse(
            industry="devtools_cloud",
            query=query_data.query,
            response=response,
            provider=query_data.provider,
            context_used=query_data.context,
            timestamp=str(datetime.now()),
        )
    except Exception as e:
        logger.error(f"Error querying devtools_cloud: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai_ml_platforms/query", response_model=IndustryResponse)
async def query_ai_ml_platforms(
    query_data: IndustryQuery, current_user: dict = Depends(get_current_user)
):
    """Query AI/ML Platforms industry AI with RAG integration"""
    try:
        response = rag_manager.query_industry_rag(
            industry_id="ai_ml_platforms",
            query=query_data.query,
            provider=query_data.provider,
        )

        return IndustryResponse(
            industry="ai_ml_platforms",
            query=query_data.query,
            response=response,
            provider=query_data.provider,
            context_used=query_data.context,
            timestamp=str(datetime.now()),
        )
    except Exception as e:
        logger.error(f"Error querying ai_ml_platforms: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/data_infra/query", response_model=IndustryResponse)
async def query_data_infra(
    query_data: IndustryQuery, current_user: dict = Depends(get_current_user)
):
    """Query Data Infrastructure industry AI with RAG integration"""
    try:
        response = rag_manager.query_industry_rag(
            industry_id="data_infra",
            query=query_data.query,
            provider=query_data.provider,
        )

        return IndustryResponse(
            industry="data_infra",
            query=query_data.query,
            response=response,
            provider=query_data.provider,
            context_used=query_data.context,
            timestamp=str(datetime.now()),
        )
    except Exception as e:
        logger.error(f"Error querying data_infra: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Blockchain & Crypto Industry Endpoints
@app.post("/api/exchanges/query", response_model=IndustryResponse)
async def query_exchanges(
    query_data: IndustryQuery, current_user: dict = Depends(get_current_user)
):
    """Query Cryptocurrency Exchanges industry AI with RAG integration"""
    try:
        response = rag_manager.query_industry_rag(
            industry_id="exchanges",
            query=query_data.query,
            provider=query_data.provider,
        )

        return IndustryResponse(
            industry="exchanges",
            query=query_data.query,
            response=response,
            provider=query_data.provider,
            context_used=query_data.context,
            timestamp=str(datetime.now()),
        )
    except Exception as e:
        logger.error(f"Error querying exchanges: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/defi/query", response_model=IndustryResponse)
async def query_defi(
    query_data: IndustryQuery, current_user: dict = Depends(get_current_user)
):
    """Query DeFi industry AI with RAG integration"""
    try:
        response = rag_manager.query_industry_rag(
            industry_id="defi", query=query_data.query, provider=query_data.provider
        )

        return IndustryResponse(
            industry="defi",
            query=query_data.query,
            response=response,
            provider=query_data.provider,
            context_used=query_data.context,
            timestamp=str(datetime.now()),
        )
    except Exception as e:
        logger.error(f"Error querying defi: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/wallets_infra/query", response_model=IndustryResponse)
async def query_wallets_infra(
    query_data: IndustryQuery, current_user: dict = Depends(get_current_user)
):
    """Query Wallets & Infrastructure industry AI with RAG integration"""
    try:
        response = rag_manager.query_industry_rag(
            industry_id="wallets_infra",
            query=query_data.query,
            provider=query_data.provider,
        )

        return IndustryResponse(
            industry="wallets_infra",
            query=query_data.query,
            response=response,
            provider=query_data.provider,
            context_used=query_data.context,
            timestamp=str(datetime.now()),
        )
    except Exception as e:
        logger.error(f"Error querying wallets_infra: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "industries": len(rag_manager.industries)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
