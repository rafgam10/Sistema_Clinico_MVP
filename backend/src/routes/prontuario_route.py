from flask import Blueprint, request, jsonify

from src.settings.extensions import db
from src.models.db.handler_fb_db import ConnectionDBFireBird
from src.models.db.handler_redis_db import ConnectionDBRedis

prontuario_bp = Blueprint("prontuario", __name__, url_prefix="/prontuario")

@prontuario_bp.route("/doenca-cid", methods=["GET"])
def doenca_cid():
    try:
        q = (request.args.get("q") or "").strip()

        limit = request.args.get("limit", default=50, type=int)
        offset = request.args.get("offset", default=0, type=int)

        limit = min(max(limit or 50, 1), 100)
        offset = max(offset or 0, 0)

        row_start = offset + 1
        row_end = offset + limit

        where = [
            "COD IS NOT NULL",
            "NOME IS NOT NULL"
        ]
        params = []

        if q:
            if len(q) <= 6:
                where.append("(COD CONTAINING ? OR NOME CONTAINING ?)")
                params.extend([q, q])
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

        return jsonify({
            "items": result,
            "limit": limit,
            "offset": offset,
            "has_more": len(result) == limit
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500