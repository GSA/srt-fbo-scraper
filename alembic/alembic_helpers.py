from alembic import op
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
