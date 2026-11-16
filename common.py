"""Funções compartilhadas: conversa com o Ollama local (embeddings e geração)."""
import json
import urllib.request
from pathlib import Path

import os


def _pick_ollama() -> str:
    """Usa o primeiro Ollama que responder. No Docker: host primeiro, depois o container."""
    candidates = os.environ.get("OLLAMA_CANDIDATES", "http://localhost:11434").split(",")
    for url in candidates:
        try:
            urllib.request.urlopen(url.strip() + "/api/tags", timeout=2)
            return url.strip()
        except Exception:
            continue
    return candidates[0].strip()  # nenhum respondeu: falha depois, com mensagem clara


OLLAMA_URL = _pick_ollama()
EMBED_MODEL = "bge-m3"           # embeddings multilíngues (bom para português)
CHAT_MODEL = "gemma4:e4b"        # Gemma 4 local (modelo menor e mais rápido)
INDEX_DIR = Path(__file__).parent / "index"


def _post(path: str, payload: dict) -> dict:
    req = urllib.request.Request(
        OLLAMA_URL + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=600) as resp:
        return json.loads(resp.read().decode("utf-8"))


def embed(texts: list[str]) -> list[list[float]]:
    return _post("/api/embed", {"model": EMBED_MODEL, "input": texts})["embeddings"]


def chat(system: str, user: str, model: str = CHAT_MODEL) -> str:
    data = _post("/api/chat", {
        "model": model,
        "stream": False,
        "think": False,          # Gemma 4 gasta o limite de tokens "pensando" e devolve resposta vazia
        "keep_alive": -1,        # mantém o modelo carregado; recarregar custa ~10 s
        "options": {
            "temperature": 0,
            "num_ctx": 8192,     # padrão do Ollama é 4096, pequeno para 6-10 trechos
        },
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    })
    return data["message"]["content"]
