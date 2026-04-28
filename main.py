from typing import Optional
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from data_manager import data_manager

app = FastAPI(title="MVoice Optimization Engine API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "MVoice Optimization Engine API is running", "docs": "/docs"}

@app.get("/api/filters")
async def get_filters():
    """Get unique values for all filters (BU, Brands, etc.)"""
    return data_manager.get_filter_options()

@app.get("/api/creatives")
async def get_creatives(
    business_unit: Optional[str] = None,
    brand: Optional[str] = None,
    talent_type: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):
    df = data_manager.filter_creatives(
        business_unit=business_unit,
        brand=brand,
        talent_type=talent_type,
        from_date=from_date,
        to_date=to_date
    )
    return df.to_dict(orient="records")

@app.get("/api/top-brands")
async def get_top_brands(
    business_unit: Optional[str] = "All",
    metric: str = "views" # "views" or "frequency"
):
    return {
        "our_brands": data_manager.get_top_brands(business_unit, is_our_brand=True, metric=metric),
        "competitor_brands": data_manager.get_top_brands(business_unit, is_our_brand=False, metric=metric)
    }

@app.get("/api/charts/duration-histogram")
async def get_duration_histogram(
    business_unit: Optional[str] = None,
    brand: Optional[str] = None,
    talent_type: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):
    return data_manager.get_duration_histogram(
        business_unit=business_unit,
        brand=brand,
        talent_type=talent_type,
        from_date=from_date,
        to_date=to_date
    )

@app.get("/api/stats")
async def get_stats(business_unit: Optional[str] = None):
    df = data_manager.filter_creatives(business_unit=business_unit)
    if df.empty:
        return {"error": "No data available"}
        
    stats = {
        "total_creatives": len(df),
        "total_views": int(df["views"].sum()),
        "avg_duration": round(float(df["duration_sec"].mean()), 2),
        "brands": sorted(df["brand"].unique().tolist()),
    }
    return stats

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
