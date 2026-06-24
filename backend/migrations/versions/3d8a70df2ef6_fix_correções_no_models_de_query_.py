from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import mysql


revision = "3d8a70df2ef6"
down_revision = "1caef28cb72d"
branch_labels = None
depends_on = None


FK_NAME = "fk_med_atendimentos_spdata_agenda_id"


def table_columns(table_name):
    inspector = inspect(op.get_bind())
    return {column["name"] for column in inspector.get_columns(table_name)}


def table_indexes(table_name):
    inspector = inspect(op.get_bind())
    return {index["name"] for index in inspector.get_indexes(table_name)}


def table_foreign_keys(table_name):
    inspector = inspect(op.get_bind())
    return {fk["name"] for fk in inspector.get_foreign_keys(table_name)}


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


def create_fk_if_missing():
    if FK_NAME in table_foreign_keys("MED_ATENDIMENTOS"):
        return

    with op.batch_alter_table("MED_ATENDIMENTOS", schema=None) as batch_op:
        batch_op.create_foreign_key(
            FK_NAME,
            "MED_SPDATA_AGENDA",
            ["spdata_agenda_id"],
            ["spdata_agenda_id"],
        )


def drop_fk_if_exists():
    if FK_NAME not in table_foreign_keys("MED_ATENDIMENTOS"):
        return

    with op.batch_alter_table("MED_ATENDIMENTOS", schema=None) as batch_op:
        batch_op.drop_constraint(FK_NAME, type_="foreignkey")


