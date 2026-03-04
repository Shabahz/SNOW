"""init tables

Revision ID: 0001_init
Revises: 
Create Date: 2026-03-04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    op.create_table('households',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('invite_code', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_households_invite_code'), 'households', ['invite_code'], unique=True)

    op.create_table('household_members',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('household_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.Enum('owner', 'member', name='memberrole'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['household_id'], ['households.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('household_id', 'user_id', name='uq_household_user')
    )

    op.create_table('categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('household_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('color', sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(['household_id'], ['households.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_categories_household_id'), 'categories', ['household_id'], unique=False)

    op.create_table('budgets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('household_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('month', sa.Date(), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['household_id'], ['households.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('household_id', 'category_id', 'month', name='uq_budget_month')
    )
    op.create_index(op.f('ix_budgets_category_id'), 'budgets', ['category_id'], unique=False)
    op.create_index(op.f('ix_budgets_household_id'), 'budgets', ['household_id'], unique=False)
    op.create_index(op.f('ix_budgets_month'), 'budgets', ['month'], unique=False)

    op.create_table('plaid_connections',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('household_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('item_id', sa.String(length=255), nullable=False),
        sa.Column('access_token_encrypted', sa.Text(), nullable=False),
        sa.Column('sync_cursor', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['household_id'], ['households.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_plaid_connections_household_id'), 'plaid_connections', ['household_id'], unique=False)
    op.create_index(op.f('ix_plaid_connections_item_id'), 'plaid_connections', ['item_id'], unique=True)

    op.create_table('transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('household_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('plaid_connection_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('plaid_transaction_id', sa.String(length=255), nullable=True),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('occurred_on', sa.Date(), nullable=False),
        sa.Column('is_pending', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['household_id'], ['households.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['plaid_connection_id'], ['plaid_connections.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transactions_household_id'), 'transactions', ['household_id'], unique=False)
    op.create_index(op.f('ix_transactions_occurred_on'), 'transactions', ['occurred_on'], unique=False)
    op.create_index(op.f('ix_transactions_plaid_transaction_id'), 'transactions', ['plaid_transaction_id'], unique=True)

    op.create_table('device_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token', sa.String(length=512), nullable=False),
        sa.Column('platform', sa.String(length=30), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )
    op.create_index(op.f('ix_device_tokens_user_id'), 'device_tokens', ['user_id'], unique=False)

    op.create_table('budget_alert_state',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('budget_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('threshold_80_sent', sa.Boolean(), nullable=True),
        sa.Column('threshold_100_sent', sa.Boolean(), nullable=True),
        sa.Column('last_notified_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['budget_id'], ['budgets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('budget_id', name='uq_budget_alert_budget')
    )
    op.create_index(op.f('ix_budget_alert_state_budget_id'), 'budget_alert_state', ['budget_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_budget_alert_state_budget_id'), table_name='budget_alert_state')
    op.drop_table('budget_alert_state')
    op.drop_index(op.f('ix_device_tokens_user_id'), table_name='device_tokens')
    op.drop_table('device_tokens')
    op.drop_index(op.f('ix_transactions_plaid_transaction_id'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_occurred_on'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_household_id'), table_name='transactions')
    op.drop_table('transactions')
    op.drop_index(op.f('ix_plaid_connections_item_id'), table_name='plaid_connections')
    op.drop_index(op.f('ix_plaid_connections_household_id'), table_name='plaid_connections')
    op.drop_table('plaid_connections')
    op.drop_index(op.f('ix_budgets_month'), table_name='budgets')
    op.drop_index(op.f('ix_budgets_household_id'), table_name='budgets')
    op.drop_index(op.f('ix_budgets_category_id'), table_name='budgets')
    op.drop_table('budgets')
    op.drop_index(op.f('ix_categories_household_id'), table_name='categories')
    op.drop_table('categories')
    op.drop_table('household_members')
    op.drop_index(op.f('ix_households_invite_code'), table_name='households')
    op.drop_table('households')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.execute('DROP TYPE memberrole')
