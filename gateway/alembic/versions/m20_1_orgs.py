"""M20.1 - Organizations and RBAC

Revision ID: m20_1_orgs
Revises: m19_3_orchestrator
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'm20_1_orgs'
down_revision = 'm19_3_orchestrator'
branch_labels = None
depends_on = None


def upgrade():
    # Create organizations table
    op.create_table('organizations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organizations_slug'), 'organizations', ['slug'], unique=True)
    op.create_index(op.f('ix_organizations_created_by'), 'organizations', ['created_by'], unique=False)

    # Create org_users table
    op.create_table('org_users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('invited_by', sa.String(length=255), nullable=True),
        sa.Column('joined_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_org_users_org_id'), 'org_users', ['org_id'], unique=False)
    op.create_index(op.f('ix_org_users_user_id'), 'org_users', ['user_id'], unique=False)
    op.create_index(op.f('ix_org_users_email'), 'org_users', ['email'], unique=False)
    op.create_index(op.f('ix_org_users_status'), 'org_users', ['status'], unique=False)
    op.create_index(op.f('ix_org_users_role'), 'org_users', ['role'], unique=False)

    # Create org_invites table
    op.create_table('org_invites',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('invited_by', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('accepted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_org_invites_token'), 'org_invites', ['token'], unique=True)
    op.create_index(op.f('ix_org_invites_email'), 'org_invites', ['email'], unique=False)
    op.create_index(op.f('ix_org_invites_status'), 'org_invites', ['status'], unique=False)
    op.create_index(op.f('ix_org_invites_expires_at'), 'org_invites', ['expires_at'], unique=False)

    # Add org_id to existing tables for multi-tenancy
    op.add_column('posts', sa.Column('org_id', sa.String(), nullable=True))
    op.add_column('comments', sa.Column('org_id', sa.String(), nullable=True))
    op.add_column('invocations', sa.Column('org_id', sa.String(), nullable=True))
    op.add_column('ledger_entries', sa.Column('org_id', sa.String(), nullable=True))
    op.add_column('rag_chunks', sa.Column('org_id', sa.String(), nullable=True))
    op.add_column('flows', sa.Column('org_id', sa.String(), nullable=True))
    op.add_column('flow_runs', sa.Column('org_id', sa.String(), nullable=True))

    # Create indexes for org_id columns
    op.create_index(op.f('ix_posts_org_id'), 'posts', ['org_id'], unique=False)
    op.create_index(op.f('ix_comments_org_id'), 'comments', ['org_id'], unique=False)
    op.create_index(op.f('ix_invocations_org_id'), 'invocations', ['org_id'], unique=False)
    op.create_index(op.f('ix_ledger_entries_org_id'), 'ledger_entries', ['org_id'], unique=False)
    op.create_index(op.f('ix_rag_chunks_org_id'), 'rag_chunks', ['org_id'], unique=False)
    op.create_index(op.f('ix_flows_org_id'), 'flows', ['org_id'], unique=False)
    op.create_index(op.f('ix_flow_runs_org_id'), 'flow_runs', ['org_id'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_flow_runs_org_id'), table_name='flow_runs')
    op.drop_index(op.f('ix_flows_org_id'), table_name='flows')
    op.drop_index(op.f('ix_rag_chunks_org_id'), table_name='rag_chunks')
    op.drop_index(op.f('ix_ledger_entries_org_id'), table_name='ledger_entries')
    op.drop_index(op.f('ix_invocations_org_id'), table_name='invocations')
    op.drop_index(op.f('ix_comments_org_id'), table_name='comments')
    op.drop_index(op.f('ix_posts_org_id'), table_name='posts')

    # Drop org_id columns
    op.drop_column('flow_runs', 'org_id')
    op.drop_column('flows', 'org_id')
    op.drop_column('rag_chunks', 'org_id')
    op.drop_column('ledger_entries', 'org_id')
    op.drop_column('invocations', 'org_id')
    op.drop_column('comments', 'org_id')
    op.drop_column('posts', 'org_id')

    # Drop org_invites table
    op.drop_index(op.f('ix_org_invites_expires_at'), table_name='org_invites')
    op.drop_index(op.f('ix_org_invites_status'), table_name='org_invites')
    op.drop_index(op.f('ix_org_invites_email'), table_name='org_invites')
    op.drop_index(op.f('ix_org_invites_token'), table_name='org_invites')
    op.drop_table('org_invites')

    # Drop org_users table
    op.drop_index(op.f('ix_org_users_role'), table_name='org_users')
    op.drop_index(op.f('ix_org_users_status'), table_name='org_users')
    op.drop_index(op.f('ix_org_users_email'), table_name='org_users')
    op.drop_index(op.f('ix_org_users_user_id'), table_name='org_users')
    op.drop_index(op.f('ix_org_users_org_id'), table_name='org_users')
    op.drop_table('org_users')

    # Drop organizations table
    op.drop_index(op.f('ix_organizations_created_by'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_slug'), table_name='organizations')
    op.drop_table('organizations')
