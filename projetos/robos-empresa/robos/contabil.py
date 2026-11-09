"""Robô Contábil.

Lê o extrato do banco (CSV exportado do internet banking) e as contas a pagar,
classifica cada lançamento por categoria, fecha o mês (entradas, saídas,
resultado, por categoria) e monta o pacote para o contador com o que falta.

Não substitui o contador: organiza e entrega mastigado, e aponta o que não
conseguiu classificar para uma pessoa decidir.

Uso:  python3 robos/contabil.py [AAAA-MM] [AAAA-MM-DD hoje]
"""
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cobranca import brl, dbr  # noqa: E402
from moveri import PASTA, _data_iso, _numero_br, carregar_config  # noqa: E402


def ler_extrato(caminho: Path) -> list[dict]:
    """CSV com colunas data;descricao;valor (saída negativa)."""
    texto = caminho.read_text(encoding="utf-8-sig")
    sep = ";" if texto.splitlines()[0].count(";") >= texto.splitlines()[0].count(",") else ","
    return [
        {"data": _data_iso(l["data"]), "descricao": l["descricao"].strip(), "valor": _numero_br(l["valor"])}
        for l in csv.DictReader(texto.splitlines(), delimiter=sep) if l.get("data")
    ]


def classificar(lanc: dict, regras: dict) -> str:
    desc = lanc["descricao"].upper()
    for categoria, palavras in regras.items():
        if any(p.upper() in desc for p in palavras):
            return categoria
    return "A classificar"


def fechamento(lancs: list[dict], mes: str, regras: dict) -> dict:
    do_mes = [l for l in lancs if l["data"].startswith(mes)]
    por_cat = defaultdict(float)
    pendentes = []
    for l in do_mes:
        cat = classificar(l, regras)
        l["categoria"] = cat
        por_cat[cat] += l["valor"]
        if cat == "A classificar":
            pendentes.append(l)
    entradas = sum(l["valor"] for l in do_mes if l["valor"] > 0)
    saidas = sum(l["valor"] for l in do_mes if l["valor"] < 0)
    return {
        "mes": mes, "entradas": entradas, "saidas": saidas, "resultado": entradas + saidas,
        "categorias": dict(sorted(por_cat.items(), key=lambda kv: kv[1])),
        "pendentes": pendentes, "qtd": len(do_mes),
    }


def contas_da_semana(pagar: list[dict], hoje: date) -> list[dict]:
    fim = hoje + timedelta(days=7)
    return sorted((c for c in pagar if not c.get("pago") and date.fromisoformat(c["vencimento"]) <= fim),
                  key=lambda c: c["vencimento"])


def relatorio(f: dict, semana: list[dict], hoje: date) -> str:
    a, m = f["mes"].split("-")
    l = [f"# Fechamento contábil — {m}/{a}", "",
         f"Entradas: **{brl(f['entradas'])}**  ", f"Saídas: **{brl(-f['saidas'])}**  ",
         f"Resultado do caixa: **{brl(f['resultado'])}**", "", "## Por categoria", "",
         "| Categoria | Valor |", "|---|---:|"]
    l += [f"| {c} | {brl(v)} |" for c, v in f["categorias"].items()]
    l += ["", f"## Para uma pessoa classificar ({len(f['pendentes'])})", ""]
    l += [f"- {dbr(p['data'])} — {p['descricao']} — {brl(p['valor'])}" for p in f["pendentes"]] or ["- Nada pendente."]
    l += ["", f"## Contas a pagar até {dbr((hoje + timedelta(days=7)).isoformat())}", ""]
    for c in semana:
        atraso = " **(ATRASADA)**" if date.fromisoformat(c["vencimento"]) < hoje else ""
        l.append(f"- {dbr(c['vencimento'])} — {c['descricao']} — {brl(c['valor'])}{atraso}")
    if not semana:
        l.append("- Nenhuma.")
    l += ["", "## Pacote para o contador", "",
          f"- Extrato do mês com {f['qtd']} lançamentos classificados (anexo).",
          "- Conferir: notas fiscais de entrada e saída do mês, guia do Simples (DAS), folha/pró-labore.",
          "- Itens 'A classificar' acima precisam de resposta antes de enviar."]
    return "\n".join(l) + "\n"


def main() -> None:
    cfg = carregar_config()
    hoje = date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else date.today()
    mes = sys.argv[1] if len(sys.argv) > 1 else hoje.strftime("%Y-%m")
    c = cfg["contabil"]
    f = fechamento(ler_extrato(PASTA / c["arquivo_extrato"]), mes, c["regras"])
    pagar = json.loads((PASTA / c["arquivo_contas_pagar"]).read_text(encoding="utf-8"))
    saida = PASTA / "saida" / f"contabil-{mes}.md"
    saida.write_text(relatorio(f, contas_da_semana(pagar, hoje), hoje), encoding="utf-8")
    print(f"{f['qtd']} lançamentos, resultado {brl(f['resultado'])}, {len(f['pendentes'])} a classificar -> {saida}")


if __name__ == "__main__":
    main()
