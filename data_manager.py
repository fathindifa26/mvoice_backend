import pandas as pd
import os
from typing import Optional, List, Dict

class DataManager:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self._df = None
        self.load_data()

    def load_data(self):
        if not os.path.exists(self.csv_path):
            self._df = pd.DataFrame()
            return
        self._df = pd.read_csv(self.csv_path)
        # Pre-process dates
        self._df['date_post'] = pd.to_datetime(self._df['date_post'])
        # Replace 'null' strings with actual None
        self._df = self._df.where(pd.notnull(self._df), None)

    def get_df(self):
        # Refresh if needed or just return
        return self._df

    def get_filter_options(self) -> Dict:
        df = self.get_df()
        if df.empty:
            return {"business_units": [], "brands": [], "talent_types": []}
        
        return {
            "business_units": sorted(df["business_unit"].unique().tolist()),
            "brands": sorted(df["brand"].unique().tolist()),
            "talent_types": sorted(df["talent_type"].dropna().unique().tolist()),
            "date_range": {
                "min": df["date_post"].min().strftime('%Y-%m-%d') if not df.empty else None,
                "max": df["date_post"].max().strftime('%Y-%m-%d') if not df.empty else None,
            }
        }

    def filter_creatives(self, 
                         business_unit: Optional[str] = None, 
                         brand: Optional[str] = None,
                         talent_type: Optional[str] = None,
                         from_date: Optional[str] = None,
                         to_date: Optional[str] = None) -> pd.DataFrame:
        df = self.get_df()
        if df.empty:
            return df
        
        if business_unit and business_unit != "All":
            df = df[df["business_unit"] == business_unit]
        if brand and brand != "All":
            df = df[df["brand"] == brand]
        if talent_type and talent_type != "All":
            df = df[df["talent_type"] == talent_type]
            
        if from_date:
            df = df[df["date_post"] >= pd.to_datetime(from_date)]
        if to_date:
            df = df[df["date_post"] <= pd.to_datetime(to_date)]
            
        return df

    def get_top_brands(self, 
                       business_unit: Optional[str] = None,
                       is_our_brand: bool = True,
                       metric: str = "views", # "views" or "frequency"
                       limit: int = 3) -> List[Dict]:
        df = self.get_df()
        if df.empty:
            return []
            
        # Filter by BU and Brand Ownership
        filtered_df = df[df["is_our_brand"] == is_our_brand]
        if business_unit and business_unit != "All":
            filtered_df = filtered_df[filtered_df["business_unit"] == business_unit]
            
        if filtered_df.empty:
            return []

        if metric == "views":
            # Group by brand and get mean views
            top = filtered_df.groupby("brand")["views"].mean().sort_values(ascending=False).head(limit)
            return [{"name": name, "value": f"{val/1000000:.1f}M" if val >= 1000000 else f"{val/1000:.0f}K"} 
                    for name, val in top.items()]
        else:
            # Frequency (let's assume it's based on some score or count for dummy)
            # For now, let's just use the 'face_present' or something as dummy frequency score
            # Real frequency would be count of occurrences in a time period.
            top = filtered_df.groupby("brand").size().sort_values(ascending=False).head(limit)
            # Normalize to a 0-10 scale for dummy
            max_val = top.max() if not top.empty else 1
            return [{"name": name, "value": f"{(val/max_val)*10:.1f}"} 
                    for name, val in top.items()]

CSV_PATH = os.path.join(os.path.dirname(__file__), "creatives_dummy.csv")
data_manager = DataManager(CSV_PATH)
