from flask import (
    Blueprint,
    request,
    jsonify
)

from flask_jwt_extended import jwt_required, get_jwt_identity

from src.controllers.login_controller import LoginController

login_bp = Blueprint('login', __name__, url_prefix="/login")
controller = LoginController()

@login_bp.route("/auth", methods=["POST"])
def login():
    
    data = request.get_json()
    email = data.get("email")
    senha = data.get("senha")
    
    token = controller.generate_JWT_usuario(email, senha)
    return jsonify(access_token=token)