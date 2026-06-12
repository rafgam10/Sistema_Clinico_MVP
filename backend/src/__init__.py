from flask import Flask
from .settings.config import Config
from .settings.extensions import db, migrate, jwt, cors

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)

    try:
        # Importações de Models:
        from src.models.atendimentos_model import Atendimento
        from src.models.anamnese_model import Anamnese
        from src.models.evolucoes_medicas_model import EvolucaoMedica
        from src.models.evolucao_medica_versao_model import EvolucaoMedicaVersao
        from src.models.diagnostico_model import Diagnostico
        from src.models.prescricao_model import Prescricao
        from src.models.solicitacao_exame_model import SolicitacaoExame
        from src.models.documento_medico_model import DocumentoMedico
        from src.models.fila_sincronizacao_model import FilaSincronizacao
        from src.models.log_integracao_model import LogIntegracao
        from src.models.auditoria_model import Auditoria
        from src.models.usuario_model import Usuario
        
        
        # Importações de Routes/Rotas:
        from .routes import register_routes
        register_routes(app)
        
        from src.routes.login_route import login_bp
        from src.routes.dashboard_route import dashboard_bp
        from src.routes.check_in_route import check_in_bp
        
        app.register_blueprint(login_bp)
        app.register_blueprint(dashboard_bp)
        app.register_blueprint(check_in_bp)
        
        
        
    except Exception:
        pass

    return app
