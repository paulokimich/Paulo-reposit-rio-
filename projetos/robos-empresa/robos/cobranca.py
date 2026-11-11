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


# Modelos de mensagem. Os MESMOS textos são cadastrados na Meta como modelos
# "Utilidade" (pt_BR) para o envio automático: {{1}} nome, {{2}} valor,
# {{3}} empresa, {{4}} data, {{5}} como pagar. Ver vendedor/../MODELOS-WHATSAPP.md
MODELOS = {
    "lembrete": ("aviso_vencimento",
                 "Olá, {{1}}! Tudo bem? 😊 Passando só para avisar que sua parcela de {{2}} com a {{3}} "
                 "vence em {{4}}. Para pagar: {{5}}. Se já pagou, pode desconsiderar. Qualquer dúvida, é só responder aqui."),
    "vence_hoje": ("aviso_vence_hoje",
                   "Olá, {{1}}! Bom dia! Lembrete rápido: sua parcela de {{2}} com a {{3}} vence hoje, {{4}}. "
                   "Para pagar: {{5}}. Se já pagou, desconsidere. Obrigado pela parceria!"),
    "atraso": ("aviso_pagamento_pendente",
               "Olá, {{1}}, tudo bem? Ainda não localizamos o pagamento da parcela de {{2}} com a {{3}}, "
               "que venceu em {{4}}. Pode ter sido só um esquecimento, acontece. Para pagar: {{5}}. "
               "Se já pagou, desconsidere. Se precisar de outra data, responda aqui que a gente combina. 🙂"),
}
_PJ = ("LTDA", "ME", "EIRELI", "SA", "EPP", "TRANSPORTES", "TRANSPORTADORA", "FAZENDA", "OFICINA", "COMERCIO", "AUTO")


def nome_saudacao(conta: dict) -> str:
    if conta.get("contato"):
        return conta["contato"].split()[0].title()
    palavras = [p for p in conta["cliente"].replace(".", " ").split() if not p.startswith("(")]
    if not palavras:
        return "cliente"
    if any(p.upper() in _PJ for p in palavras):  # empresa: usa as 2 primeiras palavras do nome
        return " ".join(p.title() for p in palavras[:2] if p.upper() not in ("LTDA", "ME", "EIRELI", "SA", "EPP"))
    return palavras[0].title()


PADRAO_PAGAR = "escolha Pix ou boleto e responda esta mensagem que a gente envia na hora"


def como_pagar(conta: dict, empresa: dict) -> str:
    """O cliente escolhe Pix ou boleto. Se a conta já tem boleto (link ou linha digitável),
    manda direto; se o cliente prefere Pix e a empresa tem chave, manda a chave;
    senão oferece os dois e a moça da cobrança responde com o que ele escolher."""
    forma = str(conta.get("forma_pagamento", "")).strip().lower()
    boleto = (conta.get("link_boleto") or conta.get("linha_digitavel") or "").strip()
    pix = (empresa.get("pix") or "").strip()
    if forma == "boleto" and boleto:
        return f"boleto {boleto}"
    if forma == "pix" and pix:
        return f"Pix na chave {pix}"
    return (empresa.get("como_pagar") or PADRAO_PAGAR).rstrip(". ")


def parametros(conta: dict, empresa: dict) -> list[str]:
    return [nome_saudacao(conta), brl(conta["valor"]), empresa["nome"], dbr(conta["vencimento"]),
            como_pagar(conta, empresa)]


def mensagem(conta: dict, tipo: str, dias: int, empresa: dict) -> str:
    texto = MODELOS[tipo][1]
    for i, v in enumerate(parametros(conta, empresa), 1):
        texto = texto.replace("{{%d}}" % i, v)
    return texto


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


def disparar(r: dict, config: dict, agora=None, enviar_fn=None) -> list[dict]:
    """Envia sozinho os avisos do dia pelo WhatsApp oficial. Devolve o log."""
    import json
    import whatsapp

    cfg = config.get("whatsapp", {})
    agora = agora or whatsapp.agora_cuiaba()
    enviar_fn = enviar_fn or whatsapp.enviar_modelo
    ativo = bool(cfg.get("ativo")) and cfg.get("phone_number_id") not in (None, "", "PENDENTE")
    ok, motivo = whatsapp.pode_enviar_agora(cfg, agora)
    reg_path = PASTA / "saida" / "enviados.json"
    try:
        registro = json.loads(reg_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        registro = {}
    log, enviados_hoje = [], 0
    for item in r["enviar"]:
        chave = f"{item['id']}|{item['vencimento']}|{item['tipo']}|{item['dias']}"
        modelo = MODELOS[item["tipo"]][0]
        base = {"cliente": item["cliente"], "modelo": modelo, "valor": item["valor"]}
        if chave in registro:
            log.append({**base, "status": "já enviado antes"})
            continue
        if not ok:
            log.append({**base, "status": f"não enviado: {motivo}"})
            continue
        if enviados_hoje >= cfg.get("limite_dia", 50):
            log.append({**base, "status": "não enviado: limite do dia"})
            continue
        if not ativo:
            log.append({**base, "status": "TESTE: enviaria agora"})
            continue
        res = enviar_fn(item["telefone"], modelo, parametros(item, config["empresa"]), cfg)
        if res.get("ok"):
            registro[chave] = {"quando": agora.isoformat(timespec="minutes"), "id": res.get("id", "")}
            enviados_hoje += 1
            log.append({**base, "status": "ENVIADO"})
        else:
            log.append({**base, "status": f"ERRO: {res.get('erro')}"})
    reg_path.write_text(json.dumps(registro, ensure_ascii=False, indent=1), encoding="utf-8")
    return log


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    hoje = date.fromisoformat(args[0]) if args else date.today()
    config = carregar_config()
    r = lista_do_dia(contas_a_receber(config), hoje, config)
    saida = PASTA / "saida" / f"cobranca-{hoje.isoformat()}.md"
    texto = relatorio(r)
    if "--enviar" in sys.argv:
        log = disparar(r, config)
        texto += "\n## Envio automático\n\n" + "\n".join(
            f"- {l['cliente']} — {brl(l['valor'])} — {l['modelo']} — {l['status']}" for l in log) + "\n"
        for l in log:
            print(f"{l['status']:<28} {l['cliente']}")
    saida.write_text(texto, encoding="utf-8")
    print(f"{len(r['enviar'])} avisos, {len(r['humano'])} para ligar, vencido {brl(r['total_vencido'])} -> {saida}")


if __name__ == "__main__":
    main()
