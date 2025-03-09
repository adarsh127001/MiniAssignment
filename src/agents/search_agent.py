from typing import Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_community.tools.tavily_search import TavilySearchResults
from config import Config

class SearchAgent:
    def __init__(self, llm, logger):
        self.llm = llm
        self.logger = logger
        self.search_tool = TavilySearchResults(
            max_results=3,
            api_key=Config.TAVILY_API_KEY
        )
        
        self.prompt = PromptTemplate.from_template(
            """You are a helpful AI assistant that provides information based on web search results.
            
            Search Results:
            {search_results}
            
            Question: {question}
            
            Provide a clear, concise answer based only on the search results provided.
            If the search results don't contain relevant information, say so.
            """
        )
    
    def _format_search_results(self, results: list) -> str:
        formatted = []
        for result in results:
            formatted.append(f"Title: {result.get('title', '')}")
            formatted.append(f"Content: {result.get('content', '')}")
            formatted.append(f"URL: {result.get('url', '')}\n")
        return "\n".join(formatted)
    
    def process(self, query: str) -> Dict[str, Any]:
        try:
            # Log the incoming query
            self.logger.log_agent_decision(
                "SearchAgent",
                query,
                "Initiating search"
            )
            
            # Perform search
            search_results = self.search_tool.invoke(query)
            
            # Format results
            formatted_results = self._format_search_results(search_results)
            
            # Generate response using LLM
            response = self.llm.invoke(
                self.prompt.format(
                    search_results=formatted_results,
                    question=query
                )
            )
            
            return {"tool_output": response.content}
            
        except Exception as e:
            self.logger.log_error(
                "SearchAgent",
                e,
                {"query": query}
            )
            return {"tool_output": "I encountered an error while searching for information."} 