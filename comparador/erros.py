class ErroDeNegocio(Exception):
    """Regra de negócio violada. A mensagem, em português, é mostrada à gestora.

    As exceções de regra de negócio de todos os módulos herdam desta.
    """

    def __init__(self, mensagem):
        super().__init__(mensagem)
        self.mensagem = mensagem


class AcessoNegado(ErroDeNegocio):
    """O Gestor tentou mexer no que é de outro Gestor (Loja, Pedido). As telas respondem 403."""
