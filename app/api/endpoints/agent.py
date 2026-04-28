from fastapi import APIRouter, Depends, Body
from typing import List, Dict, Optional
from pydantic import BaseModel
from app.services.agent_service import agent_service

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    history: List[Dict] = []

@router.post("/chat")
async def chat_with_agent(request: ChatRequest):
    """
    Endpoint for the AI Agent chat.
    Returns both the text answer and any tool calls to be executed on the frontend.
    """
    result = await agent_service.chat_with_agent(request.message, request.history)
    return result
