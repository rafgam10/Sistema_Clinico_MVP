import json
import re

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import select

from src.security.decorators import roles_required
from src.models.db.handler_fb_db import ConnectionDBFireBird
from src.models.db.handler_redis_db import ConnectionDBRedis
from src.settings.extensions import db
from src.models.atendimentos_model import Atendimento
from src.models.anamnese_model import Anamnese
from src.models.diagnostico_model import Diagnostico
from src.models.prescricao_model import Prescricao
from src.models.solicitacao_exame_model import SolicitacaoExame
from src.models.evolucoes_medicas_model import EvolucaoMedica


prontuario_bp = Blueprint("prontuario", __name__, url_prefix="/prontuario")

CID_CACHE_TTL = 3600
CID_CODE_PATTERN = re.compile(r"^[A-Za-z][0-9.]*$")


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
