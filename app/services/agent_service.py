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
                            "enum": ["frequency", "views"],
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
                                "enum": ["topic", "hook_type", "format", "tone", "face_emotion", "duration_sec"]
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
