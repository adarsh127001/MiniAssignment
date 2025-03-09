from typing import Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from .base_agent import BaseAgent
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import Config

class SQLAgent(BaseAgent):
    def __init__(self, llm, logger):
        self.llm = llm
        self.logger = logger
        self.engine = create_engine(Config.PG_CONNECTION)
        self.Session = sessionmaker(bind=self.engine)
        
        self.prompt = PromptTemplate.from_template(
            """You are a SQL expert that helps business users query the HashCart database.
            Convert their natural language questions into a single, clean SQL query.
            Return ONLY the SQL query without any explanations, markdown formatting, or additional text.
            
            Database Schema:
            - users (id PK, name VARCHAR(100), email VARCHAR(100) UNIQUE, created_at TIMESTAMP)
            - products (id PK, name VARCHAR(100), email VARCHAR(100), created_at TIMESTAMP)
            - orders (id PK, order_date TIMESTAMP, total_amount DECIMAL(10,2), user_id FK -> users.id CASCADE)
            
            Question: {question}
            """
        )
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        messages = state["messages"]
        last_message = messages[-1]
        
        if not isinstance(last_message, HumanMessage):
            return {"next": "chatbot"}
        
        try:
            # Special handling for schema/table listing queries
            query_lower = last_message.content.lower()
            if any(word in query_lower for word in ["schema", "tables", "list tables"]):
                sql_query = "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'"
            else:
                # Normal query processing
                sql_response = self.llm.invoke(self.prompt.format(question=last_message.content))
                sql_query = sql_response.content.strip()
                if "```" in sql_query:
                    sql_query = sql_query.split("```")[1].strip()
                    if sql_query.startswith("sql"):
                        sql_query = sql_query[3:].strip()
                sql_query = sql_query.rstrip(';')
            
            self.logger.log_agent_decision(
                "SQLAgent",
                last_message.content,
                f"Generated query: {sql_query}"
            )
            
            with self.Session() as session:
                result = session.execute(text(sql_query))
                session.commit()
                if result.returns_rows:
                    columns = result.keys()
                    rows = result.fetchall()
                    formatted_results = [dict(zip(columns, row)) for row in rows]
                    response = f"Query results:\n{formatted_results}"
                else:
                    response = "The database has been updated successfully!"
                
        except Exception as e:
            self.logger.log_error(
                "SQLAgent",
                e,
                {"query": last_message.content}
            )
            response = f"Database error: {str(e)}"
        
        return {
            "messages": [AIMessage(content=response)],
            "next": "chatbot"
        } 