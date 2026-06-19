
from datetime import datetime

from src.settings.extensions import db


class Exame(db.Model):
    __tablename__ = "exames"

    id = db.Column(db.Integer, primary_key=True)

    # ID original da SITABPRO
    spdata_id = db.Column(
        db.Integer,
        nullable=False,
        unique=True,
        index=True,
    )

    ato = db.Column(db.String(50), nullable=True, index=True)
    codigo_alfanumerico = db.Column(db.String(100), nullable=True, index=True)
    nome = db.Column(db.String(255), nullable=False, index=True)

    codigo_amb = db.Column(db.String(100), nullable=True)
    grupo = db.Column(db.String(100), nullable=True, index=True)
    unidade = db.Column(db.String(100), nullable=True)

    tipo = db.Column(db.String(50), nullable=True, index=True)
    tipo_procedimento = db.Column(db.String(50), nullable=True)

    material = db.Column(db.String(255), nullable=True)
    metodo = db.Column(db.Text, nullable=True)
    preparacao = db.Column(db.Text, nullable=True)

    coletor = db.Column(db.String(255), nullable=True)
    entrega = db.Column(db.String(100), nullable=True)
    recipiente = db.Column(db.String(255), nullable=True)

    situacao = db.Column(db.String(20), nullable=True, index=True)

    antibiograma = db.Column(db.String(20), nullable=True)
    exame_integrado_webservice = db.Column(db.String(20), nullable=True)
    somente_solicitacao_pep = db.Column(db.String(20), nullable=True)

    # Armazena todas as colunas originais do SPDATA
    dados_spdata = db.Column(db.JSON, nullable=True)

    criado_em = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    atualizado_em = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def __repr__(self):
        return f"<Exame {self.spdata_id} - {self.nome}>"