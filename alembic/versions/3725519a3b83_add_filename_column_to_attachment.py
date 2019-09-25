"""add filename column to Attachment

Revision ID: 3725519a3b83
Revises: 
Create Date: 2019-04-08 19:37:28.880047

"""
from alembic import op
import sqlalchemy as sa
import imp
import os

alembic_helpers = imp.load_source('alembic_helpers', (
    os.getcwd() + '/' + op.get_context().script.dir + '/alembic_helpers.py'))

# revision identifiers, used by Alembic.
revision = '3725519a3b83'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    if not alembic_helpers.table_has_column('attachment', 'filename'):
        op.add_column('attachment', sa.Column('filename', sa.Text, nullable = True))


def downgrade():
    if alembic_helpers.table_has_column('attachment', 'filename'):
        op.drop_column('attachment', 'filename')
