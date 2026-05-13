from fastapi import APIRouter
from typing import Optional
from app.services.analytics_service import analytics_service
from app.services.ai_service import ai_service

router = APIRouter()

@router.get("/analyze")
async def analyze_metric(
    metric: str,
    aggregation_metric: str = "frequency", # "frequency", "views", or "engagements"
    business_unit: Optional[str] = None,
    brand: Optional[str] = None,
    talent_type: Optional[str] = None,
    channel: Optional[str] = None,
    creator_type: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):
    return analytics_service.analyze_variable(
        column=metric,
        aggregation_metric=aggregation_metric,
        business_unit=business_unit,
        brand=brand,
        talent_type=talent_type,
        channel=channel,
        creator_type=creator_type,
        from_date=from_date,
        to_date=to_date
    )

@router.get("/portfolio-summary")
async def get_portfolio_summary(
    aggregation_metric: str = "views",
    business_unit: Optional[str] = None,
    brand: Optional[str] = None,
    channel: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):
    return analytics_service.get_portfolio_summary(
        aggregation_metric=aggregation_metric,
        business_unit=business_unit,
        brand=brand,
        channel=channel,
        from_date=from_date,
        to_date=to_date
    )

@router.get("/portfolio-summary-ai")
async def get_portfolio_summary_ai(
    aggregation_metric: str = "views",
    business_unit: Optional[str] = None,
    brand: Optional[str] = None,
    channel: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):
    # Get AI context and generate dynamic insights
    ai_context = analytics_service.get_ai_portfolio_context(
        aggregation_metric=aggregation_metric,
        business_unit=business_unit,
        brand=brand,
        channel=channel,
        from_date=from_date,
        to_date=to_date
    )
    
    ai_insights = await ai_service.generate_portfolio_insights(ai_context)
    
    return ai_insights

@router.get("/portfolio-ai-context")
async def get_portfolio_ai_context(
    aggregation_metric: str = "views",
    business_unit: Optional[str] = None,
    brand: Optional[str] = None,
    channel: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):
    return analytics_service.get_ai_portfolio_context(
        aggregation_metric=aggregation_metric,
        business_unit=business_unit,
        brand=brand,
        channel=channel,
        from_date=from_date,
        to_date=to_date
    )
