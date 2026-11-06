"""Tela de corrigir a data do Catálogo, em duas etapas e sem JavaScript (ticket 33). As regras estão nos testes
do caso de uso; aqui, o fluxo da tela."""

from datetime import date

from django.urls import reverse

from catalogos.casos_de_uso import buscar_ofertas, cadastrar_fornecedor, correcoes_da_data, obter_catalogo
from contas.auxiliares_de_teste import SENHA_DE_TESTE, criar_gestor
from extracao.catalogos_ficticios import CartaoFicticio
from importacao.auxiliares_de_teste import TesteComArquivosEnviados, importar_e_confirmar

# Datas do passado: a tela usa o dia de hoje de verdade para recusar data futura.
IMPORTADO_EM = date(2026, 3, 10)


class TelaDeCorrigirDataTests(TesteComArquivosEnviados):
    def setUp(self):
        self.gestora = criar_gestor('gestora')
        self.socio = criar_gestor('socio')
        self.alfa = cadastrar_fornecedor(self.gestora, 'Alfa')
        balde = [CartaoFicticio('1001', 'Balde Ficticio', '10,00', '6')]
        self.errado = importar_e_confirmar(self.gestora, self.alfa, balde, '05/03/2026', IMPORTADO_EM)
        self.outro = importar_e_confirmar(self.gestora, self.alfa, balde, '01/02/2026', IMPORTADO_EM)
        self.client.login(username='socio', password=SENHA_DE_TESTE)  # não foi quem importou
        self.url = reverse('corrigir_data_do_catalogo', kwargs={'pk': self.errado.pk})

    def test_ver_o_impacto_mostra_a_mensagem_o_aviso_e_os_botoes_confirmar_e_voltar(self):
        resposta = self.client.get(self.url, {'data': '10/2025'})

        self.assertContains(
            resposta, '<p class="atencao" role="note"><strong>Atenção:</strong> Com a nova data, 1 Oferta deste '
            'Catálogo deixa de ser vigente.</p>', html=True,
        )
        self.assertContains(
            resposta, '<p class="atencao" role="note"><strong>Atenção:</strong> Este Catálogo é mais antigo que o '
            'de 01/02/2026 deste Fornecedor: os códigos que estão nos dois continuam com o preço do mais recente.</p>',
            html=True,
        )
        self.assertContains(resposta, f'<form method="post" action="{self.url}">')
        self.assertContains(resposta, '<input type="hidden" name="data" value="10/2025">', html=True)
        self.assertContains(resposta, '<button class="botao botao--primario" type="submit">Confirmar a nova data</button>', html=True)
        self.assertContains(
            resposta, f'<a class="botao botao--secundario" href="{reverse("catalogo", kwargs={"pk": self.errado.pk})}">Voltar</a>',
            html=True,
        )
        self.assertEqual(obter_catalogo(self.gestora, self.errado.pk).data_exibida, '05/03/2026')  # só aviso

    def test_ver_o_impacto_de_uma_data_recusada_mostra_o_erro_e_nao_oferece_confirmar(self):
        resposta = self.client.get(self.url, {'data': '31/02/2026'})

        self.assertContains(
            resposta, '<p class="erro" role="alert"><strong>Não foi possível ver o impacto:</strong> Informe a data do '
            'Catálogo como dia/mês/ano ou mês/ano, por exemplo 15/10/2026 ou 10/2026.</p>', html=True,
        )
        self.assertContains(resposta, 'value="31/02/2026"')  # a gestora corrige o que digitou
        self.assertNotContains(resposta, 'Confirmar a nova data')

    def test_confirmar_a_nova_data_corrige_registra_quem_corrigiu_e_volta_ao_catalogo(self):
        resposta = self.client.post(self.url, {'data': '10/2025'}, follow=True)

        self.assertRedirects(resposta, reverse('catalogo', kwargs={'pk': self.errado.pk}))
        self.assertContains(
            resposta, '<p class="aviso" role="status"><strong>Pronto:</strong> Data do Catálogo corrigida de '
            '05/03/2026 para 10/2025.</p>', html=True,
        )
        self.assertEqual(obter_catalogo(self.gestora, self.errado.pk).data_exibida, '10/2025')
        self.assertEqual([c.gestor.get_username() for c in correcoes_da_data(self.gestora, self.errado.pk)], ['socio'])
        vigente = buscar_ofertas(self.gestora, '1001').ofertas
        self.assertEqual([o.catalogo.data_exibida for o in vigente], ['01/02/2026'])
