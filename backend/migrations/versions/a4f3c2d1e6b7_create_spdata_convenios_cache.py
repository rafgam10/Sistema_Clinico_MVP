"""create SPDATA convenios cache.

Revision ID: a4f3c2d1e6b7
Revises: 0a1b2c3d4e5f
Create Date: 2026-06-26 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "a4f3c2d1e6b7"
down_revision = "0a1b2c3d4e5f"
branch_labels = None
depends_on = None


def table_exists(table_name):
    return table_name in inspect(op.get_bind()).get_table_names()


def table_indexes(table_name):
    if not table_exists(table_name):
        return set()
    return {index["name"] for index in inspect(op.get_bind()).get_indexes(table_name)}


def create_index_if_missing(table_name, index_name, columns, unique=False):
    if index_name in table_indexes(table_name):
        return

    op.create_index(index_name, table_name, columns, unique=unique)


def upgrade():
    if table_exists("MED_SPDATA_CONVENIOS"):
        return

    op.create_table(
        "MED_SPDATA_CONVENIOS",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("codigo_spdata", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("situacao", sa.String(length=50), nullable=True),
        sa.Column("registro_ans", sa.String(length=50), nullable=True),
        sa.Column("dados_spdata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("codigo_spdata", name="uq_MED_SPDATA_CONVENIOS_codigo_spdata"),
    )
    create_index_if_missing(
        "MED_SPDATA_CONVENIOS",
        "ix_MED_SPDATA_CONVENIOS_codigo_spdata",
        ["codigo_spdata"],
    )
    create_index_if_missing(
        "MED_SPDATA_CONVENIOS",
        "ix_MED_SPDATA_CONVENIOS_nome",
        ["nome"],
    )
    create_index_if_missing(
        "MED_SPDATA_CONVENIOS",
        "ix_MED_SPDATA_CONVENIOS_situacao",
        ["situacao"],
    )


def downgrade():
    if table_exists("MED_SPDATA_CONVENIOS"):
        op.drop_table("MED_SPDATA_CONVENIOS")
