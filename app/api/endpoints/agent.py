from fastapi import APIRouter, Depends, Body
from typing import List, Dict, Optional
from pydantic import BaseModel
from app.services.agent_service import agent_service

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    history: List[Dict] = []
    agent_type: str = "comparison"  # "comparison" or "portfolio"

@router.post("/chat")
async def chat_with_agent(request: ChatRequest):
    """
    Endpoint for the AI Agent chat.
    Supports different agent types: comparison and portfolio.
    """
    from app.services.agent_service import comparison_agent, portfolio_agent
    
    service = portfolio_agent if request.agent_type == "portfolio" else comparison_agent
    result = await service.chat_with_agent(request.message, request.history)
    return result
