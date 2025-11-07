"""
Example script demonstrating how to use the REST API Agent.

Make sure to:
1. Set your OpenAI API key: export OPENAI_API_KEY="your-key"
2. Start the FastAPI server: uvicorn app.main:app --reload
3. Run this script: python example_agent_usage.py
"""

from agent.agent import RESTAPIAgent


def main():
    # Initialize the agent
    agent = RESTAPIAgent(
        api_base_url="http://localhost:8000",
        api_key="secret123",  # Optional, needed for secure endpoints
        model_name="gpt-4o-mini"
    )
    
    # Example queries
    queries = [
        "Check if the API is healthy",
        "Create a new item called 'Laptop' with price 999.99 and tags 'electronics' and 'tech'",
        "List all items",
        "Show me item with ID 1",
        "Update item 1 to have price 899.99",
        "Delete item 1",
        "What's the secret?",
    ]
    
    print("=== AI Agent Demo ===\n")
    for query in queries:
        print(f"User: {query}")
        result = agent.run(query)
        print(f"Agent: {result['output']}\n")
        print("-" * 50)
    
    # Interactive mode
    print("\n=== Interactive Mode ===")
    print("Type 'quit' to exit, 'clear' to clear memory\n")
    
    while True:
        query = input("You: ").strip()
        if query.lower() == 'quit':
            break
        if query.lower() == 'clear':
            agent.clear_memory()
            print("Memory cleared!\n")
            continue
        if not query:
            continue
        
        result = agent.run(query)
        print(f"Agent: {result['output']}\n")


if __name__ == "__main__":
    main()

