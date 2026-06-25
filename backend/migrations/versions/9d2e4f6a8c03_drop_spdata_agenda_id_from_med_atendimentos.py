"""drop spdata_agenda_id from MED_ATENDIMENTOS.

Revision ID: 9d2e4f6a8c03
Revises: 8c1d3e5f7a02
Create Date: 2026-06-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "9d2e4f6a8c03"
down_revision = "8c1d3e5f7a02"
branch_labels = None
depends_on = None


FK_MED_ATENDIMENTOS_SPDATA_AGENDA = "fk_med_atendimentos_spdata_agenda_id"
IDX_MED_ATENDIMENTOS_SPDATA_AGENDA = "ix_MED_ATENDIMENTOS_spdata_agenda_id"


def table_exists(table_name):
    return table_name in inspect(op.get_bind()).get_table_names()


def table_columns(table_name):
    if not table_exists(table_name):
        return set()
    return {column["name"] for column in inspect(op.get_bind()).get_columns(table_name)}


def table_indexes(table_name):
    if not table_exists(table_name):
        return set()
    return {index["name"] for index in inspect(op.get_bind()).get_indexes(table_name)}


def table_foreign_keys(table_name):
    if not table_exists(table_name):
        return set()
    return {fk["name"] for fk in inspect(op.get_bind()).get_foreign_keys(table_name)}


def drop_fk_if_exists(table_name, fk_name):
    if fk_name not in table_foreign_keys(table_name):
        return
    with op.batch_alter_table(table_name, schema=None) as batch_op:
        batch_op.drop_constraint(fk_name, type_="foreignkey")


def drop_index_if_exists(table_name, index_name):
    if index_name not in table_indexes(table_name):
        return
    with op.batch_alter_table(table_name, schema=None) as batch_op:
        batch_op.drop_index(index_name)


def drop_column_if_exists(table_name, column_name):
    if column_name not in table_columns(table_name):
        return
    with op.batch_alter_table(table_name, schema=None) as batch_op:
        batch_op.drop_column(column_name)


def upgrade():
    drop_fk_if_exists("MED_ATENDIMENTOS", FK_MED_ATENDIMENTOS_SPDATA_AGENDA)
    drop_index_if_exists("MED_ATENDIMENTOS", IDX_MED_ATENDIMENTOS_SPDATA_AGENDA)
    drop_column_if_exists("MED_ATENDIMENTOS", "spdata_agenda_id")


def downgrade():
    TABLE = "MED_ATENDIMENTOS"

    if "spdata_agenda_id" not in table_columns(TABLE):
        with op.batch_alter_table(TABLE, schema=None) as batch_op:
            batch_op.add_column(
                sa.Column("spdata_agenda_id", sa.Integer(), nullable=False)
            )

    if IDX_MED_ATENDIMENTOS_SPDATA_AGENDA not in table_indexes(TABLE):
        with op.batch_alter_table(TABLE, schema=None) as batch_op:
            batch_op.create_index(
                IDX_MED_ATENDIMENTOS_SPDATA_AGENDA,
                ["spdata_agenda_id"],
            )

    if FK_MED_ATENDIMENTOS_SPDATA_AGENDA not in table_foreign_keys(TABLE):
        with op.batch_alter_table(TABLE, schema=None) as batch_op:
            batch_op.create_foreign_key(
                FK_MED_ATENDIMENTOS_SPDATA_AGENDA,
                "MED_SPDATA_AGENDA",
                ["spdata_agenda_id"],
                ["spdata_agenda_id"],
            )
