from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import filters, analytics, brands, creatives, ai
from app.core.config import settings
from app.services.base import base_data_manager

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(filters.router, prefix=f"{settings.API_V1_STR}/filters", tags=["filters"])
app.include_router(analytics.router, prefix=settings.API_V1_STR, tags=["analytics"])
app.include_router(brands.router, prefix=settings.API_V1_STR, tags=["brands"])
app.include_router(creatives.router, prefix=f"{settings.API_V1_STR}/creatives", tags=["creatives"])
app.include_router(ai.router, prefix=f"{settings.API_V1_STR}/ai", tags=["ai"])

@app.get("/api/health", tags=["health"])
async def health_check():
    return {
        "status": "healthy", 
        "rows": len(base_data_manager.get_df()),
        "project": settings.PROJECT_NAME
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
