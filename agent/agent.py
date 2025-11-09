from typing import List, Dict, Any, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain_core.messages import HumanMessage, AIMessage

from .tools import create_api_tools
from .memory import ConversationMemory
from .callbacks import ConsoleCallbackHandler


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

        # Configure callbacks for live reasoning logs
        self.callback_handler = ConsoleCallbackHandler()

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
            handle_parsing_errors=True,
            callbacks=[self.callback_handler]
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
    
    @staticmethod
    def _serialize_step_value(value: Any) -> Any:
        """Convert step values to JSON-serialisable primitives when possible."""
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if isinstance(value, dict):
            return {
                key: RESTAPIAgent._serialize_step_value(sub_value)
                for key, sub_value in value.items()
            }
        if isinstance(value, (list, tuple)):
            return [RESTAPIAgent._serialize_step_value(item) for item in value]
        return str(value)

    @staticmethod
    def _normalise_step(action: Any, observation: Any) -> Dict[str, Any]:
        """Normalise a LangChain intermediate step into a uniform dictionary."""
        thought: Optional[str] = None

        if getattr(action, "log", None):
            thought = str(action.log).strip()
        elif getattr(action, "message_log", None):
            message_contents: List[str] = []
            for message in action.message_log:
                content = getattr(message, "content", None)
                if isinstance(content, list):
                    # Some message content can be a list of dict chunks. Render as string.
                    message_contents.append(str(content))
                elif content:
                    message_contents.append(str(content))
            if message_contents:
                thought = "\n".join(message_contents)
        elif isinstance(action, dict) and action.get("thought"):
            thought = str(action["thought"])

        action_name: Optional[str] = None
        if getattr(action, "tool", None):
            action_name = str(action.tool)
        elif isinstance(action, dict) and action.get("action"):
            action_name = str(action["action"])

        tool_input: Any = None
        if getattr(action, "tool_input", None) is not None:
            tool_input = action.tool_input
        elif isinstance(action, dict) and action.get("tool_input") is not None:
            tool_input = action["tool_input"]
        elif isinstance(action, dict) and action.get("input") is not None:
            tool_input = action["input"]

        return {
            "thought": thought,
            "action": action_name,
            "input": RESTAPIAgent._serialize_step_value(tool_input),
            "observation": RESTAPIAgent._serialize_step_value(observation),
        }

    def run(self, query: str) -> Dict[str, Any]:
        """
        Execute a user query using the agent.

        Args:
            query: User's natural language request

        Returns:
            Dictionary containing the final output and structured reasoning steps.
        """
        # Get conversation history
        chat_history = self.memory.get_history()

        # Run agent
        result = self.executor.invoke({
            "input": query,
            "chat_history": chat_history
        })

        raw_intermediate_steps = result.get("intermediate_steps", [])
        structured_steps: List[Dict[str, Any]] = []

        for step in raw_intermediate_steps:
            if isinstance(step, (list, tuple)) and len(step) == 2:
                action, observation = step
            else:
                action, observation = step, None
            structured_steps.append(self._normalise_step(action, observation))

        # Save to memory
        self.memory.add_message(HumanMessage(content=query))
        self.memory.add_message(AIMessage(content=result["output"]))

        return {
            **{k: v for k, v in result.items() if k != "intermediate_steps"},
            "reasoning": structured_steps,
        }
    
    def clear_memory(self):
        """Clear conversation history."""
        self.memory.clear()

