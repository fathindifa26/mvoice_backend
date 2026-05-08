import httpx
import json
from typing import List, Dict, Optional
from app.core.config import settings

class AIService:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = settings.AI_MODEL

    def get_comparison_prompt(
        self, 
        brand_a: str, 
        brand_b: str, 
        brand_a_data: List[Dict], 
        brand_b_data: List[Dict],
        bu_benchmarks: Dict
    ) -> str:
        """Generates the text prompt for AI analysis."""
        context = {
            "main_brand": {"name": brand_a, "metrics": brand_a_data},
            "compared_brand": {"name": brand_b, "metrics": brand_b_data},
            "market_averages": bu_benchmarks
        }

        return f"""
        You are a Senior Creative Strategist. Analyze the following performance data comparing two brands in the same business unit.
        The data contains:
        1. Market Benchmarks: Average performance for the whole category and a breakdown of the Top 3 Our Brands and Top 3 Competitors (Market Leaders).
        2. Graph Metrics: Detailed distributions for various creative attributes (e.g., Hook, Visuals, Talent, Messaging, Audio) and how they compare to the market average (BU Mean).

        DATA CONTEXT (JSON):
        {json.dumps(context, indent=2)}

        TASK:
        Generate a strategic summary with 4 distinct sections. Use bullet points for each section.
        Each section must be concise, data-driven, and actionable.

        OUTPUT SECTIONS:
        1. MAIN_BRAND_ANALYSIS: Insights specifically for {brand_a}. Mention where they excel or lag.
        2. COMPARED_BRAND_ANALYSIS: Insights specifically for {brand_b}. Mention their strengths.
        3. KEY_DIFFERENCES: Compare the two. What is the biggest gap in performance or strategy?
        4. STRATEGIC_RECOMMENDATIONS: Actionable steps for {brand_a} to outperform {brand_b}.

        FORMAT: Return ONLY a JSON object with these keys: "main_brand", "compared_brand", "differences", "recommendations".
        Each value should be a List of strings (bullet points).
        """

    async def generate_comparison_summary(
        self, 
        brand_a: str, 
        brand_b: str, 
        brand_a_data: List[Dict], 
        brand_b_data: List[Dict],
        bu_benchmarks: Dict
    ) -> Dict:
        """
        Generates a comparative AI summary based on performance data.
        """
        prompt = self.get_comparison_prompt(brand_a, brand_b, brand_a_data, brand_b_data, bu_benchmarks)

        if not self.api_key:
            # Fallback for testing without API key
            return self._generate_mock_response(brand_a, brand_b)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://mvoice-intelligence.com", # Required for OpenRouter
            "X-Title": "MVoice Intelligence",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a professional marketing analyst providing structured JSON insights."},
                {"role": "user", "content": prompt}
            ],
            "response_format": { "type": "json_object" }
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.base_url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return json.loads(content)
        except Exception as e:
            print(f"AI Service Error: {str(e)}")
            return self._generate_mock_response(brand_a, brand_b)

    async def generate_portfolio_insights(
        self,
        context_data: Dict
    ) -> Dict:
        """
        Generates dynamic portfolio summary, strengths, and weaknesses.
        """
        prompt = f"""
        You are a Senior Marketing Data Scientist. Analyze the following portfolio performance and creative distribution data.
        
        DATA CONTEXT (JSON):
        {json.dumps(context_data, indent=2)}
        
        TASK:
        1. Write a 2-sentence SUMMARY of the overall portfolio health.
        2. Identify 3 key STRENGTHS based on top-performing creative dimensions.
        3. Identify 3 key WEAKNESSES or areas for improvement based on the data.
        
        STRENGTHS/WEAKNESSES should be specific (e.g., mention specific Hook strategies or Visual styles that are dominant).
        
        FORMAT: Return ONLY a JSON object with these keys: 
        "summary": "string",
        "strengths": ["list of strings"],
        "weaknesses": ["list of strings"]
        """

        print("\n" + "="*50)
        print("AI PORTFOLIO INSIGHTS DEBUG")
        print("="*50)
        print("CONTEXT DATA SENT TO AI:")
        print(json.dumps(context_data, indent=2))
        print("\nFULL PROMPT SENT TO AI:")
        print(prompt)
        print("="*50 + "\n")

        if not self.api_key:
            return {
                "summary": "Analyzing your portfolio based on " + context_data.get("aggregation_used", "views") + ".",
                "strengths": ["Strong hook strategy", "Consistent visuals"],
                "weaknesses": ["Low engagement in audio", "Talent variety needed"]
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://mvoice-intelligence.com",
            "X-Title": "MVoice Intelligence",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a professional marketing analyst providing structured JSON insights."},
                {"role": "user", "content": prompt}
            ],
            "response_format": { "type": "json_object" }
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.base_url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return json.loads(content)
        except Exception as e:
            print(f"AI Portfolio Insights Error: {str(e)}")
            return {
                "summary": "Error generating insights. Please try again.",
                "strengths": [],
                "weaknesses": []
            }

    def _generate_mock_response(self, brand_a: str, brand_b: str) -> Dict:
        """Fallback mock response for development/testing."""
        return {
            "main_brand": [
                f"{brand_a} excel in visual hooks with 20% higher engagement than average.",
                "Retention drops significantly after the first 5 seconds compared to competitors."
            ],
            "compared_brand": [
                f"{brand_b} has strong performance in educational topics.",
                "High frequency of posting is driving consistent reach but lower depth of engagement."
            ],
            "differences": [
                f"The primary gap is in the hook strategy: {brand_a} uses visual hooks while {brand_b} relies on dialogue.",
                f"{brand_b} has a more diverse topic distribution than {brand_a}."
            ],
            "recommendations": [
                f"Adopt {brand_b}'s educational topic strategy for secondary content pillars.",
                "Implement mid-video re-hooks to improve retention beyond the 5-second mark."
            ]
        }

ai_service = AIService()
