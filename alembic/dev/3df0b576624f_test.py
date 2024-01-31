"""Test

Revision ID: 3df0b576624f
Revises: 
Create Date: 2023-08-03 11:11:26.143654

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import Sequence, CreateSequence, DropSequence, Column

# revision identifiers, used by Alembic.
revision = '3df0b576624f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### Alembic commands ###
    op.create_primary_key('survey_responses_pkey', 'survey_responses', ['id'])
    field_seq = Sequence('survey_responses_id_seq')
    op.execute(CreateSequence(field_seq))
    op.alter_column('survey_responses', 'id', server_default=field_seq.next_value())

    op.add_column('Predictions', Column('active', sa.Boolean , default=True))
    
    op.create_foreign_key('fk_notice_notice_type_id_notice_type', 'notice', 
                          'notice_type', ['notice_type_id'], ["id"])
    
    # ### end Alembic commands ###


def downgrade():
    # ### Alembic commands  ###
    op.drop_constraint('survey_responses_pkey', 'survey_responses', type_='primary')
    op.execute(DropSequence(Sequence('survey_responses_id_seq')))
    op.alter_column('survey_responses', 'id', server_default=None)

    op.drop_column('Predictions', 'active')

    op.drop_constraint('fk_notice_notice_type_id_notice_type', 'notice', type_='foreignkey')
    # ### end Alembic commands ###
