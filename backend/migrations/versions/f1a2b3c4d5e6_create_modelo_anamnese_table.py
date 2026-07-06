"""create modelo_anamnese table.

Revision ID: f1a2b3c4d5e6
Revises: e4f5a6b7c8d9
Create Date: 2026-07-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "f1a2b3c4d5e6"
down_revision = "e4f5a6b7c8d9"
branch_labels = None
depends_on = None


def table_exists(table_name):
    return table_name in inspect(op.get_bind()).get_table_names()


def upgrade():
    if not table_exists("MODELO_ANAMNESE"):
        op.create_table(
            "MODELO_ANAMNESE",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("nome_modelo", sa.String(length=255), nullable=False),
            sa.Column("medico_id", sa.Integer(), nullable=False),
            sa.Column("conteudo", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_MODELO_ANAMNESE_medico_id",
            "MODELO_ANAMNESE",
            ["medico_id"],
        )
        op.create_foreign_key(
            "fk_modelo_anamnese_medico_id",
            "MODELO_ANAMNESE",
            "usuarios",
            ["medico_id"],
            ["id"],
        )


def downgrade():
    if table_exists("MODELO_ANAMNESE"):
        with op.batch_alter_table("MODELO_ANAMNESE") as batch_op:
            batch_op.drop_constraint("fk_modelo_anamnese_medico_id", type_="foreignkey")
        op.drop_table("MODELO_ANAMNESE")
