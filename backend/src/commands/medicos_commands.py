import click

from flask.cli import with_appcontext
from sqlalchemy import or_, select

from src.models.db.handler_fb_db import ConnectionDBFireBird
from src.models.medico_model import Medico
from src.models.usuario_model import Usuario
from src.settings.extensions import db


COLUNAS_MEDICO_SPDATA = [
    "ID",
    "NOME",
    "CNPJ_CPF",
    "CPF",
    "EMAIL",
    "EMAIL_CONSULTORIO",
    "OLD_CRM",
    "OLD_UFCRM",
    "ESP_PRINC",
    "SITUACAO",
    "UF",
]


def normalizar_texto(valor, limite=None):
    if valor is None:
        return None

    valor = str(valor).strip()

    if limite:
        valor = valor[:limite]

    return valor or None


def row_para_dict(row, nomes_colunas):
    return {
        nome: valor
        for nome, valor in zip(nomes_colunas, row)
    }


def buscar_medicos_spdata(spdata_id=None, cpf=None, nome=None):
    colunas = ", ".join(COLUNAS_MEDICO_SPDATA)
    params = []

    if spdata_id is not None:
        where = "ID = ?"
        params.append(spdata_id)
    elif cpf:
        where = "CPF = ? OR CNPJ_CPF = ?"
        params.extend([cpf, cpf])
    elif nome:
        where = "NOME CONTAINING ?"
        params.append(nome)
    else:
        raise click.ClickException("Informe --spdata-id, --cpf ou --nome.")

    sql = f"""
        SELECT {colunas}
        FROM TBPROFIS
        WHERE {where}
        ORDER BY NOME
    """

    with ConnectionDBFireBird() as connection:
        cursor = connection.cursor()
        cursor.execute(sql, tuple(params))
        nomes_colunas = [
            descricao[0].strip().upper()
            for descricao in cursor.description
        ]

        return [
            row_para_dict(row, nomes_colunas)
            for row in cursor.fetchall()
        ]


def exibir_opcoes_medicos(medicos):
    click.echo("Mais de um médico encontrado no SPDATA:")

    for medico in medicos:
        click.echo(
            "  "
            f"ID={medico.get('ID')} | "
            f"NOME={medico.get('NOME')} | "
            f"CPF={medico.get('CPF') or medico.get('CNPJ_CPF')} | "
            f"CRM={medico.get('OLD_CRM') or '-'}"
        )


def email_do_spdata(medico_spdata):
    return normalizar_texto(
        medico_spdata.get("EMAIL_CONSULTORIO") or medico_spdata.get("EMAIL"),
        255,
    )


@click.command("registrar-medico-spdata")
@click.option("--spdata-id", type=int, help="ID do médico na TBPROFIS.")
@click.option("--cpf", help="CPF/CNPJ_CPF do médico na TBPROFIS.")
@click.option("--nome", help="Trecho do nome do médico na TBPROFIS.")
@click.option("--email", help="E-mail de login. Se omitido, usa EMAIL_CONSULTORIO/EMAIL do SPDATA.")
@click.option(
    "--senha",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="Senha inicial do usuário local.",
)
@with_appcontext
def registrar_medico_spdata_command(spdata_id, cpf, nome, email, senha):
    """Registra no banco local um médico existente no SPDATA."""

    filtros = [bool(spdata_id), bool(cpf), bool(nome)]
    if sum(filtros) != 1:
        raise click.ClickException("Use apenas um filtro: --spdata-id, --cpf ou --nome.")

    medicos_spdata = buscar_medicos_spdata(
        spdata_id=spdata_id,
        cpf=cpf,
        nome=nome,
    )

    if not medicos_spdata:
        raise click.ClickException("Médico não encontrado no SPDATA.")

    if len(medicos_spdata) > 1:
        exibir_opcoes_medicos(medicos_spdata)
        raise click.ClickException("Refaça o comando usando --spdata-id para escolher um médico.")

    medico_spdata = medicos_spdata[0]
    spdata_id = int(medico_spdata["ID"])
    nome_completo = normalizar_texto(medico_spdata.get("NOME"), 255)
    documento = normalizar_texto(
        medico_spdata.get("CNPJ_CPF") or medico_spdata.get("CPF"),
        255,
    )
    email = normalizar_texto(email, 255) or email_do_spdata(medico_spdata)

    if not nome_completo:
        raise click.ClickException("Registro do SPDATA não possui NOME.")

    if not documento:
        raise click.ClickException("Registro do SPDATA não possui CNPJ_CPF ou CPF.")

    if not email:
        raise click.ClickException("Informe --email ou preencha EMAIL/EMAIL_CONSULTORIO no SPDATA.")

    try:
        usuario = db.session.execute(
            select(Usuario).where(
                or_(
                    Usuario.email == email,
                    Usuario.cnpj_cpf == documento,
                )
            )
        ).scalars().first()

        if usuario is None:
            usuario = Usuario(
                nome_completo=nome_completo,
                cnpj_cpf=documento,
                email=email,
                senha=senha,
                role="medico",
            )
            db.session.add(usuario)
            db.session.flush()
            usuario_criado = True
        else:
            usuario.nome_completo = nome_completo
            usuario.cnpj_cpf = documento
            usuario.email = email
            usuario.senha = senha
            usuario.role = "medico"
            usuario_criado = False

        medico = db.session.execute(
            select(Medico).where(
                or_(
                    Medico.spdata_id == spdata_id,
                    Medico.usuario_id == usuario.id,
                )
            )
        ).scalars().first()

        crm = normalizar_texto(medico_spdata.get("OLD_CRM"), 20)
        crm_uf = normalizar_texto(
            medico_spdata.get("OLD_UFCRM") or medico_spdata.get("UF"),
            2,
        )
        especialidade = normalizar_texto(medico_spdata.get("ESP_PRINC"), 120)

        if medico is None:
            medico = Medico(
                usuario_id=usuario.id,
                spdata_id=spdata_id,
                crm=crm,
                crm_uf=crm_uf,
                especialidade=especialidade,
                ativo=True,
            )
            db.session.add(medico)
            medico_criado = True
        else:
            medico.usuario_id = usuario.id
            medico.spdata_id = spdata_id
            medico.crm = crm
            medico.crm_uf = crm_uf
            medico.especialidade = especialidade
            medico.ativo = True
            medico_criado = False

        db.session.commit()

    except Exception as exc:
        db.session.rollback()
        raise click.ClickException(f"Falha ao registrar médico: {exc}") from exc

    click.secho("Médico registrado com sucesso.", fg="green")
    click.echo(f"  usuario_id: {usuario.id} ({'criado' if usuario_criado else 'atualizado'})")
    click.echo(f"  medico_id: {medico.id} ({'criado' if medico_criado else 'atualizado'})")
    click.echo(f"  spdata_id: {spdata_id}")
    click.echo(f"  nome: {nome_completo}")
    click.echo(f"  email: {email}")
