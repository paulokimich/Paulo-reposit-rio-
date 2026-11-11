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


def etapa(dias: int, regua: dict) -> tuple[str, int] | None:
    """Em que etapa da régua a conta está hoje. dias = hoje - vencimento.

    Devolve (tipo, marco) ou None. Cada marco vale por `janela` dias (padrão 3),
    para não perder o aviso se o dia certo cair num domingo; o registro de
    envios garante que cada marco sai uma vez só.

    CARÊNCIA: de 1 a `carencia_dias` (padrão 10) dias de atraso o robô NÃO fala
    com o cliente, porque a baixa do pagamento pode atrasar no sistema e não
    queremos cobrar quem já pagou. Esses aparecem na lista "conferir baixa".
    """
    janela = regua.get("janela", 3)
    carencia = regua.get("carencia_dias", 10)
    if dias == 0:
        return ("vence_hoje", 0)
    for m in regua.get("lembrete_antes", []):
        if m <= dias < min(m + janela, 0):
            return ("lembrete", m)
    if 0 < dias <= carencia:
        return ("carencia", 0)
    if dias >= regua.get("passar_para_humano", 25):
        return ("humano", 0)
    for m in regua.get("atraso", []):
        if m > carencia and m <= dias < m + janela:
            return ("atraso", m)
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


def nome_empresa(conta: dict, empresa: dict) -> str:
    """Com 22 lojas, o cliente reconhece a loja onde comprou: 'Empresa (Loja Centro)'."""
    loja = (conta.get("loja") or "").strip()
    if loja and empresa.get("mostrar_loja", True):
        return f"{empresa['nome']} ({loja})"
    return empresa["nome"]


def parametros(conta: dict, empresa: dict) -> list[str]:
    return [nome_saudacao(conta), brl(conta["valor"]), nome_empresa(conta, empresa), dbr(conta["vencimento"]),
            como_pagar(conta, empresa)]


def por_loja(r: dict) -> list[dict]:
    """Quantos avisos, carências e ligações por loja (para a moça da cobrança e o dono)."""
    lojas: dict[str, dict] = {}
    for grupo in ("enviar", "carencia", "humano", "sem_telefone"):
        for i in r.get(grupo, []):
            l = lojas.setdefault(i.get("loja") or "sem loja", {"loja": i.get("loja") or "sem loja",
                                 "enviar": 0, "carencia": 0, "humano": 0, "sem_telefone": 0, "valor": 0.0})
            l[grupo] += 1
            l["valor"] += i["valor"]
    return sorted(lojas.values(), key=lambda x: -x["valor"])


def mensagem(conta: dict, tipo: str, dias: int, empresa: dict) -> str:
    texto = MODELOS[tipo][1]
    for i, v in enumerate(parametros(conta, empresa), 1):
        texto = texto.replace("{{%d}}" % i, v)
    return texto


def link_whatsapp(telefone: str, texto: str) -> str:
    fone = telefone if telefone.startswith("55") else "55" + telefone
    return f"https://wa.me/{fone}?text={urllib.parse.quote(texto)}"


def chave(item: dict) -> str:
    return f"{item['id']}|{item['vencimento']}|{item['tipo']}|{item['marco']}"


REGISTRO = PASTA / "saida" / "enviados.json"


def carregar_registro() -> dict:
    import json
    try:
        return json.loads(REGISTRO.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return {}


def registrar_listados(r: dict, hoje: date) -> None:
    """Modo manual: marca quem já saiu na lista para não repetir nos dias da janela."""
    import json
    reg = carregar_registro()
    for i in r["enviar"] + r["sem_telefone"]:
        reg.setdefault(chave(i), {"listado": hoje.isoformat()})
    REGISTRO.write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding="utf-8")


