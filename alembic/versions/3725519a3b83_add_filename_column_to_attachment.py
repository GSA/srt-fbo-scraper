"""add filename column to Attachment

Revision ID: 3725519a3b83
Revises: 
Create Date: 2019-04-08 19:37:28.880047

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3725519a3b83'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('attachment', sa.Column('filename', sa.Text, nullable = True))


def downgrade():
    op.drop_column('attachment', 'filename')
