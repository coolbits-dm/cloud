"""M19.3 Orchestrator tables

Revision ID: m19_3_orchestrator
Revises: m19_2_invocations
Create Date: 2024-01-01 00:03:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'm19_3_orchestrator'
down_revision = 'm19_2_invocations'
branch_labels = None
depends_on = None


def upgrade():
    # Create flows table
    op.create_table('flows',
        sa.Column('id', sa.Text(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('panel', sa.Text(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('spec', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create flow_runs table
    op.create_table('flow_runs',
        sa.Column('id', sa.Text(), nullable=False),
        sa.Column('flow_id', sa.Text(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.Text(), nullable=False),  # queued|running|success|failed|canceled
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.Column('trigger_ref', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('trace_id', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create run_events table
    op.create_table('run_events',
        sa.Column('id', sa.Text(), nullable=False),
        sa.Column('run_id', sa.Text(), nullable=False),
        sa.Column('ts', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('level', sa.Text(), nullable=False),  # info|error|debug
        sa.Column('node_id', sa.Text(), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create nodes_cache table
    op.create_table('nodes_cache',
        sa.Column('id', sa.Text(), nullable=False),
        sa.Column('run_id', sa.Text(), nullable=False),
        sa.Column('node_id', sa.Text(), nullable=False),
        sa.Column('output', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.Text(), nullable=False),  # queued|running|success|failed|skipped
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.Column('took_ms', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_flow_runs_flowid_ts', 'flow_runs', ['flow_id', sa.text('started_at DESC')], unique=False)
    op.create_index('idx_run_events_runid_ts', 'run_events', ['run_id', sa.text('ts')], unique=False)
    op.create_index('idx_nodes_cache_runid_node', 'nodes_cache', ['run_id', 'node_id'], unique=False)
    op.create_index('idx_flows_panel_active', 'flows', ['panel', 'is_active'], unique=False)
    op.create_index('idx_flow_runs_status', 'flow_runs', ['status'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index('idx_flow_runs_status', table_name='flow_runs')
    op.drop_index('idx_flows_panel_active', table_name='flows')
    op.drop_index('idx_nodes_cache_runid_node', table_name='nodes_cache')
    op.drop_index('idx_run_events_runid_ts', table_name='run_events')
    op.drop_index('idx_flow_runs_flowid_ts', table_name='flow_runs')
    
    # Drop tables
    op.drop_table('nodes_cache')
    op.drop_table('run_events')
    op.drop_table('flow_runs')
    op.drop_table('flows')
