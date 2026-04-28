from fastapi import APIRouter, Query
from typing import Optional, List, Dict
import json
from app.services.creative_service import creative_service

router = APIRouter()

@router.get("/")
async def get_creatives(
    business_unit: Optional[str] = None,
    brand: Optional[str] = None,
    talent_type: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    filters_json: Optional[str] = Query(None),
    limit: int = 5
):
    filters = []
    if filters_json:
        try:
            filters = json.loads(filters_json)
        except Exception:
            pass
            
    return creative_service.get_filtered_creative_list(
        business_unit=business_unit,
        brand=brand,
        talent_type=talent_type,
        from_date=from_date,
        to_date=to_date,
        filters=filters,
        limit=limit
    )
