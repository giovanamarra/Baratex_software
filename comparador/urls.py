from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from catalogos import views as catalogos
from contas import views as contas
from contas.formularios import FormularioDeEntrada
from importacao import views as importacao

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
    path('fornecedores/', catalogos.fornecedores, name='fornecedores'),
    path('fornecedores/<int:pk>/catalogos/', catalogos.catalogos_do_fornecedor, name='catalogos_do_fornecedor'),
    path('importar/', importacao.importar, name='importar'),
    path('revisoes/<int:pk>/', importacao.revisao, name='revisao'),
    path('revisoes/<int:pk>/confirmar/', importacao.confirmar, name='confirmar_revisao'),
    path('revisoes/<int:pk>/abandonar/', importacao.abandonar, name='abandonar_revisao'),
]
