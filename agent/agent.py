from typing import List, Dict, Any, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain_core.messages import HumanMessage, AIMessage

from .tools import create_api_tools
from .memory import ConversationMemory


class RESTAPIAgent:
    """
    AI Agent that can interact with REST APIs to perform operations.
    """
    
    def __init__(
        self,
        api_base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.0
    ):
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.memory = ConversationMemory()
        
        # Create tools for API interactions
        self.tools = create_api_tools(api_base_url, api_key)
        
        # Initialize LLM
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        
        # Create agent prompt
        self.prompt = self._create_prompt()
        
        # Create agent
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Create agent executor
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            return_intermediate_steps=True,
            handle_parsing_errors=True
        )
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Create the system prompt for the agent."""
        return ChatPromptTemplate.from_messages([
            ("system", """You are an AI assistant that helps users interact with REST APIs.
            
Your capabilities:
- Manage items: create, list, retrieve, update, and delete items
- Upload files to the server
- Check API health status
- Access secure endpoints (when API key is provided)

When a user asks you to do something:
1. Understand their intent
2. Choose the appropriate API endpoint(s)
3. Execute the API calls
4. Provide clear feedback about what was done

Always be helpful, clear, and informative. If an operation fails, explain what went wrong and suggest alternatives."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
    
    def run(self, query: str) -> Dict[str, Any]:
        """
        Execute a user query using the agent.
        
        Args:
            query: User's natural language request
            
        Returns:
            Dictionary with response and metadata
        """
        # Get conversation history
        chat_history = self.memory.get_history()
        
        # Run agent
        result = self.executor.invoke({
            "input": query,
            "chat_history": chat_history
        })
        
        # Save to memory
        self.memory.add_message(HumanMessage(content=query))
        self.memory.add_message(AIMessage(content=result["output"]))
        
        return result
    
    def clear_memory(self):
        """Clear conversation history."""
        self.memory.clear()

