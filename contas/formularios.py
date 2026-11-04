from django.contrib.auth.forms import AuthenticationForm


class FormularioDeEntrada(AuthenticationForm):
    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': 'Usuário ou senha incorretos.',
    }
