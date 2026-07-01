"""create SPDATA especialidades cache.

Revision ID: 2f4b6d8a0c1e
Revises: b6c9d0e1f2a3
Create Date: 2026-07-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "2f4b6d8a0c1e"
down_revision = "b6c9d0e1f2a3"
branch_labels = None
depends_on = None


TABLE = "MED_SPDATA_ESPECIALIDADES"


def table_exists(table_name):
    return table_name in inspect(op.get_bind()).get_table_names()


def table_indexes(table_name):
    if not table_exists(table_name):
        return set()
    return {index["name"] for index in inspect(op.get_bind()).get_indexes(table_name)}


def create_index_if_missing(table_name, index_name, columns):
    if index_name in table_indexes(table_name):
        return
    op.create_index(index_name, table_name, columns)


def upgrade():
    if table_exists(TABLE):
        return

    op.create_table(
        TABLE,
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("codigo_spdata", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("cred", sa.String(length=50), nullable=True),
        sa.Column("refexp", sa.String(length=50), nullable=True),
        sa.Column("sigla", sa.String(length=50), nullable=True),
        sa.Column("idade_inicial", sa.Integer(), nullable=True),
        sa.Column("idade_final", sa.Integer(), nullable=True),
        sa.Column("sexo", sa.String(length=20), nullable=True),
        sa.Column("id_tbdigital_especialidade", sa.Integer(), nullable=True),
        sa.Column("dados_spdata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "codigo_spdata",
            name="uq_MED_SPDATA_ESPECIALIDADES_codigo_spdata",
        ),
    )
    create_index_if_missing(
        TABLE,
        "ix_MED_SPDATA_ESPECIALIDADES_codigo_spdata",
        ["codigo_spdata"],
    )
    create_index_if_missing(TABLE, "ix_MED_SPDATA_ESPECIALIDADES_nome", ["nome"])
    create_index_if_missing(TABLE, "ix_MED_SPDATA_ESPECIALIDADES_cred", ["cred"])
    create_index_if_missing(TABLE, "ix_MED_SPDATA_ESPECIALIDADES_sigla", ["sigla"])
    create_index_if_missing(TABLE, "ix_MED_SPDATA_ESPECIALIDADES_sexo", ["sexo"])


def downgrade():
    if table_exists(TABLE):
        op.drop_table(TABLE)
