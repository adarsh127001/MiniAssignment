"""Sample data

Revision ID: sample_data_001
Revises: 4324ab632d1e
Create Date: 2024-03-21

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timedelta

revision = 'sample_data_001'
down_revision = '4324ab632d1e'
branch_labels = None
depends_on = None

def upgrade():
    # Insert sample users
    op.execute("""
        INSERT INTO users (name, email, created_at) VALUES
        ('John Doe', 'john@example.com', CURRENT_TIMESTAMP),
        ('Jane Smith', 'jane@example.com', CURRENT_TIMESTAMP),
        ('Bob Wilson', 'bob@example.com', CURRENT_TIMESTAMP),
        ('Alice Brown', 'alice@example.com', CURRENT_TIMESTAMP),
        ('Charlie Davis', 'charlie@example.com', CURRENT_TIMESTAMP)
    """)
    
    # Insert sample products
    op.execute("""
        INSERT INTO products (name, email, created_at) VALUES
        ('Laptop Pro', 'sales@techstore.com', CURRENT_TIMESTAMP),
        ('Smartphone X', 'sales@techstore.com', CURRENT_TIMESTAMP),
        ('Tablet Ultra', 'sales@techstore.com', CURRENT_TIMESTAMP),
        ('Smart Watch', 'sales@techstore.com', CURRENT_TIMESTAMP),
        ('Wireless Earbuds', 'sales@techstore.com', CURRENT_TIMESTAMP)
    """)
    
    # Insert sample orders with varying dates and amounts
    op.execute("""
        WITH user_ids AS (SELECT id FROM users)
        INSERT INTO orders (order_date, total_amount, user_id)
        SELECT 
            CURRENT_TIMESTAMP - (random() * interval '30 days'),
            (random() * 1000 + 100)::numeric(10,2),
            id
        FROM user_ids, generate_series(1, 3)
    """)

def downgrade():
    op.execute("DELETE FROM orders")
    op.execute("DELETE FROM products")
    op.execute("DELETE FROM users") 