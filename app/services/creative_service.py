import pandas as pd
from typing import Optional, List, Dict
from app.services.base import base_data_manager

class CreativeService:
    @staticmethod
    def get_filtered_creative_list(
        business_unit: Optional[str] = None,
        brand: Optional[str] = None,
        talent_type: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        filters: List[Dict] = [], 
        limit: int = 5
    ) -> List[Dict]:
        df = base_data_manager.apply_base_filters(
            base_data_manager.get_df(), business_unit, brand, talent_type, from_date, to_date
        )
        
        if df.empty:
            return []

        # Apply bar-level drill-down filters
        for f in filters:
            col = f.get("column")
            vals = f.get("values", [])
            if not col or not vals or col not in df.columns:
                continue
            
            is_numeric = pd.api.types.is_numeric_dtype(df[col]) and not pd.api.types.is_bool_dtype(df[col])
            
            if is_numeric:
                combined_mask = pd.Series(False, index=df.index)
                for v in vals:
                    try:
                        low, high = map(float, v.split("-"))
                        combined_mask |= (df[col] >= low) & (df[col] <= high)
                    except:
                        continue
                df = df[combined_mask]
            else:
                df = df[df[col].astype(str).isin(vals)]

        # Sort by views and take top N
        top_df = df.sort_values(by="views", ascending=False).head(limit)
        
        return top_df.to_dict(orient="records")

creative_service = CreativeService()
