import json
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.services.analytics_service import analytics_service
import httpx

class BaseAgentService:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = settings.AI_MODEL

    async def _call_llm(self, messages: List[Dict], tools: List[Dict]) -> Dict:
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": [{"type": "function", "function": t} for t in tools],
            "tool_choice": "auto"
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://mvoice-intelligence.com",
            "X-Title": "MVoice Intelligence Agent",
            "Content-Type": "application/json"
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            message = result["choices"][0]["message"]
            tool_calls = message.get("tool_calls", [])
            return {
                "answer": message.get("content"),
                "tool_calls": [
                    {
                        "id": tc["id"],
                        "name": tc["function"]["name"],
                        "args": json.loads(tc["function"]["arguments"])
                    } for tc in tool_calls
                ]
            }

class ComparisonAgentService(BaseAgentService):
    """Handles logic for the Comparison menu (Brand A vs Brand B)"""
    def get_tools_definition(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "set_benchmark_type",
                "description": "Change the main dashboard benchmark metric between frequency and views",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "metric": {
                            "type": "string",
                            "enum": ["frequency", "views", "engagements"],
                            "description": "The metric to use for benchmarking"
                        }
                    },
                    "required": ["metric"]
                }
            },
            {
                "name": "set_brands",
                "description": "Change the brands being compared on the dashboard",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "brand_a": {
                            "type": "string",
                            "description": "The name of the main brand (left)"
                        },
                        "brand_b": {
                            "type": "string",
                            "description": "The name of the compared brand (right)"
                        }
                    },
                    "required": ["brand_a", "brand_b"]
                }
            },
            {
                "name": "set_filters",
                "description": "Update filters like talent type for either or both brands",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "talent_type_a": {
                            "type": "string",
                            "enum": ["All", "Mega", "Makro", "Mikro", "Nano"],
                            "description": "Talent type filter for brand A"
                        },
                        "talent_type_b": {
                            "type": "string",
                            "enum": ["All", "Mega", "Makro", "Mikro", "Nano"],
                            "description": "Talent type filter for brand B"
                        }
                    }
                }
            },
            {
                "name": "set_active_metrics",
                "description": "Change which creative metrics are visualized in the charts",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "metrics": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": [
                                    "views", "engagements", "channels", "creator type",
                                    "Visuals__Total Video Duration (Seconds)", "Visuals__Visual Aesthetic/Style", 
                                    "Visuals__Primary Color Palette", "Visuals__Lighting Style",
                                    "Talent__Main Talent Type", "Talent__Number of Key Talent", "Talent__Apparent Demographics (Primary)",
                                    "Messaging__Core Message/Overall Takeaway", "Messaging__Message Originality/Uniqueness",
                                    "Messaging__Primary Emotional Appeal", "Messaging__Key Product/Service Benefit Highlighted", "Messaging__Call to Action (CTA) Type",
                                    "Meaningful & Different__Social or Cultural Impact Potential", "Meaningful & Different__Emotional Depth", "Meaningful & Different__Authenticity & Relatability",
                                    "Hook__Analyzed Duration (Seconds)", "Hook__Primary Message/Question", "Hook__Visual Strategy", "Hook__Audio Strategy",
                                    "Hook__On-Screen Text Presence", "Hook__Emotional Tone Evoked", "Hook__Pacing/Editing (First 3-5s)", "Hook__Uniqueness & Effectiveness (Overall)",
                                    "Audio__Primary Audio Composition", "Audio__Music Presence", "Audio__Music Genre/Style"
                                ]
                            },
                            "description": "List of metrics to display"
                        }
                    },
                    "required": ["metrics"]
                }
            },
            {
                "name": "generate_strategic_summary",
                "description": "Trigger the AI to generate a new strategic comparative summary",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_current_analysis",
                "description": "Read the current strategic summary and performance data displayed on the dashboard to discuss it with the user",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]

    async def chat_with_agent(self, user_message: str, history: List[Dict] = []) -> Dict:
        system_prompt = "You are a Comparison Specialist AI for MVoice. You help users compare two brands side-by-side. Use tools to update the dashboard view."
        messages = [{"role": "system", "content": system_prompt}]
        
        # Avoid duplicating the last user message if it's already in history
        if history and history[-1].get("role") == "user" and history[-1].get("content") == user_message:
            messages.extend(history)
        else:
            messages.extend(history)
            if user_message:
                messages.append({"role": "user", "content": user_message})
                
        return await self._call_llm(messages, self.get_tools_definition())

class PortfolioAgentService(BaseAgentService):
    """Handles logic for the Main Dashboard / Portfolio Insights (Deep Dives)"""
    def get_tools_definition(self) -> List[Dict[str, Any]]:
        # ... (definition remains same)
        return [
            {
                "name": "get_portfolio_insights",
                "description": "Get high-level performance values (High Performing, Average, Needs Review counts) for a specific brand or business unit.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "brand": {"type": "string", "description": "Specific brand to analyze"},
                        "business_unit": {"type": "string", "description": "Business unit to filter by"},
                        "metric": {"type": "string", "enum": ["frequency", "views", "engagements"]}
                    }
                }
            },
            {
                "name": "get_creative_deep_dive",
                "description": "Get detailed data context for specific creative categories. Categories available: Visuals, Talent, Messaging, Hook, Audio, Meaningful & Different.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "brand": {"type": "string", "description": "Brand to analyze"},
                        "business_unit": {"type": "string", "description": "Business unit to analyze"},
                        "metric": {"type": "string", "enum": ["frequency", "views", "engagements"], "description": "The metric to analyze (views, frequency/count, or engagements)"},
                        "dimensions": {
                            "type": "array", 
                            "items": {"type": "string"},
                            "description": "List of categories to fetch (e.g. ['Visuals', 'Hook']). If empty, fetches all categories."
                        },
                        "limit": {"type": "integer", "description": "How many rows per dimension. Default is 3.", "default": 3},
                        "sort_order": {"type": "string", "enum": ["desc", "asc"], "description": "Use 'desc' for Top performers, 'asc' for Bottom performers. Default is 'desc'."}
                    }
                }
            }
        ]

    async def chat_with_agent(self, user_message: str, history: List[Dict] = []) -> Dict:
        system_prompt = (
            "You are a Portfolio Intelligence Agent. You help users explore creative performance across their entire portfolio. "
            "WORKFLOW FOR DATA REQUESTS: \n"
            "1. TARGETED FETCH: Call `get_creative_deep_dive` with relevant categories (Visuals, Hook, Messaging, Talent, Audio, Meaningful & Different). "
            "If the user asks for a general overview, you can leave the dimensions empty to fetch all.\n"
            "2. Decide if the user wants 'Top performers' (sort_order='desc') or 'Bottom performers' (sort_order='asc') "
            "and set an appropriate `limit` (default is 3).\n"
            "3. ANALYSIS: Once you have the data, synthesize a comprehensive answer.\n"
            "Be efficient: Only fetch the categories that are actually relevant to the user's question."
        )
        messages = [{"role": "system", "content": system_prompt}]
        
        # Avoid duplicating the last user message if it's already in history
        if history and history[-1].get("role") == "user" and history[-1].get("content") == user_message:
            messages.extend(history)
        else:
            messages.extend(history)
            if user_message:
                messages.append({"role": "user", "content": user_message})

        return await self._call_llm(messages, self.get_tools_definition())

# Export specialized instances
comparison_agent = ComparisonAgentService()
portfolio_agent = PortfolioAgentService()

# Backward compatibility alias
agent_service = comparison_agent
