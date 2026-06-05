from datetime import datetime
from src.settings.extensions import db

""" 
    Armazena a evolução escrita pelo médico.
    Essa tabela deve ter controle de versão, porque evolução médica é informação sensível.
"""

class EvolucaoMedica(db.Model):
    __tablename__ = "evolucoes_medicas"

    id = db.Column(db.Integer, primary_key=True)

    atendimento_id = db.Column(
        db.Integer,
        db.ForeignKey("atendimentos.id"),
        nullable=False
    )

    medico_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    texto_evolucao = db.Column(db.Text, nullable=False)

    versao = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )

    status = db.Column(
        db.String(50),
        nullable=False,
        default="rascunho"
    )

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
        back_populates="evolucoes_medicas"
    )

    medico = db.relationship(
        "Usuario",
        back_populates="evolucoes_medicas"
    )
    
    # Relacionamentos:
    versoes = db.relationship(
        "EvolucaoMedicaVersao",
        back_populates="evolucao",
        cascade="all, delete-orphan",
        order_by="EvolucaoMedicaVersao.created_at.desc()"
    )

    def __repr__(self):
        return (
            f"<EvolucaoMedica atendimento_id={self.atendimento_id} "
            f"medico_id={self.medico_id} versao={self.versao}>"
        )