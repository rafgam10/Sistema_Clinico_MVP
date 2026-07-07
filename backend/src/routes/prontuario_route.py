import json
import re
from datetime import date, datetime, time

from flask import Blueprint, current_app, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import select

from src.security.decorators import roles_required
from src.models.db.handler_fb_db import ConnectionDBFireBird
from src.models.db.handler_sql_server import ConnectionSqlServer
from src.models.db.handler_redis_db import ConnectionDBRedis
from src.settings.extensions import db
from src.models.atendimentos_model import Atendimento
from src.models.anamnese_model import Anamnese
from src.models.diagnostico_model import Diagnostico
from src.models.prescricao_model import Prescricao
from src.models.solicitacao_exame_model import SolicitacaoExame
from src.models.evolucoes_medicas_model import EvolucaoMedica
from src.models.model_mydsystem.med_spdata_atendimentos_model import MedSpdataAtendimento
from src.utils.normalizar import normalizar_cpf


prontuario_bp = Blueprint("prontuario", __name__, url_prefix="/prontuario")

CID_CACHE_TTL = 3600
CID_CODE_PATTERN = re.compile(r"^[A-Za-z][0-9.]*$")
RTF_DESTINATIONS = {
    "fonttbl", "colortbl", "datastore", "themedata", "stylesheet", "info",
    "pict", "object", "header", "footer", "generator", "xmlnstbl",
}
RTF_SYMBOLS = {
    "par": "\n",
    "line": "\n",
    "tab": "\t",
    "emdash": "—",
    "endash": "–",
    "bullet": "•",
    "lquote": "‘",
    "rquote": "’",
    "ldblquote": "“",
    "rdblquote": "”",
}


def _solicitacao_exame_to_dict(solicitacao):
    exame = solicitacao.exame
    nome = exame.nome if exame else (solicitacao.descricao or solicitacao.tipo_exame)

    return {
        "nome": nome,
        "exame_id": solicitacao.exame_id,
        "descricao": solicitacao.descricao,
        "tipo_exame": solicitacao.tipo_exame,
        "codigo_alfanumerico": exame.codigo_alfanumerico if exame else None,
        "codigo_amb": exame.codigo_amb if exame else None,
    }


def _somente_digitos(valor):
    return re.sub(r"\D", "", str(valor or ""))


def _cpf_valido(valor):
    return normalizar_cpf(valor)


def _texto_ou_none(valor):
    if valor is None:
        return None

    texto = str(valor).strip()
    return texto or None


def _normalizar_sql_value(valor):
    if isinstance(valor, (datetime, date, time)):
        return valor.isoformat()

    if isinstance(valor, bytes):
        try:
            return valor.decode("utf-8")
        except UnicodeDecodeError:
            return valor.decode("cp1252", errors="replace")

    return valor


def _normalizar_texto_linhas(texto):
    if texto is None:
        return None

    linhas = [linha.strip() for linha in str(texto).splitlines()]
    texto = "\n".join(linha for linha in linhas if linha)
    return texto or None


def _decode_rtf_hex(valor):
    try:
        return bytes.fromhex(valor).decode("cp1252")
    except (ValueError, UnicodeDecodeError):
        return ""


