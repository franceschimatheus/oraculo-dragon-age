"""Carrega o modelo de chat e o de embeddings na memória do Ollama antes do primeiro uso.

keep_alive = -1 mantém os modelos carregados até o Ollama ser reiniciado, então a primeira
pergunta da página não paga o tempo de carregamento.
"""
from common import CHAT_MODEL, EMBED_MODEL, OLLAMA_URL, _post


def main():
    print(f"aquecendo {CHAT_MODEL} em {OLLAMA_URL} ...", flush=True)
    # o contexto precisa ser o mesmo que a página usa (8192); outro valor recarrega o modelo
    _post("/api/generate", {"model": CHAT_MODEL, "prompt": "", "keep_alive": -1,
                            "options": {"num_ctx": 8192}})  # prompt vazio só carrega
    print(f"aquecendo {EMBED_MODEL} ...", flush=True)
    _post("/api/embed", {"model": EMBED_MODEL, "input": ["aquecimento"], "keep_alive": -1})
    print("modelos carregados", flush=True)


if __name__ == "__main__":
    main()
