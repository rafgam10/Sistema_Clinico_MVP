"""corrige campos para registro medico.

Revision ID: f2a9d7c6e8b1
Revises: c14ac1d3af8b
Create Date: 2026-06-19 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f2a9d7c6e8b1"
down_revision = "c14ac1d3af8b"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("usuarios", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "role",
                sa.String(length=50),
                nullable=False,
                server_default="medico",
            )
        )

    with op.batch_alter_table("atendimentos", schema=None) as batch_op:
        batch_op.add_column(sa.Column("spdata_paciente_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("spdata_agenda_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("spdata_medico_id", sa.Integer(), nullable=True))

    with op.batch_alter_table("medicos", schema=None) as batch_op:
        batch_op.alter_column(
            "crm",
            existing_type=sa.String(length=20),
            nullable=True,
        )
        batch_op.alter_column(
            "crm_uf",
            existing_type=sa.String(length=2),
            nullable=True,
        )


def downgrade():
    with op.batch_alter_table("medicos", schema=None) as batch_op:
        batch_op.alter_column(
            "crm_uf",
            existing_type=sa.String(length=2),
            nullable=False,
        )
        batch_op.alter_column(
            "crm",
            existing_type=sa.String(length=20),
            nullable=False,
        )

    with op.batch_alter_table("atendimentos", schema=None) as batch_op:
        batch_op.drop_column("spdata_medico_id")
        batch_op.drop_column("spdata_agenda_id")
        batch_op.drop_column("spdata_paciente_id")

    with op.batch_alter_table("usuarios", schema=None) as batch_op:
        batch_op.drop_column("role")
