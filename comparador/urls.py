from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from contas import views as contas
from contas.formularios import FormularioDeEntrada

# Toda página tem nome: o teste de login obrigatório percorre esta lista.
urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'entrar/',
        LoginView.as_view(
            template_name='contas/entrar.html', authentication_form=FormularioDeEntrada
        ),
        name='entrar',
    ),
    path('sair/', LogoutView.as_view(), name='sair'),
    path('', contas.inicio, name='inicio'),
    path('lojas/<int:pk>/editar/', contas.editar_loja, name='editar_loja'),
]
