import pandas as pd
import numpy as np
import os
from typing import Optional, List, Dict, Union

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
                       metric: str = "views",
                       limit: int = 3) -> List[Dict]:
        df = self.get_df()
        if df.empty:
            return []
            
        filtered_df = df[df["is_our_brand"] == is_our_brand]
        if business_unit and business_unit != "All":
            filtered_df = filtered_df[filtered_df["business_unit"] == business_unit]
            
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

    def analyze_variable(self, 
                         column: str,
                         business_unit: Optional[str] = None,
                         brand: Optional[str] = None,
                         talent_type: Optional[str] = None,
                         from_date: Optional[str] = None,
                         to_date: Optional[str] = None) -> Dict:
        df = self.filter_creatives(business_unit, brand, talent_type, from_date, to_date)
        if df.empty or column not in df.columns:
            return {"type": "unknown", "data": []}
            
        # Determine if numeric or categorical
        col_data = df[column].dropna()
        if col_data.empty:
             return {"type": "empty", "data": []}

        # Check for numeric types (int or float)
        is_numeric = pd.api.types.is_numeric_dtype(df[column]) and not pd.api.types.is_bool_dtype(df[column])
        
        if is_numeric:
            # Percentile-based Histogram
            # We use fixed percentiles or dynamic bins
            # Let's use 5 bins based on quantiles for "percentile-based"
            try:
                # If too few unique values, treat as categorical (e.g. face_present)
                if df[column].nunique() < 6:
                    counts = df[column].value_counts().sort_index()
                    return {
                        "type": "categorical",
                        "data": [{"bin": str(k), "count": int(v)} for k, v in counts.items()]
                    }

                # Otherwise, true numerical histogram
                q = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
                bins = df[column].quantile(q).unique()
                if len(bins) < 2: # All values the same
                     return {"type": "categorical", "data": [{"bin": str(df[column].iloc[0]), "count": len(df)}]}
                
                df_temp = df.copy()
                df_temp['bin'] = pd.cut(df_temp[column], bins=bins, include_lowest=True)
                counts = df_temp['bin'].value_counts().sort_index()
                
                formatted_data = []
                for interval, count in counts.items():
                    label = f"{interval.left:.1f}-{interval.right:.1f}" if isinstance(interval.left, float) else f"{interval.left}-{interval.right}"
                    formatted_data.append({"bin": label, "count": int(count)})
                
                return {"type": "numerical", "data": formatted_data}
            except:
                # Fallback to simple counts if quantiles fail
                counts = df[column].value_counts().head(10)
                return {"type": "categorical", "data": [{"bin": str(k), "count": int(v)} for k, v in counts.items()]}
        else:
            # Categorical - value counts sorted
            counts = df[column].value_counts().sort_values(ascending=False)
            return {
                "type": "categorical",
                "data": [{"bin": str(k), "count": int(v)} for k, v in counts.items()]
            }

CSV_PATH = os.path.join(os.path.dirname(__file__), "creatives_dummy.csv")
data_manager = DataManager(CSV_PATH)
