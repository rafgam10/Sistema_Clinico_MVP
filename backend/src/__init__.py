from flask import Flask
from .settings.config import Config
from .settings.extensions import db, migrate, jwt, cors

from src.commands.exames_commands import importar_exames_spdata_command
from src.commands.medicos_commands import registrar_medico_spdata_command

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)
    
    app.cli.add_command(importar_exames_spdata_command)
    app.cli.add_command(registrar_medico_spdata_command)

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
    from src.models.medico_model import Medico

    # Cruzamento:
    from src.models.model_mydsystem.med_spdata_agenda_model import MedSpdataAgenda
    from src.models.model_mydsystem.med_atendimentos_model import MedAtendimentos

    # Modelos Médicos:
    from src.models.model_padroes_solicitacoes.modelo_receita_model import ModeloReceita
    from src.models.model_padroes_solicitacoes.medicamentos_para_modelo_receita_model import Medicamentos

    from src.models.model_mydsystem.med_exames_model import Exame

    # Importações de Routes/Rotas:
    from .routes import register_routes
    register_routes(app)

    from src.routes.login_route import login_bp
    from src.routes.dashboard_route import dashboard_bp
    from src.routes.check_in_route import check_in_bp
    from src.routes.prontuario_route import prontuario_bp
    from src.routes.modelo_solicitacao_medicos_route import padrao_medico_receita_bp

    app.register_blueprint(login_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(check_in_bp)
    app.register_blueprint(prontuario_bp)
    app.register_blueprint(padrao_medico_receita_bp)

    return app
