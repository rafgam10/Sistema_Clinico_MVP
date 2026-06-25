"""create SPDATA atendimentos mirror.

Revision ID: 7b9c2d4e6f01
Revises: 3d8a70df2ef6
Create Date: 2026-06-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import mysql


revision = "7b9c2d4e6f01"
down_revision = "3d8a70df2ef6"
branch_labels = None
depends_on = None


FK_MED_ATENDIMENTOS_SPDATA = "fk_med_atendimentos_med_spdata_atendimento_id"


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


def add_column_if_missing(table_name, column):
    if column.name in table_columns(table_name):
        return

    with op.batch_alter_table(table_name, schema=None) as batch_op:
        batch_op.add_column(column)


def create_index_if_missing(table_name, index_name, columns, unique=False):
    if index_name in table_indexes(table_name):
        return

    with op.batch_alter_table(table_name, schema=None) as batch_op:
        batch_op.create_index(index_name, columns, unique=unique)


def drop_index_if_exists(table_name, index_name):
    if index_name not in table_indexes(table_name):
        return

    with op.batch_alter_table(table_name, schema=None) as batch_op:
        batch_op.drop_index(index_name)


def create_table_med_spdata_atendimentos():
    if table_exists("MED_SPDATA_ATENDIMENTOS"):
        return

    op.create_table(
        "MED_SPDATA_ATENDIMENTOS",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("spdata_atendimento_id", sa.Integer(), nullable=False),
        sa.Column("cod_atendimento", sa.String(length=50), nullable=True),
        sa.Column("id_paciente_spdata", sa.Integer(), nullable=True),
        sa.Column("id_medico_spdata", sa.Integer(), nullable=True),
        sa.Column("medico", sa.String(length=255), nullable=True),
        sa.Column("crm_medico", sa.String(length=50), nullable=True),
        sa.Column("data_hora_entrada", sa.DateTime(), nullable=False),
        sa.Column("data_atendimento", sa.Date(), nullable=False),
        sa.Column("hora_entrada", sa.Time(), nullable=True),
        sa.Column("data_hora_alta_medica", sa.DateTime(), nullable=True),
        sa.Column("id_convenio_spdata", sa.Integer(), nullable=True),
        sa.Column("id_centro_custo_spdata", sa.Integer(), nullable=True),
        sa.Column("obs_atendimento", sa.Text(), nullable=True),
        sa.Column("paciente", sa.String(length=255), nullable=False),
        sa.Column("cpf", sa.String(length=20), nullable=True),
        sa.Column("prontuario", sa.String(length=50), nullable=True),
        sa.Column("data_nascimento", sa.Date(), nullable=True),
        sa.Column("sexo", sa.String(length=20), nullable=True),
        sa.Column("celular", sa.String(length=30), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("endereco", sa.String(length=500), nullable=True),
        sa.Column("dados_spdata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("spdata_atendimento_id", name="uq_MED_SPDATA_ATENDIMENTOS_spdata_atendimento_id"),
    )

    create_index_if_missing("MED_SPDATA_ATENDIMENTOS", "ix_MED_SPDATA_ATENDIMENTOS_cod_atendimento", ["cod_atendimento"])
    create_index_if_missing("MED_SPDATA_ATENDIMENTOS", "ix_MED_SPDATA_ATENDIMENTOS_cpf", ["cpf"])
    create_index_if_missing("MED_SPDATA_ATENDIMENTOS", "ix_MED_SPDATA_ATENDIMENTOS_crm_medico", ["crm_medico"])
    create_index_if_missing("MED_SPDATA_ATENDIMENTOS", "ix_MED_SPDATA_ATENDIMENTOS_data_atendimento", ["data_atendimento"])
    create_index_if_missing("MED_SPDATA_ATENDIMENTOS", "ix_MED_SPDATA_ATENDIMENTOS_data_hora_entrada", ["data_hora_entrada"])
    create_index_if_missing("MED_SPDATA_ATENDIMENTOS", "ix_MED_SPDATA_ATENDIMENTOS_id_centro_custo_spdata", ["id_centro_custo_spdata"])
    create_index_if_missing("MED_SPDATA_ATENDIMENTOS", "ix_MED_SPDATA_ATENDIMENTOS_id_convenio_spdata", ["id_convenio_spdata"])
    create_index_if_missing("MED_SPDATA_ATENDIMENTOS", "ix_MED_SPDATA_ATENDIMENTOS_id_medico_spdata", ["id_medico_spdata"])
    create_index_if_missing("MED_SPDATA_ATENDIMENTOS", "ix_MED_SPDATA_ATENDIMENTOS_id_paciente_spdata", ["id_paciente_spdata"])
    create_index_if_missing("MED_SPDATA_ATENDIMENTOS", "ix_MED_SPDATA_ATENDIMENTOS_paciente", ["paciente"])
    create_index_if_missing("MED_SPDATA_ATENDIMENTOS", "ix_MED_SPDATA_ATENDIMENTOS_prontuario", ["prontuario"])


def upgrade():
    create_table_med_spdata_atendimentos()

    add_column_if_missing(
        "MED_ATENDIMENTOS",
        sa.Column("med_spdata_atendimento_id", sa.Integer(), nullable=True),
    )
    add_column_if_missing(
        "MED_ATENDIMENTOS",
        sa.Column("spdata_atendimento_id", sa.Integer(), nullable=True),
    )
    add_column_if_missing(
        "MED_ATENDIMENTOS",
        sa.Column("cod_atendimento", sa.String(length=50), nullable=True),
    )

    with op.batch_alter_table("MED_ATENDIMENTOS", schema=None) as batch_op:
        batch_op.alter_column(
            "status",
            existing_type=mysql.ENUM("EM_ATENDIMENTO", "ATENDIDO", "FALTOU"),
            type_=sa.String(length=50),
            existing_nullable=False,
            nullable=False,
        )

    op.execute("""
        UPDATE MED_ATENDIMENTOS
        SET status = CASE
            WHEN status = 'EM_ATENDIMENTO' THEN 'em-atendimento'
            WHEN status = 'ATENDIDO' THEN 'atendido'
            WHEN status = 'FALTOU' THEN 'faltou'
            WHEN status = 'em_atendimento' THEN 'em-atendimento'
            ELSE status
        END
    """)

    create_index_if_missing(
        "MED_ATENDIMENTOS",
        "ix_MED_ATENDIMENTOS_med_spdata_atendimento_id",
        ["med_spdata_atendimento_id"],
        unique=True,
    )
    create_index_if_missing(
        "MED_ATENDIMENTOS",
        "ix_MED_ATENDIMENTOS_spdata_atendimento_id",
        ["spdata_atendimento_id"],
    )
    create_index_if_missing(
        "MED_ATENDIMENTOS",
        "ix_MED_ATENDIMENTOS_cod_atendimento",
        ["cod_atendimento"],
    )

    if FK_MED_ATENDIMENTOS_SPDATA not in table_foreign_keys("MED_ATENDIMENTOS"):
        with op.batch_alter_table("MED_ATENDIMENTOS", schema=None) as batch_op:
            batch_op.create_foreign_key(
                FK_MED_ATENDIMENTOS_SPDATA,
                "MED_SPDATA_ATENDIMENTOS",
                ["med_spdata_atendimento_id"],
                ["id"],
            )

    add_column_if_missing(
        "atendimentos",
        sa.Column("spdata_atendimento_id", sa.Integer(), nullable=True),
    )
    create_index_if_missing(
        "atendimentos",
        "ix_atendimentos_spdata_atendimento_id",
        ["spdata_atendimento_id"],
    )

    with op.batch_alter_table("atendimentos", schema=None) as batch_op:
        batch_op.alter_column(
            "hora_fim",
            existing_type=mysql.TIME(),
            nullable=True,
        )


def downgrade():
    with op.batch_alter_table("atendimentos", schema=None) as batch_op:
        batch_op.alter_column(
            "hora_fim",
            existing_type=mysql.TIME(),
            nullable=False,
        )

    drop_index_if_exists("atendimentos", "ix_atendimentos_spdata_atendimento_id")
    if "spdata_atendimento_id" in table_columns("atendimentos"):
        with op.batch_alter_table("atendimentos", schema=None) as batch_op:
            batch_op.drop_column("spdata_atendimento_id")

    if FK_MED_ATENDIMENTOS_SPDATA in table_foreign_keys("MED_ATENDIMENTOS"):
        with op.batch_alter_table("MED_ATENDIMENTOS", schema=None) as batch_op:
            batch_op.drop_constraint(FK_MED_ATENDIMENTOS_SPDATA, type_="foreignkey")

    drop_index_if_exists("MED_ATENDIMENTOS", "ix_MED_ATENDIMENTOS_cod_atendimento")
    drop_index_if_exists("MED_ATENDIMENTOS", "ix_MED_ATENDIMENTOS_spdata_atendimento_id")
    drop_index_if_exists("MED_ATENDIMENTOS", "ix_MED_ATENDIMENTOS_med_spdata_atendimento_id")

    op.execute("""
        UPDATE MED_ATENDIMENTOS
        SET status = CASE
            WHEN status = 'em-atendimento' THEN 'EM_ATENDIMENTO'
            WHEN status = 'atendido' THEN 'ATENDIDO'
            WHEN status = 'faltou' THEN 'FALTOU'
            ELSE status
        END
    """)

    with op.batch_alter_table("MED_ATENDIMENTOS", schema=None) as batch_op:
        batch_op.alter_column(
            "status",
            existing_type=sa.String(length=50),
            type_=mysql.ENUM("EM_ATENDIMENTO", "ATENDIDO", "FALTOU"),
            existing_nullable=False,
            nullable=False,
        )

    columns = table_columns("MED_ATENDIMENTOS")
    with op.batch_alter_table("MED_ATENDIMENTOS", schema=None) as batch_op:
        if "cod_atendimento" in columns:
            batch_op.drop_column("cod_atendimento")
        if "spdata_atendimento_id" in columns:
            batch_op.drop_column("spdata_atendimento_id")
        if "med_spdata_atendimento_id" in columns:
            batch_op.drop_column("med_spdata_atendimento_id")

    if table_exists("MED_SPDATA_ATENDIMENTOS"):
        op.drop_table("MED_SPDATA_ATENDIMENTOS")
