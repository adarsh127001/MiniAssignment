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
    
    def process(self, query: str) -> Dict[str, Any]:
        try:
            query_lower = query.lower()
            if any(word in query_lower for word in ["schema", "tables", "list tables"]):
                sql_query = "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'"
            else:
                sql_response = self.llm.invoke(self.prompt.format(question=query))
                sql_query = sql_response.content.replace('\_', '_').strip().rstrip(';')
            
            self.logger.log_agent_decision(
                "SQLAgent",
                query,
                f"Generated query: {sql_query}"
            )
            
            with self.Session() as session:
                result = session.execute(text(sql_query))
                session.commit()
                if result.returns_rows:
                    columns = result.keys()
                    rows = result.fetchall()
                    formatted_results = [dict(zip(columns, row)) for row in rows]
                    # Return in format expected by LangChain agent
                    return {"tool_output": str(formatted_results)}
                return {"tool_output": "Database updated successfully!"}
            
        except Exception as e:
            self.logger.log_error("SQLAgent", e, {"query": query})
            return {"tool_output": f"Database error: {str(e)}"} 