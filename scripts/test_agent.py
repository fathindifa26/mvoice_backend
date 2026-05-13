import asyncio
import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.agent_service import portfolio_agent
from app.services.analytics_service import analytics_service
from app.services.base import base_data_manager

async def execute_tool(name, args):
    print(f"\n[AI Calling Tool: {name} with args: {args}]")
    
    # Simple case-insensitive matching helper
    def get_exact_name(df, column, value):
        if not value or value == "All": return value
        unique_names = df[column].dropna().unique()
        for name in unique_names:
            if str(name).lower() == str(value).lower():
                return name
        return value

    df = base_data_manager.get_df()
    brand = get_exact_name(df, "brand", args.get("brand"))
    bu = get_exact_name(df, "business_unit", args.get("business_unit"))

    if name == "get_portfolio_insights":
        data = analytics_service.get_portfolio_summary(
            aggregation_metric=args.get("metric", "views"),
            brand=brand,
            business_unit=bu
        )
        if "summaryText" in data:
            del data["summaryText"]
        return data
    
    elif name == "get_creative_deep_dive":
        return analytics_service.get_ai_portfolio_context(
            aggregation_metric=args.get("metric", "views"),
            brand=brand,
            business_unit=bu
        )

    return {"error": "Tool not found"}

async def terminal_chat():
    print("=== MVoice Portfolio AI Agent Test Console ===")
    print("Type 'exit' to quit.\n")
    
    history = []
    # Get system prompt from the actual service
    system_prompt = (
        "You are a Portfolio Intelligence Agent. You help users explore creative performance across their entire portfolio. "
        "WORKFLOW: \n"
        "1. If the user's request requires data, use the available tools to fetch it.\n"
        "2. Once you have the tool output in the message history, STOP calling tools.\n"
        "3. Analyze the provided data and synthesize a comprehensive, professional answer for the user.\n"
        "4. If comparing brands, fetch data for both before summarizing.\n"
        "CRITICAL: Do NOT repeat a tool call if the exact same parameters were already used in the current conversation history. "
        "Always prioritize providing a strategic answer over fetching more data if you already have relevant insights."
    )
    
    while True:
        import json
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
            
        messages = [
            {"role": "system", "content": system_prompt},
            *history,
            {"role": "user", "content": user_input}
        ]

        loop_count = 0
        while loop_count < 5:
            result = await portfolio_agent._call_llm(messages, portfolio_agent.get_tools_definition())
            
            if result.get("tool_calls"):
                # Add assistant message with tool calls to history
                assistant_msg = {
                    "role": "assistant",
                    "content": result.get("answer"),
                    "tool_calls": [
                        {
                            "id": tc["id"],
                            "type": "function",
                            "function": {"name": tc["name"], "arguments": json.dumps(tc["args"])}
                        } for tc in result["tool_calls"]
                    ]
                }
                messages.append(assistant_msg)
                
                # Execute tools
                for tc in result["tool_calls"]:
                    tool_output = await execute_tool(tc["name"], tc["args"])
                    
                    # PRINT DATA FOR USER
                    print(f"[Tool Result Data]: {json.dumps(tool_output, indent=2, default=str)[:1000]}...") # Truncate if too long
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "name": tc["name"],
                        "content": json.dumps(tool_output, default=str)
                    })
                
                print("\nAI is thinking with data...")
                loop_count += 1
                continue
            else:
                answer = result.get("answer")
                if answer:
                    print(f"\nAI: {answer}")
                else:
                    print("\nAI: [No text response, possibly waiting for more context or tool call error]")
                
                # Update history for next turn
                history.append({"role": "user", "content": user_input})
                if answer:
                    history.append({"role": "assistant", "content": answer})
                break

if __name__ == "__main__":
    asyncio.run(terminal_chat())
