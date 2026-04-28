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

brand_service = BrandService()
