"""add na flag to notice table

Revision ID: 48a836bedb3f
Revises: 3725519a3b83
Create Date: 2019-09-25 10:16:10.507488

"""
from alembic import op
import sqlalchemy as sa
import imp
import os

alembic_helpers = imp.load_source('alembic_helpers', (
    os.getcwd() + '/' + op.get_context().script.dir + '/alembic_helpers.py'))

# revision identifiers, used by Alembic.
revision = '48a836bedb3f'
down_revision = '3725519a3b83'
branch_labels = None
depends_on = None


def upgrade():
    if alembic_helpers.table_has_column('notice', 'na_flag'):
        op.drop_column('notice', 'na_flag')
    op.add_column('notice', sa.Column('na_flag', 
                                      sa.Boolean, 
                                      default = False))


def downgrade():
    op.drop_column('notice', 'na_flag')
    
