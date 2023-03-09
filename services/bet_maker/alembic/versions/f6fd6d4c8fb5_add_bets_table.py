"""Add bets table

Revision ID: f6fd6d4c8fb5
Revises: 
Create Date: 2023-03-08 20:04:19.435080

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f6fd6d4c8fb5'
down_revision = None
branch_labels = None
depends_on = None

bet_state_enum = sa.Enum('active', 'close_win', 'close_lose', name='bet_state_enum')


def upgrade() -> None:
    op.create_table(
        'bets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('state', bet_state_enum, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('bets')
    bet_state_enum.drop(op.get_bind())