def _rtf_para_texto(valor):
    texto = _texto_ou_none(valor)
    if not texto:
        return None

    if texto.startswith('"') and texto.endswith('"'):
        texto = texto[1:-1].strip()

    if not texto.lstrip().startswith("{\\rtf"):
        return _normalizar_texto_linhas(texto)

    resultado = []
    stack = []
    ignorable = False
    ucskip = 1
    curskip = 0
    i = 0

    while i < len(texto):
        char = texto[i]

        if char == "{":
            stack.append((ucskip, ignorable))
            i += 1
            continue

        if char == "}":
            if stack:
                ucskip, ignorable = stack.pop()
            i += 1
            continue

        if char == "\\":
            i += 1
            if i >= len(texto):
                break

            marcador = texto[i]
            if marcador in "{}\\":
                if not ignorable and curskip == 0:
                    resultado.append(marcador)
                elif curskip > 0:
                    curskip -= 1
                i += 1
                continue

            if marcador == "'" and i + 2 < len(texto):
                if not ignorable and curskip == 0:
                    resultado.append(_decode_rtf_hex(texto[i + 1:i + 3]))
                elif curskip > 0:
                    curskip -= 1
                i += 3
                continue

            if marcador == "*":
                ignorable = True
                i += 1
                continue

            if not marcador.isalpha():
                if not ignorable and marcador == "~":
                    resultado.append(" ")
                i += 1
                continue

            inicio = i
            while i < len(texto) and texto[i].isalpha():
                i += 1
            palavra = texto[inicio:i]

            sinal = 1
            if i < len(texto) and texto[i] == "-":
                sinal = -1
                i += 1

            numero_inicio = i
            while i < len(texto) and texto[i].isdigit():
                i += 1
            numero = texto[numero_inicio:i]
            argumento = sinal * int(numero) if numero else None

            if i < len(texto) and texto[i] == " ":
                i += 1

            if palavra in RTF_DESTINATIONS:
                ignorable = True
                continue

            if ignorable:
                continue

            if palavra == "uc" and argumento is not None:
                ucskip = argumento
                continue

            if palavra == "u" and argumento is not None:
                codigo = argumento if argumento >= 0 else argumento + 65536
                try:
                    resultado.append(chr(codigo))
                except ValueError:
                    pass
                curskip = ucskip
                continue

            simbolo = RTF_SYMBOLS.get(palavra)
            if simbolo is not None:
                resultado.append(simbolo)
                continue

            continue

        if not ignorable:
            if curskip > 0:
                curskip -= 1
            else:
                resultado.append(char)

        i += 1

    return _normalizar_texto_linhas("".join(resultado))


def _referencia_paciente_biodata(paciente_id):
    cpf = _cpf_valido(request.args.get("cpf"))
    nome = _texto_ou_none(request.args.get("nome"))

    if cpf and nome:
        return cpf, nome

    registro = db.session.execute(
        select(MedSpdataAtendimento).where(
            MedSpdataAtendimento.id_paciente_spdata == paciente_id
        ).order_by(MedSpdataAtendimento.data_hora_entrada.desc())
    ).scalars().first()

    if registro:
        cpf = cpf or _cpf_valido(registro.cpf)
        nome = nome or _texto_ou_none(registro.paciente)

    return cpf, nome


def _executar_historico_biodata(where_clause, params, limit, offset):
    row_start = offset + 1
    row_end = offset + limit + 1
    sql = f"""
        WITH historico AS (
            SELECT
                a.intAtendimentoId AS ID_ATENDIMENTO,
                a.datAtendimento AS DATA_CONSULTA,
                a.datEncerrado AS DATA_ENCERRAMENTO,
                p.strProfissional AS MEDICO,
                a.strObservacao AS OBS_ATENDIMENTO,
                a.strQueixaPrincipal AS QUEIXA_PRINCIPAL,
                a.strCodigoCID AS CID_PRINCIPAL,
                a.strCID2 AS CID_SECUNDARIO,
                a.strCID3 AS CID_TERCIARIO,
                a.strCID4 AS CID_QUATERNARIO,
                an.intAnamneseId AS ID_ANAMNESE,
                an.datAnamnese AS DATA_ANAMNESE,
                CAST(an.strAnamnese AS NVARCHAR(MAX)) AS ANAMNESE_RTF,
                CAST(an.strAnamneseMobile AS NVARCHAR(MAX)) AS ANAMNESE_MOBILE,
                ROW_NUMBER() OVER (
                    ORDER BY COALESCE(an.datAnamnese, a.datEncerrado, a.datAtendimento, a.datAtende) DESC,
                             an.intAnamneseId DESC
                ) AS RN
            FROM [BioData].[dbo].[tblAnamnese] an
            JOIN [BioData].[dbo].[tblAtendimento] a
                ON a.intAtendimentoId = an.intAtendimentoId
            JOIN [Repositorio].[dbo].[tblCliente] c
                ON c.intClienteId = a.intClienteId
            LEFT JOIN [BioData].[dbo].[tblProfissional] p
                ON p.intProfissionalId = a.intProfissionalId
            WHERE UPPER(ISNULL(a.bolEncerrado, 'N')) = 'S'
              AND UPPER(ISNULL(an.bolNaoCompartilhar, 'N')) <> 'S'
              AND {where_clause}
        )
        SELECT
            ID_ATENDIMENTO,
            DATA_CONSULTA,
            DATA_ENCERRAMENTO,
            MEDICO,
            OBS_ATENDIMENTO,
            QUEIXA_PRINCIPAL,
            CID_PRINCIPAL,
            CID_SECUNDARIO,
            CID_TERCIARIO,
            CID_QUATERNARIO,
            ID_ANAMNESE,
            DATA_ANAMNESE,
            ANAMNESE_RTF,
            ANAMNESE_MOBILE
        FROM historico
        WHERE RN BETWEEN ? AND ?
        ORDER BY RN;
    """

    with ConnectionSqlServer() as con:
        cursor = con.cursor()
        cursor.execute(sql, [*params, row_start, row_end])
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        cursor.close()

    items = [
        {
            coluna: _normalizar_sql_value(valor)
            for coluna, valor in zip(columns, row)
        }
        for row in rows
    ]
    return items[:limit], len(items) > limit


