from datetime import date, datetime, time
from decimal import Decimal

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import select

from src.models.db.handler_fb_db import ConnectionDBFireBird
from src.models.model_mydsystem.med_atendimentos_model import MedAtendimentos
from src.security.decorators import roles_required
from src.settings.extensions import db


check_in_bp = Blueprint("check_in", __name__, url_prefix="/check_in")

MAX_PAGE_SIZE = 100

STATUS_VALIDOS = {
    "agendado",
    "em-espera",
    "em-atendimento",
    "atendido",
    "faltou",
}

STATUS_LOCAL_ALIASES = {
    "EM_ATENDIMENTO": "em-atendimento",
    "em_atendimento": "em-atendimento",
    "em-atendimento": "em-atendimento",
    "ATENDIDO": "atendido",
    "atendido": "atendido",
    "FALTOU": "faltou",
    "faltou": "faltou",
}

RESUMO_KEYS = {
    "agendado": "agendados",
    "em-espera": "emEspera",
    "em-atendimento": "emAtendimento",
    "atendido": "atendidos",
    "faltou": "faltas",
}


def normalizar_valor(valor):
    if valor is None:
        return None
    if isinstance(valor, Decimal):
        return float(valor)
    if isinstance(valor, datetime):
        return valor.isoformat()
    if isinstance(valor, date):
        return valor.isoformat()
    if isinstance(valor, time):
        return valor.strftime("%H:%M")
    return valor


def normalizar_texto(valor):
    if valor is None:
        return ""
    return str(valor).strip()


def normalizar_status_local(status):
    return STATUS_LOCAL_ALIASES.get(normalizar_texto(status))


def status_repacagd(valor):
    atendido = normalizar_texto(valor).upper()
    if atendido == "S":
        return "em-espera"
    if atendido == "N":
        return "agendado"
    return "desconhecido"


def status_para_resumo():
    return {
        "agendados": 0,
        "emEspera": 0,
        "emAtendimento": 0,
        "atendidos": 0,
        "faltas": 0,
        "desconhecidos": 0,
    }


def parse_int_param(nome, default, minimo=1, maximo=None):
    valor = request.args.get(nome, default=default, type=int)
    valor = max(valor or default, minimo)
    if maximo is not None:
        valor = min(valor, maximo)
    return valor


def parse_data_param():
    valor = request.args.get("data")
    if not valor:
        return date.today()
    return datetime.fromisoformat(str(valor)[:10]).date()


def row_para_dict(row, nomes_colunas):
    return {
        nome: normalizar_valor(valor)
        for nome, valor in zip(nomes_colunas, row)
    }


def buscar_agendamentos_firebird(data_ref, medico=None, q=None):
    where = ["CAST(DATA AS DATE) = ?"]
    params = [data_ref]

    medico = normalizar_texto(medico)
    if medico:
        where.append(
            "("
            "CAST(CRM_ATEND AS VARCHAR(50)) = ? "
            "OR CAST(CRM AS VARCHAR(50)) = ? "
            "OR NOME = ?"
            ")"
        )
        params.extend([medico, medico, medico])

    q = normalizar_texto(q)
    if q:
        where.append(
            "(PACIENTE CONTAINING ? "
            "OR CPF CONTAINING ? "
            "OR PRONT CONTAINING ? "
            "OR CAST(REGISTRO AS VARCHAR(50)) CONTAINING ?)"
        )
        params.extend([q, q, q, q])

    sql = f"""
        SELECT
            ID AS ID_AGENDAMENTO,
            REGISTRO AS REGISTRO,
            GRV_ATE AS GRV_ATE,
            NOME AS MEDICO,
            CRM AS CRM,
            CRM_ATEND AS CRM_ATEND,
            DATA AS DATA,
            HORA AS HORA,
            HR_AGE AS HR_AGE,
            PACIENTE AS PACIENTE,
            CPF AS CPF,
            PRONT AS PRONTUARIO,
            CONV AS CONVENIO,
            FONE AS FONE,
            CELULAR AS CELULAR,
            EMAIL AS EMAIL,
            ESPEC AS ESPECIALIDADE,
            UNIDADE AS UNIDADE,
            RETORNO AS RETORNO,
            TP_AGE AS TIPO_AGENDA,
            PROC_SOL AS PROCEDIMENTO_SOLICITADO,
            PROCED AS PROCEDIMENTO,
            OBS AS OBS,
            DATA_NASCIMENTO AS DATA_NASCIMENTO,
            ATENDIDO AS ATENDIDO,
            ID_RICADPAC AS ID_PACIENTE_SPDATA,
            DATA_HORA_AGENDAMENTO AS DATA_HORA_AGENDAMENTO
        FROM REPACAGD
        WHERE {' AND '.join(where)}
        ORDER BY DATA, HORA, PACIENTE
    """

    with ConnectionDBFireBird() as con:
        cursor = con.cursor()
        cursor.execute(sql, tuple(params))
        nomes_colunas = [desc[0].strip().upper() for desc in cursor.description]
        return [row_para_dict(row, nomes_colunas) for row in cursor.fetchall()]


