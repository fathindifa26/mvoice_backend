import asyncio
import json
import os
import sys

# Add current directory to path so we can import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.analytics_service import analytics_service
from app.services.brand_service import brand_service
from app.services.ai_service import ai_service
from app.core.config import settings

async def test_ai_summary():
    print("=== AI SUMMARY TEST SCRIPT (MULTI-METRIC) ===\n")
    
    # 1. Configuration
    brand_a = "Wardah"
    brand_b = "Pond's"
    business_unit = "Beauty and Wellbeing"
    metrics = ["topic", "hook_type", "format", "tone", "face_emotion"]
    
    print(f"Targeting: {brand_a} vs {brand_b} ({business_unit})")
    print(f"Metrics: {', '.join(metrics)}")
    print(f"AI Model: {settings.AI_MODEL}")
    print(f"API Key present: {'Yes' if settings.OPENROUTER_API_KEY else 'No (Using Mock Mode)'}")
    print("-" * 50)

    # 2. Fetch Data for all metrics
    print("\nFetching data for 5 metrics + Brand Summaries...")
    
    all_brand_a_data = {}
    all_brand_b_data = {}
    all_benchmarks = {}

    for metric in metrics:
        data_a = analytics_service.analyze_variable(
            column=metric,
            business_unit=business_unit,
            brand=brand_a
        )
        
        data_b = analytics_service.analyze_variable(
            column=metric,
            business_unit=business_unit,
            brand=brand_b
        )
        
        all_brand_a_data[metric] = data_a.get("data", [])
        all_brand_b_data[metric] = data_b.get("data", [])
        all_benchmarks[metric] = {
            "bu_mean": data_a.get("bu_mean"),
            "bu_mean_bin": data_a.get("bu_mean_bin")
        }
        
    # Additional Performance Summaries
    perf_a = brand_service.get_brand_performance_summary(brand_a, business_unit)
    perf_b = brand_service.get_brand_performance_summary(brand_b, business_unit)
    perf_market = brand_service.get_market_performance_summary(business_unit, exclude_brands=[brand_a, brand_b])
    
    # Fetch Top 3 Our and Top 3 Competitors for context
    top_our = brand_service.get_top_brands(business_unit, True, limit=3)
    top_comp = brand_service.get_top_brands(business_unit, False, limit=3)
    
    top_leaders_data = {}
    for b in top_our + top_comp:
        brand_name = b["name"]
        top_leaders_data[brand_name] = brand_service.get_brand_performance_summary(brand_name, business_unit)

    all_brand_a_data["performance_summary"] = perf_a
    all_brand_b_data["performance_summary"] = perf_b
    all_benchmarks["market_performance"] = perf_market
    all_benchmarks["top_leaders_performance"] = top_leaders_data
    
    # 3. Generate Prompt
    print("\nGenerating AI Prompt...")
    prompt = ai_service.get_comparison_prompt(
        brand_a=brand_a,
        brand_b=brand_b,
        brand_a_data=all_brand_a_data,
        brand_b_data=all_brand_b_data,
        bu_benchmarks=all_benchmarks
    )
    
    print("\n" + "="*20 + " FULL PROMPT " + "="*20)
    print(prompt)
    print("="*53)

    # 4. Generate Summary
    print("\nCalling AI Service...")
    summary = await ai_service.generate_comparison_summary(
        brand_a=brand_a,
        brand_b=brand_b,
        brand_a_data=all_brand_a_data,
        brand_b_data=all_brand_b_data,
        bu_benchmarks=all_benchmarks
    )
    
    print("\n" + "="*20 + " AI RESPONSE (JSON) " + "="*20)
    print(json.dumps(summary, indent=2))
    print("="*60)
    
    print("\nTest complete.")

if __name__ == "__main__":
    asyncio.run(test_ai_summary())
