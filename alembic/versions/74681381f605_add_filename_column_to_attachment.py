"""add filename column to Attachment

Revision ID: 74681381f605
Revises: 877732a28f4a
Create Date: 2019-04-08 13:40:20.173775

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74681381f605'
down_revision = '877732a28f4a'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('attachment', sa.Column('filename', sa.Text, nullable = True))


def downgrade():
    op.drop_column('attachment', 'filename')
