from typing import Dict, Any
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph
from typing_extensions import TypedDict
from .base_agent import BaseAgent

class RouterAgent(BaseAgent):
    def analyze_query(self, query: str) -> str:
        query_lower = query.lower()
        
        # SQL related keywords - check first
        if any(keyword in query_lower for keyword in [
            "database", "sql", "table", "record", "order", "user", "product",
            "sales", "customer", "purchase", "transaction", "show me", "list",
            "how many", "count", "total", "schema"
        ]):
            return "sql"
        
        # RAG related keywords - check second
        elif any(keyword in query_lower for keyword in [
            "policy", "handbook", "leave", "increment", "rules"
        ]):
            return "rag"
        
        # Search only if no other agent matches
        else:
            return "search"
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        messages = state["messages"]
        last_message = messages[-1]
        
        if not isinstance(last_message, BaseMessage):
            return {"next": "chatbot"}
        
        agent_type = self.analyze_query(last_message.content)
        # Return directly to the appropriate agent
        return {"next": agent_type}