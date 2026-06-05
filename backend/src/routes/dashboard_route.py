from flask import (
    Blueprint, request, jsonify
)

from src.models.db.handler_fb_db import ConnectionDBFireBird

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

@dashboard_bp.route("pacientes")
def dashboard_paciente_lista():
    try:
        with ConnectionDBFireBird() as con:
            cursor = con.cursor()
            cursor.execute("""
            SELECT *
            FROM ATCABECATEND a
            WHERE a.id_tbcencus = '350'
            AND CAST(a.DATA_HORA_ENTRADA AS DATE) = CURRENT_DATE;
            """)

            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            result = [dict(zip(columns, row)) for row in rows]

            return jsonify(result), 200

        
    except Exception as e:
        return jsonify(str(e))