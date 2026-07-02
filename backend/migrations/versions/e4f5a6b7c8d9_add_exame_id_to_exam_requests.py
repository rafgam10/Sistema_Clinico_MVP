"""add exame_id to exam requests and templates.

Revision ID: e4f5a6b7c8d9
Revises: d7e8f9a0b1c2
Create Date: 2026-07-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "e4f5a6b7c8d9"
down_revision = "d7e8f9a0b1c2"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "solicitacoes_exames",
        sa.Column("exame_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        "ix_solicitacoes_exames_exame_id",
        "solicitacoes_exames",
        ["exame_id"],
    )
    op.create_foreign_key(
        "fk_solicitacoes_exames_exame_id_exames",
        "solicitacoes_exames",
        "exames",
        ["exame_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column(
        "EXAMES_MODELO_EXAME",
        sa.Column("exame_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        "ix_EXAMES_MODELO_EXAME_exame_id",
        "EXAMES_MODELO_EXAME",
        ["exame_id"],
    )
    op.create_foreign_key(
        "fk_EXAMES_MODELO_EXAME_exame_id_exames",
        "EXAMES_MODELO_EXAME",
        "exames",
        ["exame_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.execute(
        """
        UPDATE solicitacoes_exames AS s
        JOIN (
            SELECT nome, MIN(id) AS id
            FROM exames
            GROUP BY nome
            HAVING COUNT(*) = 1
        ) AS e ON e.nome = s.tipo_exame
        SET s.exame_id = e.id
        WHERE s.exame_id IS NULL
        """
    )

    op.execute(
        """
        UPDATE EXAMES_MODELO_EXAME AS em
        JOIN (
            SELECT nome, MIN(id) AS id
            FROM exames
            GROUP BY nome
            HAVING COUNT(*) = 1
        ) AS e ON e.nome = em.nome_exame
        SET em.exame_id = e.id
        WHERE em.exame_id IS NULL
        """
    )


def downgrade():
    op.drop_constraint(
        "fk_EXAMES_MODELO_EXAME_exame_id_exames",
        "EXAMES_MODELO_EXAME",
        type_="foreignkey",
    )
    op.drop_index("ix_EXAMES_MODELO_EXAME_exame_id", table_name="EXAMES_MODELO_EXAME")
    op.drop_column("EXAMES_MODELO_EXAME", "exame_id")

    op.drop_constraint(
        "fk_solicitacoes_exames_exame_id_exames",
        "solicitacoes_exames",
        type_="foreignkey",
    )
    op.drop_index("ix_solicitacoes_exames_exame_id", table_name="solicitacoes_exames")
    op.drop_column("solicitacoes_exames", "exame_id")
