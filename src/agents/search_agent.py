from typing import Dict, Any, List
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import AIMessage, HumanMessage

from config import Config
from .base_agent import BaseAgent
from langchain_community.tools.tavily_search import TavilySearchResults

class SearchAgent(BaseAgent):
    def __init__(self, llm, logger):
        self.llm = llm
        self.logger = logger
        self.search_tool = TavilySearchResults(
            max_results=3,
            api_key=Config.TAVILY_API_KEY
        )
        
        self.prompt = PromptTemplate.from_template(
            """You are a helpful AI assistant that provides information based on real-time web search results.
            Analyze the following search results and provide a comprehensive answer.
            If the search results don't contain relevant information, say so.
            
            Previous conversation context:
            {chat_history}
            
            Search Results:
            {search_results}
            
            Current question: {question}
            
            Provide a clear, concise answer based on the search results.
            """
        )
    
    def _format_chat_history(self, messages: List[Dict]) -> str:
        formatted = []
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted.append(f"{role}: {msg['content']}")
        return "\n".join(formatted[-4:])
    
    def _format_search_results(self, results: List[Dict]) -> str:
        formatted_results = []
        for result in results:
            formatted_results.append(f"Title: {result.get('title', 'No title')}")
            formatted_results.append(f"Content: {result.get('content', 'No content')}")
            formatted_results.append(f"URL: {result.get('url', 'No URL')}")
            formatted_results.append("")
        return "\n".join(formatted_results)
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            messages = state["messages"]
            last_message = messages[-1]
            
            if not isinstance(last_message, HumanMessage):
                return {"next": "chatbot"}
            
            query = last_message.content
            search_results = self.search_tool.invoke(query)
            
            self.logger.log_agent_decision(
                "SearchAgent",
                query,
                f"Found {len(search_results)} search results"
            )
            
            formatted_results = self._format_search_results(search_results)
            
            prompt = self.prompt.format(
                search_results=formatted_results,
                question=query,
                chat_history=self._format_chat_history(state.get("memory", []))
            )
            
            response = self.llm.invoke(prompt)
            
            return {
                "messages": [AIMessage(content=response.content)],
                "next": "chatbot"
            }
            
        except Exception as e:
            self.logger.log_error(
                "SearchAgent",
                e,
                {"query": query if 'query' in locals() else None}
            )
            return {
                "messages": [AIMessage(content="I encountered an error while searching for information.")],
                "next": "chatbot"
            } 