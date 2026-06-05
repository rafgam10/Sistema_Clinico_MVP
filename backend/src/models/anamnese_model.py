from datetime import datetime
from src.settings.extensions import db

""" 
    Armazena os dados clínicos preenchidos na tela de anamnese.
"""

class Anamnese(db.Model):
    __tablename__ = "anamneses"

    id = db.Column(db.Integer, primary_key=True)

    atendimento_id = db.Column(
        db.Integer,
        db.ForeignKey("atendimentos.id"),
        nullable=False
    )

    queixa_principal = db.Column(db.Text, nullable=True)
    historia_doenca_atual = db.Column(db.Text, nullable=True)
    antecedentes_pessoais = db.Column(db.Text, nullable=True)
    antecedentes_familiares = db.Column(db.Text, nullable=True)
    alergias = db.Column(db.Text, nullable=True)
    medicamentos_em_uso = db.Column(db.Text, nullable=True)
    habitos_de_vida = db.Column(db.Text, nullable=True)
    observacoes = db.Column(db.Text, nullable=True)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    atendimento = db.relationship(
        "Atendimento",
        back_populates="anamnese"
    )

    def __repr__(self):
        return f"<Anamnese atendimento_id={self.atendimento_id}>"