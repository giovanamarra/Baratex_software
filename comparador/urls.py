from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import path

from contas import views as contas

# Toda página tem nome: o teste de login obrigatório percorre esta lista.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('entrar/', LoginView.as_view(template_name='contas/entrar.html'), name='entrar'),
    path('', contas.inicio, name='inicio'),
]
