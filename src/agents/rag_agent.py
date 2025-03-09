from typing import Dict, Any, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredFileLoader
)
from .base_agent import BaseAgent
from config import Config
import os

class RAGAgent(BaseAgent):
    def __init__(self, llm, logger):
        self.llm = llm
        self.logger = logger
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )
        self.vector_store = PGVector(
            embeddings=self.embeddings,
            collection_name=Config.VECTOR_COLLECTION,
            connection=Config.PG_CONNECTION,
            use_jsonb=True
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=50
        )
        
        self.load_documents()
        
        self.prompt = PromptTemplate.from_template(
            """You are a helpful AI assistant that answers questions based on provided context.
            Use only the following context to answer the question. If you cannot find the answer
            in the context, say "I don't have enough information to answer that question."
            
            Previous conversation context:
            {chat_history}
            
            Relevant documents:
            {context}
            
            Current question: {question}
            """
        )
    
    def load_documents(self):
        try:
            data_dir = "data"
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            
            file_path = os.path.join(data_dir, "policies.txt")
            try:
                loader = TextLoader(file_path, encoding='utf-8')
                docs = loader.load()
                
                # Split into chunks
                chunks = self.text_splitter.split_documents(docs)
                
                # Add to vector store
                self.vector_store.add_documents(documents=chunks)
                
                self.logger.log_agent_decision(
                    "RAGAgent",
                    f"Loading document: {file_path}",
                    f"Successfully loaded {len(chunks)} chunks"
                )
                
            except Exception as e:
                self.logger.log_error(
                    "RAGAgent",
                    e,
                    {"file_path": file_path}
                )
                
        except Exception as e:
            self.logger.log_error("RAGAgent", e, {"action": "load_documents"})
    
    def _format_chat_history(self, messages: List[Dict]) -> str:
        formatted = []
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted.append(f"{role}: {msg['content']}")
        return "\n".join(formatted[-4:])
    
    def process(self, query: str) -> Dict[str, Any]:
        try:
            results = self.vector_store.similarity_search(query, k=3)
            
            context = "\n".join([
                f"Document {i+1}:\n{doc.page_content}\n"
                for i, doc in enumerate(results)
            ])
            
            prompt = self.prompt.format(
                context=context,
                question=query,
                chat_history=""
            )
            
            response = self.llm.invoke(prompt)
            return {"output": response.content}
            
        except Exception as e:
            self.logger.log_error("RAGAgent", e, {"query": query})
            return {"output": "I encountered an error while processing your request."} 