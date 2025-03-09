from typing import Annotated, Dict, List
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages

from config import Config
from agents.router_agent import RouterAgent
from agents.rag_agent import RAGAgent
from agents.sql_agent import SQLAgent
from agents.search_agent import SearchAgent
from utils.logger import AgentLogger

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    memory: list[Dict]

def create_llm():
    return ChatGroq(
        model=Config.LLM_MODEL,
        temperature=Config.LLM_TEMPERATURE,
        max_tokens=Config.LLM_MAX_TOKENS,
        timeout=Config.LLM_TIMEOUT,
        max_retries=Config.LLM_MAX_RETRIES,
        api_key=Config.GROQ_API_KEY,
    )

def create_agent_graph():
    graph = StateGraph(State)
    
    # Initialize components
    logger = AgentLogger()
    llm = create_llm()
    
    # Initialize agents
    router_agent = RouterAgent()
    rag_agent = RAGAgent(llm, logger)
    sql_agent = SQLAgent(llm, logger)
    search_agent = SearchAgent(llm, logger)
    
    def chatbot(state: State):
        if "memory" not in state:
            state["memory"] = []
        
        messages = state["messages"]
        last_message = messages[-1]
        
        if isinstance(last_message, HumanMessage):
            state["memory"].append({
                "role": "user",
                "content": last_message.content
            })
            
            response = llm.invoke(messages)
            
            state["memory"].append({
                "role": "assistant",
                "content": response.content
            })
            
            return {
                "messages": [AIMessage(content=response.content)],
                "memory": state["memory"]
            }
        return state
    
    # Add nodes
    graph.add_node("chatbot", chatbot)
    graph.add_node("router", router_agent.process)
    graph.add_node("rag", rag_agent.process)
    graph.add_node("sql", sql_agent.process)
    graph.add_node("search", search_agent.process)
    
    # Add edges with clear flow
    graph.add_edge("router", "chatbot")
    graph.add_edge("router", "search")
    graph.add_edge("router", "rag")
    graph.add_edge("router", "sql")
    graph.add_edge("search", "chatbot")
    graph.add_edge("rag", "chatbot")
    graph.add_edge("sql", "chatbot")
    
    # Set entry point
    graph.set_entry_point("router")
    
    return graph.compile()

def main():
    agent_graph = create_agent_graph()
    memory = []
    
    while True:
        try:
            user_input = input("\nEnter your question (or 'exit' to quit): ")
            if user_input.lower() == 'exit':
                break
                
            state = {
                "messages": [HumanMessage(content=user_input)],
                "memory": memory
            }
            
            # Set a higher recursion limit and add config
            result = agent_graph.invoke(state, {"recursion_limit": 50})
            
            if "messages" in result:
                for message in result["messages"]:
                    if isinstance(message, (HumanMessage, AIMessage)):
                        print(f"Response: {message.content}")
            if "memory" in result:
                memory = result["memory"]
                    
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Please try another question.")

if __name__ == "__main__":
    main() 