"""add filename column to Attachment

Revision ID: 3725519a3b83
Revises: 
Create Date: 2019-04-08 19:37:28.880047

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
