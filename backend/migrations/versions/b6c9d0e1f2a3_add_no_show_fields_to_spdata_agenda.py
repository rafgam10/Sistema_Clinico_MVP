"""add no-show fields to SPDATA agenda mirror.

Revision ID: b6c9d0e1f2a3
Revises: a4f3c2d1e6b7
Create Date: 2026-06-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "b6c9d0e1f2a3"
down_revision = "a4f3c2d1e6b7"
branch_labels = None
depends_on = None


TABLE = "MED_SPDATA_AGENDA"


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


def add_column_if_missing(table_name, column):
    if column.name in table_columns(table_name):
        return
    with op.batch_alter_table(table_name, schema=None) as batch_op:
        batch_op.add_column(column)


def drop_column_if_exists(table_name, column_name):
    if column_name not in table_columns(table_name):
        return
    with op.batch_alter_table(table_name, schema=None) as batch_op:
        batch_op.drop_column(column_name)


def create_index_if_missing(table_name, index_name, columns):
    if index_name in table_indexes(table_name):
        return
    with op.batch_alter_table(table_name, schema=None) as batch_op:
        batch_op.create_index(index_name, columns)


def drop_index_if_exists(table_name, index_name):
    if index_name not in table_indexes(table_name):
        return
    with op.batch_alter_table(table_name, schema=None) as batch_op:
        batch_op.drop_index(index_name)


def upgrade():
    add_column_if_missing(TABLE, sa.Column("registro", sa.String(length=50), nullable=True))
    add_column_if_missing(TABLE, sa.Column("grv_ate", sa.Integer(), nullable=True))
    add_column_if_missing(TABLE, sa.Column("crm", sa.String(length=50), nullable=True))
    add_column_if_missing(TABLE, sa.Column("id_convenio_spdata", sa.Integer(), nullable=True))
    add_column_if_missing(TABLE, sa.Column("especialidade", sa.String(length=120), nullable=True))
    add_column_if_missing(TABLE, sa.Column("telefone", sa.String(length=30), nullable=True))

    create_index_if_missing(TABLE, "ix_MED_SPDATA_AGENDA_registro", ["registro"])
    create_index_if_missing(TABLE, "ix_MED_SPDATA_AGENDA_crm", ["crm"])
    create_index_if_missing(TABLE, "ix_MED_SPDATA_AGENDA_id_convenio_spdata", ["id_convenio_spdata"])


def downgrade():
    drop_index_if_exists(TABLE, "ix_MED_SPDATA_AGENDA_id_convenio_spdata")
    drop_index_if_exists(TABLE, "ix_MED_SPDATA_AGENDA_crm")
    drop_index_if_exists(TABLE, "ix_MED_SPDATA_AGENDA_registro")

    drop_column_if_exists(TABLE, "telefone")
    drop_column_if_exists(TABLE, "especialidade")
    drop_column_if_exists(TABLE, "id_convenio_spdata")
    drop_column_if_exists(TABLE, "crm")
    drop_column_if_exists(TABLE, "grv_ate")
    drop_column_if_exists(TABLE, "registro")
