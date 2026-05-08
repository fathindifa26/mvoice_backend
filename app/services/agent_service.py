import json
from typing import List, Dict, Any, Optional
from app.core.config import settings
import httpx

class AgentService:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = settings.AI_MODEL

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
        """Processes user message and determines which tools to call."""
        
        messages = [
            {"role": "system", "content": "You are a helpful AI Assistant for MVoice Intelligence. You help users navigate and configure their marketing dashboard. If a user asks to change something, use the provided tools. If you use a tool, explain what you've done to the dashboard."},
            *history,
            {"role": "user", "content": user_message}
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "tools": [{"type": "function", "function": t} for t in self.get_tools_definition()],
            "tool_choice": "auto"
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://mvoice-intelligence.com",
            "X-Title": "MVoice Intelligence Agent",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            
            message = result["choices"][0]["message"]
            
            # Handle Tool Calls
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

agent_service = AgentService()
