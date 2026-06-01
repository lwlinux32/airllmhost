"""
Example Python client for AirLLM API Server
"""

import requests
import json

BASE_URL = "http://localhost:1410"


def health_check():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_model_info():
    """Get model information"""
    response = requests.get(f"{BASE_URL}/info")
    return response.json()


def generate(prompt, max_new_tokens=100, temperature=0.7, top_p=0.9):
    """
    Generate text from a prompt
    
    Args:
        prompt: The input prompt
        max_new_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        top_p: Nucleus sampling parameter
    """
    response = requests.post(
        f"{BASE_URL}/generate",
        json={
            "prompt": prompt,
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "use_cache": True
        }
    )
    return response.json()


def chat(message, max_new_tokens=100, temperature=0.7):
    """
    Single turn chat (no history)
    
    Args:
        message: User message
        max_new_tokens: Maximum tokens to generate
        temperature: Sampling temperature
    """
    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "message": message,
            "max_new_tokens": max_new_tokens,
            "temperature": temperature
        }
    )
    return response.json()


def chat_with_session(session_id, message, max_new_tokens=100, temperature=0.7, reset=False):
    """
    Multi-turn chat with session history
    
    Args:
        session_id: Unique session identifier
        message: User message
        max_new_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        reset: Whether to reset the session history
    """
    response = requests.post(
        f"{BASE_URL}/chat/session",
        json={
            "session_id": session_id,
            "message": message,
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "reset": reset
        }
    )
    return response.json()


def get_session_history(session_id):
    """Get the conversation history for a session"""
    response = requests.get(f"{BASE_URL}/session/{session_id}")
    return response.json()


def clear_session(session_id):
    """Clear the conversation history for a session"""
    response = requests.delete(f"{BASE_URL}/session/{session_id}")
    return response.json()


def interactive_chat():
    """Interactive single-turn chat"""
    print("=" * 60)
    print("AirLLM Single-Turn Chat (Type 'exit' to quit)")
    print("=" * 60)
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        print("Waiting for response...")
        result = chat(user_input, max_new_tokens=150)
        
        if result.get('success'):
            print(f"Model: {result['assistant_response']}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")


def interactive_session_chat():
    """Interactive multi-turn chat with history"""
    print("=" * 60)
    print("AirLLM Multi-Turn Chat with History (Type 'exit' to quit)")
    print("=" * 60)
    
    session_id = input("\nEnter session ID (or press Enter for 'default'): ").strip() or "default"
    print(f"Using session: {session_id}\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Goodbye!")
            break
        
        if user_input.lower() == 'history':
            result = get_session_history(session_id)
            if result.get('error'):
                print(f"No history found")
            else:
                print(f"\n--- Conversation History ({result['message_count']} messages) ---")
                for i, line in enumerate(result['history'], 1):
                    print(f"{i}. {line}")
                print("---\n")
            continue
        
        if user_input.lower() == 'reset':
            result = clear_session(session_id)
            if result.get('success'):
                print("Session cleared!\n")
            continue
        
        if not user_input:
            continue
        
        print("Waiting for response...")
        result = chat_with_session(session_id, user_input, max_new_tokens=150)
        
        if result.get('success'):
            print(f"Model: {result['assistant_response']}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    import sys
    
    print("Checking server connection...")
    health = health_check()
    
    if 'error' in health:
        print(f"Error: Cannot connect to server. Make sure api_server.py is running!")
        print(f"Details: {health['error']}")
        sys.exit(1)
    
    print(f"✓ Server is running")
    
    # Get model info
    info = get_model_info()
    print(f"✓ Model: {info.get('model_name', 'Unknown')}")
    print(f"✓ Status: {info.get('status', 'Unknown')}\n")
    
    # Choose mode
    print("Select mode:")
    print("1. Single-turn chat (no history)")
    print("2. Multi-turn chat with history")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        interactive_chat()
    elif choice == "2":
        interactive_session_chat()
    else:
        print("Invalid choice!")
