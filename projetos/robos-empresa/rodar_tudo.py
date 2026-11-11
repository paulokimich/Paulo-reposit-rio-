"""Roda todos os robôs da empresa de uma vez e gera um painel único do dia.

    python3 rodar_tudo.py [AAAA-MM-DD] [--enviar]

--enviar liga o envio automático dos avisos de vencimento (só funciona se
`whatsapp.ativo` = true no config; senão fica em modo teste).
Robô sem dados (arquivo ainda não entregue) é pulado com aviso, sem quebrar os outros.
É este comando que a rotina agendada vai rodar toda manhã.
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

PASTA = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA / "robos"))

import cobranca  # noqa: E402
import contabil  # noqa: E402
import posvenda  # noqa: E402
import resumo  # noqa: E402
from moveri import carregar_config, contas_a_receber  # noqa: E402


def rodar(hoje: date, enviar: bool = False, gravar: bool = False) -> str:
    cfg = carregar_config()
    partes = [f"# Robôs da empresa — {cobranca.dbr(hoje.isoformat())}", "",
              f"Fonte dos dados: **{cfg.get('fonte', 'exemplo')}**" +
              (" (DADOS DE EXEMPLO, não são clientes reais)" if cfg.get("fonte", "exemplo") == "exemplo" else ""), ""]
    status = []

    try:
        contas = contas_a_receber(cfg)
        r = cobranca.lista_do_dia(contas, hoje, cfg, set(cobranca.carregar_registro()) if gravar else set())
        partes.append(cobranca.relatorio(r))
        if enviar:
            log = cobranca.disparar(r, cfg)
            partes += ["## Envio automático", ""] + [f"- {x['cliente']} — {x['status']}" for x in log] + [""]
        elif gravar:
            cobranca.registrar_listados(r, hoje)
        partes.append("## Resumo para o dono\n\n```\n" + resumo.texto(resumo.resumo(contas, hoje)) + "```\n")
        status.append(f"Avisos: {len(r['enviar'])} hoje, {len(r['carencia'])} em carência (conferir baixa), {len(r['humano'])} para ligar")
    except FileNotFoundError as e:
        status.append(f"Avisos e Gerente: sem dados ({Path(e.filename).name} não entregue)")

    try:
        c = cfg["contabil"]
        f = contabil.fechamento(contabil.ler_extrato(PASTA / c["arquivo_extrato"]), hoje.strftime("%Y-%m"), c["regras"])
        pagar = json.loads((PASTA / c["arquivo_contas_pagar"]).read_text(encoding="utf-8"))
        partes.append(contabil.relatorio(f, contabil.contas_da_semana(pagar, hoje), hoje))
        status.append(f"Contábil: {f['qtd']} lançamentos, {len(f['pendentes'])} a classificar")
    except (FileNotFoundError, KeyError) as e:
        status.append(f"Contábil: sem dados ({e})")

    try:
        listados = posvenda.carregar_listados() if gravar else set()
        p = posvenda.lista_posvenda(posvenda.ler_vendas(PASTA / cfg["posvenda"]["arquivo_vendas"]), hoje, cfg["empresa"], listados)
        if gravar:
            posvenda.salvar_listados(listados, p)
        partes.append(posvenda.relatorio(p))
        status.append(f"Pós-venda: {len(p['enviar'])} mensagens")
    except (FileNotFoundError, KeyError) as e:
        status.append(f"Pós-venda: sem dados ({e})")

    partes[4:4] = ["## Situação", ""] + [f"- {s}" for s in status] + [""]
    return "\n".join(partes)


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    hoje = date.fromisoformat(args[0]) if args else date.today()
    texto = rodar(hoje, "--enviar" in sys.argv, gravar=True)
    saida = PASTA / "saida" / f"painel-{hoje.isoformat()}.md"
    saida.write_text(texto, encoding="utf-8")
    print(texto.split("## Situação")[1].split("\n#")[0].strip())
    print(f"\n-> {saida}")


if __name__ == "__main__":
    main()