def _historico_biodata(paciente_id, limit=10, offset=0):
    cpf, nome = _referencia_paciente_biodata(paciente_id)
    historico = []
    has_more = False

    if cpf:
        historico, has_more = _executar_historico_biodata(
            "REPLACE(REPLACE(REPLACE(REPLACE(c.strCPF, '.', ''), '-', ''), '/', ''), ' ', '') = ?",
            [cpf],
            limit,
            offset,
        )

    if not historico and offset == 0 and nome:
        historico, has_more = _executar_historico_biodata(
            "UPPER(LTRIM(RTRIM(c.strCliente))) = UPPER(LTRIM(RTRIM(?)))",
            [nome],
            limit,
            offset,
        )

    result = []
    for item in historico:
        anamnese = _rtf_para_texto(item.get("ANAMNESE_RTF")) or _rtf_para_texto(item.get("ANAMNESE_MOBILE"))
        cid_secundarios = [
            item.get("CID_SECUNDARIO"),
            item.get("CID_TERCIARIO"),
            item.get("CID_QUATERNARIO"),
        ]
        cid_secundarios = [cid for cid in cid_secundarios if _texto_ou_none(cid)]

        result.append({
            "ID_ATENDIMENTO": str(item.get("ID_ATENDIMENTO")) if item.get("ID_ATENDIMENTO") is not None else None,
            "ID_ANAMNESE": str(item.get("ID_ANAMNESE")) if item.get("ID_ANAMNESE") is not None else None,
            "ID_PACIENTE": paciente_id,
            "PACIENTE": nome,
            "DATA_CONSULTA": item.get("DATA_CONSULTA"),
            "DATA_ENCERRAMENTO": item.get("DATA_ENCERRAMENTO"),
            "DATA_ANAMNESE": item.get("DATA_ANAMNESE"),
            "MEDICO": item.get("MEDICO"),
            "ANAMNESE": anamnese,
            "OBS_ATENDIMENTO": item.get("OBS_ATENDIMENTO"),
            "QUEIXA_PRINCIPAL": item.get("QUEIXA_PRINCIPAL"),
            "CID_PRINCIPAL": item.get("CID_PRINCIPAL"),
            "DIAGNOSTICO_PRINCIPAL": None,
            "CID_SECUNDARIO": "\n".join(cid_secundarios) if cid_secundarios else None,
            "DIAGNOSTICO_SECUNDARIO": None,
            "ID_EVOLUCAO": None,
            "ID_SOLICITACAO_EXAME": None,
        })

    return {
        "items": result,
        "limit": limit,
        "offset": offset,
        "has_more": has_more,
    }

