from datetime import datetime
from enum import Enum

from src.settings.extensions import db

""" 
    Para atestados, declarações, encaminhamentos e outros documentos.
"""

class TipoDocumentoMedico(Enum):
    ATESTADO = "ATESTADO"
    DECLARACAO = "DECLARACAO"
    ENCAMINHAMENTO = "ENCAMINHAMENTO"
    RELATORIO = "RELATORIO"
    RECEITA = "RECEITA"


class DocumentoMedico(db.Model):
    __tablename__ = "documentos_medicos"

    id = db.Column(db.Integer, primary_key=True)

    atendimento_id = db.Column(
        db.Integer,
        db.ForeignKey("atendimentos.id"),
        nullable=False
    )

    tipo_documento = db.Column(
        db.Enum(TipoDocumentoMedico),
        nullable=False
    )

    conteudo = db.Column(
        db.Text,
        nullable=False
    )

    arquivo_pdf = db.Column(
        db.String(255),
        nullable=True
    )

    assinado = db.Column(
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
        back_populates="documentos_medicos"
    )

    def __repr__(self):
        return (
            f"<DocumentoMedico atendimento_id={self.atendimento_id} "
            f"tipo_documento={self.tipo_documento.value} "
            f"assinado={self.assinado}>"
        )