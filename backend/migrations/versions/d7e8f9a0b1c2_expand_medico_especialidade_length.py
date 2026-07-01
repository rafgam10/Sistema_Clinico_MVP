"""expand medico especialidade length.

Revision ID: d7e8f9a0b1c2
Revises: 2f4b6d8a0c1e
Create Date: 2026-07-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "d7e8f9a0b1c2"
down_revision = "2f4b6d8a0c1e"
branch_labels = None
depends_on = None


TABLE = "medicos"
COLUMN = "especialidade"


def table_exists(table_name):
    return table_name in inspect(op.get_bind()).get_table_names()


def column_length(table_name, column_name):
    if not table_exists(table_name):
        return None

    for column in inspect(op.get_bind()).get_columns(table_name):
        if column["name"] == column_name:
            return getattr(column["type"], "length", None)

    return None


def alter_especialidade_length(length):
    current_length = column_length(TABLE, COLUMN)
    if current_length == length:
        return

    with op.batch_alter_table(TABLE, schema=None) as batch_op:
        batch_op.alter_column(
            COLUMN,
            existing_type=sa.String(length=current_length or 120),
            type_=sa.String(length=length),
            existing_nullable=True,
        )


def upgrade():
    alter_especialidade_length(255)


def downgrade():
    alter_especialidade_length(120)
