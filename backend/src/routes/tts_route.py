import asyncio
import io

from flask import Blueprint, Response, current_app, jsonify, request


tts_bp = Blueprint("tts", __name__, url_prefix="/tts")

MAX_TTS_TEXT_LENGTH = 240
VOICES = {
    "antonio": "pt-BR-AntonioNeural",
    "francisca": "pt-BR-FranciscaNeural",
}
DEFAULT_VOICE = "antonio"


async def _gerar_audio_edge_tts(texto, voice):
    import edge_tts

    communicate = edge_tts.Communicate(texto, voice)
    buffer = io.BytesIO()

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buffer.write(chunk["data"])

    return buffer.getvalue()


@tts_bp.route("/speak", methods=["POST"])
def speak():
    body = request.get_json(silent=True) or {}
    texto = str(body.get("text") or "").strip()
    voice_key = str(body.get("voice") or DEFAULT_VOICE).strip().casefold()

    if not texto:
        return jsonify({"error": "Campo 'text' é obrigatório"}), 400

    if len(texto) > MAX_TTS_TEXT_LENGTH:
        error = f"Campo 'text' deve ter até {MAX_TTS_TEXT_LENGTH} caracteres"
        return (
            jsonify({"error": error}),
            400,
        )

    voice = VOICES.get(voice_key)
    if not voice:
        return jsonify({"error": "Voz inválida"}), 400

    try:
        audio_bytes = asyncio.run(_gerar_audio_edge_tts(texto, voice))
    except ModuleNotFoundError as e:
        if e.name != "edge_tts":
            raise

        current_app.logger.exception("Dependência edge-tts indisponível")
        return jsonify({"error": "Dependência edge-tts não instalada"}), 500
    except Exception:
        current_app.logger.exception("Falha ao gerar TTS")
        return jsonify({"error": "Erro ao gerar TTS"}), 500

    if not audio_bytes:
        return jsonify({"error": "Nenhum áudio gerado"}), 500

    return Response(
        audio_bytes,
        mimetype="audio/mpeg",
        headers={
            "Content-Disposition": "inline",
            "Cache-Control": "no-store",
        },
    )
