import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "robos"))
from cobranca import brl, lista_do_dia  # noqa: E402
from moveri import carregar_config, contas_a_receber  # noqa: E402
from resumo import resumo  # noqa: E402


class TestCobranca(unittest.TestCase):
    def setUp(self):
        self.cfg = carregar_config()
        self.contas = contas_a_receber(self.cfg)
        self.r = lista_do_dia(self.contas, date(2026, 11, 9), self.cfg)

    def test_regua(self):
        tipos = {i["id"]: i["tipo"] for i in self.r["enviar"]}
        self.assertEqual(tipos, {"1": "lembrete", "2": "vence_hoje", "3": "atraso", "4": "atraso"})

    def test_humano_sem_telefone_e_pago(self):
        self.assertEqual([i["id"] for i in self.r["humano"]], ["6"])
        self.assertEqual([i["id"] for i in self.r["sem_telefone"]], ["5"])
        self.assertNotIn("7", [i["id"] for i in self.r["enviar"] + self.r["humano"]])

    def test_link_e_tom(self):
        item = next(i for i in self.r["enviar"] if i["id"] == "3")
        self.assertTrue(item["link"].startswith("https://wa.me/5565999990003?text="))
        for proibido in ("protesto", "SPC", "Serasa", "justiça"):
            self.assertNotIn(proibido, item["mensagem"])

    def test_brl(self):
        self.assertEqual(brl(1280.5), "R$ 1.280,50")

    def test_resumo(self):
        r = resumo(self.contas, date(2026, 11, 9))
        self.assertEqual(r["vencido"], 3900 + 320 + 760 + 2100)
        self.assertEqual(r["vence_hoje"], 1280.5)
        self.assertEqual(r["vence_7d"], 450 + 5400)


class TestEnvioAutomatico(unittest.TestCase):
    def setUp(self):
        from moveri import PASTA
        self.reg = PASTA / "saida" / "enviados.json"
        self.backup = self.reg.read_text() if self.reg.exists() else None
        if self.reg.exists():
            self.reg.unlink()
        self.cfg = carregar_config()
        self.r = lista_do_dia(contas_a_receber(self.cfg), date(2026, 11, 9), self.cfg)

    def tearDown(self):
        if self.reg.exists():
            self.reg.unlink()
        if self.backup is not None:
            self.reg.write_text(self.backup)

    def test_envia_uma_vez_e_respeita_horario(self):
        from datetime import datetime
        from cobranca import disparar
        from whatsapp import CUIABA
        cfg = {**self.cfg, "whatsapp": {**self.cfg["whatsapp"], "ativo": True, "phone_number_id": "123"}}
        chamadas = []
        fake = lambda tel, modelo, params, c: chamadas.append((tel, modelo, params)) or {"ok": True, "id": "x"}
        seg_9h = datetime(2026, 11, 9, 9, 0, tzinfo=CUIABA)
        log = disparar(self.r, cfg, seg_9h, fake)
        self.assertEqual([l["status"] for l in log], ["ENVIADO"] * 4)
        self.assertEqual(chamadas[0][1], "aviso_vencimento")
        self.assertEqual(len(chamadas[0][2]), 5)
        log2 = disparar(self.r, cfg, seg_9h, fake)  # rodou de novo: não repete
        self.assertTrue(all(l["status"] == "já enviado antes" for l in log2))
        self.assertEqual(len(chamadas), 4)
        self.reg.unlink()
        noite = datetime(2026, 11, 9, 20, 0, tzinfo=CUIABA)
        self.assertTrue(all("fora do horário" in l["status"] for l in disparar(self.r, cfg, noite, fake)))

    def test_modo_teste_nao_envia(self):
        from datetime import datetime
        from cobranca import disparar
        from whatsapp import CUIABA
        log = disparar(self.r, self.cfg, datetime(2026, 11, 9, 9, 0, tzinfo=CUIABA),
                       lambda *a: self.fail("não deveria enviar"))
        self.assertTrue(all(l["status"] == "TESTE: enviaria agora" for l in log))

    def test_tom_gentil(self):
        from cobranca import MODELOS
        for _, texto in MODELOS.values():
            self.assertIn("desconsider", texto)
            for palavra in ("protesto", "SPC", "Serasa", "cobrança", "débito", "dívida"):
                self.assertNotIn(palavra, texto)


class TestPlanilha(unittest.TestCase):
    def test_csv_brasileiro(self):
        cfg = {"fonte": "planilha", "arquivo_planilha": "dados/exemplo_planilha.csv"}
        c = contas_a_receber(cfg)
        self.assertEqual(c[1]["valor"], 3900.0)
        self.assertEqual(c[1]["vencimento"], "2026-11-08")
        self.assertEqual(c[0]["telefone"], "65999990001")
        self.assertTrue(c[2]["pago"])


class TestContabil(unittest.TestCase):
    def test_fechamento(self):
        from contabil import contas_da_semana, fechamento, ler_extrato
        from moveri import PASTA
        cfg = carregar_config()["contabil"]
        f = fechamento(ler_extrato(PASTA / cfg["arquivo_extrato"]), "2026-11", cfg["regras"])
        self.assertAlmostEqual(f["entradas"], 21170.0)
        self.assertAlmostEqual(f["resultado"], -1349.9)
        self.assertEqual([p["descricao"] for p in f["pendentes"]], ["PIX ENVIADO JOSE ALGUEM"])
        import json
        pagar = json.loads((PASTA / cfg["arquivo_contas_pagar"]).read_text(encoding="utf-8"))
        self.assertEqual(len(contas_da_semana(pagar, date(2026, 11, 9))), 3)


class TestVendedor(unittest.TestCase):
    def test_sistema_e_sinal(self):
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "vendedor"))
        from vendedor import SINAL_HUMANO, carregar_ficha, montar_sistema, separar_resposta
        ficha = carregar_ficha()
        s = montar_sistema(ficha)
        self.assertIn("295/80 R22.5", s)
        self.assertNotIn("_aviso", s)
        self.assertEqual(s, montar_sistema(ficha))  # estável para o cache
        texto, humano = separar_resposta("Um vendedor já continua.\n" + SINAL_HUMANO)
        self.assertTrue(humano)
        self.assertNotIn(SINAL_HUMANO, texto)


if __name__ == "__main__":
    unittest.main()
