"""Add events table

Revision ID: 047d9fc6ec81
Revises: 
Create Date: 2023-03-09 18:18:13.861380

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '047d9fc6ec81'
down_revision = None
branch_labels = None
depends_on = None

event_state_enum = sa.Enum('active', 'close_win', 'close_lose', name='event_state_enum')


def upgrade() -> None:
    op.create_table(
        'events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('coefficient', sa.Float(), nullable=False),
        sa.Column('deadline', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('state', event_state_enum, nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('events')
    event_state_enum.drop(op.get_bind())

