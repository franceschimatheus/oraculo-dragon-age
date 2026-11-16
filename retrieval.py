"""Busca híbrida: similaridade de embeddings + BM25 (palavras-chave), fundidos com Reciprocal Rank Fusion.

A mesma lógica está em static/index.html; mantenha as duas alinhadas.
"""
import math
import re
import unicodedata

import numpy as np

K1 = 1.5
B = 0.75
RRF_K = 60
STOPWORDS = {
    "a", "o", "as", "os", "um", "uma", "de", "do", "da", "dos", "das", "em", "no", "na",
    "nos", "nas", "e", "ou", "que", "pra", "para", "por", "com", "se", "eu", "voce", "meu",
    "minha", "um", "uns", "umas", "ao", "aos", "como", "qual", "quais", "é", "e", "ser",
}
# Sinônimos comuns em conversa sobre RPG que não aparecem literalmente no livro.
EXPAND = {
    "conjurar": ["lancar"],
    "usar": ["lancar"],
    "rodo": ["rolar", "rolagem"],
    "rodar": ["rolar", "rolagem"],
    "rolo": ["rolar", "rolagem"],
    "rolar": ["rolagem"],
    "dado": ["rolagem"],
}


def _stem(tok: str) -> str:
    # plural simples: feitiços -> feitico, rolagens -> rolagem
    return tok[:-1] if len(tok) > 3 and tok.endswith("s") else tok


def tokenize(text: str) -> list[str]:
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    toks = [_stem(t) for t in re.findall(r"[a-z0-9]+", text)]
    return [t for t in toks if t not in STOPWORDS]


def expand(tokens: list[str]) -> list[str]:
    out = list(tokens)
    for t in tokens:
        out.extend(EXPAND.get(t, []))
    return out


class BM25:
    def __init__(self, docs_tokens: list[list[str]]):
        self.docs = docs_tokens
        self.n = len(docs_tokens)
        self.avgdl = sum(len(d) for d in docs_tokens) / max(self.n, 1)
        self.df: dict[str, int] = {}
        for d in docs_tokens:
            for t in set(d):
                self.df[t] = self.df.get(t, 0) + 1
        self.tf = [self._counts(d) for d in docs_tokens]

    @staticmethod
    def _counts(d):
        c: dict[str, int] = {}
        for t in d:
            c[t] = c.get(t, 0) + 1
        return c

    def scores(self, query_tokens: list[str]) -> np.ndarray:
        out = np.zeros(self.n, dtype=np.float32)
        for t in set(query_tokens):
            df = self.df.get(t, 0)
            if not df:
                continue
            idf = math.log(1 + (self.n - df + 0.5) / (df + 0.5))
            for i, counts in enumerate(self.tf):
                f = counts.get(t, 0)
                if f:
                    dl = len(self.docs[i])
                    out[i] += idf * f * (K1 + 1) / (f + K1 * (1 - B + B * dl / self.avgdl))
        return out


def rrf(rankings: list[np.ndarray], n: int) -> np.ndarray:
    """Recebe listas de scores; devolve score fundido (maior = melhor)."""
    fused = np.zeros(n, dtype=np.float32)
    for scores in rankings:
        order = np.argsort(-scores)
        ranks = np.empty(n, dtype=np.int32)
        ranks[order] = np.arange(n)
        fused += 1.0 / (RRF_K + ranks + 1)
    return fused


def hybrid_search(question: str, chunks, matrix, embed_fn, bm25: BM25, k: int):
    q_vec = np.asarray(embed_fn([question])[0], dtype=np.float32)
    q_vec /= np.linalg.norm(q_vec)
    vec_scores = matrix @ q_vec

    q_tokens = expand(tokenize(question))
    kw_scores = bm25.scores(q_tokens)

    fused = rrf([vec_scores, kw_scores], len(chunks))
    top = np.argsort(-fused)[:k]
    return [(chunks[i], float(fused[i])) for i in top]
