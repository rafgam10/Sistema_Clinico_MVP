import json
from pathlib import Path

from src.models.db.handler_fb_db import ConnectionDBFireBird


IMAGENS_SUPORTADAS = (
    (b"\xff\xd8\xff", "jpg"),
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"GIF87a", "gif"),
    (b"GIF89a", "gif"),
    (b"BM", "bmp"),
    (b"RIFF", "webp"),
)


def output_dir_padrao():
    raiz_projeto = Path(__file__).resolve().parents[3]
    return raiz_projeto / "frontend" / "public" / "img" / "convenios"


def ler_blob(blob):
    if blob is None:
        return b""
    if hasattr(blob, "read"):
        blob = blob.read()
    if isinstance(blob, bytes):
        return blob
    if isinstance(blob, bytearray):
        return bytes(blob)
    if isinstance(blob, str):
        return blob.encode("latin1")
    return bytes(blob)


def detectar_extensao(conteudo):
    for assinatura, extensao in IMAGENS_SUPORTADAS:
        if conteudo.startswith(assinatura):
            if extensao == "webp" and conteudo[8:12] != b"WEBP":
                continue
            return extensao
    return None


def exportar_logos_tiss(output_dir=None):
    output = Path(output_dir or output_dir_padrao()).resolve()
    output.mkdir(parents=True, exist_ok=True)

    resultado = {
        "lidos": 0,
        "exportados": 0,
        "sem_logo": 0,
        "ignorados": 0,
        "erros": 0,
        "output_dir": str(output),
        "index_path": str(output / "index.json"),
    }
    index = {}

    sql = """
        SELECT CONV, LOGOTIPO
        FROM TBTISS
        ORDER BY CONV
    """

    with ConnectionDBFireBird() as connection:
        cursor = connection.cursor()
        cursor.execute(sql)

        for conv, blob in cursor.fetchall():
            resultado["lidos"] += 1

            try:
                if conv is None or str(conv).strip() == "":
                    resultado["ignorados"] += 1
                    continue

                conteudo = ler_blob(blob)
                if not conteudo:
                    resultado["sem_logo"] += 1
                    continue

                extensao = detectar_extensao(conteudo)
                if not extensao:
                    resultado["ignorados"] += 1
                    continue

                codigo = int(conv)
                nome_arquivo = f"convenio-{codigo}.{extensao}"
                caminho = output / nome_arquivo
                caminho.write_bytes(conteudo)
                index[str(codigo)] = f"/img/convenios/{nome_arquivo}"
                resultado["exportados"] += 1
            except Exception:
                resultado["erros"] += 1

        cursor.close()

    (output / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return resultado
