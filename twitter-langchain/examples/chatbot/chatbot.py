import sys
import time
import os
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

# Import CDP Agentkit Twitter Langchain Extension.
from twitter_langchain import (
    TwitterApiWrapper,
    TwitterToolkit,
)

# Configure a file to persist the agent's CDP MPC Wallet Data.
wallet_data_file = "wallet_data.txt"

# Load .env file at the beginning
load_dotenv()


def initialize_agent():
    """Initialize the agent with Twitter API."""
    # Get Twitter API credentials from environment variables
    values = {
        "twitter_api_key": os.getenv("TWITTER_API_KEY"),
        "twitter_api_secret": os.getenv("TWITTER_API_SECRET"),
        "twitter_access_token": os.getenv("TWITTER_ACCESS_TOKEN"),
        "twitter_access_token_secret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
        "bearer_token": os.getenv("TWITTER_BEARER_TOKEN")
    }

    # Print keys for debugging (remember to remove later)
    print("Checking API credentials:")
    for key, value in values.items():
        print(f"{key}: {'[SET]' if value else '[MISSING]'}")

    # Verify all required keys exist
    missing_keys = [k for k, v in values.items() if not v]
    if missing_keys:
        raise ValueError(f"Missing required Twitter API keys: {', '.join(missing_keys)}")

    # Initialize Twitter API wrapper
    wrapper = TwitterApiWrapper(**values)

    # Test connection
    try:
        test = wrapper.client.get_me()
        print("API Connection Test:", "Success" if test else "Failed")
    except Exception as e:
        print("API Connection Error:", str(e))

    def process_with_twitter(input_text):
        try:
            if "my twitter account" in input_text.lower():
                # Get user information
                user = wrapper.client.get_me()
                return {
                    "messages": [{
                        "content": f"Your Twitter account info:\n{user}",
                        "role": "assistant"
                    }]
                }
            elif input_text.lower().startswith("tweet "):
                # Send tweet
                tweet_text = input_text[6:]  # Remove "tweet " prefix
                result = wrapper.client.create_tweet(text=tweet_text)
                return {
                    "messages": [{
                        "content": f"Tweet posted successfully!\n{result}",
                        "role": "assistant"
                    }]
                }
            else:
                return {
                    "messages": [{
                        "content": "Available commands:\n"
                                 "- 'what's my twitter account': Show your account info\n"
                                 "- 'tweet [message]': Post a new tweet\n"
                                 "What would you like to do?",
                        "role": "assistant"
                    }]
                }
        except Exception as e:
            return {
                "messages": [{
                    "content": f"Error: {str(e)}",
                    "role": "assistant"
                }]
            }

    return process_with_twitter, {"thread_id": "Twitter Bot Example"}


# Autonomous Mode
def run_autonomous_mode(agent_executor, config, interval=10):
    """Run Twitter bot autonomously."""
    print("Starting autonomous mode...")
    while True:
        try:
            thought = "Checking Twitter timeline..."
            response = agent_executor(thought)
            print(response["messages"][0]["content"])
            print("-------------------")
            time.sleep(interval)

        except KeyboardInterrupt:
            print("Goodbye!")
            sys.exit(0)


# Chat Mode
def run_chat_mode(agent_executor, config):
    """Run Twitter bot interactively."""
    print("Starting chat mode... Type 'exit' to end.")
    while True:
        try:
            user_input = input("\nPrompt: ")
            if user_input.lower() == "exit":
                break

            # Process input using Twitter API
            response = agent_executor(user_input)
            print(response["messages"][0]["content"])
            print("-------------------")

        except KeyboardInterrupt:
            print("Goodbye!")
            sys.exit(0)


# Mode Selection
def choose_mode():
    """Choose whether to run in autonomous or chat mode based on user input."""
    while True:
        print("\nAvailable modes:")
        print("1. chat    - Interactive chat mode")
        print("2. auto    - Autonomous action mode")

        choice = input("\nChoose a mode (enter number or name): ").lower().strip()
        if choice in ["1", "chat"]:
            return "chat"
        elif choice in ["2", "auto"]:
            return "auto"
        print("Invalid choice. Please try again.")


def main():
    """Start the chatbot agent."""
    agent_executor, config = initialize_agent()

    mode = choose_mode()
    if mode == "chat":
        run_chat_mode(agent_executor=agent_executor, config=config)
    elif mode == "auto":
        run_autonomous_mode(agent_executor=agent_executor, config=config)


if __name__ == "__main__":
    print("Starting Agent...")
    main()
