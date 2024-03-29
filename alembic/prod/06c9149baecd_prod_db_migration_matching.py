"""prod db migration matching

Revision ID: 06c9149baecd
Revises: 
Create Date: 2023-05-22 15:30:25.932722

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "06c9149baecd"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("solicitations_pre_dla_update_oct_2021")
    op.alter_column(
        "Agencies",
        "updatedAt",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=True,
    )
    op.alter_column(
        "Predictions", "noticeType", existing_type=sa.VARCHAR(), nullable=True
    )
    op.alter_column(
        "Predictions", "createdAt", existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.drop_constraint("uniqueSolNum", "Predictions", type_="unique")
    op.create_unique_constraint(
        op.f("uq_Predictions_solNum"), "Predictions", ["solNum"]
    )
    op.alter_column(
        "Surveys", "updatedAt", existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        "Users",
        "updatedAt",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=True,
    )
    op.alter_column(
        "agency_alias", "agency_id", existing_type=sa.INTEGER(), nullable=True
    )
    op.alter_column(
        "notice_type",
        "createdAt",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
        existing_server_default=sa.text("now()"),
    )
    op.alter_column(
        "solicitations", "solNum", existing_type=sa.VARCHAR(), nullable=False
    )
    op.alter_column(
        "solicitations",
        "createdAt",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
        existing_server_default=sa.text("now()"),
    )
    op.drop_constraint("solicitations_solNum_key", "solicitations", type_="unique")
    op.create_unique_constraint(
        op.f("uq_solicitations_solNum"), "solicitations", ["solNum"]
    )
    op.alter_column(
        "survey_responses",
        "createdAt",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
        existing_server_default=sa.text("CURRENT_TIMESTAMP"),
    )
    op.drop_index("ix_feedback_solNum", table_name="survey_responses")
    op.create_index(
        op.f("ix_survey_responses_solNum"), "survey_responses", ["solNum"], unique=False
    )
    op.alter_column(
        "survey_responses_archive",
        "createdAt",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
        existing_server_default=sa.text("CURRENT_TIMESTAMP"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "survey_responses_archive",
        "createdAt",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
        existing_server_default=sa.text("CURRENT_TIMESTAMP"),
    )
    op.drop_index(op.f("ix_survey_responses_solNum"), table_name="survey_responses")
    op.create_index("ix_feedback_solNum", "survey_responses", ["solNum"], unique=False)
    op.alter_column(
        "survey_responses",
        "createdAt",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
        existing_server_default=sa.text("CURRENT_TIMESTAMP"),
    )
    op.drop_constraint(op.f("uq_solicitations_solNum"), "solicitations", type_="unique")
    op.create_unique_constraint("solicitations_solNum_key", "solicitations", ["solNum"])
    op.alter_column(
        "solicitations",
        "createdAt",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
        existing_server_default=sa.text("now()"),
    )
    op.alter_column(
        "solicitations", "solNum", existing_type=sa.VARCHAR(), nullable=True
    )
    op.alter_column(
        "notice_type",
        "createdAt",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
        existing_server_default=sa.text("now()"),
    )
    op.alter_column(
        "agency_alias", "agency_id", existing_type=sa.INTEGER(), nullable=False
    )
    op.alter_column(
        "Users",
        "updatedAt",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=False,
    )
    op.alter_column(
        "Surveys", "updatedAt", existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.drop_constraint(op.f("uq_Predictions_solNum"), "Predictions", type_="unique")
    op.create_unique_constraint("uniqueSolNum", "Predictions", ["solNum"])
    op.alter_column(
        "Predictions", "createdAt", existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        "Predictions", "noticeType", existing_type=sa.VARCHAR(), nullable=False
    )
    op.alter_column(
        "Agencies",
        "updatedAt",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=False,
    )
    op.create_table(
        "solicitations_pre_dla_update_oct_2021",
        sa.Column("id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("solNum", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("active", sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column(
            "updatedAt", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "createdAt", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
        sa.Column("title", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("url", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("agency", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("numDocs", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("notice_type_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("noticeType", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("date", postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.Column("office", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("na_flag", sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column(
            "category_list",
            postgresql.JSONB(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("undetermined", sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column(
            "history",
            postgresql.JSONB(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "action",
            postgresql.JSONB(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "actionDate", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
        sa.Column("actionStatus", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "contactInfo",
            postgresql.JSONB(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "parseStatus",
            postgresql.JSONB(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "predictions",
            postgresql.JSONB(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("reviewRec", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("searchText", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("compliant", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column(
            "noticeData",
            postgresql.JSONB(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("agency_id", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    # ### end Alembic commands ###
