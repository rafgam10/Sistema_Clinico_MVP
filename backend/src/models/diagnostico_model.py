from datetime import datetime
from src.settings.extensions import db

""" 
    Armazena o diagnóstico informado pelo médico.
"""

class Diagnostico(db.Model):
    __tablename__ = "diagnosticos"

    id = db.Column(db.Integer, primary_key=True)

    atendimento_id = db.Column(
        db.Integer,
        db.ForeignKey("atendimentos.id"),
        nullable=False
    )

    cid_codigo = db.Column(
        db.String(20),
        nullable=True
    )

    cid_descricao = db.Column(
        db.String(255),
        nullable=True
    )

    diagnostico_descritivo = db.Column(
        db.Text,
        nullable=True
    )

    principal = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    atendimento = db.relationship(
        "Atendimento",
        back_populates="diagnosticos"
    )

    def __repr__(self):
        return (
            f"<Diagnostico atendimento_id={self.atendimento_id} "
            f"cid_codigo={self.cid_codigo} principal={self.principal}>"
        )