# Oráculo de Thedas

Tire dúvidas sobre o Dragon Age (Livro Básico). Cada resposta cita a página do livro.

## Precisa de

- Docker
- Seu PDF do livro, em `data/Livro.pdf`

## Subir

```bash
docker compose up -d
```

Abra http://localhost:8000

Na primeira vez demora (baixa os modelos e indexa o livro). Depois sobe em segundos.

Se o Ollama estiver rodando no computador, a IA usa ele (mais rápido). Senão, usa um dentro do Docker.

## Celular

Na mesma rede Wi-Fi, abra `http://IP_DO_COMPUTADOR:8000`. Libere a porta 8000 no firewall.

## Parar

```bash
docker compose down
```

## Problemas

- **Porta 8000 em uso:** feche o programa que a está usando.
- **No Linux, não consigo apagar `index/` ou `static/data.js`:** são criados pelo Docker como `root`. Use `sudo rm -rf index static/data.js`.
