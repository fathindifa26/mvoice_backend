from typing import Optional, List, Dict
from app.services.base import base_data_manager

class BrandService:
    @staticmethod
    def get_top_brands(
        business_unit: Optional[str] = None,
        is_our_brand: bool = True,
        metric: str = "views",
        limit: int = 3
    ) -> List[Dict]:
        df = base_data_manager.get_df()
        if df.empty:
            return []
            
        filtered_df = df[df["is_our_brand"] == is_our_brand]
        filtered_df = base_data_manager.apply_base_filters(filtered_df, business_unit=business_unit)
            
        if filtered_df.empty:
            return []

        if metric == "views":
            top = filtered_df.groupby("brand")["views"].mean().sort_values(ascending=False).head(limit)
            return [{"name": name, "value": f"{val/1000000:.1f}M" if val >= 1000000 else f"{val/1000:.0f}K"} 
                    for name, val in top.items()]
        else:
            top = filtered_df.groupby("brand").size().sort_values(ascending=False).head(limit)
            max_val = top.max() if not top.empty else 1
            return [{"name": name, "value": f"{(val/max_val)*10:.1f}"} 
                    for name, val in top.items()]

    @staticmethod
    def get_brand_performance_summary(
        brand: str,
        business_unit: Optional[str] = None
    ) -> Dict:
        df = base_data_manager.get_df()
        if df.empty:
            return {}
            
        brand_df = df[df["brand"] == brand]
        if business_unit and business_unit != "All":
            brand_df = brand_df[brand_df["business_unit"] == business_unit]
            
        if brand_df.empty:
            return {}
            
        avg_views = float(brand_df["views"].mean())
        
        # Talent type breakdown
        talent_breakdown = brand_df.groupby("talent_type")["views"].mean().to_dict()
        talent_breakdown = {k: float(v) for k, v in talent_breakdown.items()}
        
        return {
            "avg_views": avg_views,
            "talent_performance": talent_breakdown,
            "total_creatives": int(len(brand_df))
        }

    @staticmethod
    def get_market_performance_summary(
        business_unit: str,
        exclude_brands: List[str] = []
    ) -> Dict:
        df = base_data_manager.get_df()
        if df.empty:
            return {}
            
        market_df = df[df["business_unit"] == business_unit]
        if exclude_brands:
            market_df = market_df[~market_df["brand"].isin(exclude_brands)]
            
        if market_df.empty:
            return {}
            
        avg_views = float(market_df["views"].mean())
        talent_breakdown = market_df.groupby("talent_type")["views"].mean().to_dict()
        talent_breakdown = {k: float(v) for k, v in talent_breakdown.items()}
        
        return {
            "avg_views": avg_views,
            "talent_performance": talent_breakdown,
            "total_creatives": int(len(market_df))
        }

brand_service = BrandService()
