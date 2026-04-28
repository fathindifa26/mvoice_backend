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
        if 'date_post' in self._df.columns:
            self._df['date_post'] = pd.to_datetime(self._df['date_post'])
        if 'is_our_brand' in self._df.columns:
            self._df['is_our_brand'] = self._df['is_our_brand'].map(lambda x: str(x).strip().lower() == 'true')
        self._df = self._df.where(pd.notnull(self._df), None)

    def get_df(self):
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
            
        if from_date and "date_post" in df.columns:
            df = df[df["date_post"] >= pd.to_datetime(from_date)]
        if to_date and "date_post" in df.columns:
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

    def get_filtered_creative_list(self, 
                                   business_unit: Optional[str] = None,
                                   brand: Optional[str] = None,
                                   talent_type: Optional[str] = None,
                                   from_date: Optional[str] = None,
                                   to_date: Optional[str] = None,
                                   filters: List[Dict] = [], 
                                   limit: int = 5) -> List[Dict]:
        df = self.filter_creatives(business_unit, brand, talent_type, from_date, to_date)
        
        if df.empty:
            return []

        # Apply bar-level filters
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

    def analyze_variable(self, 
                         column: str,
                         aggregation_metric: str = "frequency",
                         business_unit: Optional[str] = None,
                         brand: Optional[str] = None,
                         talent_type: Optional[str] = None,
                         from_date: Optional[str] = None,
                         to_date: Optional[str] = None) -> Dict:
        
        df = self.filter_creatives(business_unit, brand, talent_type, from_date, to_date)
        df_bench = self.filter_creatives(business_unit, "All", None, from_date, to_date)

        if df.empty or column not in df.columns:
            return {"type": "unknown", "data": []}
            
        is_numeric = pd.api.types.is_numeric_dtype(df[column]) and not pd.api.types.is_bool_dtype(df[column])
        
        if is_numeric:
            bu_mean = float(df_bench[column].mean()) if not df_bench.empty else 0
            
            q = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
            try:
                bins = df_bench[column].quantile(q).unique()
                if len(bins) < 2: bins = [df_bench[column].min(), df_bench[column].max() + 0.001]
            except:
                bins = [0, 1]

            temp = df.copy()
            temp['bin'] = pd.cut(temp[column], bins=bins, include_lowest=True)
            if aggregation_metric == "views":
                counts = temp.groupby('bin', observed=True)['views'].sum()
            else:
                counts = temp['bin'].value_counts()
            
            total = counts.sum() if counts.sum() > 0 else 1
            formatted_data = [{"bin": f"{i.left:.1f}-{i.right:.1f}", "count": float(v), "percentage": float(v/total)} 
                             for i, v in counts.sort_index().items()]

            bu_mean_bin = ""
            for i in range(len(bins)-1):
                if bins[i] <= bu_mean <= bins[i+1]:
                    bu_mean_bin = f"{bins[i]:.1f}-{bins[i+1]:.1f}"
                    break

            return {
                "type": "numerical",
                "data": formatted_data,
                "bu_mean": bu_mean,
                "bu_mean_bin": bu_mean_bin
            }
        else:
            # Categorical
            bu_mode = str(df_bench[column].mode().iloc[0]) if not df_bench.empty and not df_bench[column].mode().empty else ""

            if aggregation_metric == "views":
                counts = df.groupby(column)["views"].sum().sort_values(ascending=False)
            else:
                counts = df[column].value_counts().sort_values(ascending=False)
            
            total = counts.sum() if counts.sum() > 0 else 1
            formatted_data = [{"bin": str(k), "count": float(v), "percentage": float(v/total)} for k, v in counts.items()]
            
            return {
                "type": "categorical",
                "data": formatted_data,
                "bu_mean": 0,
                "bu_mean_bin": bu_mode
            }

CSV_PATH = os.path.join(os.path.dirname(__file__), "creatives_dummy.csv")
data_manager = DataManager(CSV_PATH)
