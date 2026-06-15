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
