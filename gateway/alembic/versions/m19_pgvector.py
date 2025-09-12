"""Add pgvector support

Revision ID: m19_pgvector
Revises: m19_ddl_base
Create Date: 2024-01-01 00:01:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'm19_pgvector'
down_revision = 'm19_ddl_base'
branch_labels = None
depends_on = None


def upgrade():
    # Convert embedding column to vector type
    op.execute('ALTER TABLE rag_embeddings ALTER COLUMN embedding TYPE vector(1536) USING embedding::vector')
    
    # Create ANN index
    op.execute('''
        CREATE INDEX IF NOT EXISTS idx_rag_embeddings_ann
        ON rag_embeddings USING ivfflat (embedding vector_l2_ops) 
        WITH (lists = 100)
    ''')


def downgrade():
    # Drop ANN index
    op.execute('DROP INDEX IF EXISTS idx_rag_embeddings_ann')
    
    # Convert back to text
    op.execute('ALTER TABLE rag_embeddings ALTER COLUMN embedding TYPE text USING embedding::text')
