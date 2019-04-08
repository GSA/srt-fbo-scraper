"""add machine_readable column to Attachment

Revision ID: 877732a28f4a
Revises: 
Create Date: 2019-04-08 13:37:30.221666

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '877732a28f4a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('attachment', sa.Column('machine_readable', sa.Boolean))


def downgrade():
    op.drop_column('attachment', 'machine_readable')
