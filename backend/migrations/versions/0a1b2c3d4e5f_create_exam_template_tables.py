"""create exam template tables.

Revision ID: 0a1b2c3d4e5f
Revises: 9d2e4f6a8c03
Create Date: 2026-06-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0a1b2c3d4e5f"
down_revision = "9d2e4f6a8c03"
branch_labels = None
depends_on = None


def table_exists(table_name):
    return table_name in inspect(op.get_bind()).get_table_names()


def upgrade():
    if not table_exists("MODELO_SOLICITACAO_EXAME"):
        op.create_table(
            "MODELO_SOLICITACAO_EXAME",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("nome_modelo", sa.String(length=255), nullable=False),
            sa.Column("medico_id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_MODELO_SOLICITACAO_EXAME_medico_id",
            "MODELO_SOLICITACAO_EXAME",
            ["medico_id"],
        )
        op.create_foreign_key(
            "fk_modelo_exame_medico_id",
            "MODELO_SOLICITACAO_EXAME",
            "usuarios",
            ["medico_id"],
            ["id"],
        )

    if not table_exists("EXAMES_MODELO_EXAME"):
        op.create_table(
            "EXAMES_MODELO_EXAME",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("nome_exame", sa.String(length=255), nullable=False),
            sa.Column(
                "id_modelo_solicitacao_exame", sa.Integer(), nullable=False
            ),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_EXAMES_MODELO_EXAME_id_modelo",
            "EXAMES_MODELO_EXAME",
            ["id_modelo_solicitacao_exame"],
        )
        op.create_foreign_key(
            "fk_exame_modelo_exame_id",
            "EXAMES_MODELO_EXAME",
            "MODELO_SOLICITACAO_EXAME",
            ["id_modelo_solicitacao_exame"],
            ["id"],
        )


def downgrade():
    if table_exists("EXAMES_MODELO_EXAME"):
        with op.batch_alter_table("EXAMES_MODELO_EXAME") as batch_op:
            batch_op.drop_constraint("fk_exame_modelo_exame_id", type_="foreignkey")
        op.drop_table("EXAMES_MODELO_EXAME")

    if table_exists("MODELO_SOLICITACAO_EXAME"):
        with op.batch_alter_table("MODELO_SOLICITACAO_EXAME") as batch_op:
            batch_op.drop_constraint("fk_modelo_exame_medico_id", type_="foreignkey")
        op.drop_table("MODELO_SOLICITACAO_EXAME")
