class ErroDeNegocio(Exception):
    """Regra de negócio violada. A mensagem, em português, é mostrada à gestora.

    As exceções de regra de negócio de todos os módulos herdam desta.
    """

    def __init__(self, mensagem):
        super().__init__(mensagem)
        self.mensagem = mensagem
