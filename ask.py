"""Faz uma pergunta sobre o livro, pelo terminal.

Uso:
    python ask.py "Como funciona o teste de Força?"
    python ask.py "sua pergunta" --k 6 --show-context
"""
import argparse
import json

import numpy as np

from common import CHAT_MODEL, INDEX_DIR, chat, embed
from retrieval import BM25, hybrid_search, tokenize

SYSTEM = """Você é um assistente de regras do RPG Dragon Age (Livro Básico).
Responda em português, usando APENAS os trechos do livro fornecidos abaixo.
- Procure nos trechos a regra que responde à pergunta, mesmo que ela use outras palavras (por exemplo "rolar" = "rolagem", "conjurar" = "lançar").
- Se a regra estiver em mais de um trecho, junte as informações.
- Cite a página de cada informação no formato (p. N).
- Se a resposta não estiver nos trechos, diga que não encontrou no livro e não invente regras.
- Copie fórmulas, valores e nomes exatamente como estão no texto."""

DEFAULT_K = 6  # trechos enviados ao Gemma


def load_index():
    chunks = json.loads((INDEX_DIR / "chunks.json").read_text(encoding="utf-8"))
    matrix = np.load(INDEX_DIR / "embeddings.npy")
    bm25 = BM25([tokenize(c["text"]) for c in chunks])
    return chunks, matrix, bm25


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    parser.add_argument("--model", default=CHAT_MODEL)
    parser.add_argument("--k", type=int, default=DEFAULT_K)
    parser.add_argument("--show-context", action="store_true")
    args = parser.parse_args()

    chunks, matrix, bm25 = load_index()
    hits = hybrid_search(args.question, chunks, matrix, embed, bm25, args.k)

    context = "\n\n".join(f"[p. {c['page']}]\n{c['text']}" for c, _ in hits)
    if args.show_context:
        print("páginas:", [c["page"] for c, _ in hits])
        print()

    user = f"Trechos do livro:\n\n{context}\n\nPergunta: {args.question}"
    print(chat(SYSTEM, user, model=args.model))


if __name__ == "__main__":
    main()
