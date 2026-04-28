import asyncio
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path to import app modules
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.agent_service import agent_service

async def main():
    print("\n=== MVOICE INTELLIGENCE AI AGENT TEST ===")
    print("Type 'exit' to quit. Try commands like:")
    print("- 'Bandingkan Wardah dengan Sunsilk'")
    print("- 'Ganti ke metrik views'")
    print("- 'Filter brand A hanya untuk talent Nano'")
    print("- 'Tampilkan grafik topik dan hook type'")
    print("------------------------------------------\n")

    history = []
    
    while True:
        user_input = input("User: ")
        if user_input.lower() in ['exit', 'quit']:
            break
        
        print("\nThinking...")
        try:
            result = await agent_service.chat_with_agent(user_input, history)
            
            # Print Tool Calls if any
            if result["tool_calls"]:
                print("\n[AI ACTIONS]")
                for tc in result["tool_calls"]:
                    print(f"-> Calling Tool: {tc['name']}")
                    print(f"   Arguments: {json.dumps(tc['args'], indent=2)}")
            
            # Print AI Answer
            if result["answer"]:
                print(f"\nAI: {result['answer']}")
            else:
                # If AI only called tools without a text answer, provide a generic one
                print(f"\nAI: Oke, saya telah memperbarui dashboard sesuai permintaan Anda.")
            
            # Add to history
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": result["answer"] or "Dashboard updated."})
            
            print("-" * 40 + "\n")
            
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
