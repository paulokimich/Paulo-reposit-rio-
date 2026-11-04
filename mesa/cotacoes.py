#!/usr/bin/env python3
"""Mesa de Operações do Paulo — coleta de cotações e sinais simples.

Uso:  python3 mesa/cotacoes.py            (relatório no terminal + arquivo em mesa/relatorios/)
      python3 mesa/cotacoes.py --sem-arquivo

Fontes gratuitas, sem chave:
  - Moedas: AwesomeAPI (economia.awesomeapi.com.br)
  - Ações B3: Yahoo Finance (ticker + ".SA")
Só usa a biblioteca padrão do Python. Nada aqui compra ou vende: a mesa só informa, quem decide e assina é o Paulo.
"""
import datetime as dt
import json
import pathlib
import sys
import urllib.request

BASE = pathlib.Path(__file__).resolve().parent
UA = {"User-Agent": "Mozilla/5.0 (mesa-paulo)"}


def baixar_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def media(valores, n):
    v = [x for x in valores if x is not None][-n:]
    return sum(v) / len(v) if len(v) == n else None


def moedas(pares):
    if not pares:
        return {}
    dados = baixar_json("https://economia.awesomeapi.com.br/json/last/" + ",".join(pares))
    out = {}
    for par in pares:
        d = dados.get(par.replace("-", ""))
        if d:
            out[par] = {"preco": float(d["bid"]), "var_dia_pct": float(d["pctChange"])}
    return out


def acao(ticker):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}.SA?range=6mo&interval=1d"
    res = baixar_json(url)["chart"]["result"][0]
    fech = res["indicators"]["quote"][0]["close"]
    fech = [x for x in fech if x is not None]
    preco = res["meta"].get("regularMarketPrice", fech[-1])
    anterior = fech[-2] if len(fech) > 1 else preco
    return {
        "preco": preco,
        "var_dia_pct": (preco / anterior - 1) * 100 if anterior else 0.0,
        "mm20": media(fech, 20),
        "mm50": media(fech, 50),
        "max_6m": max(fech),
        "min_6m": min(fech),
    }


def tendencia(d):
    """Sinal do agente Tendência: cruzamento de médias móveis (simples, não é recomendação)."""
    p, m20, m50 = d["preco"], d.get("mm20"), d.get("mm50")
    if m20 is None or m50 is None:
        return "sem dados"
    if p > m20 > m50:
        return "alta"
    if p < m20 < m50:
        return "baixa"
    return "lateral"


def alertas(nome, preco, regra):
    msgs = []
    if regra.get("alerta_abaixo") is not None and preco <= regra["alerta_abaixo"]:
        msgs.append(f"🔻 {nome} em {preco:.2f}, abaixo do alerta {regra['alerta_abaixo']:.2f}")
    if regra.get("alerta_acima") is not None and preco >= regra["alerta_acima"]:
        msgs.append(f"🔺 {nome} em {preco:.2f}, acima do alerta {regra['alerta_acima']:.2f}")
    return msgs


def montar_relatorio(cfg, cot_moedas, cot_acoes, erros):
    agora = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    linhas = [f"# Relatório da Mesa — {agora}", "", "## Câmbio", "",
              "| Par | Preço | Var. dia |", "|---|---|---|"]
    avisos = []
    for par, d in cot_moedas.items():
        linhas.append(f"| {par} | R$ {d['preco']:.4f} | {d['var_dia_pct']:+.2f}% |")
        avisos += alertas(par, d["preco"], cfg["moedas"][par])
    linhas += ["", "## Ações", "",
               "| Ativo | Preço | Var. dia | MM20 | MM50 | Mín/Máx 6m | Tendência |",
               "|---|---|---|---|---|---|---|"]
    for t, d in cot_acoes.items():
        f = lambda x: f"{x:.2f}" if x is not None else "-"
        linhas.append(f"| {t} | R$ {d['preco']:.2f} | {d['var_dia_pct']:+.2f}% | {f(d['mm20'])} | "
                      f"{f(d['mm50'])} | {d['min_6m']:.2f} / {d['max_6m']:.2f} | {tendencia(d)} |")
        avisos += alertas(t, d["preco"], cfg["acoes"][t])
    linhas += ["", "## Alertas", ""] + ([f"- {a}" for a in avisos] or ["- Nenhum alerta disparado."])
    if erros:
        linhas += ["", "## Falhas de coleta", ""] + [f"- {e}" for e in erros]
    linhas += ["", "_Sinais automáticos e simples. Não são recomendação. Quem decide e assina é o Paulo._"]
    return "\n".join(linhas)


def main():
    cfg = json.loads((BASE / "carteira.json").read_text(encoding="utf-8"))
    erros, cot_acoes = [], {}
    try:
        cot_moedas = moedas(list(cfg.get("moedas", {})))
    except Exception as e:
        cot_moedas = {}
        erros.append(f"moedas: {e}")
    for t in cfg.get("acoes", {}):
        try:
            cot_acoes[t] = acao(t)
        except Exception as e:
            erros.append(f"{t}: {e}")
    rel = montar_relatorio(cfg, cot_moedas, cot_acoes, erros)
    print(rel)
    if "--sem-arquivo" not in sys.argv:
        destino = BASE / "relatorios" / (dt.date.today().isoformat() + ".md")
        destino.write_text(rel + "\n", encoding="utf-8")
        print(f"\nSalvo em {destino}")


if __name__ == "__main__":
    main()
