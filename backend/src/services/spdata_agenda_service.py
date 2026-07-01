from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import select

from src.models.db.handler_fb_db import ConnectionDBFireBird
from src.models.model_mydsystem.med_spdata_agenda_model import MedSpdataAgenda
from src.models.model_mydsystem.med_spdata_convenios_model import MedSpdataConvenio
from src.settings.extensions import db


def normalizar_valor(valor):
    if valor is None:
        return None
    if isinstance(valor, Decimal):
        return int(valor) if valor == int(valor) else float(valor)
    if isinstance(valor, datetime):
        return valor
    if isinstance(valor, date):
        return valor
    if isinstance(valor, time):
        return valor.replace(microsecond=0)
    return valor


def normalizar_texto(valor, limite=None):
    if valor is None:
        return None

    texto = str(valor).strip()
    if limite:
        texto = texto[:limite]

    return texto or None


def normalizar_int(valor):
    if valor is None:
        return None

    texto = normalizar_texto(valor)
    if not texto:
        return None

    try:
        return int(valor)
    except (TypeError, ValueError):
        try:
            return int(float(texto.replace(",", ".")))
        except (TypeError, ValueError):
            return None


def normalizar_data(valor):
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    return datetime.fromisoformat(str(valor)[:10]).date()


def normalizar_hora(valor):
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor.time().replace(microsecond=0)
    if isinstance(valor, time):
        return valor.replace(microsecond=0)

    texto = str(valor).strip()
    if not texto:
        return None

    if texto.isdigit():
        texto = texto.zfill(4)
        return time(int(texto[:2]), int(texto[2:4]))

    if len(texto) == 5:
        return time.fromisoformat(texto)
    if len(texto) >= 8:
        return time.fromisoformat(texto[:8])

    return None


def row_para_dict(row, nomes_colunas):
    return {
        nome: normalizar_valor(valor)
        for nome, valor in zip(nomes_colunas, row)
    }


def buscar_convenios_locais(codigos_spdata):
    codigos = sorted({
        codigo
        for codigo in (normalizar_int(codigo) for codigo in codigos_spdata)
        if codigo is not None
    })
    if not codigos:
        return {}

    rows = db.session.execute(
        select(MedSpdataConvenio.codigo_spdata, MedSpdataConvenio.nome).where(
            MedSpdataConvenio.codigo_spdata.in_(codigos)
        )
    ).all()

    return {
        codigo: nome
        for codigo, nome in rows
        if normalizar_texto(nome)
    }


def buscar_agenda_spdata(data_ini, data_fim):
    sql = """
        SELECT
            ID AS SPDATA_AGENDA_ID,
            REGISTRO AS REGISTRO,
            GRV_ATE AS GRV_ATE,
            NOME AS MEDICO,
            CRM AS CRM,
            CRM_ATEND AS CRM_ATEND,
            DATA AS DATA_AGENDA,
            HORA AS HORA_AGENDA,
            HR_AGE AS HR_AGE,
            PACIENTE AS PACIENTE,
            CPF AS CPF,
            PRONT AS PRONTUARIO,
            CONV AS ID_CONVENIO_SPDATA,
            ESPEC AS ESPECIALIDADE,
            FONE AS TELEFONE,
            CELULAR AS CELULAR,
            EMAIL AS EMAIL,
            DATA_NASCIMENTO AS DATA_NASCIMENTO,
            ATENDIDO AS ATENDIDO_SPDATA,
            ID_RICADPAC AS ID_PACIENTE_SPDATA,
            OBS AS OBS
        FROM REPACAGD
        WHERE CAST(DATA AS DATE) BETWEEN ? AND ?
        ORDER BY DATA, HORA, PACIENTE
    """

    with ConnectionDBFireBird() as connection:
        cursor = connection.cursor()
        cursor.execute(sql, (data_ini, data_fim))
        nomes_colunas = [desc[0].strip().upper() for desc in cursor.description]
        return [row_para_dict(row, nomes_colunas) for row in cursor.fetchall()]


def sincronizar_agenda_spdata(data_ini, data_fim):
    dados_spdata = buscar_agenda_spdata(data_ini, data_fim)
    ids_spdata = [
        normalizar_int(item.get("SPDATA_AGENDA_ID"))
        for item in dados_spdata
        if item.get("SPDATA_AGENDA_ID") is not None
    ]
    convenios_por_codigo = buscar_convenios_locais(
        item.get("ID_CONVENIO_SPDATA")
        for item in dados_spdata
    )

    existentes = {}
    if ids_spdata:
        registros = db.session.execute(
            select(MedSpdataAgenda).where(
                MedSpdataAgenda.spdata_agenda_id.in_(ids_spdata)
            )
        ).scalars().all()
        existentes = {registro.spdata_agenda_id: registro for registro in registros}

    total_criados = 0
    total_atualizados = 0

    for item in dados_spdata:
        spdata_agenda_id = normalizar_int(item.get("SPDATA_AGENDA_ID"))
        paciente = normalizar_texto(item.get("PACIENTE"), 255)
        data_agenda = normalizar_data(item.get("DATA_AGENDA"))

        if not spdata_agenda_id or not paciente or not data_agenda:
            continue

        registro = existentes.get(spdata_agenda_id)
        if registro is None:
            registro = MedSpdataAgenda(
                spdata_agenda_id=spdata_agenda_id,
                paciente=paciente,
                data_agenda=data_agenda,
            )
            db.session.add(registro)
            existentes[spdata_agenda_id] = registro
            total_criados += 1
        else:
            total_atualizados += 1

        id_convenio = normalizar_int(item.get("ID_CONVENIO_SPDATA"))
        registro.registro = normalizar_texto(item.get("REGISTRO"), 50)
        registro.grv_ate = normalizar_int(item.get("GRV_ATE"))
        registro.crm = normalizar_texto(item.get("CRM"), 50)
        registro.crm_atend = normalizar_texto(item.get("CRM_ATEND"), 50)
        registro.medico = normalizar_texto(item.get("MEDICO"), 255)
        registro.data_agenda = data_agenda
        registro.hora_agenda = normalizar_hora(item.get("HORA_AGENDA") or item.get("HR_AGE"))
        registro.paciente = paciente
        registro.cpf = normalizar_texto(item.get("CPF"), 20)
        registro.prontuario = normalizar_texto(item.get("PRONTUARIO"), 50)
        registro.id_paciente_spdata = normalizar_int(item.get("ID_PACIENTE_SPDATA"))
        registro.id_convenio_spdata = id_convenio
        registro.convenio = convenios_por_codigo.get(id_convenio)
        registro.especialidade = normalizar_texto(item.get("ESPECIALIDADE"), 120)
        registro.telefone = normalizar_texto(item.get("TELEFONE"), 30)
        registro.celular = normalizar_texto(item.get("CELULAR"), 30)
        registro.email = normalizar_texto(item.get("EMAIL"), 255)
        registro.data_nascimento = normalizar_data(item.get("DATA_NASCIMENTO"))
        registro.atendido_spdata = normalizar_texto(item.get("ATENDIDO_SPDATA"), 1)
        registro.obs = normalizar_texto(item.get("OBS"))

    db.session.commit()

    return {
        "lidos": len(dados_spdata),
        "criados": total_criados,
        "atualizados": total_atualizados,
    }
