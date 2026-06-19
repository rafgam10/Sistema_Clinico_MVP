from flask_jwt_extended import create_access_token

from src.models.repositories.usuario_repository import UsuarioRepository

class LoginController:
    
    def __init__(self):
        self.__repo = UsuarioRepository()
    
    def generate_JWT_usuario(self, email:str, senha: str):
        usuario = self.__repo.get_usuario(email)
        
        if not usuario:
            return None

        if usuario.senha != senha:
            return None

        token = create_access_token(
            identity=str(usuario.id),
            additional_claims={
                "id": usuario.id,
                "email": usuario.email,
                "role": usuario.role
            }
        )
        return token
        
        