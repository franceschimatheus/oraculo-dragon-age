"""Indexa o PDF do Dragon Age: extrai texto por página, quebra em trechos e gera embeddings locais via Ollama.

Uso:
    python ingest.py "C:/caminho/Livro.pdf"

Gera index/chunks.json (texto + página) e index/embeddings.npy (vetores).
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np
from pypdf import PdfReader

from common import EMBED_MODEL, INDEX_DIR, embed

CHUNK_SIZE = 1200   # caracteres por trecho
OVERLAP = 150       # sobreposição entre trechos da mesma página
BATCH = 16


def clean(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)        # ligaturas: ﬁ -> fi, ﬂ -> fl
    # letra capitular separada em títulos: "M ESTRE" -> "MESTRE", "D ESTREZA" -> "DESTREZA"
    text = re.sub(r"\b([BCDFGHJKLMNPQRSTVWXZÇ]) ([A-ZÀ-Ú]{2,})\b", r"\1\2", text)
    text = text.replace("\u00ad", "")                 # hífen de quebra de linha invisível
    text = re.sub(r"-\n(\w)", r"\1", text)            # palavra partida por hífen no fim da linha
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_page(text: str):
    if len(text) <= CHUNK_SIZE:
        return [text] if text else []
    out, start = [], 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        if end < len(text):
            # tenta cortar em fim de frase/parágrafo para não quebrar no meio
            cut = text.rfind("\n", start + CHUNK_SIZE // 2, end)
            if cut == -1:
                cut = text.rfind(". ", start + CHUNK_SIZE // 2, end)
            if cut == -1:
                cut = text.rfind(" ", start + CHUNK_SIZE // 2, end) - 1  # nunca corta uma palavra
            if cut != -1:
                end = cut + 1
        out.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - OVERLAP, start + 1)
        # a sobreposição começa numa palavra inteira (evita "6 + MAGIA" no lugar de "3D6 + MAGIA")
        if 0 < start < len(text) and not text[start - 1].isspace():
            sp = text.rfind(" ", max(0, start - 40), start)  # recua até o começo da palavra cortada
            if sp != -1:
                start = sp + 1
    return [c for c in out if c]


def main(pdf_path: str):
    reader = PdfReader(pdf_path)
    chunks = []
    for page_num, page in enumerate(reader.pages, start=1):
        text = clean(page.extract_text() or "")
        if len(text) < 40:   # capa, páginas em branco, ilustrações
            continue
        for piece in chunk_page(text):
            chunks.append({"id": len(chunks), "page": page_num, "text": piece})
    print(f"{len(reader.pages)} páginas -> {len(chunks)} trechos")

    vectors = []
    for i in range(0, len(chunks), BATCH):
        batch = [c["text"] for c in chunks[i:i + BATCH]]
        vectors.extend(embed(batch))
        print(f"embeddings: {min(i + BATCH, len(chunks))}/{len(chunks)}", end="\r")
    print()

    INDEX_DIR.mkdir(exist_ok=True)
    (INDEX_DIR / "chunks.json").write_text(json.dumps(chunks, ensure_ascii=False), encoding="utf-8")
    matrix = np.asarray(vectors, dtype=np.float32)
    matrix /= np.linalg.norm(matrix, axis=1, keepdims=True)
    np.save(INDEX_DIR / "embeddings.npy", matrix)
    (INDEX_DIR / "meta.json").write_text(
        json.dumps({"source": Path(pdf_path).name, "embed_model": EMBED_MODEL, "chunks": len(chunks)}),
        encoding="utf-8",
    )
    print(f"índice salvo em {INDEX_DIR}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit('uso: python ingest.py "caminho/Livro.pdf"')
    main(sys.argv[1])
