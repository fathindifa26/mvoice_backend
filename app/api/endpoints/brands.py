from fastapi import APIRouter
from typing import Optional
from app.services.brand_service import brand_service

router = APIRouter()

@router.get("/top-brands")
async def get_top_brands(
    business_unit: Optional[str] = None,
    metric: str = "views",
    limit: int = 3
):
    return {
        "our_brands": brand_service.get_top_brands(business_unit, True, metric, limit),
        "competitor_brands": brand_service.get_top_brands(business_unit, False, metric, limit)
    }
