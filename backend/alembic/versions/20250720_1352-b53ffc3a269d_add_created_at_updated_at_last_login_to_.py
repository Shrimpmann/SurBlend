"""Add created_at, updated_at, last_login to User model

Revision ID: b53ffc3a269d
Revises: 4312f4460cca
Create Date: 2025-07-20 13:52:XX

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b53ffc3a269d'
down_revision = '4312f4460cca'
branch_labels = None
depends_on = None

def upgrade():
    # Add columns with server_default for created_at to handle existing rows
    op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))

def downgrade():
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'created_at')
