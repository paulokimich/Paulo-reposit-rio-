"""Robô Gerente / Financeiro: resumo do dia para o dono.

Por enquanto usa só contas a receber. Quando a API da Moveri mostrar caixa,
contas a pagar e vendas, este resumo ganha essas linhas.

Uso:  python3 robos/resumo.py [AAAA-MM-DD]
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cobranca import brl, dbr  # noqa: E402
from moveri import PASTA, carregar_config, contas_a_receber  # noqa: E402


def resumo(contas: list[dict], hoje: date) -> dict:
    abertas = [c for c in contas if not c.get("pago")]
    venc = lambda c: date.fromisoformat(c["vencimento"])  # noqa: E731
    vencidas = [c for c in abertas if venc(c) < hoje]
    return {
        "data": hoje.isoformat(),
        "vencido": sum(c["valor"] for c in vencidas),
        "qtd_vencido": len(vencidas),
        "vence_hoje": sum(c["valor"] for c in abertas if venc(c) == hoje),
        "vence_7d": sum(c["valor"] for c in abertas if hoje < venc(c) <= hoje + timedelta(days=7)),
        "maiores": sorted(vencidas, key=lambda c: -c["valor"])[:5],
        "lojas": ranking_lojas(contas, hoje),
    }


def ranking_lojas(contas: list[dict], hoje: date) -> list[dict]:
    """Inadimplência por loja: % do valor em aberto que já venceu há mais de 10 dias."""
    lojas: dict[str, dict] = {}
    for c in contas:
        if c.get("pago"):
            continue
        l = lojas.setdefault(c.get("loja") or "sem loja", {"loja": c.get("loja") or "sem loja", "aberto": 0.0, "atraso10": 0.0})
        l["aberto"] += c["valor"]
        if (hoje - date.fromisoformat(c["vencimento"])).days > 10:
            l["atraso10"] += c["valor"]
    for l in lojas.values():
        l["pct"] = round(100 * l["atraso10"] / l["aberto"], 1) if l["aberto"] else 0.0
    return sorted(lojas.values(), key=lambda x: -x["pct"])


def texto(r: dict) -> str:
    l = [f"Resumo da empresa — {dbr(r['data'])}", "",
         f"Vencido e não pago: {brl(r['vencido'])} ({r['qtd_vencido']} contas)",
         f"Vence hoje: {brl(r['vence_hoje'])}",
         f"Vence nos próximos 7 dias: {brl(r['vence_7d'])}"]
    if len(r.get("lojas", [])) > 1:
        l += ["", "Lojas com mais atraso (+10 dias, % do valor em aberto):"]
        l += [f"- {x['loja']}: {x['pct']}% ({brl(x['atraso10'])} de {brl(x['aberto'])})" for x in r["lojas"][:5]]
    if r["maiores"]:
        l += ["", "Maiores atrasos:"]
        l += [f"- {c['cliente']}: {brl(c['valor'])} (venceu {dbr(c['vencimento'])})" for c in r["maiores"]]
    return "\n".join(l) + "\n"


def main() -> None:
    hoje = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
    r = resumo(contas_a_receber(carregar_config()), hoje)
    saida = PASTA / "saida" / f"resumo-{hoje.isoformat()}.md"
    saida.write_text(texto(r), encoding="utf-8")
    print(texto(r))


if __name__ == "__main__":
    main()
