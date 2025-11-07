from typing import List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


class ConversationMemory:
    """Manages conversation history for the agent."""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.history: List[BaseMessage] = []
    
    def add_message(self, message: BaseMessage):
        """Add a message to history."""
        self.history.append(message)
        # Keep only recent history
        if len(self.history) > self.max_history * 2:  # *2 because pairs
            self.history = self.history[-self.max_history * 2:]
    
    def get_history(self) -> List[BaseMessage]:
        """Get conversation history."""
        return self.history
    
    def clear(self):
        """Clear conversation history."""
        self.history = []

