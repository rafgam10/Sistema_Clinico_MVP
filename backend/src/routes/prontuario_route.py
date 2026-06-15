from flask import Blueprint, request, jsonify

from src.settings.extensions import db
from src.models.db.handler_fb_db import ConnectionDBFireBird
from src.models.db.handler_redis_db import ConnectionDBRedis

prontuario_bp = Blueprint("prontuario", __name__, url_prefix="/prontuario")

@prontuario_bp.route("/doenca-cid", methods=["GET"])
def doenca_cid():
    try:
        with ConnectionDBFireBird() as con:
            cursor = con.cursor()
            cursor.execute("""
                SELECT
                    COD AS CID,
                    NOME AS DOENCA
                FROM TBCID10
                WHERE COD IS NOT NULL
                AND NOME IS NOT NULL
                ORDER BY COD;
            """)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            result = [dict(zip(columns, row)) for row in rows]
            
            return jsonify(result), 200
    
    except Exception as e:
        return jsonify({"error": str(e)})