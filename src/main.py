from typing import Dict
from langchain_groq import ChatGroq
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.agents import initialize_agent
from langchain_core.tools import Tool

from config import Config
from agents.rag_agent import RAGAgent
from agents.sql_agent import SQLAgent
from agents.search_agent import SearchAgent
from utils.logger import AgentLogger

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
    
    # Initialize agents
    sql_agent = SQLAgent(llm, logger)
    rag_agent = RAGAgent(llm, logger)
    search_agent = SearchAgent(llm, logger)
    
    tools = [
        Tool(
            name="SQL_Database",
            func=lambda x: sql_agent.process(x)["tool_output"],
            description="Use for database queries (e.g., list tables, update records, query data)"
        ),
        Tool(
            name="Policy_Documents",
            func=lambda x: rag_agent.process(x)["tool_output"],
            description="Use for company policies, leave rules, or increments"
        ),
        Tool(
            name="Internet_Search",
            func=search_agent.process,
            description="Use for general information or current events"
        )
    ]
    
    memory = ConversationBufferWindowMemory(
        memory_key='chat_history',
        k=3,
        return_messages=True
    )
    
    agent = initialize_agent(
        agent='chat-conversational-react-description',
        tools=tools,
        llm=llm,
        verbose=True,
        max_iterations=3,
        early_stopping_method='generate',
        memory=memory,
        handle_parsing_errors=True
    )
    
    while True:
        try:
            user_input = input("\nEnter your question (or 'exit' to quit): ")
            if user_input.lower() == 'exit':
                break
            
            response = agent.invoke({"input": user_input})
            print(f"Response: {response['output']}")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Please try another question.")

if __name__ == "__main__":
    main() 