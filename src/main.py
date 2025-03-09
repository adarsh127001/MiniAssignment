from typing import Dict
from langchain_groq import ChatGroq
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.agents import initialize_agent
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate

from config import Config
from agents.rag_agent import RAGAgent
from agents.sql_agent import SQLAgent
from agents.search_agent import SearchAgent
from utils.logger import AgentLogger

def main():
    logger = AgentLogger()
    llm = ChatGroq(
        model=Config.LLM_MODEL,
        temperature=0,
        api_key=Config.GROQ_API_KEY,
    )
    
    # Initialize tools with better descriptions
    tools = [
        Tool(
            name="Database_Query",
            func=SQLAgent(llm, logger).process,
            description="Use for database operations: querying tables, updating records, or getting data from HashCart database"
        ),
        Tool(
            name="Policy_Search",
            func=RAGAgent(llm, logger).process,
            description="Use for questions about company policies, employee handbook, leave rules, or increments"
        ),
        Tool(
            name="Internet_Search",
            func=SearchAgent(llm, logger).process,
            description="Use for real-time information from the internet about current events or general knowledge"
        )
    ]
    
    # Add memory with larger context window
    memory = ConversationBufferWindowMemory(
        memory_key='chat_history',
        k=5,
        return_messages=True
    )
    
    # Initialize agent with better parameters
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
    
    print("Agent initialized! Ask me anything about policies, database, or general information.")
    
    while True:
        try:
            query = input("\nQuestion (or 'exit' to quit): ")
            if query.lower() == 'exit':
                break
            
            response = agent.invoke({"input": query})
            print(f"\nResponse: {response['output']}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main() 