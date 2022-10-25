"""add content column to posts table

Revision ID: 167336143d3e
Revises: 2d87eee3bb47
Create Date: 2022-10-25 10:29:38.086436

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '167336143d3e'
down_revision = '2d87eee3bb47'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("posts", sa.Column('content', sa.String(), nullable=False))


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass
