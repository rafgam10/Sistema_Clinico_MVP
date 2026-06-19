from flask import Blueprint, jsonify
import json
from flask_jwt_extended import jwt_required
from src.security.decorators import roles_required

from src.models.db.handler_fb_db import ConnectionDBFireBird
from src.models.db.handler_redis_db import ConnectionDBRedis


check_in_bp = Blueprint("check_in", __name__, url_prefix="/check_in")

CACHE_KEY_CHECK_IN = "check_in:pacientes"
CACHE_TTL = 300


@check_in_bp.route("/", methods=["GET"])
@jwt_required()
@roles_required("recepcao")
def home_check_in():
    try:
        redis_connection = ConnectionDBRedis()

        cached = redis_connection.get_cache(CACHE_KEY_CHECK_IN)
        if cached is not None:
            return jsonify(json.loads(cached)), 200

        with ConnectionDBFireBird() as con:
            cursor = con.cursor()

            sql = """
                SELECT
                    NOME AS MEDICO,
                    DATA AS DATA,
                    HORA AS HORA,
                    PACIENTE AS PACIENTE,
                    CASE 
                        WHEN ATENDIDO = 'N' THEN 'NÃO ATENDIDO'
                        WHEN ATENDIDO = 'S' THEN 'ATENDIDO'
                        ELSE 'DESCONHECIDO'
                    END AS STATUS
                FROM REPACAGD
                ORDER BY DATA DESC, HORA DESC
                ROWS 15;
            """

            cursor.execute(sql)

            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            result = [dict(zip(columns, row)) for row in rows]

        redis_connection.set_cache(
            CACHE_KEY_CHECK_IN,
            json.dumps(result, default=str),
            ttl=CACHE_TTL
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    