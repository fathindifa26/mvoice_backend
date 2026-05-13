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

    @staticmethod
    def normalize_string(s: str) -> str:
        """Removes spaces, punctuation and converts to lowercase for robust matching."""
        if not s: return ""
        import re
        # Remove all non-alphanumeric characters and convert to lower
        return re.sub(r'[^a-zA-Z0-9]', '', str(s)).lower()

    def find_exact_name(self, column: str, value: str) -> str:
        """Matches a value against a column's unique values using normalization."""
        if not value or value == "All" or value == "Select Brand":
            return value
            
        df = self.get_df()
        if df.empty or column not in df.columns:
            return value
            
        target = self.normalize_string(value)
        unique_names = df[column].dropna().unique()
        
        for name in unique_names:
            if self.normalize_string(str(name)) == target:
                return name
                
        return value

    def load_data(self):
        if not os.path.exists(self.csv_path):
            print(f"Warning: CSV file not found at {self.csv_path}")
            self._df = pd.DataFrame()
            return
            
        try:
            self._df = pd.read_csv(self.csv_path)
            # Strip whitespace from column names
            self._df.columns = [c.strip() for c in self._df.columns]
            
            if 'date_post' in self._df.columns:
                self._df['date_post'] = pd.to_datetime(self._df['date_post'], errors='coerce')
                
            if 'channels' in self._df.columns:
                self._df['channels'] = self._df['channels'].str.title()
            
            if 'creator type' in self._df.columns:
                self._df['creator type'] = self._df['creator type'].str.title()
                
            if 'is_our_brand' in self._df.columns:
                self._df['is_our_brand'] = self._df['is_our_brand'].map(
                    lambda x: str(x).strip().lower() == 'true' if pd.notnull(x) else False
                )
                
            self._df = self._df.where(pd.notnull(self._df), None)
            print(f"Successfully loaded {len(self._df)} rows from {self.csv_path}")
        except Exception as e:
            print(f"Error loading CSV: {e}")
            self._df = pd.DataFrame()

    def get_df(self) -> pd.DataFrame:
        if self._df is None:
            self.load_data()
        return self._df

    def get_filter_options(self, business_unit: Optional[str] = None) -> Dict:
        df = self.get_df()
        
        # Always return these keys to avoid frontend errors
        options = {
            "business_units": [],
            "brands": [],
            "talent_types": [],
            "channels": [],
            "creator_types": [],
            "date_range": {"min": None, "max": None}
        }
        
        if df.empty:
            return options
        
        options["business_units"] = sorted(df["business_unit"].dropna().unique().tolist())
        
        filtered_df = df
        if business_unit and business_unit != "All":
            filtered_df = df[df["business_unit"] == business_unit]
        
        options["brands"] = sorted(filtered_df["brand"].dropna().unique().tolist())
        options["talent_types"] = sorted(filtered_df["talent_type"].dropna().unique().tolist()) if "talent_type" in filtered_df.columns else []
        options["channels"] = sorted(filtered_df["channels"].dropna().unique().tolist()) if "channels" in filtered_df.columns else []
        
        # Use 'creator type' (with space) to match CSV but 'creator_types' as JSON key
        if "creator type" in filtered_df.columns:
            options["creator_types"] = sorted(filtered_df["creator type"].dropna().unique().tolist())
            
        if not filtered_df.empty and "date_post" in filtered_df.columns:
            valid_dates = filtered_df["date_post"].dropna()
            if not valid_dates.empty:
                options["date_range"]["min"] = valid_dates.min().strftime('%Y-%m-%d')
                options["date_range"]["max"] = valid_dates.max().strftime('%Y-%m-%d')
            
        return options

    def apply_base_filters(self, 
                           df: pd.DataFrame,
                           business_unit: Optional[str] = None, 
                           brand: Optional[str] = None,
                           talent_type: Optional[str] = None,
                           channel: Optional[str] = None,
                           creator_type: Optional[str] = None,
                           from_date: Optional[str] = None,
                           to_date: Optional[str] = None) -> pd.DataFrame:
        if df.empty:
            return df
        
        filtered_df = df.copy()
        
        if business_unit and business_unit != "All":
            exact_bu = self.find_exact_name("business_unit", business_unit)
            filtered_df = filtered_df[filtered_df["business_unit"] == exact_bu]
            
        if brand and brand != "All" and brand != "Select Brand":
            exact_brand = self.find_exact_name("brand", brand)
            filtered_df = filtered_df[filtered_df["brand"] == exact_brand]
        if talent_type and talent_type != "All":
            filtered_df = filtered_df[filtered_df["talent_type"] == talent_type]
        if channel and channel != "All" and "channels" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["channels"] == channel]
        if creator_type and creator_type != "All" and "creator type" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["creator type"] == creator_type]
            
        if from_date and "date_post" in filtered_df.columns:
            try:
                filtered_df = filtered_df[filtered_df["date_post"] >= pd.to_datetime(from_date)]
            except:
                pass
        if to_date and "date_post" in filtered_df.columns:
            try:
                filtered_df = filtered_df[filtered_df["date_post"] <= pd.to_datetime(to_date)]
            except:
                pass
            
        return filtered_df

# Shared instance
base_data_manager = BaseDataManager(settings.CSV_PATH)
