"""Robô de Pós-venda.

Lê o histórico de vendas (planilha CSV exportada do sistema ou, depois, a API da
Moveri) e prepara, para cada cliente, a mensagem certa no momento certo:

- 7 dias depois:   "ficou tudo certo?" + pedir avaliação/indicação
- 90 dias depois:  lembrete de rodízio, calibragem e alinhamento
- 180 dias depois: revisão dos pneus (desgaste) e oferta de avaliação gratuita

Mensagens de pós-venda são "marketing" para a Meta (mais caras e com regras
mais duras), por isso este robô NÃO envia sozinho: monta a lista com botão do
WhatsApp para uma pessoa da empresa enviar. Quem pedir para não receber
(coluna `nao_contatar` = sim) nunca entra na lista.

Uso:  python3 robos/posvenda.py [AAAA-MM-DD]
"""
from __future__ import annotations

import csv
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cobranca import dbr, link_whatsapp, nome_saudacao  # noqa: E402
from moveri import PASTA, _data_iso, carregar_config  # noqa: E402

MARCOS = {
    7: ("Pós-venda 7 dias",
        "Olá, {nome}! Aqui é da {empresa}. Passando para saber se ficou tudo certo com {produto}. "
        "Se tiver qualquer coisa, é só responder aqui. E se puder indicar a gente para um amigo, agradecemos muito! 🙂"),
    90: ("Revisão 90 dias",
         "Olá, {nome}! Já faz uns 3 meses que você colocou {produto} com a gente. "
         "É uma boa hora para rodízio, calibragem e alinhamento: deixa o pneu durar bem mais. "
         "Quer que a gente reserve um horário? — {empresa}"),
    180: ("Avaliação 180 dias",
          "Olá, {nome}! Faz 6 meses da sua compra de {produto}. Que tal passar aqui para uma avaliação "
          "gratuita do desgaste dos pneus? Leva poucos minutos. — {empresa}"),
}


def ler_vendas(caminho: Path) -> list[dict]:
    """CSV com colunas: cliente;telefone;produto;data[;nao_contatar] (separador ; ou ,)."""
    texto = caminho.read_text(encoding="utf-8-sig")
    primeira = texto.splitlines()[0]
    sep = ";" if primeira.count(";") >= primeira.count(",") else ","
    vendas = []
    for i, l in enumerate(csv.DictReader(texto.splitlines(), delimiter=sep), 1):
        if not l.get("cliente") or not l.get("data"):
            continue
        vendas.append({
            "id": str(l.get("id") or i),
            "cliente": l["cliente"].strip(),
            "telefone": "".join(ch for ch in l.get("telefone", "") if ch.isdigit()),
            "produto": (l.get("produto") or "os pneus").strip(),
            "data": _data_iso(l["data"]),
            "nao_contatar": str(l.get("nao_contatar", "")).strip().lower() in ("sim", "s", "1", "true"),
        })
    return vendas


JANELA = 3  # dias de tolerância: se o marco cair num domingo, sai no dia útil seguinte


def marco_do_dia(dias: int) -> int | None:
    for m in MARCOS:
        if m <= dias < m + JANELA:
            return m
    return None


def lista_posvenda(vendas: list[dict], hoje: date, empresa: dict, ja_listados: set | None = None) -> dict:
    """ja_listados: chaves "id|data|marco" que já saíram em listas anteriores (não repete)."""
    ja_listados = ja_listados or set()
    enviar, sem_telefone = [], []
    for v in vendas:
        if v["nao_contatar"]:
            continue
        dias = (hoje - date.fromisoformat(v["data"])).days
        m = marco_do_dia(dias)
        chave = f"{v['cliente']}|{v['data']}|{m}"
        if m is None or chave in ja_listados:
            continue
        rotulo, modelo = MARCOS[m]
        texto = modelo.format(nome=nome_saudacao(v), empresa=empresa["nome"], produto=v["produto"])
        item = {**v, "dias": dias, "marco": rotulo, "mensagem": texto, "chave": chave}
        if len(v["telefone"]) < 10:
            sem_telefone.append(item)
        else:
            item["link"] = link_whatsapp(v["telefone"], texto)
            enviar.append(item)
    return {"data": hoje.isoformat(), "enviar": enviar, "sem_telefone": sem_telefone}


def relatorio(r: dict) -> str:
    l = [f"# Pós-venda do dia — {dbr(r['data'])}", "", f"## Enviar hoje ({len(r['enviar'])})", "",
         "Mensagens de relacionamento: uma pessoa confere e envia pelo WhatsApp.", ""]
    l += [f"- **{i['cliente']}** — {i['marco']} (comprou {dbr(i['data'])}: {i['produto']}) — [abrir WhatsApp]({i['link']})"
          for i in r["enviar"]] or ["- Ninguém hoje."]
    if r["sem_telefone"]:
        l += ["", f"## Sem telefone ({len(r['sem_telefone'])})", ""]
        l += [f"- {i['cliente']} — {i['marco']}" for i in r["sem_telefone"]]
    return "\n".join(l) + "\n"


REGISTRO = PASTA / "saida" / "posvenda_listados.json"


def carregar_listados() -> set:
    import json
    try:
        return set(json.loads(REGISTRO.read_text(encoding="utf-8")))
    except (FileNotFoundError, ValueError):
        return set()


def salvar_listados(listados: set, r: dict) -> None:
    import json
    novos = listados | {i["chave"] for i in r["enviar"] + r["sem_telefone"]}
    REGISTRO.write_text(json.dumps(sorted(novos), ensure_ascii=False, indent=1), encoding="utf-8")


def main() -> None:
    hoje = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
    cfg = carregar_config()
    listados = carregar_listados()
    r = lista_posvenda(ler_vendas(PASTA / cfg["posvenda"]["arquivo_vendas"]), hoje, cfg["empresa"], listados)
    salvar_listados(listados, r)
    saida = PASTA / "saida" / f"posvenda-{hoje.isoformat()}.md"
    saida.write_text(relatorio(r), encoding="utf-8")
    print(f"{len(r['enviar'])} mensagens de pós-venda -> {saida}")


if __name__ == "__main__":
    main()
