import json
import re

from flask import Blueprint, request, jsonify

from src.models.db.handler_fb_db import ConnectionDBFireBird
from src.models.db.handler_redis_db import ConnectionDBRedis

prontuario_bp = Blueprint("prontuario", __name__, url_prefix="/prontuario")

CID_CACHE_TTL = 3600
CID_CODE_PATTERN = re.compile(r"^[A-Za-z][0-9.]*$")

@prontuario_bp.route("/doenca-cid", methods=["GET"])
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


@prontuario_bp.route("/historico-paciente/<int:id>")
def historico_paciente(id:int):
    try:
        id_paciente = id
        
        with ConnectionDBFireBird() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT FIRST 5
                /* Paciente */
                p.ID AS ID_PACIENTE,
                p.PRONT AS PRONTUARIO,
                p.NOME AS PACIENTE,
                p.NASC AS DATA_NASCIMENTO,

                /* Consulta */
                a.ID AS ID_ATENDIMENTO,
                a.COD_ATENDIMENTO,
                a.TP_ATENDIMENTO,
                a.DATA_HORA_ENTRADA AS DATA_CONSULTA,
                a.DATA_HORA_ALTA_MEDICA,
                a.OBS_ATENDIMENTO,

                /* Diagnóstico principal */
                cid_principal.COD AS CID_PRINCIPAL,
                cid_principal.NOME AS DIAGNOSTICO_PRINCIPAL,

                /* Diagnóstico secundário */
                cid_secundario.COD AS CID_SECUNDARIO,
                cid_secundario.NOME AS DIAGNOSTICO_SECUNDARIO,

                /* Histórico do atendimento */
                ht.ID AS ID_HISTORICO_ATENDIMENTO,
                ht.DATA_HORA_HISTORICO,

                /* Evolução/anamnese */
                ev.ID_CABEVOL,
                ev.ID_EVOLUCAO,
                ev.DATA_HORA_EVOLUCAO,
                ev.DATA_HORA_LANCAMENTO,
                ev.ID_TBCBOPRO_EVOLUCAO,
                ev.PRE_IMPRESSO,

                /* Exames */
                ex.ID AS ID_SOLICITACAO_EXAME,
                ex.DATA AS DATA_EXAME,
                ex.HORA AS HORA_EXAME,
                ex.REQUIS AS REQUISICAO,
                ex.NREQUIS AS NUMERO_REQUISICAO,
                ex.DATA_REQUISICAO,
                ex.CRM,
                ex.MEDICO,
                ex.UNIDADE

            FROM RICADPAC p

            INNER JOIN ATCABECATEND a
                ON a.ID_RICADPAC = p.ID

            LEFT OUTER JOIN HTATENDIMENTO ht
                ON ht.ID_ATCABECATEND = a.ID

            LEFT OUTER JOIN PRCABEVOL ev
                ON ev.ID_HTATENDIMENTO = ht.ID

            LEFT OUTER JOIN TBCID10 cid_principal
                ON cid_principal.ID = a.ID_TBCID10_PRINCIPAL

            LEFT OUTER JOIN TBCID10 cid_secundario
                ON cid_secundario.ID = a.ID_TBCID10_SECUNDARIO

            LEFT OUTER JOIN SICADATE ex
                ON ex.ID_ATCABECATEND = a.ID

            WHERE p.ID = ?
            ORDER BY
                a.DATA_HORA_ENTRADA DESC,
                ev.DATA_HORA_EVOLUCAO,
                ex.DATA,
                ex.HORA;             
            """, (id_paciente,))
            
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            result = [dict(zip(columns, row)) for row in rows]
            
            return jsonify(result), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500