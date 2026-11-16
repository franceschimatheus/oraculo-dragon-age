# Oráculo de Thedas

Tire dúvidas sobre as regras do Dragon Age (Livro Básico). As respostas usam o texto do livro, citam a página de onde saíram e rodam **no seu computador**, com o Gemma 4 via Ollama. Nada vai para a internet depois que os modelos são baixados.

## O que você precisa

- **Docker** com o comando `docker compose` (Compose v2): Docker Desktop no Windows/Mac, ou Docker Engine + plugin Compose no Linux. É só isso.
- O **PDF do Livro Básico** de Dragon Age. Ele não vem neste repositório, então use o seu exemplar.
- Cerca de **10 GB** livres no disco (os modelos de IA).
- Portas **8000** e **11434** livres no computador.

## Subir tudo (3 passos)

**1. Coloque o PDF em `data/` com o nome `Livro.pdf`.**

```
oraculo-dragon-age/
└── data/
    └── Livro.pdf
```

**2. Suba os serviços.** Na pasta do projeto, rode:

```bash
docker compose up -d
```

Na primeira vez, o Docker baixa as imagens e os modelos de IA e depois indexa o livro. Isso leva bastante tempo, principalmente sem placa de vídeo. Para acompanhar:

```bash
docker compose logs -f ingest
```

Quando a linha `índice salvo` aparecer, a indexação terminou.

**3. Abra no navegador:** http://localhost:8000

## Usar no celular

Com o celular na **mesma rede Wi-Fi** do computador, abra `http://IP_DO_COMPUTADOR:8000`. O IP aparece com `ipconfig` (Windows) ou `ip addr` (Linux/Mac). Se não conectar, libere as portas 8000 e 11434 no firewall para redes privadas.

## Comandos úteis

| O que fazer | Comando |
|---|---|
| Parar tudo | `docker compose down` |
| Subir de novo (depois de parar) | `docker compose up -d` |
| Ver se está rodando | `docker compose ps` |
| Apagar tudo, inclusive os modelos baixados | `docker compose down -v` |
| Refazer o índice (ex.: trocou o PDF) | apague `static/data.js` e `index/` e rode `docker compose up -d` de novo |

## Problemas comuns

- **"port is already allocated" / porta em uso:** outro programa usa a 8000 ou a 11434. Feche-o (por exemplo, o Ollama instalado direto no Windows, que usa a mesma porta 11434) e rode o comando de novo.
- **A página abre mas a IA não responde:** confira `docker compose ps`. O serviço `ollama` precisa estar `healthy`. Veja também `docker compose logs models`, que mostra o download dos modelos.
- **No Linux, não consigo apagar `index/` ou `static/data.js`:** esses arquivos são criados pelo container e ficam com dono `root`. Apague com `sudo rm -rf index static/data.js` (ou use `sudo chown -R $USER .` para recuperar a pasta).
- **Respostas lentas:** sem placa de vídeo, o Gemma roda na CPU. Para usar uma GPU NVIDIA, instale o *NVIDIA Container Toolkit* e descomente a seção `deploy` do serviço `ollama` no `docker-compose.yml`.

## Como funciona (resumo)

- **`ollama`**: roda o Gemma 4 (`gemma4:e4b`) e o modelo de busca (`bge-m3`).
- **`models`**: baixa esses dois modelos (executa uma vez).
- **`ingest`**: lê o PDF, quebra em trechos com número de página e gera os vetores da busca. Só roda se o índice ainda não existir.
- **`web`**: entrega a página do chat (pasta `static/`).

A busca combina similaridade de significado com busca por palavras-chave. Os trechos mais relevantes vão para o Gemma, que escreve a resposta citando as páginas.

---

## Para quem mexe no código (sem Docker)

Precisa de Python 3.12+ e do Ollama instalado no computador.

```bash
pip install -r requirements.txt
ollama pull gemma4:e4b
ollama pull bge-m3
python ingest.py "caminho/para/Livro.pdf"
python build_web_data.py
```

Depois sirva a pasta `static/` com um servidor simples. No Windows, `serve.bat` faz isso; no Linux e no Mac, rode `python -m http.server 8000` dentro de `static/` e abra `http://localhost:8000`. Para abrir o arquivo direto do disco, o Ollama precisa aceitar a origem `null` (variável `OLLAMA_ORIGINS`).

Arquivos principais: `ingest.py` (PDF → trechos e vetores), `retrieval.py` (busca híbrida), `ask.py` (pergunta pelo terminal), `common.py` (conversa com o Ollama), `build_web_data.py` (gera `static/data.js`), `static/index.html` (a interface).
