from datetime import datetime
from enum import Enum

from src.settings.extensions import db

""" 
    Armazena pedidos de exames feitos pelo médico.
"""

class StatusSolicitacaoExame(Enum):
    SOLICITADO = "SOLICITADO"
    ENVIADO_SPDATA = "ENVIADO_SPData"
    PENDENTE_SINCRONIZACAO = "PENDENTE_SINCRONIZACAO"
    CANCELADO = "CANCELADO"


class SolicitacaoExame(db.Model):
    __tablename__ = "solicitacoes_exames"

    id = db.Column(db.Integer, primary_key=True)

    atendimento_id = db.Column(
        db.Integer,
        db.ForeignKey("atendimentos.id"),
        nullable=False
    )

    tipo_exame = db.Column(
        db.String(255),
        nullable=False
    )

    exame_id = db.Column(
        db.Integer,
        db.ForeignKey("exames.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    descricao = db.Column(
        db.Text,
        nullable=True
    )

    justificativa = db.Column(
        db.Text,
        nullable=True
    )

    status = db.Column(
        db.Enum(StatusSolicitacaoExame),
        nullable=False,
        default=StatusSolicitacaoExame.SOLICITADO
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    atendimento = db.relationship(
        "Atendimento",
        back_populates="solicitacoes_exames"
    )

    exame = db.relationship(
        "Exame",
        back_populates="solicitacoes_exames"
    )

    def __repr__(self):
        return (
            f"<SolicitacaoExame atendimento_id={self.atendimento_id} "
            f"tipo_exame={self.tipo_exame} status={self.status.value}>"
        )
