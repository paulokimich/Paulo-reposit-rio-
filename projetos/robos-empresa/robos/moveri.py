"""Conexão com a Moveri.

Enquanto não temos a documentação da API, o robô lê dados de exemplo
(`dados/exemplo_contas_receber.json`). Quando a documentação chegar, só esta
camada muda: os robôs de cobrança e resumo continuam iguais.

Formato interno de uma conta a receber (o que os robôs esperam):
    {
      "id": "123",
      "cliente": "Nome do cliente",
      "telefone": "65999990000",      # só dígitos, com DDD
      "valor": 450.00,
      "vencimento": "2026-11-10",     # AAAA-MM-DD
      "pago": false,
      "documento": "Boleto 123"       # opcional
    }
"""
from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

PASTA = Path(__file__).resolve().parent.parent


def carregar_config() -> dict:
    caminho = PASTA / "config.json"
    if not caminho.exists():
        caminho = PASTA / "config.example.json"
    return json.loads(caminho.read_text(encoding="utf-8"))


def contas_a_receber(config: dict) -> list[dict]:
    fonte = config.get("fonte", "exemplo")
    if fonte == "exemplo":
        arquivo = PASTA / config.get("arquivo_exemplo", "dados/exemplo_contas_receber.json")
        return json.loads(arquivo.read_text(encoding="utf-8"))
    if fonte == "planilha":
        return _contas_da_planilha(PASTA / config["arquivo_planilha"], config.get("colunas_planilha", {}))
    if fonte == "api":
        return _contas_da_api(config["moveri"])
    raise ValueError(f"fonte desconhecida: {fonte}")


def _numero_br(txt: str) -> float:
    t = str(txt).replace("R$", "").strip()
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    return float(t or 0)


def _data_iso(txt: str) -> str:
    t = str(txt).strip()[:10]
    if "/" in t:
        d, m, a = t.split("/")
        return f"{a}-{int(m):02d}-{int(d):02d}"
    return t


def _contas_da_planilha(caminho: Path, colunas: dict) -> list[dict]:
    """Plano B: planilha CSV exportada do sistema (separador ; ou ,).

    `colunas` mapeia nome interno -> cabeçalho da planilha. Aceita valor no
    formato 1.234,56 e data DD/MM/AAAA. Coluna "pago" vale sim/s/pago/1.
    """
    import csv
    texto = caminho.read_text(encoding="utf-8-sig")
    dialeto = csv.Sniffer().sniff(texto.splitlines()[0], delimiters=";,")
    col = {k: colunas.get(k, k) for k in ("id", "cliente", "telefone", "valor", "vencimento", "pago", "documento")}
    contas = []
    for i, linha in enumerate(csv.DictReader(texto.splitlines(), dialect=dialeto), 1):
        if not linha.get(col["cliente"]):
            continue
        contas.append({
            "id": str(linha.get(col["id"]) or i),
            "cliente": linha[col["cliente"]].strip(),
            "telefone": "".join(ch for ch in str(linha.get(col["telefone"], "")) if ch.isdigit()),
            "valor": _numero_br(linha.get(col["valor"], 0)),
            "vencimento": _data_iso(linha[col["vencimento"]]),
            "pago": str(linha.get(col["pago"], "")).strip().lower() in ("sim", "s", "pago", "1", "true"),
            "documento": (linha.get(col["documento"]) or "").strip(),
            "forma_pagamento": (linha.get(colunas.get("forma_pagamento", "forma_pagamento")) or "").strip(),
            "link_boleto": (linha.get(colunas.get("link_boleto", "link_boleto")) or "").strip(),
        })
    return contas


def _contas_da_api(cfg: dict) -> list[dict]:
    """Busca na API da Moveri e converte para o formato interno.

    PENDENTE: preencher endpoint, autenticação e nomes dos campos quando a
    documentação chegar. A chave NUNCA fica no repositório: vem da variável
    de ambiente indicada em `cfg["variavel_chave"]` ou é injetada pelo proxy.
    """
    url = cfg["url_base"].rstrip("/") + cfg["endpoint_contas_receber"]
    req = urllib.request.Request(url)
    chave = os.environ.get(cfg.get("variavel_chave", "MOVERI_API_KEY"), "")
    if chave:
        req.add_header(cfg.get("cabecalho_chave", "Authorization"), cfg.get("prefixo_chave", "Bearer ") + chave)
    with urllib.request.urlopen(req, timeout=30) as resp:
        brutos = json.load(resp)
    campos = cfg["campos"]  # mapa: nome interno -> nome na API
    itens = brutos.get(cfg.get("chave_lista", "data"), brutos) if isinstance(brutos, dict) else brutos
    return [
        {
            "id": str(b.get(campos["id"], "")),
            "cliente": b.get(campos["cliente"], ""),
            "telefone": "".join(ch for ch in str(b.get(campos["telefone"], "")) if ch.isdigit()),
            "valor": float(b.get(campos["valor"], 0)),
            "vencimento": str(b.get(campos["vencimento"], ""))[:10],
            "pago": bool(b.get(campos["pago"], False)),
            "documento": b.get(campos.get("documento", ""), ""),
        }
        for b in itens
    ]
