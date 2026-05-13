import pandas as pd
from typing import Optional, Dict, List
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

    @staticmethod
    def get_portfolio_summary(
        aggregation_metric: str = "views",
        business_unit: Optional[str] = None,
        brand: Optional[str] = None,
        channel: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> Dict:
        df = base_data_manager.apply_base_filters(
            base_data_manager.get_df(), business_unit=business_unit, brand=brand, channel=channel, from_date=from_date, to_date=to_date
        )
        
        if df.empty:
            return {
                "successRate": 0,
                "highPerforming": 0,
                "average": 0,
                "needsReview": 0,
                "summaryText": "No data available for the selected filters."
            }
            
        # Use views or engagements as performance column. Default to views for frequency.
        perf_col = aggregation_metric if aggregation_metric in ["views", "engagements"] else "views"
        
        # Calculate median
        median_val = df[perf_col].median()
        
        # Thresholds: Average is +/- 15% around median
        high_threshold = median_val * 1.15
        low_threshold = median_val * 0.85
        
        high_performing_count = int(df[df[perf_col] > high_threshold].shape[0])
        average_count = int(df[(df[perf_col] <= high_threshold) & (df[perf_col] >= low_threshold)].shape[0])
        needs_review_count = int(df[df[perf_col] < low_threshold].shape[0])
        
        total = df.shape[0]
        success_rate = round(((high_performing_count + average_count) / total) * 100) if total > 0 else 0
        
        metric_label = perf_col.capitalize()
        summary_text = (
            f"Your portfolio shows a {success_rate}% success rate, with {high_performing_count} assets "
            f"performing significantly above the median {metric_label}. This indicates a stable creative performance "
            f"across your current inventory."
        )
        
        return {
            "successRate": success_rate,
            "highPerforming": high_performing_count,
            "average": average_count,
            "needsReview": needs_review_count,
            "summaryText": summary_text
        }

    @staticmethod
    def get_available_dimensions() -> Dict:
        """Returns all available creative categories and their specific sub-metrics (columns)."""
        df = base_data_manager.get_df()
        prefixes = ["Visuals__", "Talent__", "Messaging__", "Hook__", "Audio__", "Meaningful & Different__"]
        
        dimensions = {}
        for p in prefixes:
            category_name = p.replace("__", "").strip()
            cols = [col for col in df.columns if col.startswith(p)]
            dimensions[category_name] = cols
            
        return {
            "categories": list(dimensions.keys()),
            "dimensions": dimensions
        }

    @staticmethod
    def get_ai_portfolio_context(
        aggregation_metric: str = "views",
        business_unit: Optional[str] = None,
        brand: Optional[str] = None,
        channel: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        dimensions: Optional[List[str]] = None,
        limit: int = 3,
        sort_order: str = "desc" # "desc" for top, "asc" for bottom
    ):
        df = base_data_manager.apply_base_filters(base_data_manager.get_df(), business_unit, brand, None, channel, None, from_date, to_date)
        if df.empty:
            return {"error": "No data found for selected filters"}

        prefixes = ["Visuals__", "Talent__", "Messaging__", "Hook__", "Audio__", "Meaningful & Different__"]
        
        # Identify dimensions to process
        if dimensions:
            # Match input categories to prefixes
            # e.g. "Visuals" -> all columns starting with "Visuals__"
            creative_cols = []
            for dim in dimensions:
                matched_prefix = next((p for p in prefixes if p.lower().startswith(dim.lower())), None)
                if matched_prefix:
                    creative_cols.extend([col for col in df.columns if col.startswith(matched_prefix)])
                elif dim in df.columns: # fallback to exact column if provided
                    creative_cols.append(dim)
        else:
            # Default behavior: all creative dimensions
            creative_cols = [col for col in df.columns if any(col.startswith(p) for p in prefixes)]
        
        creative_context = {}
        ascending = (sort_order == "asc")
        
        for col in creative_cols:
            # Group by dimension and aggregate based on metric
            if aggregation_metric == "frequency":
                dist = df.groupby(col).size().reset_index(name='value')
            else:
                dist = df.groupby(col)[aggregation_metric].sum().reset_index(name='value')
            
            # Sort and take limit
            dist = dist.sort_values(by='value', ascending=ascending).head(limit)
            
            # Calculate percentages relative to the whole dataset (not just the head)
            total_sum = df[aggregation_metric].sum() if aggregation_metric != "frequency" else len(df)
            
            if total_sum > 0:
                dist['percentage'] = (dist['value'] / total_sum) * 100
            else:
                dist['percentage'] = 0
                
            creative_context[col] = dist.to_dict('records')

        # Add some overall performance stats
        total_assets = len(df)
        avg_views = df['views'].mean() if 'views' in df.columns else 0
        avg_eng = df['engagements'].mean() if 'engagements' in df.columns else 0

        return {
            "filters": {
                "business_unit": business_unit,
                "brand": brand,
                "metric": aggregation_metric,
                "total_assets": total_assets,
                "limit": limit,
                "sort_order": sort_order
            },
            "performance_stats": {
                "avg_views": round(avg_views, 2),
                "avg_engagements": round(avg_eng, 2)
            },
            "creative_distributions": creative_context
        }

analytics_service = AnalyticsService()
