# Swagger Demo with FastAPI

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

## Docs
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

## AI Agent

This project includes an AI agent that can interact with the REST APIs using natural language.

### Setup

1. Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

2. Make sure the FastAPI server is running (see Run section above)

### Usage

Run the example script:
```bash
python example_agent_usage.py
```

Or use the agent programmatically:
```python
from agent.agent import RESTAPIAgent

agent = RESTAPIAgent(
    api_base_url="http://localhost:8000",
    api_key="secret123",  # Optional, for secure endpoints
    model_name="gpt-4o-mini"
)

# Natural language queries
result = agent.run("Create a new item called 'Widget' priced at $19.99")
print(result['output'])

result = agent.run("List all items")
print(result['output'])

result = agent.run("Show me item with ID 1")
print(result['output'])
```

### Agent Capabilities

The AI agent can:
- ✅ Check API health status
- ✅ Create, list, retrieve, update, and delete items
- ✅ Upload files to the server
- ✅ Access secure endpoints (with API key)
- ✅ Maintain conversation context
- ✅ Understand natural language queries

### Architecture

- `agent/agent.py` - Main agent class with LLM integration
- `agent/tools.py` - API interaction tools
- `agent/memory.py` - Conversation history management

