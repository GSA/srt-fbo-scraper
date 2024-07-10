"""Adding art language table

Revision ID: 2e38f559933b
Revises: 78823e9293e9
Create Date: 2024-06-25 14:55:27.913403

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = '2e38f559933b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('art_language',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('solicitation_id', sa.Integer(), nullable=True),
    sa.Column('language', JSONB(), nullable=False),
    sa.Column('createdAt', sa.DateTime(), nullable=False),
    sa.Column('updatedAt', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['solicitation_id'], ['solicitations.id'], name=op.f('fk_art_language_solicitation_solicitations')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_art_language'))
    )
    
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    
    op.drop_table('art_language')
    # ### end Alembic commands ###