def lista_do_dia(contas: list[dict], hoje: date, config: dict, ja: set | None = None) -> dict:
    """ja = chaves já enviadas/listadas antes (não repete o mesmo marco)."""
    ja = ja or set()
    regua, empresa = config["regua"], config["empresa"]
    enviar, humano, sem_telefone, carencia = [], [], [], []
    for c in contas:
        if c.get("pago"):
            continue
        dias = (hoje - date.fromisoformat(c["vencimento"])).days
        e = etapa(dias, regua)
        if e is None:
            continue
        tipo, marco = e
        item = {**c, "dias": dias, "tipo": tipo, "marco": marco}
        if tipo in ("lembrete", "vence_hoje", "atraso") and chave(item) in ja:
            continue
        if tipo == "carencia":
            carencia.append(item)
        elif tipo == "humano":
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
        "carencia": sorted(carencia, key=lambda x: -x["dias"]),
        "total_vencido": sum(c["valor"] for c in em_aberto),
    }


def _tabela_lojas(r: dict) -> list[str]:
    lojas = por_loja(r)
    if len(lojas) <= 1:
        return []
    l = ["## Por loja", "", "| Loja | Avisos | Conferir baixa | Ligar | Sem telefone | Valor envolvido |", "|---|---:|---:|---:|---:|---:|"]
    l += [f"| {x['loja']} | {x['enviar']} | {x['carencia']} | {x['humano']} | {x['sem_telefone']} | {brl(x['valor'])} |" for x in lojas]
    return l + [""]


def relatorio(r: dict) -> str:
    rot = {"lembrete": "Lembrete", "vence_hoje": "Vence hoje", "atraso": "Atraso"}
    linhas = [f"# Cobrança do dia — {dbr(r['data'])}", "",
              f"Total vencido em aberto: **{brl(r['total_vencido'])}**", "",
              *(_tabela_lojas(r)),
              f"## Enviar hoje ({len(r['enviar'])})", "",
              "Clique no link, confira a mensagem e envie. Horário: 8h–18h, seg–sáb.", ""]
    for i in r["enviar"]:
        quando = f"{-i['dias']} dia(s) para vencer" if i["dias"] < 0 else ("hoje" if i["dias"] == 0 else f"{i['dias']} dia(s) de atraso")
        loja = f" [{i['loja']}]" if i.get("loja") else ""
        linhas.append(f"- **{i['cliente']}**{loja} — {brl(i['valor'])} — {rot[i['tipo']]} ({quando}) — [abrir WhatsApp]({i['link']})")
    carencia = r.get("carencia", [])
    linhas += ["", f"## Conferir baixa ({len(carencia)})", "",
               "Vencidos há até 10 dias: o robô NÃO fala com eles ainda. Se já pagaram, dar baixa no sistema.", ""]
    linhas += [f"- {i['cliente']} — {brl(i['valor'])} — venceu {dbr(i['vencimento'])} ({i['dias']} dia(s))" for i in carencia] or ["- Nenhum."]
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
        k = chave(item)
        modelo = MODELOS[item["tipo"]][0]
        base = {"cliente": item["cliente"], "modelo": modelo, "valor": item["valor"]}
        if k in registro and "listado" not in registro[k]:
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
            registro[k] = {"quando": agora.isoformat(timespec="minutes"), "id": res.get("id", "")}
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
    r = lista_do_dia(contas_a_receber(config), hoje, config, set(carregar_registro()))
    saida = PASTA / "saida" / f"cobranca-{hoje.isoformat()}.md"
    texto = relatorio(r)
    if "--enviar" in sys.argv:
        log = disparar(r, config)
        texto += "\n## Envio automático\n\n" + "\n".join(
            f"- {l['cliente']} — {brl(l['valor'])} — {l['modelo']} — {l['status']}" for l in log) + "\n"
        for l in log:
            print(f"{l['status']:<28} {l['cliente']}")
    else:
        registrar_listados(r, hoje)
    saida.write_text(texto, encoding="utf-8")
    print(f"{len(r['enviar'])} avisos, {len(r['humano'])} para ligar, vencido {brl(r['total_vencido'])} -> {saida}")


if __name__ == "__main__":
    main()
