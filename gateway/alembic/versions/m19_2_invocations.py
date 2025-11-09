"""M19.2 Invocations enhancements

Revision ID: m19_2_invocations
Revises: m19_pgvector
Create Date: 2024-01-01 00:02:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'm19_2_invocations'
down_revision = 'm19_pgvector'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to invocations
    op.add_column('invocations', sa.Column('error', sa.Text(), nullable=True))
    op.add_column('invocations', sa.Column('trace_id', sa.Text(), nullable=True))
    
    # Add meta column to comments
    op.add_column('comments', sa.Column('meta', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'::jsonb))
    
    # Add balance_after to ledger_entries (optional)
    op.add_column('ledger_entries', sa.Column('balance_after', sa.Numeric(), nullable=True))
    
    # Create indexes
    op.create_index('idx_inv_post', 'invocations', ['post_id'], unique=False)
    op.create_index('idx_inv_status', 'invocations', ['status'], unique=False)
    op.create_index('idx_inv_agent_status', 'invocations', ['agent_id', 'status'], unique=False)
    op.create_index('idx_inv_trace', 'invocations', ['trace_id'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index('idx_inv_trace', table_name='invocations')
    op.drop_index('idx_inv_agent_status', table_name='invocations')
    op.drop_index('idx_inv_status', table_name='invocations')
    op.drop_index('idx_inv_post', table_name='invocations')
    
    # Drop columns
    op.drop_column('ledger_entries', 'balance_after')
    op.drop_column('comments', 'meta')
    op.drop_column('invocations', 'trace_id')
    op.drop_column('invocations', 'error')
