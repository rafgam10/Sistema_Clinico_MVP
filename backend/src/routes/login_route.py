from flask import (
    Blueprint,
    request,
    jsonify
)

from flask_jwt_extended import jwt_required, get_jwt_identity

from src.controllers.login_controller import LoginController

from src.settings.extensions import db
from src.models.usuario_model import Usuario
from src.models.db.handler_fb_db import ConnectionDBFireBird

login_bp = Blueprint('login', __name__, url_prefix="/login")
controller = LoginController()

@login_bp.route("/auth", methods=["POST"])
def login():
    
    data = request.get_json()
    email = data.get("email")
    senha = data.get("senha")
    
    token = controller.generate_JWT_usuario(email, senha)
    return jsonify(access_token=token)


@login_bp.route("/register", methods=["POST"])
def register_medic():
    try:
        data = request.get_json()
        
        email = data["email_medico"]
        senha = data["senha_medico"]
        nome_completo = data["nome_completo_medico"]
        cpf_cnpj = data["CNPJ_CPF"]
        
        
        sql_find_1 = """
            SELECT * FROM TBPROFIS medico WHERE NOME = '?' and CNPJ_CPF = '?'; 
        """
        sql_find_2 = """
        
        """
        
        with ConnectionDBFireBird() as con:
            cursor = con.cursor()
            cursor.execute(sql_find_1, (nome_completo,))
            
            medico_select = cursor.fetchone()
            
            if(medico_select is None):
                return jsonify({"error": "Médico não foi encontado!"}), 404
            
            usuario_medico = Usuario(nome_completo, cpf_cnpj, email, senha)
            db.session.add(usuario_medico)
            db.session.commit()
            
            
            
        return jsonify({"msg": "usuários criando com sucesso!"}), 200
        
        
    except Exception as e:
        jsonify({"error": str(e)})