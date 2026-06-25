"""add crm_atendimento_spdata to medicos.

Revision ID: 8c1d3e5f7a02
Revises: 7b9c2d4e6f01
Create Date: 2026-06-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "8c1d3e5f7a02"
down_revision = "7b9c2d4e6f01"
branch_labels = None
depends_on = None


def table_columns(table_name):
    return {column["name"] for column in inspect(op.get_bind()).get_columns(table_name)}


def table_indexes(table_name):
    return {index["name"] for index in inspect(op.get_bind()).get_indexes(table_name)}


def upgrade():
    if "crm_atendimento_spdata" not in table_columns("medicos"):
        with op.batch_alter_table("medicos", schema=None) as batch_op:
            batch_op.add_column(sa.Column("crm_atendimento_spdata", sa.String(length=50), nullable=True))

    if "ix_medicos_crm_atendimento_spdata" not in table_indexes("medicos"):
        with op.batch_alter_table("medicos", schema=None) as batch_op:
            batch_op.create_index("ix_medicos_crm_atendimento_spdata", ["crm_atendimento_spdata"], unique=False)

    op.execute("""
        UPDATE medicos
        SET crm_atendimento_spdata = crm
        WHERE crm_atendimento_spdata IS NULL
          AND crm IS NOT NULL
          AND crm <> ''
    """)


def downgrade():
    if "ix_medicos_crm_atendimento_spdata" in table_indexes("medicos"):
        with op.batch_alter_table("medicos", schema=None) as batch_op:
            batch_op.drop_index("ix_medicos_crm_atendimento_spdata")

    if "crm_atendimento_spdata" in table_columns("medicos"):
        with op.batch_alter_table("medicos", schema=None) as batch_op:
            batch_op.drop_column("crm_atendimento_spdata")
