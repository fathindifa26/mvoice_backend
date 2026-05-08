import asyncio
import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.agent_service import portfolio_agent
from app.services.analytics_service import analytics_service

async def execute_tool(name, args):
    print(f"\n[AI Calling Tool: {name} with args: {args}]")
    
    if name == "get_portfolio_insights":
        # Map tool to analytics service
        return analytics_service.get_ai_portfolio_context(
            aggregation_metric=args.get("metric", "views"),
            brand=args.get("brand"),
            business_unit=args.get("business_unit")
        )
    
    elif name == "get_creative_deep_dive":
        # For now, we use the same context but filter by category in the description if needed
        # Or we can just return the full context and let AI filter
        context = analytics_service.get_ai_portfolio_context(
            aggregation_metric=args.get("metric", "views"),
            brand=args.get("brand")
        )
        
        category = args.get("category")
        if category != "All":
            # Filter the creative_distributions to only include the requested category
            dists = context.get("creative_distributions", {})
            filtered_dists = {k: v for k, v in dists.items() if k.startswith(category)}
            context["creative_distributions"] = filtered_dists
            
        return context

    return {"error": "Tool not found"}

async def terminal_chat():
    print("=== MVoice Portfolio AI Agent Test Console ===")
    print("Type 'exit' to quit.\n")
    
    history = []
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
            
        # First turn: Get tool calls or direct answer
        result = await portfolio_agent.chat_with_agent(user_input, history)
        
        if result.get("tool_calls"):
            # Execute all tool calls
            tool_results_messages = []
            
            # Add the assistant's tool call message to history
            # Note: In a real API, we need to match the exact format OpenRouter/OpenAI expects
            # For this test, we'll simulate the multi-turn
            
            for tc in result["tool_calls"]:
                tool_output = await execute_tool(tc["name"], tc["args"])
                
                # Create a message representing the tool output
                # (Simulating the second pass to LLM)
                tool_results_messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "name": tc["name"],
                    "content": str(tool_output)
                })
            
            # Second turn: Send tool results back to LLM for final answer
            # We need to include the original assistant message with tool_calls too
            llm_messages = [
                {"role": "system", "content": "You are a Portfolio Intelligence Agent..."}, # System prompt
                *history,
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": result.get("answer"), "tool_calls": [
                    {"id": tc["id"], "type": "function", "function": {"name": tc["name"], "arguments": str(tc["args"])}} 
                    for tc in result["tool_calls"]
                ]},
                *tool_results_messages
            ]
            
            # This is a bit simplified for the test script
            # In production, we'd handle the full message chain
            print("\nAI is thinking with data...")
            final_result = await portfolio_agent._call_llm(llm_messages, portfolio_agent.get_tools_definition())
            print(f"\nAI: {final_result['answer']}")
            
            # Update history
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": final_result["answer"]})
            
        else:
            print(f"\nAI: {result['answer']}")
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": result["answer"]})

if __name__ == "__main__":
    asyncio.run(terminal_chat())