@prontuario_bp.route("/doenca-cid", methods=["GET"])
@jwt_required()
@roles_required("medico")
def doenca_cid():
    try:
        q = (request.args.get("q") or "").strip()

        limit = request.args.get("limit", default=20, type=int)
        offset = request.args.get("offset", default=0, type=int)

        limit = min(max(limit or 20, 1), 50)
        offset = max(offset or 0, 0)

        if not q:
            return jsonify({
                "items": [],
                "limit": limit,
                "offset": offset,
                "has_more": False
            }), 200

        is_codigo_cid = bool(CID_CODE_PATTERN.fullmatch(q))

        if (is_codigo_cid and len(q) < 2) or (not is_codigo_cid and len(q) < 3):
            return jsonify({
                "items": [],
                "limit": limit,
                "offset": offset,
                "has_more": False
            }), 200

        cache_key = f"prontuario:cid:{'codigo' if is_codigo_cid else 'nome'}:{q.casefold()}:{limit}:{offset}"
        redis_connection = ConnectionDBRedis()

        cached = redis_connection.get_cache(cache_key)
        if cached is not None:
            return jsonify(json.loads(cached)), 200

        row_start = offset + 1
        row_end = offset + limit

        where = [
            "COD IS NOT NULL",
            "NOME IS NOT NULL"
        ]
        params = []

        if is_codigo_cid:
            where.append("COD STARTING WITH ?")
            params.append(q.upper())
        else:
            where.append("NOME CONTAINING ?")
            params.append(q)

        sql = f"""
            SELECT
                COD AS CID,
                NOME AS DOENCA
            FROM TBCID10
            WHERE {' AND '.join(where)}
            ORDER BY COD
            ROWS {row_start} TO {row_end};
        """

        with ConnectionDBFireBird() as con:
            cursor = con.cursor()
            cursor.execute(sql, params)

            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            result = [dict(zip(columns, row)) for row in rows]

        response = {
            "items": result,
            "limit": limit,
            "offset": offset,
            "has_more": len(result) == limit
        }

        redis_connection.set_cache(
            cache_key,
            json.dumps(response, default=str),
            ttl=CID_CACHE_TTL
        )

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@prontuario_bp.route("/historico-local/<int:paciente_id>")
@jwt_required()
@roles_required("medico")
def historico_paciente_local(paciente_id):
    # Busca no banco LOCAL os atendimentos finalizados deste paciente,
    # incluindo dados completos de anamnese, CIDs, medicamentos e exames.
    try:
        atendimentos = db.session.execute(
            select(Atendimento).where(
                Atendimento.spdata_paciente_id == paciente_id,
                Atendimento.status == "finalizado"
            ).order_by(Atendimento.data_atendimento.desc())
        ).scalars().all()

        result = []
        for a in atendimentos:
            # Separa CID principal dos secundários
            diag_principal = next((d for d in a.diagnosticos if d.principal), None)
            diag_secundarios = [d for d in a.diagnosticos if not d.principal]

            # Busca nome do médico na primeira evolução registrada
            medico_nome = None
            if a.evolucoes_medicas:
                evol = a.evolucoes_medicas[0]
                if evol.medico:
                    medico_nome = evol.medico.nome_completo

            result.append({
                "spdata_atendimento_id": a.spdata_atendimento_id,
                "data_consulta": a.data_atendimento.isoformat() if a.data_atendimento else None,
                "medico_nome": medico_nome,
                "anamnese": a.anamnese.observacoes if a.anamnese else None,
                "cid_principal": diag_principal.cid_codigo if diag_principal else None,
                "cid_principal_descricao": diag_principal.cid_descricao if diag_principal else None,
                "cids_secundarios": [
                    {"codigo": d.cid_codigo, "descricao": d.cid_descricao}
                    for d in diag_secundarios
                ],
                "medicamentos": [
                    f"{p.medicamento} — {p.dosagem}" if p.dosagem else p.medicamento
                    for p in a.prescricoes
                ],
                "exames": [
                    _solicitacao_exame_to_dict(s)
                    for s in a.solicitacoes_exames
                ],
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@prontuario_bp.route("/historico-paciente/<int:id>")
@jwt_required()
@roles_required("medico")
def historico_paciente(id:int):
    try:
        limit = request.args.get("limit", default=10, type=int)
        offset = request.args.get("offset", default=0, type=int)

        limit = min(max(limit or 10, 1), 50)
        offset = max(offset or 0, 0)

        return jsonify(_historico_biodata(id, limit, offset)), 200
            
    except Exception as e:
        current_app.logger.exception("Erro ao buscar histórico do paciente no BioData")
        return jsonify({"error": str(e)}), 500
