from flask import (
    Blueprint, request, jsonify
)

import json

from src.models.db.handler_fb_db import ConnectionDBFireBird
from src.models.db.handler_redis_db import ConnectionDBRedis

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

CACHE_KEY_PACIENTES = "dashboard:pacientes"
CACHE_TTL = 300

@dashboard_bp.route("/pacientes", methods=["GET"])
def dashboard_paciente_lista():
    try:
        # redis_connection = ConnectionDBRedis()
        # cached = redis_connection.get_cache(CACHE_KEY_PACIENTES)
        # if cached is not None:
        #     return jsonify(json.loads(cached)), 200
        
        with ConnectionDBFireBird() as con:
            cursor = con.cursor()
            # cursor.execute("""
            # SELECT *
            # FROM ATCABECATEND a
            # WHERE a.id_tbcencus = '350'
            # AND CAST(a.DATA_HORA_ENTRADA AS DATE) = CURRENT_DATE;
            # """)
            
            # Query de SELECT:
            cursor.execute("""
                SELECT *
                    FROM ATCABECATEND A 
                    JOIN TBCBOPRO TB ON A.ID_TBCBOPRO_ATENDIMENTO = TB.ID
                    JOIN TBPROFIS TF ON TB.ID_TBPROFIS = TF.ID 
                WHERE  a.id_tbcencus = '203' AND -- < id_tbcencus > Codigo da unidade
                tb.cod = '11700' AND -- < TBCBOPRO --:  >
                CAST(a.DATA_HORA_ENTRADA AS DATE) = CURRENT_DATE - 6;       
            """)

            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            result = [dict(zip(columns, row)) for row in rows]
            
            #redis_connection.set_cache(CACHE_KEY_PACIENTES, json.dumps(result, default=str), ttl=CACHE_TTL)

            return jsonify(result), 200

        
    except Exception as e:
        return jsonify(str(e))