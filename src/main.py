from typing import Dict, List
from langchain_groq import ChatGroq
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.agents import initialize_agent
from langchain_core.tools import Tool
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

from config import Config
from agents.rag_agent import RAGAgent
from agents.sql_agent import SQLAgent
from agents.search_agent import SearchAgent
from utils.logger import AgentLogger
from agents.router_agent import RouterAgent

def create_tools(llm, logger):
    # Create our specialized tools
    sql_agent = SQLAgent(llm, logger)
    rag_agent = RAGAgent(llm, logger)
    search_agent = SearchAgent(llm, logger)
    
    tools = [
        Tool(
            name="SQL_Database",
            func=sql_agent.process,
            description="Use this tool for database queries, listing tables, or getting data from the HashCart database"
        ),
        Tool(
            name="Policy_Documents",
            func=rag_agent.process,
            description="Use this tool for questions about company policies, leave rules, or increments"
        ),
        Tool(
            name="Internet_Search",
            func=search_agent.process,
            description="Use this tool for general information or current events"
        )
    ]
    return tools

def create_agent_graph():
    graph = StateGraph(State)
    
    # Initialize components
    logger = AgentLogger()
    llm = ChatGroq(
        model=Config.LLM_MODEL,
        temperature=Config.LLM_TEMPERATURE,
        max_tokens=Config.LLM_MAX_TOKENS,
        timeout=Config.LLM_TIMEOUT,
        max_retries=Config.LLM_MAX_RETRIES,
        api_key=Config.GROQ_API_KEY,
    )
    
    # Add memory to state
    memory = ConversationBufferWindowMemory(
        memory_key='chat_history',
        k=3,
        return_messages=True
    )
    
    # Initialize agents
    router_agent = RouterAgent()
    rag_agent = RAGAgent(llm, logger)
    sql_agent = SQLAgent(llm, logger)
    search_agent = SearchAgent(llm, logger)
    
    # Add nodes
    graph.add_node("router", router_agent.process)
    graph.add_node("rag", rag_agent.process)
    graph.add_node("sql", sql_agent.process)
    graph.add_node("search", search_agent.process)
    
    # Add edges
    graph.add_edge("router", "rag")
    graph.add_edge("router", "sql")
    graph.add_edge("router", "search")
    
    # Set entry point
    graph.set_entry_point("router")
    
    return graph.compile()

def main():
    logger = AgentLogger()
    llm = ChatGroq(
        model=Config.LLM_MODEL,
        temperature=Config.LLM_TEMPERATURE,
        max_tokens=Config.LLM_MAX_TOKENS,
        timeout=Config.LLM_TIMEOUT,
        max_retries=Config.LLM_MAX_RETRIES,
        api_key=Config.GROQ_API_KEY,
    )
    
    # Create memory
    memory = ConversationBufferWindowMemory(
        memory_key='chat_history',
        k=3,
        return_messages=True
    )
    
    # Create tools
    tools = create_tools(llm, logger)
    
    # Initialize the agent
    agent = initialize_agent(
        agent='chat-conversational-react-description',
        tools=tools,
        llm=llm,
        verbose=True,
        max_iterations=3,
        early_stopping_method='generate',
        memory=memory
    )
    
    while True:
        try:
            user_input = input("\nEnter your question (or 'exit' to quit): ")
            if user_input.lower() == 'exit':
                break
            
            response = agent(user_input)
            print(f"Response: {response['output']}")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Please try another question.")

if __name__ == "__main__":
    main() 