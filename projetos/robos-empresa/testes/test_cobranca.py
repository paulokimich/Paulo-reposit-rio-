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
