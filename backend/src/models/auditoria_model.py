from datetime import datetime
from enum import Enum

from src.settings.extensions import db

"""  
    Registra ações importantes do sistema.
"""

class AcaoAuditoria(Enum):
    VISUALIZOU_PRONTUARIO = "VISUALIZOU_PRONTUARIO"
    INICIOU_ATENDIMENTO = "INICIOU_ATENDIMENTO"
    EDITOU_EVOLUCAO = "EDITOU_EVOLUCAO"
    FINALIZOU_ATENDIMENTO = "FINALIZOU_ATENDIMENTO"
    GEROU_RECEITA = "GEROU_RECEITA"
    GEROU_ATESTADO = "GEROU_ATESTADO"
    SINCRONIZOU_SPDATA = "SINCRONIZOU_SPData"


class Auditoria(db.Model):
    __tablename__ = "auditorias"

    id = db.Column(db.Integer, primary_key=True)

    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)

    medico_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)

    acao = db.Column(
        db.Enum(AcaoAuditoria),
        nullable=False
    )

    entidade = db.Column(
        db.String(100),
        nullable=True
    )

    entidade_id = db.Column(
        db.Integer,
        nullable=True
    )

    descricao = db.Column(
        db.Text,
        nullable=True
    )

    ip = db.Column(
        db.String(100),
        nullable=True
    )

    user_agent = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    usuario = db.relationship(
        "Usuario",
        foreign_keys=[usuario_id],
        back_populates="auditorias"
    )

    medico = db.relationship(
        "Usuario",
        foreign_keys=[medico_id],
        back_populates="auditorias_medicas"
    )

    def __repr__(self):
        return (
            f"<Auditoria acao={self.acao.value} "
            f"entidade={self.entidade} "
            f"entidade_id={self.entidade_id}>"
        )