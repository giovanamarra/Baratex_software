"""Testes pelo cliente HTTP: só login obrigatório e autorização (spec, Testing Decisions)."""

from django.urls import reverse

from catalogos.casos_de_uso import cadastrar_fornecedor
from contas.auxiliares_de_teste import SENHA_DE_TESTE, criar_gestor
from extracao.catalogos_ficticios import CartaoFicticio, catalogo_ficticio_layout_a
from importacao.auxiliares_de_teste import TesteComArquivosEnviados, arquivo_enviado
from importacao.casos_de_uso import iniciar_importacao


class TelasDeImportacaoTests(TesteComArquivosEnviados):
    def test_abrir_pela_url_a_revisao_de_outro_gestor_e_recusado(self):
        gestora = criar_gestor('gestora')
        criar_gestor('outro-gestor')
        fornecedor = cadastrar_fornecedor(gestora, 'Fornecedor Alfa')
        catalogo = arquivo_enviado(catalogo_ficticio_layout_a([CartaoFicticio('1001', 'Balde Ficticio')]))
        revisao = iniciar_importacao(gestora, fornecedor, catalogo)
        self.client.login(username='outro-gestor', password=SENHA_DE_TESTE)

        resposta = self.client.get(reverse('revisao', kwargs={'pk': revisao.pk}))

        self.assertContains(resposta, 'Esta Revisão é de outro Gestor.', status_code=403)
        self.assertNotContains(resposta, 'Balde Ficticio', status_code=403)