def upgrade():
    # Primeiro altera MED_SPDATA_AGENDA, porque MED_ATENDIMENTOS depende dela.
    add_column_if_missing(
        "MED_SPDATA_AGENDA",
        sa.Column("spdata_agenda_id", sa.Integer(), nullable=True),
    )
    add_column_if_missing(
        "MED_SPDATA_AGENDA",
        sa.Column("crm_atend", sa.String(length=50), nullable=True),
    )
    add_column_if_missing(
        "MED_SPDATA_AGENDA",
        sa.Column("convenio", sa.String(length=100), nullable=True),
    )
    add_column_if_missing(
        "MED_SPDATA_AGENDA",
        sa.Column("data_nascimento", sa.Date(), nullable=True),
    )
    add_column_if_missing(
        "MED_SPDATA_AGENDA",
        sa.Column("celular", sa.String(length=30), nullable=True),
    )
    add_column_if_missing(
        "MED_SPDATA_AGENDA",
        sa.Column("email", sa.String(length=255), nullable=True),
    )
    add_column_if_missing(
        "MED_SPDATA_AGENDA",
        sa.Column("obs", sa.Text(), nullable=True),
    )

    # Backfill seguro para bases que já tinham registros antigos.
    op.execute("""
        UPDATE MED_SPDATA_AGENDA
        SET spdata_agenda_id = id
        WHERE spdata_agenda_id IS NULL
    """)

    with op.batch_alter_table("MED_SPDATA_AGENDA", schema=None) as batch_op:
        batch_op.alter_column(
            "spdata_agenda_id",
            existing_type=mysql.INTEGER(),
            nullable=False,
        )
        batch_op.alter_column(
            "id_paciente_spdata",
            existing_type=mysql.INTEGER(),
            nullable=True,
        )
        batch_op.alter_column(
            "medico",
            existing_type=mysql.VARCHAR(collation="utf8mb4_unicode_ci", length=255),
            nullable=True,
        )
        batch_op.alter_column(
            "data_agenda",
            existing_type=mysql.DATETIME(),
            type_=sa.Date(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "hora_agenda",
            existing_type=mysql.TIME(),
            nullable=True,
        )
        batch_op.alter_column(
            "cpf",
            existing_type=mysql.VARCHAR(collation="utf8mb4_unicode_ci", length=20),
            nullable=True,
        )
        batch_op.alter_column(
            "prontuario",
            existing_type=mysql.INTEGER(),
            type_=sa.String(length=50),
            nullable=True,
        )
        batch_op.alter_column(
            "atendido_spdata",
            existing_type=mysql.VARCHAR(collation="utf8mb4_unicode_ci", length=50),
            type_=sa.String(length=1),
            nullable=True,
        )

    create_index_if_missing(
        "MED_SPDATA_AGENDA",
        "ix_MED_SPDATA_AGENDA_spdata_agenda_id",
        ["spdata_agenda_id"],
        unique=True,
    )
    create_index_if_missing(
        "MED_SPDATA_AGENDA",
        "ix_MED_SPDATA_AGENDA_atendido_spdata",
        ["atendido_spdata"],
    )
    create_index_if_missing(
        "MED_SPDATA_AGENDA",
        "ix_MED_SPDATA_AGENDA_cpf",
        ["cpf"],
    )
    create_index_if_missing(
        "MED_SPDATA_AGENDA",
        "ix_MED_SPDATA_AGENDA_data_agenda",
        ["data_agenda"],
    )
    create_index_if_missing(
        "MED_SPDATA_AGENDA",
        "ix_MED_SPDATA_AGENDA_id_paciente_spdata",
        ["id_paciente_spdata"],
    )
    create_index_if_missing(
        "MED_SPDATA_AGENDA",
        "ix_MED_SPDATA_AGENDA_paciente",
        ["paciente"],
    )
    create_index_if_missing(
        "MED_SPDATA_AGENDA",
        "ix_MED_SPDATA_AGENDA_prontuario",
        ["prontuario"],
    )

    # Depois altera MED_ATENDIMENTOS.
    add_column_if_missing(
        "MED_ATENDIMENTOS",
        sa.Column("spdata_agenda_id", sa.Integer(), nullable=True),
    )
    add_column_if_missing(
        "MED_ATENDIMENTOS",
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    add_column_if_missing(
        "MED_ATENDIMENTOS",
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.execute("""
        UPDATE MED_ATENDIMENTOS
        SET created_at = COALESCE(created_at, started_at, NOW()),
            updated_at = COALESCE(updated_at, started_at, NOW())
    """)

    # Tenta vincular registros antigos por data, hora e CPF.
    op.execute("""
        UPDATE MED_ATENDIMENTOS M
        INNER JOIN MED_SPDATA_AGENDA S
            ON S.DATA_AGENDA = M.DATA_AGENDA
           AND S.HORA_AGENDA = M.HORA_AGENDA
           AND S.CPF = M.CPF
        SET M.SPDATA_AGENDA_ID = S.SPDATA_AGENDA_ID
        WHERE M.SPDATA_AGENDA_ID IS NULL
          AND M.CPF IS NOT NULL
          AND M.CPF <> ''
    """)

    # Fallback por data, hora e prontuario.
    op.execute("""
        UPDATE MED_ATENDIMENTOS M
        INNER JOIN MED_SPDATA_AGENDA S
            ON S.DATA_AGENDA = M.DATA_AGENDA
           AND S.HORA_AGENDA = M.HORA_AGENDA
           AND S.PRONTUARIO = M.PRONTUARIO
        SET M.SPDATA_AGENDA_ID = S.SPDATA_AGENDA_ID
        WHERE M.SPDATA_AGENDA_ID IS NULL
          AND M.PRONTUARIO IS NOT NULL
          AND M.PRONTUARIO <> ''
    """)

    with op.batch_alter_table("MED_ATENDIMENTOS", schema=None) as batch_op:
        batch_op.alter_column(
            "id_medico_spdata",
            existing_type=mysql.INTEGER(),
            nullable=True,
        )
        batch_op.alter_column(
            "medico",
            existing_type=mysql.VARCHAR(collation="utf8mb4_unicode_ci", length=255),
            nullable=True,
        )
        batch_op.alter_column(
            "data_agenda",
            existing_type=mysql.DATETIME(),
            type_=sa.Date(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "hora_agenda",
            existing_type=mysql.TIME(),
            nullable=True,
        )
        batch_op.alter_column(
            "id_paciente_spdata",
            existing_type=mysql.INTEGER(),
            nullable=True,
        )
        batch_op.alter_column(
            "cpf",
            existing_type=mysql.VARCHAR(collation="utf8mb4_unicode_ci", length=20),
            nullable=True,
        )
        batch_op.alter_column(
            "prontuario",
            existing_type=mysql.INTEGER(),
            type_=sa.String(length=50),
            nullable=True,
        )
        batch_op.alter_column(
            "finished_at",
            existing_type=mysql.DATETIME(),
            nullable=True,
        )
        batch_op.alter_column(
            "created_at",
            existing_type=mysql.DATETIME(),
            nullable=False,
        )
        batch_op.alter_column(
            "updated_at",
            existing_type=mysql.DATETIME(),
            nullable=False,
        )

    create_index_if_missing(
        "MED_ATENDIMENTOS",
        "ix_MED_ATENDIMENTOS_spdata_agenda_id",
        ["spdata_agenda_id"],
    )
    create_index_if_missing(
        "MED_ATENDIMENTOS",
        "ix_MED_ATENDIMENTOS_cpf",
        ["cpf"],
    )
    create_index_if_missing(
        "MED_ATENDIMENTOS",
        "ix_MED_ATENDIMENTOS_data_agenda",
        ["data_agenda"],
    )
    create_index_if_missing(
        "MED_ATENDIMENTOS",
        "ix_MED_ATENDIMENTOS_id_medico_spdata",
        ["id_medico_spdata"],
    )
    create_index_if_missing(
        "MED_ATENDIMENTOS",
        "ix_MED_ATENDIMENTOS_id_paciente_spdata",
        ["id_paciente_spdata"],
    )
    create_index_if_missing(
        "MED_ATENDIMENTOS",
        "ix_MED_ATENDIMENTOS_prontuario",
        ["prontuario"],
    )
    create_index_if_missing(
        "MED_ATENDIMENTOS",
        "ix_MED_ATENDIMENTOS_status",
        ["status"],
    )

    # Só agora cria a FK, quando a coluna referenciada já existe e tem índice único.
    create_fk_if_missing()


def downgrade():
    drop_fk_if_exists()

    drop_index_if_exists("MED_ATENDIMENTOS", "ix_MED_ATENDIMENTOS_status")
    drop_index_if_exists("MED_ATENDIMENTOS", "ix_MED_ATENDIMENTOS_spdata_agenda_id")
    drop_index_if_exists("MED_ATENDIMENTOS", "ix_MED_ATENDIMENTOS_prontuario")
    drop_index_if_exists("MED_ATENDIMENTOS", "ix_MED_ATENDIMENTOS_id_paciente_spdata")
    drop_index_if_exists("MED_ATENDIMENTOS", "ix_MED_ATENDIMENTOS_id_medico_spdata")
    drop_index_if_exists("MED_ATENDIMENTOS", "ix_MED_ATENDIMENTOS_data_agenda")
    drop_index_if_exists("MED_ATENDIMENTOS", "ix_MED_ATENDIMENTOS_cpf")

    with op.batch_alter_table("MED_ATENDIMENTOS", schema=None) as batch_op:
        batch_op.alter_column(
            "finished_at",
            existing_type=mysql.DATETIME(),
            nullable=False,
        )
        batch_op.alter_column(
            "prontuario",
            existing_type=sa.String(length=50),
            type_=mysql.INTEGER(),
            nullable=False,
        )
        batch_op.alter_column(
            "cpf",
            existing_type=mysql.VARCHAR(collation="utf8mb4_unicode_ci", length=20),
            nullable=False,
        )
        batch_op.alter_column(
            "id_paciente_spdata",
            existing_type=mysql.INTEGER(),
            nullable=False,
        )
        batch_op.alter_column(
            "hora_agenda",
            existing_type=mysql.TIME(),
            nullable=False,
        )
        batch_op.alter_column(
            "data_agenda",
            existing_type=sa.Date(),
            type_=mysql.DATETIME(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "medico",
            existing_type=mysql.VARCHAR(collation="utf8mb4_unicode_ci", length=255),
            nullable=False,
        )
        batch_op.alter_column(
            "id_medico_spdata",
            existing_type=mysql.INTEGER(),
            nullable=False,
        )

    columns = table_columns("MED_ATENDIMENTOS")
    with op.batch_alter_table("MED_ATENDIMENTOS", schema=None) as batch_op:
        if "updated_at" in columns:
            batch_op.drop_column("updated_at")
        if "created_at" in columns:
            batch_op.drop_column("created_at")
        if "spdata_agenda_id" in columns:
            batch_op.drop_column("spdata_agenda_id")

    drop_index_if_exists("MED_SPDATA_AGENDA", "ix_MED_SPDATA_AGENDA_spdata_agenda_id")
    drop_index_if_exists("MED_SPDATA_AGENDA", "ix_MED_SPDATA_AGENDA_prontuario")
    drop_index_if_exists("MED_SPDATA_AGENDA", "ix_MED_SPDATA_AGENDA_paciente")
    drop_index_if_exists("MED_SPDATA_AGENDA", "ix_MED_SPDATA_AGENDA_id_paciente_spdata")
    drop_index_if_exists("MED_SPDATA_AGENDA", "ix_MED_SPDATA_AGENDA_data_agenda")
    drop_index_if_exists("MED_SPDATA_AGENDA", "ix_MED_SPDATA_AGENDA_cpf")
    drop_index_if_exists("MED_SPDATA_AGENDA", "ix_MED_SPDATA_AGENDA_atendido_spdata")

    with op.batch_alter_table("MED_SPDATA_AGENDA", schema=None) as batch_op:
        batch_op.alter_column(
            "atendido_spdata",
            existing_type=sa.String(length=1),
            type_=mysql.VARCHAR(collation="utf8mb4_unicode_ci", length=50),
            nullable=False,
        )
        batch_op.alter_column(
            "prontuario",
            existing_type=sa.String(length=50),
            type_=mysql.INTEGER(),
            nullable=False,
        )
        batch_op.alter_column(
            "cpf",
            existing_type=mysql.VARCHAR(collation="utf8mb4_unicode_ci", length=20),
            nullable=False,
        )
        batch_op.alter_column(
            "hora_agenda",
            existing_type=mysql.TIME(),
            nullable=False,
        )
        batch_op.alter_column(
            "data_agenda",
            existing_type=sa.Date(),
            type_=mysql.DATETIME(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "medico",
            existing_type=mysql.VARCHAR(collation="utf8mb4_unicode_ci", length=255),
            nullable=False,
        )
        batch_op.alter_column(
            "id_paciente_spdata",
            existing_type=mysql.INTEGER(),
            nullable=False,
        )

    columns = table_columns("MED_SPDATA_AGENDA")
    with op.batch_alter_table("MED_SPDATA_AGENDA", schema=None) as batch_op:
        if "obs" in columns:
            batch_op.drop_column("obs")
        if "email" in columns:
            batch_op.drop_column("email")
        if "celular" in columns:
            batch_op.drop_column("celular")
        if "data_nascimento" in columns:
            batch_op.drop_column("data_nascimento")
        if "convenio" in columns:
            batch_op.drop_column("convenio")
        if "crm_atend" in columns:
            batch_op.drop_column("crm_atend")
        if "spdata_agenda_id" in columns:
            batch_op.drop_column("spdata_agenda_id")
