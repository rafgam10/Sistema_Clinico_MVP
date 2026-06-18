from flask import Blueprint, request, jsonify

from src.settings.extensions import db
from src.models.model_padroes_solicitacoes.modelo_receita_model import ModeloReceita
from src.models.model_padroes_solicitacoes.medicamentos_para_modelo_receita_model import Medicamentos

padrao_medico_bp = Blueprint("padroes_medicos", __name__, url_prefix="/padroes_medicos")


def _padrao_receita_to_dict(padrao):
    return {
        **padrao._to_dict(),
        "medicamentos": [
            medicamento._to_dict()
            for medicamento in padrao.medicamentos
        ]
    }


@padrao_medico_bp.route("/criar_padrao_medico", methods=["POST"])
def create_padrao_medico():
    try:
        data = request.get_json() or {}
        nome_modelo = (data.get("nome_modelo") or "").strip()

        if not nome_modelo:
            return jsonify({"error": "Campo nome_modelo é obrigatório"}), 400

        new_padrao_medico = ModeloReceita(nome_modelo)
        db.session.add(new_padrao_medico)
        db.session.commit()

        return jsonify(new_padrao_medico._to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@padrao_medico_bp.route("/add_medicamento_padrao_medico/<int:id_padrao_medico>", methods=["POST"])
def add_medicamento_padrao_medico(id_padrao_medico: int):
    try:
        padrao = db.session.query(ModeloReceita).filter(ModeloReceita.id == id_padrao_medico).first()

        if not padrao:
            return jsonify({"error": "Padrão médico não encontrado"}), 404

        data = request.get_json() or {}

        nome_medicamento = (data.get("nome_medicamento") or "").strip()
        dosagem = (data.get("dosagem") or "").strip()
        detalhes = data.get("detalhes")

        if not nome_medicamento:
            return jsonify({"error": "Campo nome_medicamento é obrigatório"}), 400

        if not dosagem:
            return jsonify({"error": "Campo dosagem é obrigatório"}), 400

        new_medicamento = Medicamentos(nome_medicamento, dosagem, detalhes, id_padrao_medico)

        db.session.add(new_medicamento)
        db.session.commit()

        return jsonify(new_medicamento._to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


### ROTAS DE GET

@padrao_medico_bp.route("/lista_padroes_medicos_receitas", methods=["GET"])
def lista_padroes_medicos_receita():
    try:
        lista_padroes_receitas = db.session.query(ModeloReceita).all()

        return jsonify({
            "padroes_receitas": [
                _padrao_receita_to_dict(padrao)
                for padrao in lista_padroes_receitas
            ]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@padrao_medico_bp.route("/padrao_medico_receita/<int:id>", methods=["GET"])
def detalhes_padrao_medico_receita(id: int):
    try:
        detalhe_padrao_receita_select = db.session.query(ModeloReceita).filter(ModeloReceita.id == id).first()

        if not detalhe_padrao_receita_select:
            return jsonify({"error": "Padrão médico não encontrado"}), 404

        return jsonify(_padrao_receita_to_dict(detalhe_padrao_receita_select)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


### ROTAS DE UPDATE

@padrao_medico_bp.route("/editar_padrao_medico/<int:id>", methods=["PUT", "PATCH"])
def editar_padrao_medico(id: int):
    try:
        padrao = db.session.query(ModeloReceita).filter(ModeloReceita.id == id).first()

        if not padrao:
            return jsonify({"error": "Padrão médico não encontrado"}), 404

        data = request.get_json() or {}
        nome_modelo = (data.get("nome_modelo") or "").strip()

        if not nome_modelo:
            return jsonify({"error": "Campo nome_modelo é obrigatório"}), 400

        padrao.nome_modelo = nome_modelo

        db.session.commit()

        return jsonify(_padrao_receita_to_dict(padrao)), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@padrao_medico_bp.route("/editar_medicamento_padrao_medico/<int:id>", methods=["PUT", "PATCH"])
def editar_medicamento_padrao_medico(id: int):
    try:
        medicamento = db.session.query(Medicamentos).filter(Medicamentos.id == id).first()

        if not medicamento:
            return jsonify({"error": "Medicamento não encontrado"}), 404

        data = request.get_json() or {}
        campos_atualizados = False

        if "nome_medicamento" in data:
            nome_medicamento = (data.get("nome_medicamento") or "").strip()

            if not nome_medicamento:
                return jsonify({"error": "Campo nome_medicamento não pode ser vazio"}), 400

            medicamento.nome_medicamento = nome_medicamento
            campos_atualizados = True

        if "dosagem" in data:
            dosagem = (data.get("dosagem") or "").strip()

            if not dosagem:
                return jsonify({"error": "Campo dosagem não pode ser vazio"}), 400

            medicamento.dosagem = dosagem
            campos_atualizados = True

        if "detalhes" in data:
            medicamento.detalhes = data.get("detalhes")
            campos_atualizados = True

        if not campos_atualizados:
            return jsonify({"error": "Nenhum campo válido informado para atualização"}), 400

        db.session.commit()

        return jsonify(medicamento._to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


### ROTAS DE DELETE

@padrao_medico_bp.route("/deletar_padrao_medico/<int:id>", methods=["DELETE"])
def deletar_padrao_medico(id: int):
    try:
        padrao = db.session.query(ModeloReceita).filter(ModeloReceita.id == id).first()

        if not padrao:
            return jsonify({"error": "Padrão médico não encontrado"}), 404

        db.session.delete(padrao)
        db.session.commit()

        return jsonify({"message": "Padrão médico deletado com sucesso"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@padrao_medico_bp.route("/deletar_medicamento_padrao_medico/<int:id>", methods=["DELETE"])
def deletar_medicamento_padrao_medico(id: int):
    try:
        medicamento = db.session.query(Medicamentos).filter(Medicamentos.id == id).first()

        if not medicamento:
            return jsonify({"error": "Medicamento não encontrado"}), 404

        db.session.delete(medicamento)
        db.session.commit()

        return jsonify({"message": "Medicamento deletado com sucesso"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
