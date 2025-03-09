# Agent Query Routing System

## Setup Instructions

1. **Environment Setup**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   Create a `.env` file in the root directory with:
   ```
   GROQ_API_KEY=your_groq_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```

3. **Database Setup**
   ```bash
   # Start PostgreSQL with pgvector
   docker run -d \
     --name vectordb \
     -e POSTGRES_DB=vectordb \
     -e POSTGRES_USER=vectordb \
     -e POSTGRES_PASSWORD=vectordb \
     -p 5432:5432 \
     ankane/pgvector
   ```

4. **Database Migration**
   ```bash
   # Initialize Alembic
   alembic init alembic

   # Create initial migration
   alembic revision --autogenerate -m "Initial schema"

   # Apply migrations
   alembic upgrade head
   ```

5. **Document Setup**
   Place your documents in the `data` directory:
   ```
   data/
   ├── employee_handbook.pdf
   ├── policies.txt
   └── procedures.docx
   ```
   Documents will be automatically loaded when the RAG agent initializes.

## Running the System

1. Start the main application:
   ```bash
   python src/main.py
   ```

2. Test with various queries:
   ```
   # Test RAG
   Q: "What does our employee handbook say about vacation policy?"

   # Test SQL
   Q: "How many orders were placed last month?"
   Q: "Show me the top 5 customers by order value"

   # Test Search
   Q: "What are the latest developments in AI?"
   Q: "Search for recent breakthroughs in quantum computing"
   ```

## Project Structure 