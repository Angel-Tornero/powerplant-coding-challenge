from fastapi import APIRouter
import logging

from app.models.payload import PayloadModel
from app.services.production_plan_service import ProductionPlanService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
async def root():
    return {"message": "Hello World"}

@router.post("/productionplan")
async def post_payload(payload: PayloadModel):
    production_plan_service = ProductionPlanService(payload)
    try:
        return production_plan_service.calculate_production_plan()
    except Exception as e:
        return {"message": e.args[0]}
