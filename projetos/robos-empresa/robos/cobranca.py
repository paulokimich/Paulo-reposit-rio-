"""Robô de Cobrança.

Lê as contas a receber, aplica a régua de cobrança e gera a lista do dia com
mensagem pronta e link do WhatsApp (wa.me). Na fase 1 uma pessoa da empresa
clica no link e envia: custo zero e nada sai sem alguém ver.

Regras (CDC art. 42 e LGPD): tom educado, sem ameaça, só para o próprio
cliente, envio em horário comercial, sem expor a dívida a terceiros.

Uso:  python3 robos/cobranca.py [AAAA-MM-DD]
"""
from __future__ import annotations

import sys
import urllib.parse
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from moveri import PASTA, carregar_config, contas_a_receber  # noqa: E402


def brl(v: float) -> str:
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def dbr(iso: str) -> str:
    a, m, d = iso.split("-")
    return f"{d}/{m}/{a}"


def etapa(dias: int, regua: dict) -> str | None:
    """dias = hoje - vencimento (negativo = ainda vai vencer)."""
    if dias in regua.get("lembrete_antes", []):
        return "lembrete"
    if dias == 0:
        return "vence_hoje"
    if dias in regua.get("atraso", []):
        return "atraso"
    if dias >= regua.get("passar_para_humano", 15):
        return "humano"
    return None


def mensagem(conta: dict, tipo: str, dias: int, empresa: dict) -> str:
    palavras = conta["cliente"].upper().replace(".", " ").split()
    empresa_pj = any(p in palavras for p in ("LTDA", "ME", "EIRELI", "SA", "EPP", "TRANSPORTES", "FAZENDA", "OFICINA"))
    nome = "tudo bem" if (empresa_pj or not palavras) else palavras[0].title()
    valor, venc = brl(conta["valor"]), dbr(conta["vencimento"])
    doc = f" ({conta['documento']})" if conta.get("documento") else ""
    pag = empresa.get("como_pagar", "")
    assinatura = f"\n\n{empresa['nome']}"
    if tipo == "lembrete":
        txt = f"Olá, {nome}! Passando para lembrar que a parcela de {valor}{doc} vence em {venc}. {pag}".strip()
    elif tipo == "vence_hoje":
        txt = f"Olá, {nome}! Sua parcela de {valor}{doc} vence hoje ({venc}). {pag} Se já pagou, desconsidere.".strip()
    else:  # atraso
        txt = (f"Olá, {nome}, tudo bem? Não identificamos o pagamento de {valor}{doc}, vencido em {venc}. "
               f"Se já pagou, pode desconsiderar. Se precisar de outra data, é só responder aqui que a gente combina.")
    return txt + assinatura


def link_whatsapp(telefone: str, texto: str) -> str:
    fone = telefone if telefone.startswith("55") else "55" + telefone
    return f"https://wa.me/{fone}?text={urllib.parse.quote(texto)}"


def lista_do_dia(contas: list[dict], hoje: date, config: dict) -> dict:
    regua, empresa = config["regua"], config["empresa"]
    enviar, humano, sem_telefone = [], [], []
    for c in contas:
        if c.get("pago"):
            continue
        dias = (hoje - date.fromisoformat(c["vencimento"])).days
        tipo = etapa(dias, regua)
        if tipo is None:
            continue
        item = {**c, "dias": dias, "tipo": tipo}
        if tipo == "humano":
            humano.append(item)
        elif len(c.get("telefone", "")) < 10:
            sem_telefone.append(item)
        else:
            item["mensagem"] = mensagem(c, tipo, dias, empresa)
            item["link"] = link_whatsapp(c["telefone"], item["mensagem"])
            enviar.append(item)
    em_aberto = [c for c in contas if not c.get("pago") and date.fromisoformat(c["vencimento"]) < hoje]
    return {
        "data": hoje.isoformat(),
        "enviar": enviar,
        "humano": sorted(humano, key=lambda x: -x["valor"]),
        "sem_telefone": sem_telefone,
        "total_vencido": sum(c["valor"] for c in em_aberto),
    }


def relatorio(r: dict) -> str:
    rot = {"lembrete": "Lembrete", "vence_hoje": "Vence hoje", "atraso": "Atraso"}
    linhas = [f"# Cobrança do dia — {dbr(r['data'])}", "",
              f"Total vencido em aberto: **{brl(r['total_vencido'])}**", "",
              f"## Enviar hoje ({len(r['enviar'])})", "",
              "Clique no link, confira a mensagem e envie. Horário: 8h–18h, seg–sáb.", ""]
    for i in r["enviar"]:
        quando = f"{-i['dias']} dia(s) para vencer" if i["dias"] < 0 else ("hoje" if i["dias"] == 0 else f"{i['dias']} dia(s) de atraso")
        linhas.append(f"- **{i['cliente']}** — {brl(i['valor'])} — {rot[i['tipo']]} ({quando}) — [abrir WhatsApp]({i['link']})")
    linhas += ["", f"## Para uma pessoa ligar ({len(r['humano'])})", "", "Atraso longo: conversa humana, não robô.", ""]
    for i in r["humano"]:
        linhas.append(f"- **{i['cliente']}** — {brl(i['valor'])} — {i['dias']} dias — tel. {i.get('telefone') or 'sem telefone'}")
    if r["sem_telefone"]:
        linhas += ["", f"## Sem telefone no cadastro ({len(r['sem_telefone'])})", ""]
        linhas += [f"- {i['cliente']} — {brl(i['valor'])}" for i in r["sem_telefone"]]
    return "\n".join(linhas) + "\n"


def main() -> None:
    hoje = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
    config = carregar_config()
    r = lista_do_dia(contas_a_receber(config), hoje, config)
    saida = PASTA / "saida" / f"cobranca-{hoje.isoformat()}.md"
    saida.write_text(relatorio(r), encoding="utf-8")
    print(f"{len(r['enviar'])} para enviar, {len(r['humano'])} para ligar, vencido {brl(r['total_vencido'])} -> {saida}")


if __name__ == "__main__":
    main()
