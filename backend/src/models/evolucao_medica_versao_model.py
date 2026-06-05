from datetime import datetime
from src.settings.extensions import db

""" 
    Sempre que o médico editar uma evolução, a versão antiga deve ser preservada.
"""

class EvolucaoMedicaVersao(db.Model):
    __tablename__ = "evolucoes_medicas_versoes"

    id = db.Column(db.Integer, primary_key=True)

    evolucao_id = db.Column(
        db.Integer,
        db.ForeignKey("evolucoes_medicas.id"),
        nullable=False
    )

    texto_anterior = db.Column(db.Text, nullable=False)

    texto_novo = db.Column(db.Text, nullable=False)

    alterado_por = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    motivo_alteracao = db.Column(db.Text, nullable=True)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    evolucao = db.relationship(
        "EvolucaoMedica",
        back_populates="versoes"
    )

    usuario_alteracao = db.relationship(
        "Usuario",
        back_populates="alteracoes_evolucoes"
    )

    def __repr__(self):
        return (
            f"<EvolucaoMedicaVersao evolucao_id={self.evolucao_id} "
            f"alterado_por={self.alterado_por}>"
        )