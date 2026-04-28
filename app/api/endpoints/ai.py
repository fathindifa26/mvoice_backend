from fastapi import APIRouter, Depends, Query
from typing import Optional, List, Dict
from app.services.ai_service import ai_service
from app.services.analytics_service import analytics_service
from app.services.brand_service import brand_service

router = APIRouter()

@router.get("/summary")
async def get_ai_comparison_summary(
    brand_a: str,
    brand_b: str,
    business_unit: str,
    metrics: List[str] = Query(["topic", "hook_type", "format", "tone", "face_emotion"]),
    aggregation: str = "views",
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):
    """
    Production endpoint for AI summary generation based on selected chart data.
    """
    
    all_brand_a_data = {}
    all_brand_b_data = {}
    all_benchmarks = {}

    # 1. Fetch data for each selected metric
    for metric in metrics:
        data_a = analytics_service.analyze_variable(
            column=metric,
            aggregation_metric=aggregation,
            business_unit=business_unit,
            brand=brand_a,
            from_date=from_date,
            to_date=to_date
        )
        
        data_b = analytics_service.analyze_variable(
            column=metric,
            aggregation_metric=aggregation,
            business_unit=business_unit,
            brand=brand_b,
            from_date=from_date,
            to_date=to_date
        )
        
        all_brand_a_data[metric] = data_a.get("data", [])
        all_brand_b_data[metric] = data_b.get("data", [])
        
        # We only need benchmark once per metric
        if metric not in all_benchmarks:
            all_benchmarks[metric] = {
                "bu_mean": data_a.get("bu_mean"),
                "bu_mean_bin": data_a.get("bu_mean_bin")
            }
    
    # 2. Fetch Market Performance Benchmarks
    all_benchmarks["market_performance"] = brand_service.get_market_performance_summary(business_unit, exclude_brands=[brand_a, brand_b])

    # 3. Fetch Top Leaders for Context
    top_our = brand_service.get_top_brands(business_unit, True, limit=3)
    top_comp = brand_service.get_top_brands(business_unit, False, limit=3)
    
    top_leaders_data = {}
    for b in top_our + top_comp:
        brand_name = b["name"]
        top_leaders_data[brand_name] = brand_service.get_brand_performance_summary(brand_name, business_unit)
    
    all_benchmarks["top_leaders_performance"] = top_leaders_data

    # 4. Generate AI summary
    summary = await ai_service.generate_comparison_summary(
        brand_a=brand_a,
        brand_b=brand_b,
        brand_a_data=all_brand_a_data,
        brand_b_data=all_brand_b_data,
        bu_benchmarks=all_benchmarks
    )
    
    return {
        "metadata": {
            "brand_a": brand_a,
            "brand_b": brand_b,
            "metrics": metrics,
            "aggregation": aggregation
        },
        "summary": summary
    }
