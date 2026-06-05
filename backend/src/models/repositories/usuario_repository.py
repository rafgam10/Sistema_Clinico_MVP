from src.models.interfaces.usuario_interface import IUsuario

from src.settings.extensions import db
from src.models.usuario_model import Usuario

class UsuarioRepository(IUsuario):
    
    def get_usuario(self, email: str):
        try:    
            usuario = db.session.query(Usuario).filter(Usuario.email == email).first()
            return usuario
        
        except Exception as e:
            db.session.rollback()
            print(str(e))
            return None