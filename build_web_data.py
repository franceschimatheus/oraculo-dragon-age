"""Converte o índice (index/) em static/data.js, para a página HTML carregar sem servidor.

Uso:
    python build_web_data.py
"""
import base64
import json
from pathlib import Path

import numpy as np

INDEX = Path(__file__).parent / "index"
OUT = Path(__file__).parent / "static" / "data.js"

chunks = json.loads((INDEX / "chunks.json").read_text(encoding="utf-8"))
matrix = np.load(INDEX / "embeddings.npy").astype(np.float32)
meta = json.loads((INDEX / "meta.json").read_text(encoding="utf-8"))

payload = {
    "meta": meta,
    "dim": int(matrix.shape[1]),
    "chunks": [{"page": c["page"], "text": c["text"]} for c in chunks],
    "embeddings": base64.b64encode(matrix.tobytes()).decode("ascii"),
}
OUT.write_text("window.ORACULO = " + json.dumps(payload, ensure_ascii=False) + ";\n", encoding="utf-8")
print(f"{len(chunks)} trechos -> {OUT} ({OUT.stat().st_size / 1e6:.1f} MB)")