def buscar_atendimentos_firebird(data_ref):
    sql = """
        SELECT
            a.ID AS ID_ATENDIMENTO,
            a.COD_ATENDIMENTO AS REGISTRO,
            a.COD_ATENDIMENTO AS COD_ATENDIMENTO,
            a.ID_RICADPAC AS ID_PACIENTE_SPDATA,
            CAST(a.DATA_HORA_ENTRADA AS DATE) AS DATA,
            CAST(a.DATA_HORA_ENTRADA AS TIME) AS HORA,
            a.DATA_HORA_ENTRADA AS DATA_HORA_AGENDAMENTO,
            a.DATA_HORA_ALTA_MEDICA AS DATA_HORA_ALTA_MEDICA,
            a.OBS_ATENDIMENTO AS OBS,
            a.ID_TBCONVEN AS ID_CONVENIO_SPDATA,
            COALESCE(convenio.NOME, CAST(a.ID_TBCONVEN AS VARCHAR(50))) AS CONVENIO,
            a.ID_TBCENCUS AS UNIDADE,

            paciente.PRONT AS PRONTUARIO,
            paciente.NOME AS PACIENTE,
            paciente.NASC AS DATA_NASCIMENTO,
            paciente.CELULAR AS CELULAR,
            paciente.EMAIL AS EMAIL,
            paciente.CPF AS CPF,
            paciente.ENDERECO AS ENDERECO,

            medico.NOME AS MEDICO,
            tb.COD AS CRM,
            tb.COD AS CRM_ATEND,

            CAST(NULL AS INTEGER) AS ID_AGENDAMENTO,
            CAST(NULL AS INTEGER) AS GRV_ATE,
            CAST(NULL AS VARCHAR(30)) AS FONE,
            CAST(NULL AS VARCHAR(120)) AS ESPECIALIDADE,
            CAST(NULL AS VARCHAR(50)) AS RETORNO,
            CAST(NULL AS VARCHAR(50)) AS TIPO_AGENDA,
            CAST(NULL AS VARCHAR(255)) AS PROCEDIMENTO_SOLICITADO,
            CAST(NULL AS VARCHAR(255)) AS PROCEDIMENTO,
            'S' AS ATENDIDO,
            'S' AS TEM_ATENDIMENTO
        FROM ATCABECATEND a
        INNER JOIN RICADPAC paciente
            ON paciente.ID = a.ID_RICADPAC
        INNER JOIN TBCBOPRO tb
            ON a.ID_TBCBOPRO_ATENDIMENTO = tb.ID
        INNER JOIN TBPROFIS medico
            ON tb.ID_TBPROFIS = medico.ID
        LEFT JOIN TBCONVEN convenio
            ON convenio.COD = a.ID_TBCONVEN
        WHERE a.ID_TBCENCUS = 203
          AND CAST(a.DATA_HORA_ENTRADA AS DATE) = ?
        ORDER BY a.DATA_HORA_ENTRADA, paciente.NOME
    """

    with ConnectionDBFireBird() as con:
        cursor = con.cursor()
        cursor.execute(sql, (data_ref,))
        nomes_colunas = [desc[0].strip().upper() for desc in cursor.description]
        return [row_para_dict(row, nomes_colunas) for row in cursor.fetchall()]


