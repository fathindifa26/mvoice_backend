import pandas as pd
import os
from typing import Optional, Dict
from app.core.config import settings

class BaseDataManager:
    """
    Handles raw data loading and common filtering logic.
    """
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self._df = None
        self.load_data()

    def load_data(self):
        if not os.path.exists(self.csv_path):
            print(f"Warning: CSV file not found at {self.csv_path}")
            self._df = pd.DataFrame()
            return
            
        self._df = pd.read_csv(self.csv_path)
        
        if 'date_post' in self._df.columns:
            self._df['date_post'] = pd.to_datetime(self._df['date_post'])
            
        if 'is_our_brand' in self._df.columns:
            self._df['is_our_brand'] = self._df['is_our_brand'].map(
                lambda x: str(x).strip().lower() == 'true' if pd.notnull(x) else False
            )
            
        self._df = self._df.where(pd.notnull(self._df), None)

    def get_df(self) -> pd.DataFrame:
        if self._df is None:
            self.load_data()
        return self._df

    def get_filter_options(self, business_unit: Optional[str] = None) -> Dict:
        df = self.get_df()
        if df.empty:
            return {"business_units": [], "brands": [], "talent_types": []}
        
        bus = sorted(df["business_unit"].unique().tolist())
        
        if business_unit and business_unit != "All":
            brands = sorted(df[df["business_unit"] == business_unit]["brand"].unique().tolist())
        else:
            brands = sorted(df["brand"].unique().tolist())
            
        return {
            "business_units": bus,
            "brands": brands,
            "talent_types": sorted(df["talent_type"].dropna().unique().tolist()),
            "date_range": {
                "min": df["date_post"].min().strftime('%Y-%m-%d') if not df.empty and pd.notnull(df["date_post"].min()) else None,
                "max": df["date_post"].max().strftime('%Y-%m-%d') if not df.empty and pd.notnull(df["date_post"].max()) else None,
            }
        }

    def apply_base_filters(self, 
                           df: pd.DataFrame,
                           business_unit: Optional[str] = None, 
                           brand: Optional[str] = None,
                           talent_type: Optional[str] = None,
                           from_date: Optional[str] = None,
                           to_date: Optional[str] = None) -> pd.DataFrame:
        if df.empty:
            return df
        
        if business_unit and business_unit != "All":
            df = df[df["business_unit"] == business_unit]
        if brand and brand != "All" and brand != "Select Brand":
            df = df[df["brand"] == brand]
        if talent_type and talent_type != "All":
            df = df[df["talent_type"] == talent_type]
            
        if from_date and "date_post" in df.columns:
            df = df[df["date_post"] >= pd.to_datetime(from_date)]
        if to_date and "date_post" in df.columns:
            df = df[df["date_post"] <= pd.to_datetime(to_date)]
            
        return df

# Shared instance
base_data_manager = BaseDataManager(settings.CSV_PATH)
