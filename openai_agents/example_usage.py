import os
from dotenv import load_dotenv
from tool_calling_agent.simple_agent import Agent
from realtime_agent.realtime_agent import RT_Agent
from common.tools import tool_map

# Load the .env from the project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))



# Define the model to use
MODEL_NAME = "gpt-4o-mini"

def simple_agent_example():
    """Example usage of the Simple Tool-Calling Agent."""
    print("\n🔹 Running Simple Agent Example...\n")

    # Initialize agent with available tools
    tools = list(tool_map.keys())
    sys_msg = f"You are a helpful Agent equipped with these tools: {str(tools)}"

    agent = Agent(MODEL_NAME, tools, sys_msg, verbose=True)

    # Example 1: Basic AI response
    print("\n📝 Example 1: Simple Interaction")
    response = agent.invoke("Hello! How are you?")
    print(f"\nAgent: {response}")

    # Example 2: Asking about the weather (Assumes tool is available)
    print("\n🌦 Example 2: Tool-Calling for Weather")
    response = agent.invoke("What's the weather in Paris?")
    print(f"\nAgent: {response}")

    # Example 3: Streaming response
    print("\n🔄 Example 3: Streaming Response")
    agent.stream("Tell me an interesting fact about space.")

    # Example 4: Interactive conversation mode
    print("\n💬 Example 4: Interactive Chat Mode (Type 'exit' to quit)")
    agent.convo(stream=True)


def realtime_agent_example():
    """Example usage of the Realtime Agent."""
    print("\n🔹 Running Realtime Agent Example...\n")

    # Initialize the real-time agent
    tools = list(tool_map.keys())
    sys_msg = "You are a helpful real-time AI assistant."
    
    agent = RT_Agent(sys_msg=sys_msg, tools=tools, verbose=True)

    # Example 1: Invoke a real-time response
    print("\n🗣 Example 1: Realtime AI Response")
    user_message = "Tell me a fun fact about technology."
    agent.invoke(user_message)

    # Example 2: Start real-time conversation
    print("\n🎙 Example 2: Realtime Interactive Mode (Type 'exit' to quit)")
    agent.convo()


if __name__ == "__main__":
    print("Choose an agent to test:")
    print("1. Simple Agent (Tool-Calling)")
    print("2. Realtime Agent (WebSocket)")

    choice = input("Enter 1 or 2: ")

    if choice == "1":
        simple_agent_example()
    elif choice == "2":
        realtime_agent_example()
    else:
        print("Invalid choice. Please restart and enter 1 or 2.")
