import pandas as pd
from typing import Optional, Dict
from app.services.base import base_data_manager

class AnalyticsService:
    @staticmethod
    def analyze_variable(
        column: str,
        aggregation_metric: str = "frequency",
        business_unit: Optional[str] = None,
        brand: Optional[str] = None,
        talent_type: Optional[str] = None,
        channel: Optional[str] = None,
        creator_type: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> Dict:
        df = base_data_manager.apply_base_filters(
            base_data_manager.get_df(), business_unit, brand, talent_type, channel, creator_type, from_date, to_date
        )
        # Benchmark usually only filtered by BU and channel
        df_bench = base_data_manager.apply_base_filters(
            base_data_manager.get_df(), business_unit=business_unit, channel=channel, from_date=from_date, to_date=to_date
        )

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
            elif aggregation_metric == "engagements":
                counts = temp.groupby('bin', observed=True)['engagements'].sum()
            else:
                counts = temp.groupby('bin', observed=True).size()
            
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
            elif aggregation_metric == "engagements":
                counts = df.groupby(column)["engagements"].sum().sort_values(ascending=False)
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

analytics_service = AnalyticsService()
