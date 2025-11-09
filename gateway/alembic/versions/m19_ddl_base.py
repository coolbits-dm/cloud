"""M19 DDL Base

Revision ID: m19_ddl_base
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'm19_ddl_base'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create posts table
    op.create_table('posts',
        sa.Column('id', sa.Text(), nullable=False),
        sa.Column('panel', sa.Text(), nullable=False),
        sa.Column('author', sa.Text(), nullable=False),
        sa.Column('ts', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('attachments', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'::jsonb),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("panel IN ('user','business','agency','dev')", name='posts_panel_check')
    )
    
    # Create comments table
    op.create_table('comments',
        sa.Column('id', sa.Text(), nullable=False),
        sa.Column('post_id', sa.Text(), nullable=False),
        sa.Column('author', sa.Text(), nullable=False),
        sa.Column('ts', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create invocations table
    op.create_table('invocations',
        sa.Column('id', sa.Text(), nullable=False),
        sa.Column('post_id', sa.Text(), nullable=True),
        sa.Column('agent_id', sa.Text(), nullable=False),
        sa.Column('role', sa.Text(), nullable=False),
        sa.Column('status', sa.Text(), nullable=False),
        sa.Column('result_ref', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('cost_cbt', sa.Numeric(), nullable=True, server_default='0'),
        sa.Column('ts', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("status IN ('queued','running','done','error')", name='invocations_status_check')
    )
    
    # Create ledger_entries table
    op.create_table('ledger_entries',
        sa.Column('id', sa.Text(), nullable=False),
        sa.Column('ts', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('ref', sa.Text(), nullable=True),
        sa.Column('delta', sa.Numeric(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('meta', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'::jsonb),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create rag_chunks table
    op.create_table('rag_chunks',
        sa.Column('id', sa.Text(), nullable=False),
        sa.Column('panel', sa.Text(), nullable=False),
        sa.Column('source', sa.Text(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('meta', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'::jsonb),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("panel IN ('user','business','agency','dev')", name='rag_chunks_panel_check')
    )
    
    # Create rag_embeddings table
    op.create_table('rag_embeddings',
        sa.Column('chunk_id', sa.Text(), nullable=False),
        sa.Column('embedding', sa.Text(), nullable=False),  # Will be converted to vector(1536) in separate migration
        sa.ForeignKeyConstraint(['chunk_id'], ['rag_chunks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('chunk_id')
    )
    
    # Create indexes
    op.create_index('idx_posts_panel_ts', 'posts', ['panel', 'ts'], unique=False, postgresql_using='btree')
    op.create_index('idx_rag_chunks_panel', 'rag_chunks', ['panel'], unique=False, postgresql_using='btree')


def downgrade():
    # Drop indexes
    op.drop_index('idx_rag_chunks_panel', table_name='rag_chunks')
    op.drop_index('idx_posts_panel_ts', table_name='posts')
    
    # Drop tables
    op.drop_table('rag_embeddings')
    op.drop_table('rag_chunks')
    op.drop_table('ledger_entries')
    op.drop_table('invocations')
    op.drop_table('comments')
    op.drop_table('posts')
    
    # Drop extension
    op.execute('DROP EXTENSION IF EXISTS vector')
