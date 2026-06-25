from sqlalchemy import or_, select

from src.models.db.handler_fb_db import ConnectionDBFireBird
from src.models.medico_model import Medico
from src.models.usuario_model import Usuario
from src.settings.extensions import db


COLUNAS_MEDICO_SPDATA = [
    "p.ID",
    "p.NOME",
    "p.CNPJ_CPF",
    "p.CPF",
    "p.EMAIL",
    "p.EMAIL_CONSULTORIO",
    "p.OLD_CRM",
    "p.OLD_UFCRM",
    "p.ESP_PRINC",
    "p.SITUACAO",
    "p.UF",
    "(SELECT FIRST 1 cb.COD FROM TBCBOPRO cb WHERE cb.ID_TBPROFIS = p.ID ORDER BY cb.COD) AS CRM_ATENDIMENTO_SPDATA",
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
        where = "p.ID = ?"
        params.append(spdata_id)
    elif cpf:
        where = "p.CPF = ? OR p.CNPJ_CPF = ?"
        params.extend([cpf, cpf])
    elif nome:
        where = "p.NOME CONTAINING ?"
        params.append(nome)
    else:
        raise ValueError("Informe spdata_id, cpf ou nome para buscar médico no SPDATA.")

    sql = f"""
        SELECT {colunas}
        FROM TBPROFIS p
        WHERE {where}
        ORDER BY p.NOME
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


def email_do_spdata(medico_spdata):
    return normalizar_texto(
        medico_spdata.get("EMAIL_CONSULTORIO") or medico_spdata.get("EMAIL"),
        255,
    )


def dados_medico_normalizados(medico_spdata, email=None, crm_atendimento_spdata=None):
    spdata_id = int(medico_spdata["ID"])
    nome_completo = normalizar_texto(medico_spdata.get("NOME"), 255)
    documento = normalizar_texto(
        medico_spdata.get("CNPJ_CPF") or medico_spdata.get("CPF"),
        255,
    )
    email = normalizar_texto(email, 255) or email_do_spdata(medico_spdata)
    crm = normalizar_texto(medico_spdata.get("OLD_CRM"), 20)
    crm_atendimento_spdata = normalizar_texto(
        crm_atendimento_spdata or medico_spdata.get("CRM_ATENDIMENTO_SPDATA") or crm,
        50,
    )
    crm_uf = normalizar_texto(
        medico_spdata.get("OLD_UFCRM") or medico_spdata.get("UF"),
        2,
    )
    especialidade = normalizar_texto(medico_spdata.get("ESP_PRINC"), 120)

    if not nome_completo:
        raise ValueError("Registro do SPDATA não possui NOME.")
    if not documento:
        raise ValueError("Registro do SPDATA não possui CNPJ_CPF ou CPF.")
    if not email:
        raise ValueError("Informe email ou preencha EMAIL/EMAIL_CONSULTORIO no SPDATA.")

    return {
        "spdata_id": spdata_id,
        "nome_completo": nome_completo,
        "documento": documento,
        "email": email,
        "crm": crm,
        "crm_atendimento_spdata": crm_atendimento_spdata,
        "crm_uf": crm_uf,
        "especialidade": especialidade,
    }


def upsert_usuario_medico_spdata(medico_spdata, email=None, senha=None, crm_atendimento_spdata=None):
    dados = dados_medico_normalizados(
        medico_spdata,
        email=email,
        crm_atendimento_spdata=crm_atendimento_spdata,
    )

    usuario = db.session.execute(
        select(Usuario).where(
            or_(
                Usuario.email == dados["email"],
                Usuario.cnpj_cpf == dados["documento"],
            )
        )
    ).scalars().first()

    if usuario is None:
        usuario = Usuario(
            nome_completo=dados["nome_completo"],
            cnpj_cpf=dados["documento"],
            email=dados["email"],
            senha=senha,
            role="medico",
        )
        db.session.add(usuario)
        db.session.flush()
        usuario_criado = True
    else:
        usuario.nome_completo = dados["nome_completo"]
        usuario.cnpj_cpf = dados["documento"]
        usuario.email = dados["email"]
        if senha is not None:
            usuario.senha = senha
        usuario.role = "medico"
        usuario_criado = False

    medico = db.session.execute(
        select(Medico).where(
            or_(
                Medico.spdata_id == dados["spdata_id"],
                Medico.usuario_id == usuario.id,
            )
        )
    ).scalars().first()

    if medico is None:
        medico = Medico(
            usuario_id=usuario.id,
            spdata_id=dados["spdata_id"],
            crm=dados["crm"],
            crm_atendimento_spdata=dados["crm_atendimento_spdata"],
            crm_uf=dados["crm_uf"],
            especialidade=dados["especialidade"],
            ativo=True,
        )
        db.session.add(medico)
        medico_criado = True
    else:
        medico.usuario_id = usuario.id
        medico.spdata_id = dados["spdata_id"]
        medico.crm = dados["crm"]
        medico.crm_atendimento_spdata = dados["crm_atendimento_spdata"]
        medico.crm_uf = dados["crm_uf"]
        medico.especialidade = dados["especialidade"]
        medico.ativo = True
        medico_criado = False

    db.session.commit()

    return {
        "usuario": usuario,
        "medico": medico,
        "usuario_criado": usuario_criado,
        "medico_criado": medico_criado,
        "dados": dados,
    }