def chave_registro(row):
    return normalizar_texto(row.get("REGISTRO") or row.get("COD_ATENDIMENTO"))


def preencher_vazios(base, extra):
    merged = dict(base)
    for key, value in extra.items():
        if value is None:
            continue
        if normalizar_texto(merged.get(key)):
            continue
        merged[key] = value
    return merged


def mesclar_agenda_atendimentos(rows_agenda, rows_atendimentos):
    por_registro = {}
    sem_registro = []

    for row in rows_agenda:
        key = chave_registro(row)
        if key:
            por_registro[key] = row
        else:
            sem_registro.append(row)

    for row in rows_atendimentos:
        key = chave_registro(row)
        row["TEM_ATENDIMENTO"] = "S"
        if not key:
            sem_registro.append(row)
            continue

        if key in por_registro:
            merged = preencher_vazios(por_registro[key], row)
            merged["TEM_ATENDIMENTO"] = "S"
            merged["ID_ATENDIMENTO"] = row.get("ID_ATENDIMENTO")
            merged["DATA_HORA_ALTA_MEDICA"] = row.get("DATA_HORA_ALTA_MEDICA")
            por_registro[key] = merged
        else:
            por_registro[key] = row

    return [*por_registro.values(), *sem_registro]


def filtrar_rows(rows, medico=None, q=None):
    medico = normalizar_texto(medico)
    q = normalizar_texto(q).casefold()
    filtrados = []

    for row in rows:
        if medico:
            medicos_possiveis = {
                normalizar_texto(row.get("CRM_ATEND")),
                normalizar_texto(row.get("CRM")),
                normalizar_texto(row.get("MEDICO")),
            }
            if medico not in medicos_possiveis:
                continue

        if q:
            campos_busca = [
                row.get("PACIENTE"),
                row.get("CPF"),
                row.get("PRONTUARIO"),
                row.get("REGISTRO"),
                row.get("COD_ATENDIMENTO"),
            ]
            texto = " ".join(normalizar_texto(campo).casefold() for campo in campos_busca)
            if q not in texto:
                continue

        filtrados.append(row)

    return filtrados


def buscar_status_local(registros):
    registros = [normalizar_texto(registro) for registro in registros if normalizar_texto(registro)]
    if not registros:
        return {}

    rows = db.session.execute(
        select(MedAtendimentos).where(MedAtendimentos.cod_atendimento.in_(registros))
    ).scalars().all()

    status_por_registro = {}
    for row in rows:
        cod_atendimento = normalizar_texto(row.cod_atendimento)
        status = normalizar_status_local(row.status)
        if cod_atendimento and status and cod_atendimento not in status_por_registro:
            status_por_registro[cod_atendimento] = {
                "status": status,
                "medsystemAtendimentoId": row.id,
            }

    return status_por_registro


