"""add na flag to notice table

Revision ID: 48a836bedb3f
Revises: 3725519a3b83
Create Date: 2019-09-25 10:16:10.507488

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import engine_from_config
from sqlalchemy.engine import reflection


def table_has_column(table, column):
    """Check table has a column. Usefule before trying to add or drop the column 
    in an alembic migration file.
    
    Arguments:
        table {str} -- name of the table
        column {str} -- name of the column
    
    Returns:
        [bool] -- True if the table has the column. False otherwise.
    """
    config = op.get_context().config
    engine = engine_from_config(
        config.get_section(config.config_ini_section), prefix='sqlalchemy.')
    insp = reflection.Inspector.from_engine(engine)
    has_column = False
    for col in insp.get_columns(table):
        if column not in col['name']:
            continue
        has_column = True
    
    return has_column

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
    
