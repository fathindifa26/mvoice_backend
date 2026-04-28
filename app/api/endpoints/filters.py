from fastapi import APIRouter
from typing import Optional
from app.services.base import base_data_manager

router = APIRouter()

@router.get("/")
async def get_filters(
    business_unit: Optional[str] = None
):
    return base_data_manager.get_filter_options(business_unit)