def item_para_frontend(row, status_local):
    registro = normalizar_texto(row.get("REGISTRO"))
    local = status_local.get(registro)
    if local:
        status = local["status"]
    elif normalizar_texto(row.get("TEM_ATENDIMENTO")).upper() == "S":
        status = "em-espera"
    else:
        status = status_repacagd(row.get("ATENDIDO"))
    crm_atendimento = normalizar_texto(row.get("CRM_ATEND"))
    crm = normalizar_texto(row.get("CRM"))

    return {
        "id": row.get("ID_AGENDAMENTO") or registro,
        "registro": registro,
        "grvAte": row.get("GRV_ATE"),
        "medsystemAtendimentoId": local["medsystemAtendimentoId"] if local else None,
        "idPacienteSpdata": row.get("ID_PACIENTE_SPDATA"),
        "data": row.get("DATA"),
        "horario": row.get("HORA") or row.get("HR_AGE") or "",
        "paciente": normalizar_texto(row.get("PACIENTE")),
        "cpf": normalizar_texto(row.get("CPF")),
        "prontuario": normalizar_texto(row.get("PRONTUARIO")),
        "convenio": normalizar_texto(row.get("CONVENIO")),
        "telefone": normalizar_texto(row.get("FONE")),
        "celular": normalizar_texto(row.get("CELULAR")),
        "email": normalizar_texto(row.get("EMAIL")),
        "medico": normalizar_texto(row.get("MEDICO")),
        "crm": crm,
        "crmAtendimento": crm_atendimento,
        "medicoKey": crm_atendimento or crm or normalizar_texto(row.get("MEDICO")),
        "especialidade": normalizar_texto(row.get("ESPECIALIDADE")),
        "unidade": normalizar_texto(row.get("UNIDADE")),
        "retorno": normalizar_texto(row.get("RETORNO")),
        "tipoAgenda": normalizar_texto(row.get("TIPO_AGENDA")),
        "procedimentoSolicitado": normalizar_texto(row.get("PROCEDIMENTO_SOLICITADO")),
        "procedimento": normalizar_texto(row.get("PROCEDIMENTO")),
        "observacao": normalizar_texto(row.get("OBS")),
        "dataNascimento": row.get("DATA_NASCIMENTO"),
        "dataHoraAgendamento": row.get("DATA_HORA_AGENDAMENTO"),
        "atendidoSpdata": normalizar_texto(row.get("ATENDIDO")),
        "status": status,
        "statusOrigem": "medsystem" if local else "spdata",
    }


def calcular_resumo(items):
    resumo = status_para_resumo()
    for item in items:
        key = RESUMO_KEYS.get(item["status"], "desconhecidos")
        resumo[key] += 1
    return resumo


def calcular_medicos(rows):
    medicos = {}
    for row in rows:
        nome = normalizar_texto(row.get("MEDICO"))
        crm_atendimento = normalizar_texto(row.get("CRM_ATEND"))
        crm = normalizar_texto(row.get("CRM"))
        key = crm_atendimento or crm or nome
        if not key:
            continue

        if key not in medicos:
            medicos[key] = {
                "id": key,
                "nome": nome or "Médico não informado",
                "crm": crm,
                "crmAtendimento": crm_atendimento,
                "especialidade": normalizar_texto(row.get("ESPECIALIDADE")),
                "pacientesCount": 0,
            }
        medicos[key]["pacientesCount"] += 1

    return sorted(medicos.values(), key=lambda item: item["nome"])


@check_in_bp.route("/", methods=["GET"])
@jwt_required()
@roles_required("recepcao")
def home_check_in():
    try:
        data_ref = parse_data_param()
        page = parse_int_param("page", 1)
        page_size = parse_int_param("pageSize", 20, maximo=MAX_PAGE_SIZE)
        status_filtro = normalizar_texto(request.args.get("status"))
        medico = request.args.get("medico")
        q = request.args.get("q")

        if status_filtro and status_filtro not in STATUS_VALIDOS:
            return jsonify({"error": "Status inválido"}), 400

        rows_agenda = buscar_agendamentos_firebird(data_ref)
        rows_atendimentos = buscar_atendimentos_firebird(data_ref)
        rows_dia = mesclar_agenda_atendimentos(rows_agenda, rows_atendimentos)
        rows_filtradas = filtrar_rows(rows_dia, medico=medico, q=q)

        registros = [row.get("REGISTRO") for row in rows_filtradas]
        status_local = buscar_status_local(registros)
        items_com_status = [item_para_frontend(row, status_local) for row in rows_filtradas]

        resumo = calcular_resumo(items_com_status)

        if status_filtro:
            items_filtrados = [item for item in items_com_status if item["status"] == status_filtro]
        else:
            items_filtrados = items_com_status

        total = len(items_filtrados)
        start = (page - 1) * page_size
        end = start + page_size

        return jsonify({
            "items": items_filtrados[start:end],
            "page": page,
            "pageSize": page_size,
            "total": total,
            "medicos": calcular_medicos(rows_dia),
            "resumo": resumo,
            "data": data_ref.isoformat(),
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
