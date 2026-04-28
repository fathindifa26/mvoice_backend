from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict
import json
from data_manager import data_manager

app = FastAPI(title="MVoice Intelligence API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/filters")
async def get_filters(business_unit: Optional[str] = None):
    return data_manager.get_filter_options(business_unit)

@app.get("/api/analyze")
async def analyze_metric(
    metric: str,
    aggregation_metric: str = "frequency", # "frequency" or "views"
    business_unit: Optional[str] = None,
    brand: Optional[str] = None,
    talent_type: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):
    return data_manager.analyze_variable(
        column=metric,
        aggregation_metric=aggregation_metric,
        business_unit=business_unit,
        brand=brand,
        talent_type=talent_type,
        from_date=from_date,
        to_date=to_date
    )

@app.get("/api/top-brands")
async def get_top_brands(
    business_unit: Optional[str] = None,
    metric: str = "views",
    limit: int = 3
):
    return {
        "our_brands": data_manager.get_top_brands(business_unit, True, metric, limit),
        "competitor_brands": data_manager.get_top_brands(business_unit, False, metric, limit)
    }

@app.get("/api/creatives")
async def get_creatives(
    business_unit: Optional[str] = None,
    brand: Optional[str] = None,
    talent_type: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    filters_json: Optional[str] = Query(None), # Expecting JSON string of List[Dict]
    limit: int = 5
):
    filters = []
    if filters_json:
        try:
            filters = json.loads(filters_json)
        except:
            pass
            
    return data_manager.get_filtered_creative_list(
        business_unit=business_unit,
        brand=brand,
        talent_type=talent_type,
        from_date=from_date,
        to_date=to_date,
        filters=filters,
        limit=limit
    )

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "rows": len(data_manager.get_df())}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
